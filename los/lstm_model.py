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
from os import listdir
from os.path import isfile, join

logger = logging.getLogger(__name__)

torch.set_num_threads(8)
torch.manual_seed(1)
random.seed(1)


class LstmLosClassifier(nn.Module):

    def __init__(self, embedding_dim, hidden_dim, feature_size, label_size,
                 weights_matrix=None, non_trainable=False):
        super(LstmLosClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.feature_embeddings = nn.Embedding(feature_size, embedding_dim)
        if weights_matrix is not None:
            self.feature_embeddings.weight.data.copy_(
                torch.from_numpy(weights_matrix))
            if non_trainable:
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


def train(hidden_dim=50, epoch=5, optimizer_type='sgd', pretrained_path=None,
          los_group=[], save_best_model=False):
    """Summary

    Args:
        hidden_dim (int, optional): Description
        epoch (int, optional): Description
        optimizer_type (str, optional): Description
        pretrained_path (TYPE): Description
        los_groups (str, optional): Description
        save_best_model (bool, optional): Description

    Returns:
        list: list of dictionary
            {epoch: 1, avg_loss: 0, train_acc: 0, test_acc: 0}
    """
    logger.info('start train lstml with %s', locals())
    result = data_loader.load_los_data(
        los_group=los_group, pretrained_path=pretrained_path)
    train_data = result['train_data']
    test_data = result['test_data']
    feature_to_idx = result['feature_to_idx']
    label_to_idx = result['label_to_idx']
    weights_matrix = result['weights_matrix']

    EMBEDDING_DIM = 100
    best_test_acc = 0.0
    model = LstmLosClassifier(embedding_dim=EMBEDDING_DIM,
                              hidden_dim=hidden_dim,
                              feature_size=len(feature_to_idx),
                              label_size=len(label_to_idx),
                              weights_matrix=weights_matrix,
                              non_trainable=True)
    loss_function = nn.NLLLoss()

    # define optimizer
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-2)
    if optimizer_type == 'adam':
        optimizer = optim.Adam(model.parameters(), lr=1e-3)

    no_up = 0
    epoch_results = []
    for i in range(epoch):
        random.shuffle(train_data)
        logger.info('Epoch: %d start!', i + 1)
        temp_result = train_epoch(model, train_data, loss_function, optimizer,
                                  feature_to_idx, label_to_idx, i + 1)
        test_scores = evaluate(model, test_data, loss_function,
                               feature_to_idx, label_to_idx)
        temp_result.update(test_scores)
        epoch_results.append(temp_result)

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
            if no_up >= 10:
                logger.info('Stop: No better model after 10 epoch')
                exit()
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
        pred_res.append(pred_label)

        loss = loss_function(pred, label)
        avg_loss += loss.item()
    avg_loss /= len(data)
    scores = get_scores(truth_res, pred_res, prefix='test_')
    logger.info('avg_loss:%g train acc: %s', avg_loss, scores['test_acc'])
    return scores


def train_epoch(model, train_data, loss_function, optimizer, feature_to_idx,
                label_to_idx, epoch_th):
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
        pred_res.append(pred_label)
        model.zero_grad()
        loss = loss_function(pred, label)
        avg_loss += loss.item()
        count += 1
        if count % 500 == 0:
            logger.info('Epoch: %d \titerations: %d \tloss: %g',
                        epoch_th, count, loss.item())

        loss.backward()
        optimizer.step()
    avg_loss /= len(train_data)
    scores = get_scores(truth_res, pred_res, prefix='train_')
    logger.info('Epoch: %d done. \tavg_loss: %g \tacc: %g',
                epoch_th, avg_loss, scores['train_acc'])

    return scores.update({'epoch': epoch_th, 'avg_loss': avg_loss})


def grid_search():
    """Summary
    """
    pretrained_dir = '../models/'
    pretrained_paths = [join(pretrained_dir, f)
                        for f in listdir(pretrained_dir)
                        if isfile(join(pretrained_dir, f)) and '.vec' in f]
    los_groups = data_loader.load_los_groups()
    logger.info('Total pretrained paths: %s', ','.join(pretrained_paths))
    logger.info('Total los groups: %s',
                ','.join([g['name'] for g in los_groups]))

    epochs = 500
    hidden_dim = 100
    optimizer_type = 'adam'

    final_results = []
    for los_group in los_groups:
        for pretrained_path in pretrained_paths:
            logger.info('START LSTM: los_group=%s, pretrained_path=%s',
                        los_group['values'], pretrained_path)
            results = train(hidden_dim=hidden_dim, epoch=epochs,
                            optimizer_type=optimizer_type,
                            pretrained_path=pretrained_path,
                            los_group=los_group['values'])
            for item in results:
                item['los_group'] = los_group['name']
                item['pretrained_path'] = pretrained_path

            final_results.extend(results)
            df = pd.DataFrame(final_results)
            df.to_csv('grid_search_result.csv')
