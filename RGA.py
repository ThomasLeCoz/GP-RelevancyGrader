#!/usr/bin/python

"""
Revelancy Grader Assistant

This script automate scraping the number of indexed page in Google for
advanced searches.

More info at: https://thomaslecoz.com/improving-guest-post-efficiency/
"""

## Imports
import time
import sys
import os
import re
import random
import urllib
import requests
import threading
import Queue
from pprint import pprint
from itertools import islice
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

## Settings
LINKS_FILENAME = 'links.txt'
RESULTS_FILENAME = 'results.txt'
PROXY_LIST_FILENAME = 'proxies.txt'

RANDOM_TIME_MIN = 20.1
RANDOM_TIME_MAX = 60.0

threadLock = threading.Lock()
resultsFromThread = {}

class indexScraperThread(threading.Thread):
    """
    The index scraper class helps distribute the load amongst proxified
    threads
    """
    def __init__(self, scraperId, urls, proxy, ua):
        threading.Thread.__init__(self)
        self.scraperId = scraperId
        self.urls = urls.keys()
        self.proxy = proxy
        self.headers= {'User-Agent': str(ua), 'referer': 'https://www.google.com/search'}
        pprint(self.headers)

    def run(self):

        results = {}

        # For each url in the workList...
        for url in self.urls:
            page = getPage(url, self.proxy, self.headers)
            results[url] = getNumberIndexedPages(page)
            time.sleep(random.uniform(RANDOM_TIME_MIN, RANDOM_TIME_MAX))
        
        # Update the final results dictionary
        threadLock.acquire()
        resultsFromThread.update(results)
        threadLock.release()

def readProxies(proxyList):
    """
    Reads the proxy list  (ip:port:login:pass)and returns the proxies
    available and their formating for python requests.
    @params:
        proxyList - Required : name of the file with the proxies
    """
    proxyResult = []

    try:
        with open(proxyList) as f:
            for proxyLine in f.read().splitlines():
                proxyCoord = re.split(':',proxyLine)
                formattedProxy = 'http://' + proxyCoord[2] + ':' + proxyCoord[3] + '@' + proxyCoord[0] + ':' + proxyCoord[1]
                proxyResult.append(formattedProxy)
    except EnvironmentError:
        print '[-] Couldn\'t find ' + PROXY_LIST_FILENAME + ' in the working direcotry.'
        sys.exit()

    return proxyResult

def createWorkList(fname):
    """
    Returns the list of links and their corresponding index number.
    @params:
        linksFile  - Required : file with the links
    """
    linksDictionnary = {}
    try:
        with open(fname) as f:
            for link in f.read().splitlines():
                linksDictionnary[link] = '' # Adds empty links in the dictionnary
    except EnvironmentError:
            print '[-] Couldn\'t find ' + LINKS_FILENAME + ' in the working directory.'
            sys.exit()

    return linksDictionnary

def chunks(worklist, size):
    """
    Got this bit on stackoverflow to split the big worklist
    into several, equal sized ones for each thread
    """
    res = {}
    it = iter(worklist)
    j = 0 
    for i in xrange(0, len(worklist), size):
        res[j] = {k:worklist[k] for k in islice(it, size)}
        j = j + 1

    return res


def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 100, fill = '#'):
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    percent = ("{0:." + str(decimals) + "f}").format(100 * (iteration / float(total)))
    filledLength = int(barLength * iteration // total)
    bar = fill * filledLength + '-' * (barLength - filledLength)
    sys.stdout.write('\r%s |%s| %s%s %s' % (prefix, bar, percent, '%', suffix)),
    if iteration == total:
        sys.stdout.write('\n')
    sys.stdout.flush()

def op_duration(file_len, nbOfProxies, RANDOM_TIME_MIN=RANDOM_TIME_MIN, RANDOM_TIME_MAX=RANDOM_TIME_MAX):
    min_time = ( file_len * RANDOM_TIME_MIN ) / ( 3600 * nbOfProxies )
    max_time = ( file_len * RANDOM_TIME_MAX ) / ( 3600 * nbOfProxies )
    duration = [round(min_time,2), round(max_time, 2)]
    return duration

def getPage(url, proxy, random_headers):
        """
        Return the page text of the web page corresponding to the
        given URL
        @params:
            url     - Required : URL of the web page to get
            proxies - Required : http and https proxies to use for the requests
        """
        try:
            page = requests.get(url, proxy, headers=random_headers)
            page.encoding = 'utf-8'
            return page.text
            
        except requests.exceptions.RequestException as e: 
            #print '[-] ' + str(e)
            return False

def getNumberIndexedPages(page):
        """
        Returns the number of pages in the index of google
        for the given page text.
        @params:
            page - Required : web page text from requests
        """
        content = BeautifulSoup(page, "html.parser")
        stat_phrase = content.find("div", {"id": "resultStats"})
        res_index = re.search(r'\d{1,3}(,\d{3})*(\.\d+)?', str(stat_phrase))
        if res_index is not None:
            number_indexed_pages = filter(None, res_index.group())
        else:
            print '\n\n[-] Coudln\'t find the number of pages of the Google index. Two possibilities: first, your IP might have been temporarily flagged by Google, wait 2 hours or use a VPN to solve this. The other possibility is that there\'s a bad link in your ' + str(LINKS_FILENAME) + ' file.'
            number_indexed_pages = False
            
        return number_indexed_pages

def writeResults(fname, worklist):
    """
    Writes the results in an orderly manner
    @params:
        fname    - Required : the results filename
        worklist - Required : the completed worklist
    """
    results_file = open(fname, 'w')
    for link, indexNum in worklist.iteritems():
        if indexNum is not None:
            results_file.write(str(indexNum) + '\n')
        else:
            results_file.write('\n')
    results_file.close()

    return True

## Main Process
def Main():

    print '\nRevelancy Grader Assistant (RGA)\n'
    print '[+] Welcome, starting work right now. Note that there are long preiods of pause between link explorations, you might think the script has stalled, but it probably didn\'t'

    proxies = readProxies(PROXY_LIST_FILENAME)
    workList = createWorkList(LINKS_FILENAME)

    # TODO accomodate if no proxies
    nbOfProxies = len(proxies)
    if nbOfProxies == 0:
        print '[-] No proxies found in ' + PROXY_LIST_FILENAME + '. Exiting.'
        sys.exit()

    file_length = len(workList)
    if file_length == 0:
        print '[-] No links found in ' + LINKS_FILENAME + '. Exiting.'
        sys.exit()
    else:
        duration = op_duration(file_length, nbOfProxies)
        print '[+] Found ' + LINKS_FILENAME + ' with ' + str(file_length) + ' links. It will take between ' + str(duration[0]) + ' hours and ' + str(duration[1]) + ' hours to complete.'

 

    threads = []
    ua = UserAgent()

    workListShare = int(file_length / len(proxies) + 1)
    workListDict = chunks(workList, workListShare)

    i = 0


    # Start the threads, 1 by proxy detected
    for proxy in tuple(proxies):
        scraperThread = indexScraperThread(i, workListDict[i], proxy, ua.random)
        scraperThread.start()
        threads.append(scraperThread)
        i = i + 1

    # Wait for all threads to finish
    for t in threads:
        t.join()

    # Populate the workList
    for url in workList:
        if (url in resultsFromThread): 
            workList[url] = resultsFromThread[url]
        else:
            workList[url] = ''

    # End of job, output results in a file
    pprint(workList)
    if writeResults(RESULTS_FILENAME,workList):
        print '[+] Success, all done!'
    else:
        print '[-] Something went wrong when trying to write in ' + RESULTS_FILENAME + '.'


if __name__ == "__main__":
    Main()