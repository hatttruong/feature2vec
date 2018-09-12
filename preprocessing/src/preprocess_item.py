"""Summary
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

# Step 1: enrich label
for each word w in "label":
    if it is not in English word:
search "w" in google use:
    https:
        //www.medilexicon.com / abbreviations?search = PCA & target = abbreviations
select the top result


# Step 2: crawl documents
For each "label":
    search with n - grams(2, 3, .., length of label)
    get a collections of documents

# Step 3: calculate similarity
For each "label":
    Use a cluster algorithms to cluster documents of "label" and each candidate similar label, K = 2
    choose "candidate" with score > threshold


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

from src.db_util import *
from src.preprocess import *
from src.search import BingSearch

logger = logging.getLogger(__name__)

CONCEPT_WEBPAGES_FILE_NAME = 'concept_webpage.csv'


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
    IGNORED_SITES = ['scholar.google.com.vn']
    IGNORED_EXTENSIONS = ['.pdf', '.doc', '.xls']
    search = BingSearch(ignored_sites=IGNORED_SITES,
                        ignored_extensions=IGNORED_EXTENSIONS)
    i = 1

    logger.info('Fetching first %s results for "%s"...', count, term)
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
    logger.info('Export concept_webpage_dict to file')
    df = pd.DataFrame([
        {'conceptid': c, 'encrypted_urls': w}
        for c, w in concept_webpage_dict.items()
    ])
    df.to_csv(concept_webpage_fullpath, index=False)


def crawl_webpages(concept_dir, export_dir):
    """Summary
    """
    concept_fullpath = os.path.join(
        concept_dir, CONCEPT_DEFINITION_FILENAME)
    concept_webpage_fullpath = os.path.join(
        concept_dir, CONCEPT_WEBPAGES_FILE_NAME)

    concept_webpage_dict = dict()
    if os.path.isfile(concept_webpage_fullpath):
        logger.info('File %s exists', concept_webpage_fullpath)
        df = pd.DataFrame.read_csv(concept_webpage_fullpath)
        for item in df.to_dict('records'):
            concept_webpage_dict[item['conceptid']] = item['encrypted_urls']

    d_items = get_d_items()
    concept_definitions, _ = load_concept_definition(concept_fullpath)
    logger.info('Total concepts: %s', len(concept_definitions))

    for conceptid in concept_definitions.keys():
        if conceptid in concept_webpage_dict.keys():
            logger.info('already crawled data for conceptid=%s', conceptid)
            continue

        item = d_items.loc[d_items['itemid'] == conceptid]
        if item.shape[0] == 1:
            label = item['label'].values[0]
            encrypted_urls = search_term(label, export_dir, count=50)
            logger.info('conceptid=%s, label=%s, nb_webpages=%s',
                        conceptid, label, len(encrypted_urls))
            concept_webpage_dict[conceptid] = ','.join(encrypted_urls)

        if len(concept_webpage_dict) > 0 and len(concept_webpage_dict) % 10 == 0:
            logger.info('DONE %s/%s', len(concept_webpage_dict),
                        len(concept_definitions))
            # export to files
            export_concept_webpage(concept_webpage_dict,
                                   concept_webpage_fullpath)

    # export to files
    export_concept_webpage(concept_webpage_dict, concept_webpage_fullpath)


def cluster():
    """Summary
    """
    export_dir = '../data/webpages'
    concept_dir = '../data'
    crawl_webpages(concept_dir, export_dir)
