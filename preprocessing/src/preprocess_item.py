"""Summary
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
from search import BingSearch
import os
import sys
import base64
import pandas as pd
import urllib.parse


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

    print('Fetching first ' + str(count) + ' results for "' + term + '"...')
    response = search.search(term, count, prefetch_pages=True)

    print("TOTAL: " + str(response.total) + " RESULTS")
    os.makedirs(export_dir, exist_ok=True)

    for result in response.results:
        try:
            content = result.getText()
            if content is not None and len(content) > 0:
                encode_url = urllib.parse.quote(
                    base64.b64encode(result.url.encode()))
                file_path = os.path.join(export_dir, encode_url + '.txt')

                print("RESULT #" + str(i) + ":\n\t" +
                      encode_url + "\n\t" + result.url)
                i += 1
                with open(file_path, 'w') as f:
                    f.write(str(content.encode('utf-8')))
        except Exception as e:
            raise e


def cluster():
    """Summary
    """
    pass


if __name__ == '__main__':
    export_path = '../../output'
    df = pd.read_csv('../../data/d_items.csv')
    chartevent_items_df = df[(df.linksto == 'chartevents')]
    print('chartevent_items_df.shape:', chartevent_items_df.shape)
    for index, row in chartevent_items_df.iterrows():
        search_term(row['label'],
                    os.path.join(export_path, str(row['itemid'])),
                    count=50)
