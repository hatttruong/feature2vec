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
import logging
import json

logger = logging.getLogger(__name__)

SEED = 1
DATA_DIR = '../data'
FILE_TRAIN = DATA_DIR + '/los/cvd_los_data.train'
FILE_TEST = DATA_DIR + '/los/cvd_los_data.test'
CONCEPT_DEF_PATH = DATA_DIR + '/concept_definition.json'


def load_dict_from_json(file_path):
    """
    Load content from file then parse it to dictionary

    Args:
        file_path (TYPE): Description

    Returns:
        TYPE: Description
    """
    logger.debug('load_dict_to_json: %s', locals())
    data = {}
    with open(file_path, 'r') as file:
        text = file.read()
        temp = json.loads(text)
        data = temp
        logger.debug('data: %s', data)

    logger.debug('number of keys: %s', len(data))
    return data


def load_concept_definition():
    """Summary

    Args:
        file_path (TYPE): Description

    Returns:
        TYPE: Description

    No Longer Raises:
        e: Description
    """
    concepts = dict()
    data = load_dict_from_json(CONCEPT_DEF_PATH)
    for f in data['definition']:
        conceptid = f['conceptid']
        concepts[conceptid] = dict()
        concepts[conceptid]['type'] = f['type']
        concepts[conceptid]['min_value'] = f['min_value']
        concepts[conceptid]['max_value'] = f['max_value']
        concepts[conceptid]['multiply'] = f['multiply']
        concepts[conceptid]['data'] = dict()
        for v in f['data']:
            concepts[conceptid]['data'][v['value']] = v['id']

        concepts[conceptid]['segments'] = dict()
        for s in f['segments']:
            concepts[conceptid]['segments'][s['value']] = s['id']

        concepts[conceptid]['hashmaps'] = dict()
        for h in f['hashmaps']:
            concepts[conceptid]['hashmaps'][h['value']] = h['hash']

    return concepts


def load_pretrained_feature_vectors(pretrained_path):
    """
    TODO

    Args:
        pretrained_path (TYPE): Description
    """
    with open(pretrained_path, 'r') as f:
        for line in f.read():
            # TODO
            pass


def load_events(admission_id, concept_definitions, within_hours=12):
    """
    Return a list of event index in weights_matrix

    Args:
        admission_id (TYPE): Description
    """
    events_df = pd.read_csv(
        DATA_DIR + '/admissions/data_train_%s.csv' % admission_id,
        header=None,
        names=['admission_id', 'minutes_ago', 'itemid', 'value'])
    event_ids = list()
    for index, row in events_df.iterrows():
        itemid = row['itemid']
        value = row['value']
        minutes_ago = row['minutes_ago']
        if minutes_ago > within_hours * 60:
            break

        if itemid in concept_definitions:
            if value in concept_definitions[itemid]['data']:
                event_ids.append(concept_definitions[itemid]['data'][value])
    return event_ids


def build_weights_matrix(feature_to_idx, emb_dim):
    matrix_len = len(feature_to_idx)
    weights_matrix = np.zeros((matrix_len, emb_dim))
    feature_found = 0

    for feature_id in feature_to_idx.keys():
        try:
            i = feature_to_idx[feature_id]
            # TODO: get feature vector
            weights_matrix[i] = glove[word]
            feature_found += 1
        except KeyError:
            weights_matrix[i] = np.random.normal(scale=0.6, size=(emb_dim, ))
    return weights_matrix


def load_los_data():
    """
    train/test data: is a list of dictionary
        {'hadm_id': 194126, 'los_group': 9,
        'events': [1, 8, 120, 134, 144, 100529, 578098, ...]}

    Returns:
        TYPE: train_data, test_data, label_to_idx, weights_matrix
    """
    logger.info('loading LOS data from %s and %s', FILE_TRAIN, FILE_TEST)

    train_df = pd.read_csv(FILE_TRAIN)
    test_df = pd.read_csv(FILE_TEST)

    train_data = train_df[['hadm_id', 'los_group']].to_dict('records')
    test_data = test_df[['hadm_id', 'los_group']].to_dict('records')
    logger.info('train: %s, test: %s', len(train_data), len(test_data))

    # load events within 12h for each admission
    # get index of each event in concept_definitions.json
    logger.info('load events for each admission')
    concept_definitions = load_concept_definition()
    features = set()
    for index, item in enumerate(train_data + test_data):
        item['events'] = load_events(
            item['hadm_id'], concept_definitions, within_hours=12)
        features.update(set(item['events']))

        sys.stdout.write('\r')
        sys.stdout.write('Loading events for %s admissions...' % index)
        sys.stdout.flush()
    sys.stdout.write('\r')

    # define feature to index
    feature_to_idx = dict()
    for f in features:
        feature_to_idx[f] = len(feature_to_idx)
    feature_to_idx['<pad>'] = len(feature_to_idx)

    # define label to index
    label_to_idx = dict()
    for item in train_data:
        g = item['los_group']
        if g not in label_to_idx:
            label_to_idx[g] = len(label_to_idx)

    # load vectors for each features
    weights_matrix = build_weights_matrix(feature_to_idx)

    logger.info('feature size: %s, label size: %s',
                len(feature_to_idx), len(label_to_idx))
    logger.info('loading data done!')

    return {'train_data': train_data,
            'test_data': test_data,
            'feature_to_idx': feature_to_idx,
            'label_to_idx': label_to_idx,
            'weights_matrix': weights_matrix}


def prepare_sequence(seq, feature_to_idx, cuda=False):
    """
    input: a sequence of tokens, and a token_to_index dictionary
    output: a LongTensor variable to encode the sequence of idxs

    Args:
        seq (TYPE): Description
        to_ix (TYPE): Description
        cuda (bool, optional): Description

    Returns:
        TYPE: Description
    """
    var = autograd.Variable(torch.LongTensor(
        [feature_to_idx[e] for e in seq]))
    return var


def prepare_label(label, label_to_idx, cuda=False):
    var = autograd.Variable(torch.LongTensor([label_to_idx[label]]))
    return var
