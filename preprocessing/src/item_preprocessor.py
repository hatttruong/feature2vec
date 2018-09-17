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

from src.db_util import *
from src.preprocess import *
from src.search import BingSearch

sns.set(color_codes=True)

logger = logging.getLogger(__name__)

CONCEPT_WEBPAGES_FILE_NAME = 'concept_webpage.csv'
D_ITEMS_FILENAME = 'd_items.csv'


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

    concept_definitions, _ = load_concept_definition(
        os.path.join(concept_dir, CONCEPT_DEFINITION_FILENAME))
    logger.info('Total concept definitions: %s', len(concept_definitions))

    concept_webpage_dict = load_concept_webpage_mapping(
        os.path.join(concept_dir, CONCEPT_WEBPAGES_FILE_NAME))
    logger.info('Crawled %s concepts', len(concept_webpage_dict))

    # number of carevue concepts
    nb_cv_concept = len(
        [idx for idx in concept_webpage_dict.keys() if idx <= 220000])
    logger.info('Number of carevue concepts: %s', nb_cv_concept)

    nb_clusters = nb_cv_concept
    if nb_cv_concept < len(concept_webpage_dict) / 2:
        nb_clusters = len(concept_webpage_dict) - nb_cv_concept
    logger.info('Number of nb_clusters:%s', nb_clusters)

    # load tfidf model
    tfidf_vectorizer = TfidfGensimVectorizer(
        dictionary_file='',
        tfidf_model_path='')
    logger.info('number of words in tfidf model: %s',
                len(tfidf_vectorizer.token2id.keys()))


def prepare_item_info():
    """
    Summary
        Numeric items:
                calculate min, max, percentile, export distributions image

        Category & numeric items:
            Save these information to database (table `jvn_item_mapping`):
                itemid
                label
                abbr
                dbsource
                linksto
                isnumeric

    """
    # TODO: parameters
    export_dir = '../data/webpages'
    concept_dir = '../data'
    distribution_dir = '../data/distributions'

    logger.info('start prepare_numeric_item_info')
    d_items_dict = load_d_items(os.path.join(concept_dir, D_ITEMS_FILENAME))

    logger.info('start load_actual_items')
    actual_items_df = load_actual_items()
    logger.info('done load_actual_items')

    t0 = time()
    for index, row in actual_items_df.iterrows():
        logger.info('handling %s/%s...', index + 1, actual_items_df.shape[0])

        itemid = row['itemid']
        d_item = d_items_dict[itemid]
        label = d_item['label']
        abbr = d_item['abbreviation']
        dbsource = d_item['dbsource']

        # load values of itemid
        df = load_values_of_concept(itemid, 'chartevents')

        # handle numeric item
        if df.isnull().valuenum.sum() <= df.shape[0] * 0.05:

            # valuenum contained NaN
            df = df[~df['valuenum'].isnull()]
            values = df.valuenum.tolist()

            min_value = math.floor(np.percentile(values, 5) * 10) / 10
            max_value = math.floor(np.percentile(values, 95) * 10) / 10
            percentile_25 = math.floor(np.percentile(values, 25) * 10) / 10
            percentile_50 = math.floor(np.percentile(values, 50) * 10) / 10
            percentile_75 = math.floor(np.percentile(values, 75) * 10) / 10

            dist_fname = ''

            if len(values) > 1:
                try:
                    dist_fname = '%s.png' % itemid
                    sns_plot = sns.distplot(values)
                    fig = sns_plot.get_figure()
                    fig.savefig(os.path.join(distribution_dir, dist_fname))
                except Exception as e:
                    logger.error('cannot plot distribution of item=%s \nerror: %s',
                                 itemid, e)
                    dist_fname = ''
            else:
                logger.warn(
                    'cannot plot distribution of item=%s, nb of values=%s',
                    itemid, len(values))

            logger.info(
                'itemid=%s, min=%s, 25p=%s, 50p=%s, 75p=%s, max=%s, dist=%s',
                itemid, min_value, percentile_25, percentile_50, percentile_75,
                max_value, dist_fname)

            # insert data to database
            insert_jvn_items(
                itemid, label, abbr, dbsource, row['linksto'], True,
                min_value=min_value, max_value=max_value,
                percentile25th=percentile_25, percentile50th=percentile_50,
                percentile75th=percentile_75, distributionImg=dist_fname)
        else:
            # handle category item
            insert_jvn_items(
                itemid, label, abbr, dbsource, row['linksto'], False)

        logger.info('***Done %s/%s, avg. duration: %0.3fs/item ***',
                    index + 1, actual_items_df.shape[0],
                    (time() - t0) / (index + 1))

    logger.info('done in %0.3fs', (time() - t0))
