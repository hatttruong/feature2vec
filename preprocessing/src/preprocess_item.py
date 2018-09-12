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
    IGNORED_EXTENSIONS = ['.pdf']
    search = BingSearch(ignored_sites=IGNORED_SITES,
                        ignored_extensions=IGNORED_EXTENSIONS)
    i = 1

    logger.info('Fetching first %s results for "%s"...', count, term)
    response = search.search(term, count * 1.5, prefetch_pages=True)

    logger.info("TOTAL: %s RESULTS", response.total)
    os.makedirs(export_dir, exist_ok=True)

    output_files = []
    for result in response.results:
        try:
            content = result.getText()
            if content is not None and len(content) > 0:
                encrypted_url = hashlib.md5(result.url.encode()).hexdigest()
                file_path = os.path.join(export_dir, encrypted_url)

                logger.info("RESULT #%s: \n\tencrypted_url: %s \n\turl: %s",
                            i, encrypted_url, result.url)
                i += 1
                with open(file_path, 'w') as f:
                    f.write(str(content.encode('utf-8')))

                output_files.append(file_path)
                if len(output_files) >= count:
                    break
        except Exception as e:
            raise e
    return output_files


def cluster():
    """Summary
    """
    export_path = '../data/webpages'
    concept_dir = '../data'
    concept_fullpath = os.path.join(
        concept_dir, CONCEPT_DEFINITION_FILENAME)
    d_items = get_d_items()
    concept_definitions, _ = load_concept_definition(concept_fullpath)
    logger.info('Total concepts: %s', len(concept_definitions))

    files_dict = dict()
    for conceptid in concept_definitions.keys():
        item = d_items.loc[d_items['itemid'] == conceptid]
        if item.shape[0] == 1:
            label = item['label'].values[0]
            filenames = search_term(label, export_path, count=50)
            logger.info('conceptid=%s, label=%s, nb_webpages=%s',
                        conceptid, label, len(filenames))
            files_dict[conceptid] = ','.join(filenames)
            break
