'''
Based on idea of googlesearch.py of @anthony
https://github.com/anthonyhseb/googlesearch/blob/master/googlesearch

My changes:
        - add Bing search
        - use requests instead of urllib2
        - use boilerpipe to extract content of webpage

    required package "boilerpipe"
        git clone https://github.com/misja/python-boilerpipe.git
        cd python-boilerpipe
        pip install -r requirements.txt
        python setup.py install

'''
import requests
import math
import re
from bs4 import BeautifulSoup
from threading import Thread
from collections import deque
from time import sleep
import os
from boilerpipe.extract import Extractor
import base64
import sys
import urllib.parse
import logging

logger = logging.getLogger(__name__)


class BaseSearch(object):

    """Summary

    Attributes:
        ignored_extensions (list): Description
        ignored_sites (list): Description
        REQUEST_HEADER (TYPE): Description
        RESULT_SELECTOR (str): Description
        SEARCH_URL (str): Description
        TOTAL_SELECTOR (str): Description
        USER_AGENT (str): Description

    """
    # Window agent
    # USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    # Ubuntu agent
    USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0'
    REQUEST_HEADER = {'User-Agent': USER_AGENT,
                      'Cache-Control': 'no-cache',
                      'Accept-Language': 'en-US,en;q=0.5'}

    # specilize for each search tool
    SEARCH_URL = None
    RESULT_SELECTOR = None
    TOTAL_SELECTOR = None
    NEXT_PAGE_SELECTOR = None

    ignored_sites = []
    ignored_extensions = []

    def __init__(self, settings, ignored_sites=None, ignored_extensions=None):
        """Summary

        Args:
            settings (TYPE): Description
            ignored_sites (None, optional): Description
            ignored_extensions (None, optional): Description
        """
        BaseSearch.SEARCH_URL = settings['search_url']
        BaseSearch.RESULT_SELECTOR = settings['result_selector']
        BaseSearch.TOTAL_SELECTOR = settings['total_selector']
        BaseSearch.NEXT_PAGE_SELECTOR = settings['next_page_selector']

        if ignored_sites is not None:
            self.ignored_sites = ignored_sites
        if ignored_extensions is not None:
            self.ignored_extensions = ignored_extensions

    def search(self, query, num_results=10, prefetch_pages=True,
               prefetch_threads=10):
        """Summary

        Args:
            query (TYPE): Description
            num_results (int, optional): Description
            prefetch_pages (bool, optional): Description
            prefetch_threads (int, optional): Description

        Returns:
            TYPE: Description
        """
        assert BaseSearch.SEARCH_URL is not None
        assert BaseSearch.RESULT_SELECTOR is not None
        assert BaseSearch.TOTAL_SELECTOR is not None
        assert BaseSearch.NEXT_PAGE_SELECTOR is not None

        searchResults = []
        fetcher_threads = deque([])
        total = None
        url_search = '%s/search?q=%s' % (BaseSearch.SEARCH_URL,
                                         urllib.parse.quote(query))
        while True:
            response = requests.get(url_search,
                                    headers=BaseSearch.REQUEST_HEADER,
                                    allow_redirects=False)
            soup = BeautifulSoup(response.text, "lxml")

            if total is None:
                totalText = soup.select(BaseSearch.TOTAL_SELECTOR)[
                    0].text
                total = int(re.sub("[', ]", "", re.search(
                    "(([0-9]+[', ])*[0-9]+)", totalText).group(1)))
            results = self.parseResults(
                soup.select(BaseSearch.RESULT_SELECTOR))
            if len(searchResults) + len(results) > num_results:
                del results[num_results - len(searchResults):]
            searchResults += results
            if prefetch_pages:
                for result in results:
                    while True:
                        running = 0
                        for thread in fetcher_threads:
                            if thread.is_alive():
                                running += 1
                        if running < prefetch_threads:
                            break
                        sleep(1)
                    fetcher_thread = Thread(target=result.getText)
                    fetcher_thread.start()
                    fetcher_threads.append(fetcher_thread)

            # if the number of searchResults > num_results or >= total, stop
            if len(searchResults) >= num_results or len(searchResults) >= total:
                break

            # NEXT PAGE
            links = soup.select(BaseSearch.NEXT_PAGE_SELECTOR)
            if len(links) > 0 and links[0].get('href') is not None:
                url_search = BaseSearch.SEARCH_URL + links[0].get('href')
                logger.info('next_page: %s', url_search)
            else:
                break

        for thread in fetcher_threads:
            thread.join()
        return SearchResponse(searchResults, total)

    def parseResults(self, results):
        """Summary

        Args:
            results (TYPE): Description

        Returns:
            TYPE: Description
        """
        searchResults = []
        for result in results:
            url = result["href"]
            title = result.text

            if url[-4:] in self.ignored_extensions:
                logger.info('IGNORED LINK: %s', url)
                continue

            site = url.split("//")[-1].split("/")[0].split('?')[0]
            if site in self.ignored_sites:
                logger.info('IGNORED LINK: %s', url)
                continue

            searchResults.append(SearchResult(title, url))
        return searchResults


class SearchResponse:

    """Summary

    Attributes:
        results (TYPE): Description
        total (TYPE): Description
    """

    def __init__(self, results, total):
        """Summary

        Args:
            results (TYPE): Description
            total (TYPE): Description
        """
        self.results = results
        self.total = total


class SearchResult:

    """Summary

    Attributes:
        title (TYPE): Description
        url (TYPE): Description
    """

    def __init__(self, title, url):
        """Summary

        Args:
            title (TYPE): Description
            url (TYPE): Description
        """
        self.title = title
        self.url = url
        self.retrievable = True
        self.__text = None
        self.__markup = None

    def getText(self, extractor_type='ArticleExtractor'):
        """Summary

        Args:
            extractor_type (str, optional): Description

        Returns:
            TYPE: Description
        """
        if self.retrievable and self.__text is None:
            html = self.getMarkup()
            if html is not None:
                try:
                    extractor = Extractor(
                        extractor=extractor_type, html=html)
                    self.__text = extractor.getText()
                except Exception as e:
                    logger.error('cannot get text of url=%s', self.url)
                    self.__text = ''

        return self.__text

    def getMarkup(self):
        """Summary

        Returns:
            TYPE: Description

        Raises:
            e: Description
        """
        if self.retrievable and self.__markup is None:
            try:
                response = requests.get(self.url,
                                        headers=BaseSearch.REQUEST_HEADER,
                                        allow_redirects=False)
                self.__markup = response.text
            except requests.exceptions.ConnectionError as e:
                self.retrievable = False
                logger.error('cannot get content of url=%s', self.url)
                pass
            except Exception as e:
                raise e
        return self.__markup

    def __str__(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return str(self.__dict__)

    def __unicode__(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return unicode(self.__str__())

    def __repr__(self):
        """Summary

        Returns:
            TYPE: Description
        """
        return self.__str__()


class GoogleSearch(BaseSearch):

    """Summary

    Attributes:
        RESULT_SELECTOR (str): Description
        SEARCH_URL (str): Description
        TOTAL_SELECTOR (str): Description
    """

    # Google
    SEARCH_URL = 'https://google.com'
    RESULT_SELECTOR = 'h3.r a'
    TOTAL_SELECTOR = '#resultStats'
    NEXT_PAGE_SELECTOR = 'a.pn'

    def __init__(self, ignored_sites=None, ignored_extensions=None):
        """Summary

        Args:
            ignored_sites (None, optional): Description
            ignored_extensions (None, optional): Description
        """
        BaseSearch.__init__(
            self,
            settings={'search_url': GoogleSearch.SEARCH_URL,
                      'result_selector': GoogleSearch.RESULT_SELECTOR,
                      'total_selector': GoogleSearch.TOTAL_SELECTOR,
                      'next_page_selector': GoogleSearch.NEXT_PAGE_SELECTOR},

            ignored_sites=ignored_sites,
            ignored_extensions=ignored_extensions)


class BingSearch(BaseSearch):

    """Summary

    Attributes:
        RESULT_SELECTOR (str): Description
        SEARCH_URL (str): Description
        TOTAL_SELECTOR (str): Description
    """

    # Bing
    SEARCH_URL = 'https://www.bing.com'
    RESULT_SELECTOR = 'li.b_algo h2 a'
    TOTAL_SELECTOR = 'span.sb_count'
    NEXT_PAGE_SELECTOR = 'li.b_pag ul li a.sb_pagN'

    def __init__(self, ignored_sites=None, ignored_extensions=None):
        """Summary

        Args:
            ignored_sites (None, optional): Description
            ignored_extensions (None, optional): Description
        """
        BaseSearch.__init__(
            self,
            settings={'search_url': BingSearch.SEARCH_URL,
                      'result_selector': BingSearch.RESULT_SELECTOR,
                      'total_selector': BingSearch.TOTAL_SELECTOR,
                      'next_page_selector': BingSearch.NEXT_PAGE_SELECTOR},
            ignored_sites=ignored_sites,
            ignored_extensions=ignored_extensions)


if __name__ == "__main__":

    IGNORED_SITES = ['scholar.google.com.vn']
    IGNORED_EXTENSIONS = ['.pdf']
    search = BingSearch(ignored_sites=IGNORED_SITES,
                        ignored_extensions=IGNORED_EXTENSIONS)
    i = 1
    query = " ".join(sys.argv[1:])
    if len(query) == 0:
        query = "Patient controlled analgesia (PCA) [Inject]"
    count = 20
    print("Fetching first " + str(count) + " results for \"" + query + "\"...")
    response = search.search(query, count, prefetch_pages=False)

    print("TOTAL: " + str(response.total) + " RESULTS")
    export_dir = '../../output/google_search_result/'

    for result in response.results:
        try:
            content = result.getText()
            if content is not None and len(content) > 0:
                file_path = os.path.join(
                    export_dir, base64.b64encode(result.url) + '.txt')

                print("RESULT #" + str(i) + ": " +
                      base64.b64encode(result.url) + ", " + result.url)
                i += 1
                with open(file_path, 'w') as f:
                    f.write(content.encode('utf-8'))
        except Exception as e:
            print(e)
            print('ERROR: cannot get content of url=%s' % result.url)
            pass
