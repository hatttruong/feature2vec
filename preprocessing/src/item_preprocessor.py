"""Summary
Item_preprocessor contains functions to merge d_items of MIMIC database:

- prepare_item_info: copy basic information of items from d_items table to
                     insert_jvn_items table
- crawl_webpages: crawl webpages which are result of searching medical terms

- cluster: create group of items based on some criterions
           and insert to jvn_concepts and jvn_item_mapping

"""

import requests
from lxml import html
import os
import sys
import base64
import pandas as pd
import logging
import urllib.parse
import hashlib
import re
import seaborn as sns
import matplotlib.pyplot as plt
from time import time
from datetime import datetime
from scipy import stats
import numpy as np
from fuzzywuzzy import fuzz
import operator

from src.db_util import *
from src.preprocess import *
from src.search import BingSearch

sns.set(color_codes=True)

logger = logging.getLogger(__name__)

SEPERATED_ID = 220000
CONCEPT_WEBPAGES_FILE_NAME = 'concept_webpage.csv'
D_ITEMS_FILENAME = 'd_items.csv'
ACTUAL_ITEMS_FILENAME = 'actual_items.csv'


def search_term(term, export_dir, count=100):
    """
    Search term on google and crawl results

    Args:
        term (TYPE): Description
        export_dir (TYPE): Description
        count (int, optional): Description

    Raises:
        e: Description
    """
    IGNORED_SITES = ['scholar.google.com.vn', 'es.scribd.com']
    IGNORED_EXTENSIONS = ['.pdf', '.doc', '.xls', 'xlsx', '.txt']
    search = BingSearch(ignored_sites=IGNORED_SITES,
                        ignored_extensions=IGNORED_EXTENSIONS)
    i = 1

    logger.info('Fetching first %s results for "%s"...', count, term)
    response = search.search(term, int(count * 1.5), prefetch_pages=True)

    if response.total is None or response.total == 0:
        logger.info(
            'Try to replace special characters with whitespace from term="%s"',
            term)
        term = re.sub('[^A-Za-z0-9]+', ' ', term)
        response = search.search(term, int(count * 1.5), prefetch_pages=True)

    logger.info("TOTAL: %s RESULTS", response.total)
    os.makedirs(export_dir, exist_ok=True)

    encrypted_urls = []
    for result in response.results:
        try:
            content = result.getText()
            if content is not None and len(content) > 0:
                encrypted_url = hashlib.md5(result.url.encode()).hexdigest()
                file_path = os.path.join(export_dir, encrypted_url)

                logger.debug("RESULT #%s: \n\tencrypted_url: %s \n\turl: %s",
                             i, encrypted_url, result.url)
                i += 1
                with open(file_path, 'w') as f:
                    f.write(str(content.encode('utf-8')))

                encrypted_urls.append(encrypted_url)
                if len(encrypted_urls) >= count:
                    break
        except Exception as e:
            raise e
    return encrypted_urls


def export_concept_webpage(concept_webpage_dict, concept_webpage_fullpath):
    """Summary

    Args:
        concept_webpage_dict (TYPE): Description
        concept_webpage_fullpath (TYPE): Description
    """
    logger.debug('Export concept_webpage_dict to file')
    df = pd.DataFrame([
        {'conceptid': c, 'encrypted_urls': w}
        for c, w in concept_webpage_dict.items()
    ])
    df.to_csv(concept_webpage_fullpath, index=False)


def load_concept_webpage_mapping(concept_webpage_fullpath):
    """Summary

    Returns:
        TYPE: Description

    Args:
        concept_dir (TYPE): Description
    """
    concept_webpage_dict = dict()
    if os.path.isfile(concept_webpage_fullpath):
        logger.info('File %s exists', concept_webpage_fullpath)
        df = pd.read_csv(concept_webpage_fullpath)
        for item in df.to_dict('records'):
            concept_webpage_dict[item['conceptid']] = item['encrypted_urls']

    return concept_webpage_dict


def load_d_items(d_items_fullpath):
    df = None
    if os.path.isfile(d_items_fullpath):
        df = pd.read_csv(d_items_fullpath)
    else:
        # load from database
        df = get_d_items()
        df.to_csv(d_items_fullpath)

    # return list of dict [{'col1': 1.0, 'col2': 0.5}, {'col1': 2.0, 'col2':
    # 0.75}]
    temp = df.to_dict('records')
    d_items_dict = dict()
    for item in temp:
        d_items_dict[item['itemid']] = item

    return d_items_dict


def load_actual_items_from_file(actual_items_fullpath):
    """Summary

    Args:
        actual_items_fullpath (TYPE): Description

    Returns:
        TYPE: Description
    """
    df = None
    if os.path.isfile(actual_items_fullpath):
        df = pd.read_csv(actual_items_fullpath)
    else:
        # load from database
        df = load_actual_items()
        df.to_csv(actual_items_fullpath)

    # return list of dict [{'col1': 1.0, 'col2': 0.5}, {'col1': 2.0, 'col2':
    # 0.75}]
    temp = df.to_dict('records')
    actual_items_dict = dict()
    for item in temp:
        actual_items_dict[item['itemid']] = item

    return actual_items_dict


def crawl_webpages(concept_dir, export_dir):
    """Summary
    """
    concept_webpage_fullpath = os.path.join(concept_dir,
                                            CONCEPT_WEBPAGES_FILE_NAME)
    concept_webpage_dict = load_concept_webpage_mapping(
        concept_webpage_fullpath)

    logger.info('Already crawled %s concepts', len(concept_webpage_dict))

    d_items_dict = load_d_items(os.path.join(concept_dir, D_ITEMS_FILENAME))

    concept_definitions, _ = load_concept_definition(
        os.path.join(concept_dir, CONCEPT_DEFINITION_FILENAME))
    logger.info('Total concepts: %s', len(concept_definitions))

    is_export_data = False
    conceptids = [c_id for c_id in concept_definitions.keys()]
    for conceptid in conceptids.reverse():
        if conceptid in concept_webpage_dict.keys():
            logger.debug('already crawled data for conceptid=%s', conceptid)
            continue

        is_export_data = True
        item = d_items_dict[conceptid]
        if item.shape[0] == 1:
            label = item['label']

            if 'ApacheIV' in label:
                logger.info('ignore conceptid=%s, label=%s', conceptid, label)
                continue

            encrypted_urls = search_term(label, export_dir, count=50)
            logger.info('conceptid=%s, label=%s, nb_webpages=%s',
                        conceptid, label, len(encrypted_urls))
            concept_webpage_dict[conceptid] = ','.join(encrypted_urls)

        # export to files
        export_concept_webpage(concept_webpage_dict,
                               concept_webpage_fullpath)
        logger.info('DONE %s/%s', len(concept_webpage_dict),
                    len(concept_definitions))


def cluster():
    """
    Create candidate group and save to database

    Algorithm:
        - compute similarity between labels (fuzzy), select top 5 and filter with is_numeric
        - if it is numeric, compute similarity between distribution
        - if it is category, compute similarity between category values (fuzzy)
        - compute similarity between medical_webpages
    """
    # TODO: parameters
    export_dir = '../data/webpages'
    concept_dir = '../data'

    d_items_dict = load_d_items(os.path.join(concept_dir, D_ITEMS_FILENAME))

    logger.info('start load_actual_items_from_file')
    actual_items_dict = load_actual_items_from_file(
        os.path.join(concept_dir, ACTUAL_ITEMS_FILENAME))
    logger.info('done load_actual_items_from_file')

    # load clustered items
    clustered_itemids = get_auto_clustered_itemids()
    logger.info('clustered %s/%s items', len(clustered_itemids),
                len(actual_items_dict))

    # remove clustered items from actual_items_dict
    for itemid in clustered_itemids:
        del actual_items_dict[itemid]
    logger.info('remaining %s items in total (CV and MV)',
                len(actual_items_dict))

    # insert items not belong to any cluster to jvn_items
    item_with_values = dict()
    logger.info('INSERT ITEMS not belong to any cluster to jvn_items')
    for itemid, item in actual_items_dict.items():
        # get and insert item info to jvn_items
        result = get_item_with_values(itemid, item['linksto'])
        insert_item_info(itemid, result['values'], result['is_numeric'],
                         item['linksto'])
        item_with_values[itemid] = result
        logger.info('*** INSERT %s/%s jvn_items ***',
                    len(item_with_values), len(actual_items_dict))

    done_cv_items = list()
    total_cv_items = len(
        [_ for _ in actual_items_dict.keys() if _ <= SEPERATED_ID])
    logger.info('CLUSTER ITEMS...')
    for itemid, item in actual_items_dict.items():
        # for each CareVue, find its similar items which can be both CV and MV
        if itemid <= SEPERATED_ID and itemid not in done_cv_items:
            # get top items which have similar label
            candidates = compute_label_similarity(itemid, actual_items_dict,
                                                  d_items_dict, top_n=5)
            compute_value_similarity(itemid, candidates, item['linksto'],
                                     item_with_values)

            if len(candidates) == 0:
                logger.info(
                    'there is no matching candidates for item=%s', itemid)
                continue

            candidates[itemid] = {'value_score': 100, 'label_score': 100}

            # insert to database
            concept_obj = {
                'concept': actual_items_dict[itemid]['label'],
                'isnumeric': item_with_values[itemid]['is_numeric'],
                'linksto': actual_items_dict[itemid]['linksto'],
                'items': candidates
            }
            logger.info('create concept with items: %s', str(candidates))
            insert_generated_concept(concept_obj)

            # update done_cv_items
            for idx, score in candidates.items():
                if score['value_score'] >= 90:
                    done_cv_items.append(idx)

            logger.info('***REMAINING %s ITEMS***',
                        total_cv_items - len(done_cv_items))


def export_distribution_image(values, itemid):
    """Summary

    Args:
        values (TYPE): Description
        itemid (TYPE): Description
    """
    distribution_dir = '../data/distributions'

    if len(values) <= 1:
        return

    min_value = math.floor(np.percentile(values, 5) * 10) / 10
    max_value = math.floor(np.percentile(values, 95) * 10) / 10
    dist_values = [v for v in values if v >= min_value and v <= max_value]
    dist_fname = ''
    try:
        dist_fname = '%s.png' % itemid
        sns_plot = sns.distplot(dist_values)
        fig = sns_plot.get_figure()
        fig.savefig(os.path.join(distribution_dir, dist_fname))
        fig.clear()
    except Exception as e:
        logger.error('export distribution image: %s', e)
        dist_fname = ''
    return dist_fname


def compute_label_similarity(itemid, actual_items_dict, d_items_dict, top_n=5):
    """Summary

    Args:
        itemid (TYPE): Description
        actual_items_dict (TYPE): Description
        d_items_dict (TYPE): Description
        top_n (int, optional): Description

    Returns:
        dict: {itemid: score}
    """
    logger.info('compute_label_similarity: %s, %s',
                itemid, d_items_dict[itemid]['label'])

    label = d_items_dict[itemid]['label'].lower()
    label_scores = list()
    for compared_id in actual_items_dict.keys():
        if compared_id != itemid:
            compared_label = d_items_dict[compared_id]['label'].lower()
            s1 = fuzz.partial_token_set_ratio(label, compared_label)
            s2 = fuzz.token_sort_ratio(label, compared_label)
            label_scores.append((compared_id, s1, s2))

    # sort by s1 frist and filter number of item with scores >80
    label_scores = sorted(
        label_scores, key=operator.itemgetter(1), reverse=True)
    label_scores = [item for item in label_scores if item[1] >= 100]

    # if number of items is too large, filter by s2
    if len(label_scores) >= 10:
        label_scores = sorted(
            label_scores, key=operator.itemgetter(2), reverse=True)
        label_scores = label_scores[:top_n] if len(
            label_scores) >= top_n else label_scores

    candidates = dict()
    for item in label_scores:
        logger.info('itemid=%s, label=%s', item[0],
                    d_items_dict[item[0]]['label'])
        candidates[item[0]] = {'label_score': 0.5 * (item[1] + item[2])}

    logger.info('similar candidates: nb_candidates=%s, items=%s',
                len(candidates), str(candidates))

    return candidates


def compute_value_similarity(itemid, candidates, linksto, item_with_values):
    """Summary

    Args:
        itemid (TYPE): Description
        candidates (dict): {itemid: {label_score: ....}}
        item_with_values (TYPE): Description
    """
    logger.info('compute_value_similarity: %s', itemid)

    if itemid not in item_with_values.keys():
        item_with_values[itemid] = get_item_with_values(itemid, linksto)
    item = item_with_values[itemid]

    values = sorted(item['values'])

    del_candidate_ids = list()
    for candidate_id, candidate in candidates.items():
        if candidate_id not in item_with_values.keys():
            item_with_values[candidate_id] = get_item_with_values(candidate_id,
                                                                  linksto)
        candidate = item_with_values[candidate_id]

        if item['is_numeric'] != candidate['is_numeric']:
            logger.info('delete candidate=%s, not the same type',
                        candidate_id)
            del_candidate_ids.append(candidate_id)
            continue

        candidate_values = sorted(candidate['values'])
        if item['is_numeric']:
            # compare 2 distribution
            s = stats.ks_2samp(values, candidate_values)[1] * 100
        else:
            # compare 2 string
            s = fuzz.ratio(' '.join(values), ' '.join(candidate_values))

        candidates[candidate_id]['value_score'] = s

    for del_id in del_candidate_ids:
        del candidates[del_id]

    logger.info('similar candidates: %s', str(candidates))


def get_item_with_values(itemid, linksto):
    """
    Load all its values, compute its pdf if it is numeric,
    get distinct values if it is categoric

    Args:
        itemid (TYPE): Description

    Returns:
        dict: {'values': values, 'is_numeric': is_numeric}
    """
    logger.info('get_item_with_values: %s', locals())

    values = None
    is_numeric = None
    df = load_values_of_itemid(itemid, linksto)

    if df.isnull().valuenum.sum() <= df.shape[0] * 0.05:
        is_numeric = True

        # numeric
        df = df[~df['valuenum'].isnull()]
        values = df.valuenum.tolist()
    else:
        # category
        is_numeric = False
        df = df[~df['value'].isnull()]
        values = df.value.unique().tolist()

    return {'values': values, 'is_numeric': is_numeric}


def insert_item_info(itemid, values, is_numeric, linksto):
    """
    Insert single item into jvn_items

    Args:
        itemid (TYPE): Description
        values (TYPE): Description
    """
    logger.info('insert_item_info: itemid=%s', itemid)
    # TODO: parameters
    concept_dir = '../data'

    d_items_dict = load_d_items(os.path.join(concept_dir, D_ITEMS_FILENAME))
    d_item = d_items_dict[itemid]
    label = d_item['label']
    abbr = d_item['abbreviation']
    dbsource = d_item['dbsource']

    if is_numeric:
        min_value = math.floor(np.percentile(values, 5) * 10) / 10
        max_value = math.floor(np.percentile(values, 95) * 10) / 10
        percentile_25 = math.floor(np.percentile(values, 25) * 10) / 10
        percentile_50 = math.floor(np.percentile(values, 50) * 10) / 10
        percentile_75 = math.floor(np.percentile(values, 75) * 10) / 10
        logger.info(
            'itemid=%s, min=%s, 25p=%s, 50p=%s, 75p=%s, max=%s',
            itemid, min_value, percentile_25, percentile_50, percentile_75,
            max_value)

        dist_fname = ''
        if len(values) > 1:
            dist_fname = export_distribution_image(values, itemid)

        # insert data to database
        insert_jvn_items(
            itemid, label, abbr, dbsource, linksto, True,
            min_value=min_value, max_value=max_value,
            percentile25th=percentile_25, percentile50th=percentile_50,
            percentile75th=percentile_75, distributionImg=dist_fname)
    else:
        # handle category item
        insert_jvn_items(
            itemid, label, abbr, dbsource, linksto, False, values=values)


def insert_value_mapping():
    """
    REMOVED
    Ad-hoc functions
    This function is added into insert_jvn_items
    """
    # TODO: parameters
    concept_dir = '../data'
    query = "SELECT itemid FROM jvn_items WHERE isnumeric = 'f'"
    category_df = execute_query_to_df(query)
    category_ids = category_df.itemid.tolist()
    logger.info('Total category items: %s', len(category_ids))

    for index, itemid in enumerate(category_ids):
        df = load_values_of_itemid(itemid, 'chartevents')
        if df.shape[0] > 0:
            df = df[~df['value'].isnull()]
            values = df.value.unique().tolist()
            for value in values:
                value = str(value).replace("'", "''")
                insert_query = "INSERT INTO \
                    jvn_value_mapping (itemid, value, unified_value) \
                    VALUES (%s, '%s', '%s') \
                    ON CONFLICT(itemid, value) DO NOTHING" % (itemid, value, value)
                execute_non_query(insert_query)
        logger.info('*** DONE %s/%s ***', index + 1, len(category_ids))


def backup_merge_data():
    """Summary
    """
    backup_path = '../backup'
    tables = ['JvnItems', 'JvnConcepts', 'JvnItemMappings', 'JvnValueMappings']
    version = '{0:%Y%m%d.%H%M}'.format(datetime.now())
    logger.info('version=%s', version)
    for table in tables:
        query = 'SELECT * FROM "%s"' % table
        df = execute_query_to_df(query)
        df.to_csv(
            os.path.join(backup_path, '%s.%s.csv' % (table, version)),
            index=False)
        logger.info('Backup table=%s, total records=%s', table, df.shape[0])


def restore_merge_data(version=None):
    """Summary

    Args:
        version (int, optional): Description
    """
    pass
