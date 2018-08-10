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
    features (TYPE): Description
    logger (TYPE): Description
"""
import os
import json
import logging
import numpy as np
import math
import decimal
import collections
import pandas as pd

from src.db_util import *

logger = logging.getLogger(__name__)


def export_dict_to_json(dict_data, file_path):
    """
    Dict_data must follow format "key": value, "key" type must be string

    Args:
        dict_data (TYPE): Description
        file_path (TYPE): Description
    """
    data = {'data': dict_data}
    logger.info('export_dict_to_json: %s', file_path)
    with open(file_path, 'w') as file:
        # use `json.loads` to do the reverse
        file.write(json.dumps(data))


def load_dict_from_json(file_path):
    """
    Load content from file then parse it to dictionary

    Args:
        file_path (TYPE): Description

    Returns:
        TYPE: Description
    """
    logger.info('load_dict_to_json: %s', locals())
    with open(file_path, 'r') as file:
        text = file.read()
        data = json.loads(text)
        logger.debug('data: %s', data['data'])

    return data['data']


def compute_min_max_step(values):
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

    steps = 0.1
    decimal_places = []
    for i in values:
        d = decimal.Decimal(i)
        decimal_places.append(abs(d.as_tuple().exponent))
    counter_places = collections.Counter(decimal_places)
    percent_zero_decimal = counter_places[0] * 100.0 / len(values)
    if percent_zero_decimal >= 90:
        steps = 1
    logger.debug('decimal places: %s', counter_places)
    logger.debug('percent of 0 decimal place: %s', percent_zero_decimal)

    return min_value, max_value, steps


def is_number(s):
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


def hash_feature(value):
    """Summary

    Args:
        value (TYPE): Description
    """
    pass


def define_features():
    """
    Create new index for each segments of features

    """
    features = dict()
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
        first_itemid = group_item.split()[0]
        features[first_itemid] = dict()

        data_path = os.path.join('data', 'raw', '%s.csv' % group_item)
        logger.info('data_path=%s', data_path)

        df = pd.read_csv(data_path)
        seg_values = list()
        is_number = None
        min_value = None
        max_value = None
        step = None
        if df.value.dtype == np.float64:
            # handle numeric feature
            is_number = True
            values = df.value.tolist()
            min_value, max_value, step = compute_min_max_step(values)
            logger.info('min_value=%s, max_value=%s, step=%s',
                        min_value, max_value, step)
            seg_values = ['less_than']
            v = min_value
            while v <= max_value:
                seg_values.append(str(v))
                v += step
                v = round(v, 1)
                logger.info('v=%s', v)
            seg_values.append('greater')

        else:
            # handle category feature
            is_number = False
            unique_values = set(df.value.tolist())
            for v in unique_values:
                v = v.strip()
                if len(v) > 0:
                    seg_values.append(v)

        logger.info('number of values: %s', len(seg_values))

        features[first_itemid]['is_number'] = is_number
        features[first_itemid]['min_value'] = min_value
        features[first_itemid]['max_value'] = max_value
        features[first_itemid]['step'] = step
        features[first_itemid]['segments'] = dict()
        for v in seg_values:
            features[first_itemid]['segments'][v] = count_features
            count_features += 1

        logger.info('number of features: %s', count_features)

    # define static features: v_first_admission.gender,
    #   v_first_admission.marital_status
    #   v_first_admission.admission_age
    #   v_first_admissionlos_icu
    # TODO

    logger.info('export features definition to file')
    export_dict_to_json(features, 'feature_definition.txt')


features = None


def get_feature_index(itemid, value):
    """Summary

    Args:
        itemid (TYPE): Description
        value (TYPE): Description

    Returns:
        TYPE: Description

    Raises:
        e: Description
    """
    try:
        feature = features[itemid]
        if feature['is_number']:
            if value < feature['min_value']:
                return feature['segments']['less_than']
            elif value > feature['max_value']:
                return feature['segments']['greater']

        return feature['segments'][str(value)]
    except Exception as e:
        logger.error(
            'error get_feature_index(itemid=%s, value=%s)', itemid, value)
        raise e


def create_train_dataset():
    """Summary
    """

    hadm_id = 145834
    itemids = '212 220048 161 224650 162 226479 159 224651 160 226480 '
    itemids += '211 220045 814 220228 833 1542 220546 861 4200 1127 828 3789 '
    df = get_events_by_admission(hadm_id, itemids.split())

    df.to_csv('%s.csv' % hadm_id, index=False)

    pass
