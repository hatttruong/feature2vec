"""
we choose 5 category featues, 5 numeric features, static features as below:

5 category features:
      212 220048  Heart Rhythm ==>  5,325,829 data points
      161 224650  Ectopy Type 1 ==> 5,083,411
      162 226479  Ectopy Type 2 ==> 26,338
      159 224651  Ectopy Frequency 1 ==>  2,864,431
      160 226480  Ectopy Frequency 2 ==> 19,840

5 numeric features:
              211 220045  Heart Rate ==>  7,923,714
              814 220228  Hemoglobin ==>  324,335
              833 RBC ==> 175,279
              1542 220546 861 4200 1127 WBC(4 - 11, 000) ==>  626,353
              828 3789        Platelet  (150-440) ==>  198,713
    static features: v_first_admission
        patients.gender,
        admissions.marital_status

        ROUND( (CAST(EXTRACT(epoch FROM a.admittime - p.dob)/(60*60*24*365.242) AS numeric)), 4) AS admission_age
        los_icu

        ###############################################################################

Preprocessing including following steps:
    1. Grouping:
        1.1 find similar item names: using fuzzy, or word embedding.
            note: one group must contain items belonging to the same "linksto"
            result: group of similar item ids in dictionary
            example: {group_index:
                [(itemid, label, abbreviation), (itemid, name, abbreviation),...]}
            output: similar_items_step1
        1.2 compare distribution:
            using kullback-leiber to compute similarity between each pair in a group
            define threshold
            output: similar_items_step2
        1.3 review manually
            output: similar_items_final

    2. Define new features:
        - numeric features: based on min, max and step
        - category features

    3. Prepare training set
        For each admision, get all chartevents and order by time
            Create an array for each minute from admission time to discharge time +
            Attach chartevent to each

Attributes:
    logger (TYPE): Description
    STATIC_FEATURES (TYPE): Description

Deleted Attributes:
    features (TYPE): Description
"""
import os
import json
import logging
import numpy as np
import math
import decimal
import collections
import pandas as pd
from datetime import datetime

from src.pyhash import *
from src.db_util import *

logger = logging.getLogger(__name__)


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
    logger.info('load_dict_to_json: %s', locals())
    data = {}
    with open(file_path, 'r') as file:
        text = file.read()
        temp = json.loads(text)
        data = temp
        logger.debug('data: %s', data)

    logger.info('number of keys: %s', len(data))
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


STATIC_FEATURES = [('gender', 300001, False),
                   ('marital_status', 300002, False),
                   ('admission_age', 300003, True),
                   ('los_icu_h', 300004, True)]


def define_features(data_dir, output_dir):
    """
    Create new index for each segments of features

    Args:
        data_dir (TYPE): Description
        output_dir (TYPE): Description

    """
    features = list()
    count_features = 0
    group_items = [
        '212 220048  Heart Rhythm',
        '161 224650  Ectopy Type 1',
        '162 226479  Ectopy Type 2',
        '159 224651  Ectopy Frequency 1',
        '160 226480  Ectopy Frequency 2',
        '211 220045  Heart Rate',
        '814 220228  Hemoglobin',
        '833 RBC',
        '1542 220546 861 4200 1127 WBC',
        '828 3789        Platelet']
    for group_item in group_items:
        item_id = int(group_item.split()[0])
        feature_obj = dict()
        feature_obj['itemid'] = item_id
        feature_obj['segments'] = list()

        data_path = os.path.join(data_dir, '%s.csv' % group_item)
        logger.info('data_path=%s', data_path)

        df = pd.read_csv(data_path)
        unique_values = list()
        is_number = None
        min_value = None
        max_value = None
        multiply = None
        if df.value.dtype == np.float64:
            # handle numeric feature
            is_number = True
            temp_values = df.value.tolist()
            unique_values, min_value, max_value, seg_values, multiply = compute_min_max(
                temp_values)
            logger.info(
                'min_value=%s, max_value=%s, multiply=%s, len(seg_values)=%s',
                min_value, max_value, multiply, len(seg_values))
            for s in seg_values:
                feature_obj['segments'].append({'value': s})
                count_features += 1
        else:
            # handle category feature
            is_number = False
            min_value = -1
            max_value = -1
            multiply = -1
            temp_values = set(df.value.tolist())
            for v in temp_values:
                v = v.strip()
                if len(v) > 0:
                    unique_values.append(v)

        logger.info('number of values: %s', len(unique_values))
        feature_obj['type'] = 0 if is_number else 1
        feature_obj['min_value'] = min_value
        feature_obj['max_value'] = max_value
        feature_obj['multiply'] = multiply
        feature_obj['data'] = list()
        for v in unique_values:
            feature_obj['data'].append({'value': v})
            count_features += 1

        features.append(feature_obj)
        logger.info('features=%s, count=%s', item_id, count_features)

    # define static features: v_first_admission.gender,
    #   v_first_admission.marital_status
    #   v_first_admission.admission_age
    #   v_first_admission.los_icu_h
    df_admissions = get_admissions()
    for name, itemid, is_number in STATIC_FEATURES:
        feature_obj = dict()
        feature_obj['itemid'] = itemid
        feature_obj['type'] = 0 if is_number else 1
        feature_obj['segments'] = list()

        values = df_admissions[name].unique()
        values = [v for v in values if v is not None]
        min_value = None
        max_value = None
        multiply = None
        logger.info('feature: %s, is number: %s, total raw values: %s',
                    name, is_number, len(values))
        if is_number:
            multiply = 1
            # round up age and los_icu_h
            values = [int(v) for v in values if check_is_number(v)]
            _, min_value, max_value, seg_values, _ = compute_min_max(
                values)
            logger.info(
                'min_value=%s, max_value=%s, len(seg_values)=%s',
                min_value, max_value, len(seg_values))
            for s in seg_values:
                feature_obj['segments'].append({'value': s})
                count_features += 1
        else:
            min_value = -1
            max_value = -1
            multiply = -1

        feature_obj['min_value'] = min_value
        feature_obj['max_value'] = max_value
        feature_obj['multiply'] = multiply
        feature_obj['data'] = list()
        unique_values = set(values)
        logger.info('number of values: %s', len(unique_values))
        for v in unique_values:
            feature_obj['data'].append({'value': v})
            count_features += 1

        features.append(feature_obj)

        logger.info('features=%s, count=%s', name, count_features)

    logger.info('export features definition to file')
    export_dict_to_json(features,
                        os.path.join(output_dir, 'feature_definition.json'))


def load_feature_definition(file_path):
    """Summary

    Args:
        file_path (TYPE): Description

    Returns:
        TYPE: Description

    No Longer Raises:
        e: Description
    """
    features = dict()
    data = load_dict_from_json(file_path)
    for f in data:
        itemid = f['itemid']
        features[itemid] = dict()
        features[itemid]['type'] = f['type']
        features[itemid]['min_value'] = f['min_value']
        features[itemid]['max_value'] = f['max_value']
        features[itemid]['multiply'] = f['multiply']
        features[itemid]['data'] = dict()
        for v in f['data']:
            features[itemid]['data'][v['value']] = -1  # v['id']

        features[itemid]['segments'] = dict()
        for v in f['segments']:
            features[itemid]['segments'][v['value']] = -1  # v['id']

    return features


def update_value(df, features_def, group_itemids):
    """Summary

    Args:
        df (TYPE): Description
        features_def (TYPE): Description
        group_itemids (TYPE): Description

    Returns:
        TYPE: Description
    """
    for index, row in df.iterrows():
        itemid = int(row['itemid'])
        value = row['value']
        g_id = group_itemids[itemid]
        if g_id in features_def.keys():
            if features_def[g_id]['type'] == 0:
                # try to round it
                value = int(float(value) * features_def[g_id]['multiply'])
            else:
                value = str(value).strip()

            df.iloc[index, df.columns.get_loc('value')] = value
        else:
            logger.error(
                'error cannot find(itemid=%s)', itemid)

    return df


def create_group_itemid():
    group_itemids = dict()
    group_items = [
        '212 220048  Heart Rhythm',
        '161 224650  Ectopy Type 1',
        '162 226479  Ectopy Type 2',
        '159 224651  Ectopy Frequency 1',
        '160 226480  Ectopy Frequency 2',
        '211 220045  Heart Rate',
        '814 220228  Hemoglobin',
        '833 RBC',
        '1542 220546 861 4200 1127 WBC',
        '828 3789        Platelet']
    for group_item in group_items:
        g_item_id = int(group_item.split()[0])
        for i in group_item.split():
            if check_is_number(i):
                group_itemids[int(i)] = g_item_id
                logger.info('key=%s, value=%s', i, g_item_id)
            else:
                break

    return group_itemids


def create_train_dataset(output_dir):
    """Summary

    Args:
        output_dir (TYPE): Description
    """
    features_def = load_feature_definition(
        os.path.join(output_dir, 'feature_definition.json'))
    logger.info(features_def[300001]['data'])

    group_itemids = create_group_itemid()

    df_admissions = get_admissions()
    itemids = '212 220048 161 224650 162 226479 159 224651 160 226480 '
    itemids += '211 220045 814 220228 833 1542 220546 861 4200 1127 828 3789 '
    itemids = itemids.split()
    df = None  # contains 4 columns: hadm_id, minutes_ago, itemid, value
    query_times = list()
    update_times = list()
    for index, row in df_admissions.iterrows():
        admission_id = row['hadm_id']
        logger.info('admission_id = %s', admission_id)

        start = datetime.now()
        df_events = get_events_by_admission(admission_id, itemids)
        d = (datetime.now() - start).total_seconds()
        query_times.append(d)
        logger.info('Query time: %s seconds', d)

        start = datetime.now()
        df_events = update_value(df_events, features_def, group_itemids)
        d = (datetime.now() - start).total_seconds()
        update_times.append(d)
        logger.info('Update time: %s seconds', d)

        # add static features
        static_feature = {
            'gender': row['gender'].strip(),
            'admission_age': math.floor(row['admission_age']),
            'marital_status': row['marital_status'].strip(),
            'los_icu_h': math.floor(row['los_icu_h']),
            'admission_type': row['admission_type'].strip()
        }

        static_feature_dict = list()
        for name, itemid, is_number in STATIC_FEATURES:
            static_feature_dict.append({
                'hadm_id': row['hadm_id'],
                'minutes_ago': -1,
                # 'charttime': None,
                'itemid': itemid,
                'value': static_feature[name],
                # 'valuenum': static_feature[f]
            })
        temp_df = pd.DataFrame(static_feature_dict)
        logger.info('temp_df.shape = %s', temp_df.shape)

        df_events = df_events.append(temp_df, ignore_index=True)
        logger.info(
            'number of events (chartevents & static features): %s',
            df_events.shape[0])

        if df is None:
            df = df_events.copy()
        else:
            df.append(df_events, ignore_index=True)

        logger.info('DONE %s/%s admissions' %
                    (index + 1, df_admissions.shape[0]))
        if index >= 10:
            break

    print('mean query times:', np.mean(query_times))
    print('mean update times:', np.mean(update_times))

    df.sort_values(['hadm_id', 'minutes_ago'], axis=0,
                   ascending=[True, True], inplace=True)
    df.to_csv(os.path.join(output_dir, 'data_train.csv'), index=False,
              columns=['hadm_id', 'minutes_ago', 'itemid', 'value'])


def create_raw_train_dataset(output_dir):
    """Summary

    Args:
        output_dir (TYPE): Description
    """
    itemids = '212 220048 161 224650 162 226479 159 224651 160 226480 '
    itemids += '211 220045 814 220228 833 1542 220546 861 4200 1127 828 3789 '
    itemids = itemids.split()
    query = ' SELECT hadm_id, charttime, itemid, value, valuenum \
        FROM chartevents \
        WHERE itemid in (%s) ' % ','.join(itemids)

    logger.info('query="%s"', query)
    start = datetime.now()
    df = execute_query_to_df(query)
    d = (datetime.now() - start).total_seconds()
    logger.info('Query time: %s seconds', d)

    logger.info('query finishes')

    df.to_csv(os.path.join(output_dir, 'raw_train_data.csv'), index=False)
