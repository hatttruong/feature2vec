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

torch.set_num_threads(8)
torch.manual_seed(1)
random.seed(1)


class LstmLosClassifier(nn.Module):

    def __init__(self, embedding_dim, hidden_dim, feature_size, label_size,
                 weights_matrix=None, non_trainable=False):
        super(LstmLosClassifier, self).__init__()
        self.hidden_dim = hidden_dim
        self.feature_embeddings = nn.Embedding(feature_size, embedding_dim)
        if weights_matrix not None:
            self.feature_embeddings.load_state_dict({'weight': weights_matrix})
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

    def forward(self, sentence):
        embeds = self.feature_embeddings(sentence)
        x = embeds.view(len(sentence), 1, -1)
        lstm_out, self.hidden = self.lstm(x, self.hidden)
        y = self.hidden2label(lstm_out[-1])
        log_probs = F.log_softmax(y, dim=1)
        return log_probs


def get_accuracy(truth, pred):
    assert len(truth) == len(pred)
    right = 0
    for i in range(len(truth)):
        if truth[i] == pred[i]:
            right += 1.0
    return right / len(truth)


def train():
    train_data, test_data, features, label_to_idx, weights_matrix = data_loader.load_los_data()
    EMBEDDING_DIM = 100
    HIDDEN_DIM = 50
    EPOCH = 5
    best_test_acc = 0.0
    model = LstmLosClassifier(embedding_dim=EMBEDDING_DIM,
                              hidden_dim=HIDDEN_DIM,
                              feature_size=len(features),
                              label_size=len(label_to_idx),
                              weights_matrix=weights_matrix)
    loss_function = nn.NLLLoss()
    # optimizer = optim.Adam(model.parameters(), lr=1e-3)
    optimizer = torch.optim.SGD(model.parameters(), lr=1e-2)
    no_up = 0
    for i in range(EPOCH):
        random.shuffle(train_data)
        print('epoch: %d start!' % (i + 1))
        train_epoch(model, train_data, loss_function,
                    optimizer, feature_to_idx, label_to_idx, i + 1)
        print('now best dev acc:', best_test_acc)
        test_acc = evaluate(model, test_data, loss_function,
                            feature_to_idx, label_to_idx, 'test')
        if test_acc > best_test_acc:
            best_test_acc = test_acc
            os.system('rm ../models/los_best_model_acc_*.model')
            print('New Best Dev!!!')
            torch.save(model.state_dict(), '../models/mr_best_model_acc_' +
                       str(int(test_acc * 10000)) + '.model')
            no_up = 0
        else:
            no_up += 1
            if no_up >= 10:
                exit()


def evaluate(model, data, loss_function, feature_to_idx, label_to_idx, name='dev'):
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
    acc = get_accuracy(truth_res, pred_res)
    print(name + ' avg_loss:%g train acc:%g' % (avg_loss, acc))
    return acc


def train_epoch(model, train_data, loss_function, optimizer, feature_to_idx,
                label_to_idx, epoch_th):
    model.train()

    avg_loss = 0.0
    count = 0
    truth_res = []
    pred_res = []
    batch_sent = []

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
        model.zero_grad()
        loss = loss_function(pred, label)
        avg_loss += loss.item()
        count += 1
        if count % 500 == 0:
            print('epoch: %d iterations: %d loss :%g' %
                  (epoch_th, count, loss.item()))

        loss.backward()
        optimizer.step()
    avg_loss /= len(train_data)
    print('epoch: %d done! \n train avg_loss:%g , acc:%g' %
          (i, avg_loss, get_accuracy(truth_res, pred_res)))


train()
