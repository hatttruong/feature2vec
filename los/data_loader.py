'''
Reference:
https://github.com/yuchenlin/lstm_sentence_classifier/blob/master/LSTM_sentence_classifier.py

'''
# -*- coding: utf-8 -*-
import sys
import torch
import torch.autograd as autograd
import codecs
import random
import torch.utils.data as Data
import pandas as pd

SEED = 1

# input: a sequence of tokens, and a token_to_index dictionary
# output: a LongTensor variable to encode the sequence of idxs


def prepare_sequence(seq, to_ix, cuda=False):
    var = autograd.Variable(torch.LongTensor(
        [to_ix[e] for e in seq]))
    return var


def prepare_label(label, label_to_idx, cuda=False):
    var = autograd.Variable(torch.LongTensor([label_to_idx[label]]))
    return var


def load_events(admission_id):
    """
    Return a list of event index in weights_matrix

    Args:
        admission_id (TYPE): Description
    """
    pass

def load_los_data():
    """Summary

    Returns:
        TYPE: train_data, test_data, label_to_idx, weights_matrix
    """
    DATA_DIR = '../data'
    file_train = '../data/los/cvd_los_data.train'
    file_test = '../data/los/cvd_los_data.test'
    print('loading LOS data from', file_train, 'and', file_test)

    train_df = pd.read_csv(file_train)
    test_df = pd.read_csv(file_test)

    train_data = train_df[['hadm_id', 'los_group']].to_dict('records')
    test_data = test_df[['hadm_id', 'los_group']].to_dict('records')
    print('train:', len(train_data), 'test:', len(test_data))

    # load events for each admission
    print('load events for each admission')
    features = set()
    for item in train_data + test_data:
        item['events'] = load_events(item['hadm_id'])
        features.update(set(item['events']))
    features = list(features)

    # load vectors for each features
    weights_matrix = []

    label_to_idx = dict()
    for item in train_data:
        label_to_idx[item[los_group]] = los_group

    print('feature size:', len(features), ', label size:', len(label_to_ix))
    print('loading data done!')
    return train_data, test_data, features, label_to_idx, weights_matrix
