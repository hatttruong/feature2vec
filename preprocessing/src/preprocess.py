"""
Attributes:
    logger (TYPE): Description
    STATIC_FEATURES (TYPE): Description
"""
import sys
import os
from os import listdir
from os.path import isfile, join, basename
import json
import logging
import numpy as np
import math
import decimal
import collections
import pandas as pd
from datetime import datetime
from multiprocessing import Pool
import multiprocessing

from src.pyhash import *
from src.db_util import *
from src.connect_db import *

logger = logging.getLogger(__name__)


CONCEPT_DEFINITION_FILENAME = 'concept_definition.json'

STATIC_FEATURES = [('gender', 300001, False),
                   ('marital_status', 300002, False),
                   ('admission_age', 300003, True),
                   ('los_icu_h', 300004, True)]


def export_dict_to_json(dict_data, file_path):
    """
    Dict_data must follow format "key": value, "key" type must be string

    Args:
        dict_data (TYPE): Description
        file_path (TYPE): Description
    """
    # data = {'data': dict_data}
    logger.info('export_dict_to_json: %s', file_path)
    with open(file_path, 'w') as file:
        # use `json.loads` to do the reverse
        file.write(json.dumps(dict_data))


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


def compute_min_max(values):
    """Summary

    Args:
        values (TYPE): Description

    Returns:
        TYPE: Description
    """
    min_percentile = 5
    max_percentile = 95
    min_value = math.floor(np.percentile(values, min_percentile) * 10) / 10
    max_value = math.floor(np.percentile(values, max_percentile) * 10) / 10
    logger.debug('%s-percentile: %s', min_percentile, min_value)
    logger.debug('%s-percentile: %s', max_percentile, max_value)
    logger.debug('min: %s', min(values))
    logger.debug('max: %s', max(values))

    most_nb_decimal_place = 1
    decimal_places = []
    for i in values:
        d = decimal.Decimal(i)
        decimal_places.append(abs(d.as_tuple().exponent))
    counter_places = collections.Counter(decimal_places)
    percent_zero_decimal = counter_places[0] * 100.0 / len(values)
    if percent_zero_decimal >= 90:
        most_nb_decimal_place = 0
    logger.debug('decimal places: %s', counter_places)
    logger.debug('percent of 0 decimal place: %s', percent_zero_decimal)

    # if the most_nb_decimal_place is ONE, multiply value with 10 to make
    # calculation simple
    multiply = 1
    if most_nb_decimal_place == 1:
        multiply = 10

    values = [int(i * multiply) for i in values]
    min_value = int(min_value * multiply)
    max_value = int(max_value * multiply)

    step = 1

    # remove values out of range(min_value, max_value)
    values = [i for i in values if i >= min_value and i <= max_value]
    values.append(min_value - step)
    values.append(max_value + step)

    # generate segment values
    seg_values = [min_value - step]
    v = min_value
    while v <= max_value:
        seg_values.append(v)
        v += step
        logger.debug('v=%s', v)
    seg_values.append(max_value + step)

    return set(values), min_value, max_value, seg_values, multiply


def check_is_number(s):
    """Summary

    Args:
        s (TYPE): Description

    Returns:
        TYPE: Description
    """
    try:
        float(s)
        return True
    except ValueError:
        return False


def create_concept_object(conceptid, name, is_number, values):
    concept_obj = dict()
    concept_obj['conceptid'] = conceptid
    concept_obj['type'] = 0 if is_number else 1
    concept_obj['segments'] = list()
    concept_obj['hashmaps'] = list()

    min_value = None
    max_value = None
    multiply = None
    logger.debug('feature: %s, is number: %s, total raw values: %s',
                 name, is_number, len(values))
    unique_values = list()
    if is_number:
        # round up age and los_icu_h
        values = [int(v) for v in values if check_is_number(v)]
        unique_values, min_value, max_value, seg_values, multiply = compute_min_max(
            values)
        logger.debug(
            'min_value=%s, max_value=%s, len(seg_values)=%s',
            min_value, max_value, len(seg_values))
        for s in seg_values:
            concept_obj['segments'].append({'value': s})

    else:
        min_value = -1
        max_value = -1
        multiply = -1
        values = [v.strip() for v in set(values) if len(v.strip()) > 0]
        for v in values:
            concept_obj['hashmaps'].append({'value': v, 'hash': hash(v)})
            unique_values.append(hash(v))

    concept_obj['min_value'] = min_value
    concept_obj['max_value'] = max_value
    concept_obj['multiply'] = multiply
    concept_obj['data'] = list()
    logger.debug('number of unique values: %s', len(unique_values))
    for v in unique_values:
        concept_obj['data'].append({'value': v})

    return concept_obj


def define_feature_process(conceptid, label, linksto, q_log):
    """Summary

    Args:
        conceptid (TYPE): Description
        label (TYPE): Description
        linksto (TYPE): Description
        q_log (TYPE): Description

    Returns:
        TYPE: Description
    """
    start = datetime.now()
    logger.debug('load values of conceptid=%s, label=%s',
                 conceptid, label)
    df = load_values_of_concept(conceptid, linksto)
    if df.shape[0] == 0:
        logger.info('there is no values for conceptid=%s (linksto=%s)',
                    conceptid, linksto)
        duration = (datetime.now() - start).total_seconds()
        q_log.put((None, duration))
        return

    values = list()
    if df.isnull().valuenum.sum() <= df.shape[0] * 0.05:
        is_number = True

        # valuenum contained NaN
        df = df[~df['valuenum'].isnull()]
        values = df.valuenum.tolist()
    else:
        # handle category feature
        is_number = False
        values = df.value.tolist()

    concept_obj = create_concept_object(conceptid, label, is_number, values)

    duration = (datetime.now() - start).total_seconds()
    q_log.put((concept_obj, duration))

    size = q_log.qsize()
    if size % 100 == 0:
        logger.info('*********DONE %s CONCEPTS*********', size)


def define_concepts(output_dir, processes=8):
    """
    features including:
        static features:
            v_first_admission.gender,
            v_first_admission.marital_status
            v_first_admission.admission_age
            v_first_admission.los_icu_h
        non-static features: all items which links to chartevents, outputevents,
            inputevents_cv, inputevents_mv. Currently, we ONLY links to chartevents.

    category features' value will be hashed to integer
    assign unique index for each value of each concepts and for each segments of numeric features

    Args:
        output_dir (TYPE): Description
        processes (int, optional): Description

    """
    logger.info('START define_concepts func')

    concepts = list()

    '''
    define static features
    '''
    start = datetime.now()
    df_admissions = get_admissions()
    for name, conceptid, is_number in STATIC_FEATURES:
        values = df_admissions[name].tolist()
        values = [v for v in values if v is not None]
        concept_obj = create_concept_object(conceptid, name, is_number,
                                            values)
        concepts.append(concept_obj)

    logger.info('Total concepts: %s', len(concepts))
    logger.info('TOTAL DURATION (static features): %s seconds',
                (datetime.now() - start).total_seconds())

    '''
    define non-static features
    '''
    start = datetime.now()
    df_concepts = load_concepts()
    logger.info('TOTAL DURATION (load raw non-static concepts): %s seconds',
                (datetime.now() - start).total_seconds())

    # prepare arguments
    m = multiprocessing.Manager()
    q_log = m.Queue()
    list_args = []
    for index, row in df_concepts.iterrows():
        list_args.append(
            (row['conceptid'], row['label'], row['linksto'], q_log))
        # DEBUG
        # if len(list_args) == 100:
        #     break
        # END DEBUG

    logger.info('Number of concept arguments: %s', len(list_args))

    # use mutiprocessing
    if len(list_args) > 0:
        # start x worker processes
        with Pool(processes=processes) as pool:
            start_pool = datetime.now()
            logger.info('START POOL at %s', start_pool)
            pool.starmap(define_feature_process, list_args)

            logger.info('DONE %s/%s concepts', q_log.qsize(), len(list_args))
            total_duration = (datetime.now() - start_pool).total_seconds()
            logger.info(
                'TOTAL DURATION (create non-static concepts): %s seconds',
                total_duration)
            logger.info('seconds/concept: %s seconds',
                        total_duration * 1.0 / q_log.qsize())

            durations = list()
            while not q_log.empty():
                concept_obj, duration = q_log.get()
                if concept_obj is not None:
                    concepts.append(concept_obj)
                durations.append(duration)

            logger.info('mean query times: %s', np.mean(durations))

            # Check there are no outstanding tasks
            assert not pool._cache, 'cache = %r' % pool._cache

    # set id for segments and values
    count_features = 0
    count_values = 0
    count_segments = 0
    for concept_obj in concepts:
        for s in concept_obj['segments']:
            s['id'] = count_features
            count_features += 1
            count_segments += 1
        for v in concept_obj['data']:
            v['id'] = count_features
            count_features += 1
            count_values += 1

        logger.debug('conceptid=%s, number values=%s, number segments=%s',
                     concept_obj['conceptid'], len(concept_obj['data']),
                     len(concept_obj['segments']))

    logger.info('Total Values: %s', count_values)
    logger.info('Total Segments: %s', count_segments)
    logger.info('Total Features: %s', count_features)

    # mapping between itemid and conceptid
    item2concept_dict = create_item2concept()
    item2concepts = list()
    for itemid in item2concept_dict.keys():
        item2concepts.append(
            {'itemid': itemid, 'conceptid': item2concept_dict[itemid]})

    logger.info('EXPORT concept definition to file')
    data = {'item2concept': item2concepts, 'definition': concepts}
    export_dict_to_json(data,
                        os.path.join(output_dir, CONCEPT_DEFINITION_FILENAME))


def update_chartevents_value(concept_dir='../data'):
    """
    Numeric features:
        update jvn_value with value * multiply

        example:
        SELECT (floor(10.56 * 10))::int AS jvn_value

    Category feature:
        copy value to jvn_value

    TODO: after merge item, use condition:
        itemid IN (SELECT itemid FROM jvn_item_mapping WHERE conceptid=%s)
    """
    concept_fullpath = os.path.join(concept_dir, CONCEPT_DEFINITION_FILENAME)
    error_mess = concept_fullpath + " does not exist. Please run define_concepts first"
    assert os.path.isfile(concept_fullpath), error_mess

    logger.info('START update value of chartevents based on "%s"',
                CONCEPT_DEFINITION_FILENAME)
    concepts_def, _ = load_concept_definition(concept_fullpath)
    logger.info('Total concepts (load from json): %s',
                len(concepts_def))

    query = ""
    durations = list()
    for index, conceptid in enumerate(concepts_def.keys()):
        if conceptid >= 300001:
            continue

        logger.debug('update conceptid=%s', conceptid)
        start = datetime.now()

        concept_condition = " itemid = %s " % conceptid
        # TODO
        # concept_condition = " itemid IN (SELECT itemid FROM jvn_item_mapping \
        #     WHERE conceptid = %s) " % conceptid

        # numeric concept
        if concepts_def[conceptid]['type'] == 0:
            # multiply valuenum with concepts_def[conceptid]['multiply'])
            # then convert to int
            query = "UPDATE chartevents \
                SET jvn_value = (floor(valuenum * %s))::int \
                WHERE valuenum IS NOT NULL AND %s" % (
                    concepts_def[conceptid]['multiply'], concept_condition)
            logger.debug('query=\n%s', query)
            execute_non_query(query)
        else:
            # category concept: hash 'value' column
            caseelse_conditions = []
            for v in concepts_def[conceptid]['hashmaps'].keys():
                if "'" in v:
                    logger.info(
                        'There is single quote in "%s", replace with "%s"',
                        v, v.replace("'", "''"))

                caseelse_conditions.append(
                    " WHEN trim(both ' ' from value)='%s' THEN %s " % (
                        v.replace("'", "''"),
                        concepts_def[conceptid]['hashmaps'][v]))
            caseelse_condition = "CASE \
                    %s \
                    ELSE NULL \
                END" % ' '.join(caseelse_conditions)

            query = "UPDATE chartevents \
                SET jvn_value = %s \
                WHERE %s" % (caseelse_condition, concept_condition)
            logger.debug('query=\n%s', query)
            execute_non_query(query)

        durations.append((datetime.now() - start).total_seconds())

        if (index + 1) % 50 == 0:
            logger.info(
                'Done: %s/%s concepts, avg duration: %.2f seconds/concept',
                index + 1, len(concepts_def), np.mean(durations))

    logger.info('DURATION (update values): %s seconds',
                np.sum(durations))


def load_concept_definition(file_path):
    """Summary

    Args:
        file_path (TYPE): Description

    Returns:
        TYPE: Description

    No Longer Raises:
        e: Description
    """
    concepts = dict()
    data = load_dict_from_json(file_path)
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

    item2concept = dict()
    for c in data['item2concept']:
        item2concept[c['itemid']] = c['conceptid']

    return concepts, item2concept


def create_item2concept():
    """Summary

    Returns:
        dict: key = itemid, value = the first item id of each group
    """
    item2concept = dict()
    for index, row in load_item2concepts().iterrows():
        # convert to int type to prevent this error:
        # TypeError: Object of type int64 is not JSON serializable
        item2concept[int(row['itemid'])] = int(row['conceptid'])

    for _, itemid, _ in STATIC_FEATURES:
        item2concept[itemid] = itemid

    return item2concept


def create_train_dataset(export_dir, processes, concept_dir='../data'):
    """
    Use multiprocessing to get data from postgres
    """

    df_admissions = get_admissions()
    logger.info('Total admissions: %s', df_admissions.shape[0])

    # split by . to get name without extension
    # split by _ to get the last part from name (admission id)
    exported_admissions = [int(basename(f).split('.')[0].split('_')[-1])
                           for f in listdir(export_dir)
                           if isfile(join(export_dir, f))]
    logger.info('DONE %s admissions', len(exported_admissions))

    m = multiprocessing.Manager()
    q_log = m.Queue()

    # prepare arguments
    list_args = []
    for index, row in df_admissions.iterrows():
        admission_id = row['hadm_id']
        if admission_id in exported_admissions:
            continue

        gender = None if pd.isnull(row['gender']) else row['gender'].strip()
        admission_age = None if pd.isnull(
            row['admission_age']) else math.floor(row['admission_age'])
        marital_status = None if pd.isnull(row['marital_status']) else row[
            'marital_status'].strip()
        los_icu_h = None if pd.isnull(
            row['los_icu_h']) else math.floor(row['los_icu_h'])
        list_args.append((admission_id,
                          gender,
                          admission_age,
                          marital_status,
                          los_icu_h,
                          export_dir,
                          q_log))
        # DEBUG
        # if len(list_args) == 100:
        #     break
        # END DEBUG

    logger.info('Remaining: %s admissions', len(list_args))

    if len(list_args) > 0:
        # start x worker processes
        with Pool(processes=processes) as pool:
            start_pool = datetime.now()
            logger.info('START POOL at %s', start_pool)
            pool.starmap(create_admission_train, list_args)

            logger.info('DONE %s/%s admissions', q_log.qsize(), len(list_args))
            total_duration = (datetime.now() - start_pool).total_seconds()
            logger.info('TOTAL DURATION: %s seconds', total_duration)
            logger.info('seconds/admissions: %s seconds',
                        total_duration * 1.0 / q_log.qsize())

            query_times = list()
            update_times = list()
            while not q_log.empty():
                _, query_time, update_time = q_log.get()
                query_times.append(query_time)
                update_times.append(update_time)
            logger.info('mean query times: %s', np.mean(query_times))
            logger.info('mean update times: %s', np.mean(update_times))

            # Check there are no outstanding tasks
            assert not pool._cache, 'cache = %r' % pool._cache

    # concat all result to one file
    logger.info('run "concat_train_data.sh" to concat all files')


def create_admission_train(admission_id, gender, admission_age, marital_status,
                           los_icu_h, export_dir, q_log):
    """Summary

    Args:
        admission_id (TYPE): Description
        gender (TYPE): Description
        admission_age (TYPE): Description
        marital_status (TYPE): Description
        los_icu_h (TYPE): Description
        q_log (TYPE): Description

    Returns:
        TYPE: Description
    """
    logger.debug('start exporting ID=%s', admission_id)

    start = datetime.now()
    df_events = get_events_by_admission(admission_id,
                                        event_types=['chartevents'])
    d = (datetime.now() - start).total_seconds()
    query_time = d
    logger.debug('Query time: %s seconds', d)

    start = datetime.now()

    # IMPORTANT: update_value takes long time, update values directly on
    # database by run update_chartevents_value function

    # drop rows which have 'value' Empty
    # axis=0: drop rows which contain missing values.
    # how=any: If any NA values are present, drop that row or column.
    df_events.dropna(axis=0, how='any', inplace=True)

    # ignore any admissions which have no chartevents
    if df_events.shape[0] == 0:
        logger.warn('admission_id=%s has no valid chartevents', admission_id)
        return

    d = (datetime.now() - start).total_seconds()
    update_time = d
    logger.debug('Update time: %s seconds', d)

    # add static features
    static_features = {
        'gender': gender,
        'admission_age': admission_age,
        'marital_status': marital_status,
        'los_icu_h': los_icu_h,
    }

    static_feature_dict = list()
    for name, conceptid, is_number in STATIC_FEATURES:
        static_value = static_features[name]
        if static_value is None:
            continue

        static_feature_dict.append({
            'hadm_id': admission_id,
            'minutes_ago': -1,
            'conceptid': conceptid,
            'value': int(static_value) if is_number else hash(static_value)
        })
    temp_df = pd.DataFrame(static_feature_dict)
    logger.debug('temp_df.shape = %s', temp_df.shape)

    df_events = df_events.append(temp_df, ignore_index=True)
    logger.debug(
        'number of events (chartevents & static features): %s',
        df_events.shape[0])

    # ORDER BY hadm_id and minutes_ago, then export separately
    df_events.sort_values(['hadm_id', 'minutes_ago'], axis=0,
                          ascending=[True, True], inplace=True)
    df_events.to_csv(
        os.path.join(export_dir, 'data_train_%s.csv' % admission_id),
        header=False,
        index=False,
        columns=['hadm_id', 'minutes_ago', 'conceptid', 'value'])
    logger.debug('done exporting ID=%s', admission_id)

    q_log.put((admission_id, query_time, update_time))
    size = q_log.qsize()
    if size % 50 == 0:
        logger.info('*********DONE %s ADMISSIONS*********', size)
