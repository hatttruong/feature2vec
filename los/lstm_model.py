'''
Reference:
https://github.com/yuchenlin/lstm_sentence_classifier/blob/master/LSTM_sentence_classifier.py

'''
# -*- coding: utf-8 -*-
import torch
import torch.autograd as autograd
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
import data_loader
import os
import random
import logging
from sklearn import metrics
from sklearn.metrics.cluster import contingency_matrix
import pandas as pd
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool
import multiprocessing

# define a Handler which writes INFO messages or higher to the sys.stderr
console = logging.StreamHandler()
console.setLevel(logging.INFO)

# set a format which is simpler for console use
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(message)s')

# tell the handler to use this format
console.setFormatter(formatter)

# add the handler to the root logger
logger = logging.getLogger(__name__)
logger.addHandler(console)


torch.set_num_threads(8)
torch.manual_seed(1)
random.seed(1)


class LstmLosClassifier(nn.Module):

    def __init__(self, embedding_dim, hidden_dim, feature_size, label_size,
                 weights_matrix=None):
        super(LstmLosClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.feature_embeddings = nn.Embedding(feature_size, embedding_dim)
        self.non_trainable = False
        if weights_matrix is not None:
            self.non_trainable = True
            self.feature_embeddings.weight.data.copy_(
                torch.from_numpy(weights_matrix))
            if self.non_trainable:
                self.feature_embeddings.weight.requires_grad = False

        self.lstm = nn.LSTM(embedding_dim, hidden_dim)
        self.hidden2label = nn.Linear(hidden_dim, label_size)
        self.hidden = self.init_hidden()

    def init_hidden(self):
        # the first is the hidden h
        # the second is the cell  c
        return (autograd.Variable(torch.zeros(1, 1, self.hidden_dim)),
                autograd.Variable(torch.zeros(1, 1, self.hidden_dim)))

    def forward(self, events):
        embeds = self.feature_embeddings(events)
        x = embeds.view(len(events), 1, -1)
        lstm_out, self.hidden = self.lstm(x, self.hidden)
        y = self.hidden2label(lstm_out[-1])
        log_probs = F.log_softmax(y, dim=1)
        return log_probs


def get_scores(truth, pred, prefix=''):
    assert len(truth) == len(pred)
    right = 0
    for i in range(len(truth)):
        if truth[i] == pred[i]:
            right += 1.0
    acc = right / len(truth)
    ari = metrics.adjusted_rand_score(truth, pred)
    ami = metrics.adjusted_mutual_info_score(truth, pred)
    mmi = metrics.normalized_mutual_info_score(truth, pred)
    mi = metrics.mutual_info_score(truth, pred)
    v_measure = metrics.v_measure_score(truth, pred)
    return {prefix + 'acc': acc,
            prefix + 'ari': ari,
            prefix + 'ami': ami,
            prefix + 'mmi': mmi,
            prefix + 'mi': mi,
            prefix + 'v_measure': v_measure}


def train(hidden_dim=50, epoch=5, optimizer_type='adam', lr=1e-3, clip=0.25,
          pretrained_path=None, los_splitters=[], save_best_model=False):
    """Summary

    Args:
        hidden_dim (int, optional): Description
        epoch (int, optional): Description
        optimizer_type (str, optional): Description
        lr (float, optional): should use 1e-2 if using optimize sgd, 1e-3 with adam
        clip (float, optional): Description
        pretrained_path (TYPE): Description
        los_splitters (list, optional): Description
        save_best_model (bool, optional): Description

    Returns:
        list: list of dictionary
            {epoch: 1, avg_loss: 0, train_acc: 0, test_acc: 0}

    Deleted Parameters:
        los_groups (str, optional): Description
    """
    EMBEDDING_DIM = 100
    MAX_NO_UP_EPOCH = 3

    logger.info('Train LSTM with parameters: %s', locals())
    result = data_loader.load_los_data(
        los_splitters=los_splitters, pretrained_path=pretrained_path)
    train_data = result['train_data']
    test_data = result['test_data']
    feature_to_idx = result['feature_to_idx']
    label_to_idx = result['label_to_idx']
    weights_matrix = result['weights_matrix']

    best_test_acc = 0.0
    model = LstmLosClassifier(embedding_dim=EMBEDDING_DIM,
                              hidden_dim=hidden_dim,
                              feature_size=len(feature_to_idx),
                              label_size=len(label_to_idx),
                              weights_matrix=weights_matrix)
    loss_function = nn.NLLLoss()

    # define optimizer
    optimizer = torch.optim.SGD(model.parameters(), lr=lr)
    if optimizer_type == 'adam':
        optimizer = optim.Adam(model.parameters(), lr=lr)

    no_up = 0
    epoch_results = []
    for i in range(epoch):
        random.shuffle(train_data)
        logger.info('Epoch: %d start!', i + 1)
        temp_result, avg_loss = train_epoch(model, train_data, loss_function,
                                            optimizer, feature_to_idx,
                                            label_to_idx, i + 1, lr, clip)
        # logger.info('train_epoch result: %s', temp_result)
        test_scores = evaluate(model, test_data, loss_function,
                               feature_to_idx, label_to_idx)
        # logger.info('test_scores: %s', test_scores)
        temp_result.update(test_scores)
        epoch_results.append(temp_result)

        # stop training if avg_loss is nan
        if avg_loss == float('nan'):
            logger.info('WARNING: avg_loss is nan, STOP training')
            break

        test_acc = test_scores['test_acc']
        if test_acc > best_test_acc:
            best_test_acc = test_acc
            if save_best_model:
                os.system('rm ../models/los_best_model_acc_*.model')
                logger.info('New Best Test!!!')
                torch.save(model.state_dict(),
                           '../models/los_best_model_acc_' +
                           str(int(test_acc * 10000)) + '.model')
            no_up = 0
        else:
            no_up += 1
            logger.info('WARNING: No better model after %s epoch', no_up)
            if no_up >= MAX_NO_UP_EPOCH:
                logger.info(
                    'STOP TRAINING: No better model after %s epoch',
                    MAX_NO_UP_EPOCH)
                break
    return epoch_results


def evaluate(model, data, loss_function, feature_to_idx, label_to_idx):
    model.eval()
    avg_loss = 0.0
    truth_res = []
    pred_res = []

    for item in data:
        events = item['events']
        label = item['los_group']
        truth_res.append(label_to_idx[label])
        # detaching it from its history on the last instance.
        model.hidden = model.init_hidden()
        events = data_loader.prepare_sequence(events, feature_to_idx)
        label = data_loader.prepare_label(label, label_to_idx)
        pred = model(events)
        pred_label = pred.data.max(1)[1].numpy()
        pred_res.extend(pred_label)

        loss = loss_function(pred, label)
        avg_loss += loss.item()
    avg_loss /= len(data)
    scores = get_scores(truth_res, pred_res, prefix='test_')
    logger.info('Evaluate: \tavg_loss:%g \ttest acc: %s',
                avg_loss, scores['test_acc'])
    return scores


def train_epoch(model, train_data, loss_function, optimizer, feature_to_idx,
                label_to_idx, epoch_th, lr, clip):
    """Summary

    Args:
        model (TYPE): Description
        train_data (TYPE): Description
        loss_function (TYPE): Description
        optimizer (TYPE): Description
        feature_to_idx (TYPE): Description
        label_to_idx (TYPE): Description
        epoch_th (TYPE): Description

    Returns:
        DICT: {'epoch': 9, 'avg_loss': 0.8, 'train_acc': 0.7}
    """
    model.train()

    avg_loss = 0.0
    count = 0
    truth_res = []
    pred_res = []
    batch_sent = []

    for item in train_data:
        events = item['events']
        label = item['los_group']
        truth_res.append(label_to_idx[label])
        # detaching it from its history on the last instance.
        model.hidden = model.init_hidden()
        events = data_loader.prepare_sequence(events, feature_to_idx)
        label = data_loader.prepare_label(label, label_to_idx)
        pred = model(events)
        pred_label = pred.data.max(1)[1].numpy()
        # logger.debug('predict result: %s, pred_label: %s', pred.data, pred_label)
        pred_res.extend(pred_label)

        model.zero_grad()
        loss = loss_function(pred, label)
        avg_loss += loss.item()
        count += 1
        if count % 500 == 0:
            logger.info('Epoch: %d \titerations: %d \tloss: %g',
                        epoch_th, count, loss.item())

        loss.backward()

        # `clip_grad_norm` helps prevent the exploding gradient problem in RNNs / LSTMs.
        if model.non_trainable is False:
            nn.utils.clip_grad_norm_(model.parameters(), clip)
            for p in model.parameters():
                # re-check if this model could be trainable
                if p.grad is None:
                    break
                p.data.add_(-lr, p.grad.data)

        optimizer.step()

    avg_loss /= len(train_data)
    # logger.debug('truth_res: %s', truth_res)
    # logger.debug('pred_res: %s', pred_res)

    scores = get_scores(truth_res, pred_res, prefix='train_')
    scores.update({'epoch': epoch_th, 'avg_loss': avg_loss})
    logger.info('Epoch: %d done. \tavg_loss: %g \tacc: %g',
                epoch_th, avg_loss, scores['train_acc'])

    return scores, avg_loss


def grid_search(pretrained_dir, los_groups_path):
    """Summary
    """
    pretrained_paths = [None]
    pretrained_paths.extend(
        [join(pretrained_dir, f) for f in listdir(pretrained_dir)
         if isfile(join(pretrained_dir, f)) and '.vec' in f])

    los_groups = data_loader.load_los_groups(los_groups_path)
    logger.info('Total pretrained paths: %s',
                ','.join([f if f is not None else 'None' for f in pretrained_paths]))
    logger.info('Total los groups: %s',
                ','.join([g['name'] for g in los_groups]))

    epochs = 500
    hidden_dim = 100
    optimizer_type = 'adam'

    skip = 1
    logger.info('START GRID SEARCH...')

    for los_group in los_groups:
        for pretrained_path in reversed(pretrained_paths):
            if skip > 0:
                skip -= 1
                continue

            logger.info('START LSTM: los_group=%s, pretrained_path=%s',
                        los_group['values'], pretrained_path)
            results = train(hidden_dim=hidden_dim, epoch=epochs,
                            optimizer_type=optimizer_type,
                            pretrained_path=pretrained_path,
                            los_splitters=los_group['values'])
            for item in results:
                item['los_group'] = los_group['name']
                item['pretrained_path'] = pretrained_path

            df = pd.DataFrame(results)
            short_pretrain_path = pretrained_path.split('/')[-1].split('.')[0]
            df.to_csv('grid_search_result_%s_%s.csv' % (los_group['name'],
                                                        short_pretrain_path),
                      index=False)
            logger.info('DONE LSTM: los_group=%s, pretrained_path=%s',
                        los_group['values'], pretrained_path)
    logger.info('DONE GRID SEARCH.')


def train_process(los_group, pretrained_path, epochs, hidden_dim,
                  optimizer_type, q_log):
    logger.info('START LSTM: los_group=%s, pretrained_path=%s',
                los_group['values'], pretrained_path)
    results = train(hidden_dim=hidden_dim, epoch=epochs,
                    optimizer_type=optimizer_type,
                    pretrained_path=pretrained_path,
                    los_group=los_group['values'])
    for item in results:
        item['los_group'] = los_group['name']
        item['pretrained_path'] = pretrained_path

    df = pd.DataFrame(results)
    short_pretrain_path = pretrained_path.split('/')[-1].split('.')[0]
    df.to_csv('grid_search_result_%s_%s.csv' % (los_group['name'],
                                                short_pretrain_path),
              index=False)
    logger.info('DONE LSTM: los_group=%s, pretrained_path=%s',
                los_group['values'], pretrained_path)
    q_log.put(df)


def grid_search_multi_process(pretrained_dir, los_groups_path, processes=2):
    """Summary
    """
    skip_los = []
    skip_pretrained = []
    epochs = 500
    hidden_dim = 100
    optimizer_type = 'adam'

    pretrained_paths = [None]
    pretrained_paths.extend(
        [join(pretrained_dir, f) for f in listdir(pretrained_dir)
         if isfile(join(pretrained_dir, f)) and '.vec' in f])
    pretrained_paths = [
        p for p in pretrained_paths if p not in skip_pretrained]

    los_groups = data_loader.load_los_groups(los_groups_path)
    los_groups = [l for l in los_groups if l not in skip_los]

    logger.info('Total pretrained paths: %s',
                ','.join([f if f is not None else 'None' for f in pretrained_paths]))
    logger.info('Total los groups: %s',
                ','.join([g['name'] for g in los_groups]))

    # prepare arguments
    m = multiprocessing.Manager()
    q_log = m.Queue()
    list_args = []
    for los_group in los_groups:
        for pretrained_path in reversed(pretrained_paths):
            list_args.append((los_group, pretrained_path, epochs, hidden_dim,
                              optimizer_type, q_log))
    logger.info('Total cases: %s', len(list_args))

    logger.info('START GRID SEARCH (multiprocessing)...')

    # use mutiprocessing
    if len(list_args) > 0:
        # start x worker processes
        with Pool(processes=processes) as pool:
            start_pool = datetime.now()
            logger.info('START POOL at %s', start_pool)
            pool.starmap(train_process, list_args)

            logger.info('DONE %s/%s cases', q_log.qsize(), len(list_args))
            total_duration = (datetime.now() - start_pool).total_seconds()

            while not q_log.empty():
                result = q_log.get()
                # todo

            # Check there are no outstanding tasks
            assert not pool._cache, 'cache = %r' % pool._cache

    logger.info('DONE GRID SEARCH (multiprocessing).')
