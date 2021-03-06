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
from sklearn.metrics import confusion_matrix
from sklearn.metrics import accuracy_score
from sklearn.metrics import f1_score
from sklearn.metrics import precision_score
from sklearn.metrics import recall_score
import pandas as pd
from os import listdir
from os.path import isfile, join
from datetime import datetime
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


def get_scores(y_true, y_pred, prefix='', case_idx=0):
    assert len(y_true) == len(y_pred)
    is_binary = True if len(set(y_true)) == 2 else False

    acc = accuracy_score(y_true, y_pred)

    average = 'binary' if is_binary else 'weighted'
    f1_value = f1_score(y_true, y_pred, average=average)
    precision_value = precision_score(y_true, y_pred, average=average)
    recall_value = recall_score(y_true, y_pred, average=average)
    logger.info('CASE %s: Confusion_matrix: \n%s', case_idx,
                confusion_matrix(y_true, y_pred))
    return {prefix + 'acc': acc,
            prefix + 'f1': f1_value,
            prefix + 'precision': precision_value,
            prefix + 'recall': recall_value,
            }


def train(hidden_dim=50, epoch=5, optimizer_type='adam', lr=1e-3, clip=0.25,
          pretrained_path=None, los_splitters=[], model_name=None, case_idx=0):
    """Summary

    Args:
        hidden_dim (int, optional): Description
        epoch (int, optional): Description
        optimizer_type (str, optional): Description
        lr (float, optional): should use 1e-2 if using optimize sgd, 1e-3 with adam
        clip (float, optional): Description
        pretrained_path (TYPE): Description
        los_splitters (list, optional): Description
        model_name (None, optional): Description

    Returns:
        list: list of dictionary
            {epoch: 1, avg_loss: 0, train_acc: 0, test_acc: 0}

    """
    EMBEDDING_DIM = 100
    MAX_NO_UP_EPOCH = 3

    logger.info('CASE=%s: train LSTM with parameters: %s', case_idx, locals())
    result = data_loader.load_los_data(
        los_splitters=los_splitters, pretrained_path=pretrained_path,
        case_idx=case_idx)
    train_data = result['train_data']
    test_data = result['test_data']
    feature_to_idx = result['feature_to_idx']
    label_to_idx = result['label_to_idx']
    weights_matrix = result['weights_matrix']

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

    no_up_f1_score = 0
    no_up_acc_score = 0

    best_test_acc = 0.0
    best_test_f1 = 0.0

    epoch_results = []
    for i in range(epoch):
        random.shuffle(train_data)
        logger.info('CASE=%s: Epoch: %d start!', case_idx, i + 1)
        temp_result, avg_loss = train_epoch(model, train_data, loss_function,
                                            optimizer, feature_to_idx,
                                            label_to_idx, i + 1, lr, clip,
                                            case_idx=case_idx)
        # logger.info('train_epoch result: %s', temp_result)
        test_scores = evaluate(model, test_data, loss_function,
                               feature_to_idx, label_to_idx, case_idx=case_idx)
        # logger.info('test_scores: %s', test_scores)
        temp_result.update(test_scores)
        epoch_results.append(temp_result)

        # stop training if avg_loss is nan
        if avg_loss == float('nan'):
            logger.info(
                'CASE=%s: WARNING: avg_loss is nan, STOP training', case_idx)
            break

        test_f1 = test_scores['test_f1']
        test_acc = test_scores['test_acc']

        if test_f1 > best_test_f1:
            best_test_f1 = test_f1
            if model_name is not None:
                os.system('rm ../models/los_%s_f1_*.model' % model_name)
                logger.info('CASE=%s: New Best Test!!! (F1-score)', case_idx)
                torch.save(model.state_dict(),
                           '../models/los_%s_f1_%s.model' % (model_name,
                                                             str(int(test_f1 * 10000))))
            no_up_f1_score = 0
            no_up_acc_score = 0

        else:
            no_up_f1_score += 1
            logger.info(
                'CASE=%s: WARNING: No better model after %s epoch (F1)', case_idx,
                no_up_f1_score)

            if test_acc > best_test_f1:
                best_test_f1 = test_acc
                if model_name is not None:
                    os.system('rm ../models/los_%s_acc_*.model' % model_name)
                    logger.info('CASE=%s: New Best Test!!! (acc)', case_idx)
                    torch.save(model.state_dict(),
                               '../models/los_%s_acc_%s.model' % (model_name,
                                                                  str(int(test_acc * 10000))))
                no_up_acc_score = 0
            else:
                no_up_acc_score += 1
                logger.info(
                    'CASE=%s: WARNING: No better model after %s epoch (accuracy)',
                    case_idx, no_up_acc_score)

            # consider F1 score first, if it is greater than zero
            # else, consider accuracy
            if best_test_f1 > 0:
                if no_up_f1_score >= MAX_NO_UP_EPOCH:
                    logger.info(
                        'CASE=%s: STOP TRAINING: No better model (F1) after %s epoch',
                        case_idx, MAX_NO_UP_EPOCH)
                    break
            elif no_up_acc_score >= MAX_NO_UP_EPOCH:
                logger.info(
                    'CASE=%s: STOP TRAINING: No better model (accuracy) after %s epoch',
                    case_idx, MAX_NO_UP_EPOCH)
                break

    return epoch_results


def evaluate(model, data, loss_function, feature_to_idx, label_to_idx, case_idx=0):
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
    scores = get_scores(truth_res, pred_res, prefix='test_', case_idx=case_idx)
    logger.info('CASE=%s: Evaluate: \tavg_loss:%g \ttest acc: %s \ttest f1: %g ',
                case_idx, avg_loss, scores['test_acc'], scores['test_f1'])
    return scores


def train_epoch(model, train_data, loss_function, optimizer, feature_to_idx,
                label_to_idx, epoch_th, lr, clip, case_idx=0):
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
            logger.info('CASE=%s: Epoch: %d \titerations: %d \tloss: %g',
                        case_idx, epoch_th, count, loss.item())

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

    scores = get_scores(truth_res, pred_res,
                        prefix='train_', case_idx=case_idx)
    scores.update({'epoch': epoch_th, 'avg_loss': avg_loss})
    logger.info(
        'CASE=%s: Epoch: %d done. \tavg_loss: %g \ttrain_acc: %g \ttrain_f1: %g',
        case_idx, epoch_th, avg_loss, scores['train_acc'], scores['train_f1'])

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
            df.to_csv('grid_search_result/result_%s_%s.csv' % (los_group['name'],
                                                               short_pretrain_path),
                      index=False)
            logger.info('DONE LSTM: los_group=%s, pretrained_path=%s',
                        los_group['values'], pretrained_path)
    logger.info('DONE GRID SEARCH.')


def train_process(los_group, pretrained_path, epochs, hidden_dim,
                  optimizer_type, q_log, case_idx):
    logger.info('START LSTM: los_group=%s, pretrained_path=%s',
                los_group['values'], pretrained_path)

    short_pretrain_path = 'None'
    if pretrained_path is not None:
        short_pretrain_path = pretrained_path.split('/')[-1].split('.')[0]
    model_name = '%s_%s' % (los_group['name'], short_pretrain_path)

    results = train(hidden_dim=hidden_dim, epoch=epochs,
                    optimizer_type=optimizer_type,
                    pretrained_path=pretrained_path,
                    los_splitters=los_group['values'],
                    model_name=model_name,
                    case_idx=case_idx)
    for item in results:
        item['los_group'] = los_group['name']
        item['pretrained_path'] = short_pretrain_path

    df = pd.DataFrame(results)
    df.to_csv('grid_search_result/result_%s.csv' % model_name, index=False)
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
                              optimizer_type, q_log, len(list_args)))
    for index, items in enumerate(list_args):
        logger.info('CASE %s: %s', index, items)
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
