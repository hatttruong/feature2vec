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
import numpy as np
import collections

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


SEED = 1
DATA_DIR = '../data'
DATA_FILE_PATH = DATA_DIR + '/los/cvd_los_data.csv'
LOS_GROUPS_PATH = DATA_DIR + '/los/los_groups.csv'
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


def load_pretrained_vectors(pretrained_path, concept_definitions):
    """
    TODO

    Args:
        pretrained_path (TYPE): Description
    """
    logger.info('start load_pretrained_vectors')
    vector_size = 0
    id_to_vectors = dict()
    with open(pretrained_path) as f:
        content = f.readlines()
    content = [x.strip() for x in content]

    for index, line in enumerate(content):
        if index == 0:
            items = line.split()
            assert len(items) == 2, 'line=%s has incorrect format' % index
            vector_size = int(items[1])
            is_first_line = False
        else:
            items = line.split(',')
            assert len(items) == 3, 'line=%s has incorrect format' % index
            itemid = int(items[0])
            value = int(items[1])
            if itemid in concept_definitions:
                if value in concept_definitions[itemid]['data']:
                    feature_id = concept_definitions[itemid]['data'][value]
                    vector = np.asarray([float(i) for i in items[2].split()])
                    id_to_vectors[feature_id] = np.asarray(vector)
        sys.stdout.write('\r')
        sys.stdout.write('load pretrained for %s features...' % (index + 1))
        sys.stdout.flush()
    sys.stdout.write('\r')

    logger.info('done load_pretrained_vectors')

    return id_to_vectors, vector_size


def get_los_group_idx(los_value, los_group):
    los_group = sorted(los_group, reverse=True)
    group_idx = len(los_group)
    for x in los_group:
        if los_value >= x:
            break
        else:
            group_idx -= 1
    return group_idx


def create_train_data(admission_id, los_value, los_group, concept_definitions):
    """
    Return a list of event index in weights_matrix

    Args:
        admission_id (TYPE): Description
        los_value (float): days in hospital
        los_group (TYPE): splitters in descending order
        concept_definitions (TYPE): Description

    Returns:
        LIST: list of dictionary
    """
    events_df = pd.read_csv(
        DATA_DIR + '/heart_admissions/data_train_%s.csv' % int(admission_id),
        header=None,
        names=['admission_id', 'minutes_ago', 'itemid', 'value'])
    samples = list()
    event_ids = list()
    step = 6
    upper_bound = step
    within_hours = 48
    for index, row in events_df.iterrows():
        itemid = row['itemid']
        value = row['value']
        minutes_ago = row['minutes_ago']
        if minutes_ago > within_hours * 60:
            break

        # create a sample for every next 6 hours
        if minutes_ago > upper_bound * 60:
            samples.append(
                {'admission_id': admission_id,
                 'event_range': upper_bound,
                 'los_group': get_los_group_idx(los_value - upper_bound * 1.0 / 24, los_group),
                 'events': list(event_ids)
                 })
            upper_bound += step

        if itemid in concept_definitions:
            if value in concept_definitions[itemid]['data']:
                event_ids.append(concept_definitions[itemid]['data'][value])
    return samples, event_ids


def build_weights_matrix(feature_to_idx, emb_dim, id_to_vectors):
    """
    build weights matrix based on pretrained vectors

    Args:
        feature_to_idx (TYPE): Description
        emb_dim (TYPE): Description
        id_to_vectors (TYPE): Description

    Returns:
        TYPE: Description
    """
    logger.info('start build_weights_matrix, emb_dim=%s', emb_dim)
    matrix_len = len(feature_to_idx)
    weights_matrix = np.zeros((matrix_len, emb_dim))
    feature_found = 0

    done = 0
    for feature_id in feature_to_idx.keys():
        try:
            i = feature_to_idx[feature_id]
            weights_matrix[i] = id_to_vectors[feature_id]
            feature_found += 1
        except KeyError:
            weights_matrix[i] = np.random.normal(scale=0.6, size=(emb_dim, ))
            logger.debug(
                'cannot found feature_id=%s in pretrained', feature_id)

        done += 1
        sys.stdout.write('\r')
        sys.stdout.write('build weights matrix for %s features...' % done)
        sys.stdout.flush()
    sys.stdout.write('\r')

    logger.info('found %s/%s features in pretrained',
                feature_found, len(feature_to_idx))
    return weights_matrix


def load_los_groups(los_groups_path=None):
    if los_groups_path is not None:
        df = pd.read_csv(los_groups_path)
    else:
        df = pd.read_csv(LOS_GROUPS_PATH)
    los_groups = df.to_dict('records')
    for index, g in enumerate(los_groups):
        g['values'] = [int(v) for v in g['values'].split(',')]
    return los_groups


def load_los_data(los_group, pretrained_path=None, min_threshold=5):
    """
    train/test data: is a list of dictionary
        {'hadm_id': 194126, 'los_group': 9, 'event_range': 6,
        'events': [1, 8, 120, 134, 144, 100529, 578098, ...]}

    Args:
        los_group (TYPE): splitters in decensing order
        pretrained_path (None, optional): Description

    Returns:
        DICT: train_data, test_data, feature_to_idx, label_to_idx, weights_matrix

    """
    logger.info('loading LOS data from %s', DATA_FILE_PATH)

    data_df = pd.read_csv(DATA_FILE_PATH)
    data_dict = data_df[['hadm_id', 'los_hospital']].to_dict('records')

    # create train/test admission ids
    random.seed(SEED)
    random.shuffle(data_dict)
    split = int(len(data_dict) * 0.7)
    train_admission_ids = [x['hadm_id'] for x in data_dict[: split]]
    test_admission_ids = [x['hadm_id'] for x in data_dict[split:]]

    # for each admissions, create samples with different time range
    logger.info('load events for each admission')
    concept_definitions = load_concept_definition()
    features = collections.Counter()
    samples = []
    for index, admission in enumerate(data_dict):
        temp_samples, event_ids = create_train_data(admission['hadm_id'],
                                                    admission['los_hospital'],
                                                    los_group,
                                                    concept_definitions)
        samples.extend(temp_samples)

        features.update(event_ids)

        sys.stdout.write('\r')
        sys.stdout.write(
            'create train data for %s admissions, total samples: %s' % (
                index, len(samples)))
        sys.stdout.flush()
    sys.stdout.write('\r')
    logger.info('create train data for %s admissions, total samples: %s' % (
                len(data_dict), len(samples)))

    # define feature to index, keep features with frequency >= min_threshold
    feature_to_idx = dict()
    for f in features:
        if features[f] >= min_threshold:
            feature_to_idx[f] = len(feature_to_idx)
    # feature_to_idx['<pad>'] = len(feature_to_idx)

    # remove unused features in samples
    for idx, _ in enumerate(samples):
        samples[idx]['events'] = [e for e in samples[idx]['events']
                                  if e in feature_to_idx]
        sys.stdout.write('\r')
        sys.stdout.write(
            'remove unused features in %s samples...' % idx)
        sys.stdout.flush()
    sys.stdout.write('\r')

    # define label to index
    label_to_idx = dict()
    for i in range(len(los_group) + 1):
        label_to_idx[i] = i

    logger.info('feature size: %s, label size: %s',
                len(feature_to_idx), len(label_to_idx))

    # load vectors for each features
    weights_matrix = None
    if pretrained_path is not None:
        id_to_vectors, vector_size = load_pretrained_vectors(
            pretrained_path, concept_definitions)
        weights_matrix = build_weights_matrix(feature_to_idx, vector_size,
                                              id_to_vectors)

    # split train/test
    train_data = [s for s in samples if s[
        'admission_id'] in train_admission_ids]
    test_data = [s for s in samples if s['admission_id'] in test_admission_ids]
    random.shuffle(train_data)
    random.shuffle(test_data)
    logger.info('train: %s, test: %s', len(train_data), len(test_data))

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
