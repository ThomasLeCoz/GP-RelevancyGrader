## Imports
import time, sys, os, re, random
import urllib
import requests
from bs4 import BeautifulSoup

## Settings

##### Files
LINKS_FILENAME = 'links.txt'
RESULTS_FILENAME = 'results.txt'

##### Timing
RANDOM_TIME_MIN = 20.1
RANDOM_TIME_MAX = 60.0

#### Browser Config
BROWSER_HEADERS = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36', 'referer': 'https://www.google.com/search'}

## Functions
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

def file_len(fname):
	try:
		with open(fname) as f:
			for i, l in enumerate(f):
				pass
	except EnvironmentError:
		print '[-] Couldn\'t find ' + LINKS_FILENAME + ' in the working directory.'
		sys.exit()

	return i + 1

def op_duration(file_len, RANDOM_TIME_MIN=RANDOM_TIME_MIN, RANDOM_TIME_MAX=RANDOM_TIME_MAX):
	min_time = ( file_len * RANDOM_TIME_MIN ) / 3600
	max_time = ( file_len * RANDOM_TIME_MAX ) / 3600
	duration = [round(min_time,2), round(max_time, 2)]
	return duration

def getPage(url):
	try:
	    page = requests.get(url, headers=BROWSER_HEADERS)
	    page.encoding = 'utf-8'
	    return page.text
	    
	except requests.exceptions.RequestException as e: 
	    #print '[-] ' + str(e)
	    return False
	

def getNumberIndexedPages(page):
	content = BeautifulSoup(page, "html.parser")
	stat_phrase = content.find("div", {"id": "resultStats"})
	res_index = re.search(r'\d{1,3}(,\d{3})*(\.\d+)?', str(stat_phrase))
	if res_index is not None:
		number_indexed_pages = filter(None, res_index.group())
	else:
		print '\n\n[-] Coudln\'t find the number of pages of the Google index. Two possibilities: first, your IP might have been temporarily flagged by Google, wait 2 hours or use a VPN to solve this. The other possibility is that there\'s a bad link in your ' + str(LINKS_FILENAME) + ' file.'
		sys.exit()
		
	return number_indexed_pages


## Main Process
def Main():

	print '\nRevelancy Grader Assistant (RGA)\n'
	print '[+] Welcome, starting work right now. Note that there are long preiods of pause between link explorations, you might think the script has stalled, but it probably didn\'t'

	# Check if there's a file and the number of lines
	file_length = file_len(LINKS_FILENAME)
	if file_length == 0:
		print '[-] Looks like ' + LINKS_FILENAME + ' is empty.'
		sys.exit()
	else:
		duration = op_duration(file_length)
		print '[+] Found ' + LINKS_FILENAME + ' with ' + str(file_length) + ' links. It will take between ' + str(duration[0]) + ' hours and ' + str(duration[1]) + ' hours to complete.'
	
	# File to output the results
	results_file = open(RESULTS_FILENAME, 'w')
	i = 0

	print '\n'
	printProgress(i, file_length, prefix = 'Progress:', suffix = 'Complete', barLength = 50)

	with open(LINKS_FILENAME, 'r') as f:
		for url in f:
			page = getPage(url)
			if page != False:
				index_nb = getNumberIndexedPages(page)
				results_file.write(str(index_nb) + '\n')
			else:
				results_file.write('\n')
			i += 1
			printProgress(i, file_length, prefix = 'Progress:', suffix = 'Complete', barLength = 50)
			time.sleep(random.uniform(RANDOM_TIME_MIN, RANDOM_TIME_MAX))

	results_file.close()
	print '\n[+] All done, results are in ' + RESULTS_FILENAME 


if __name__ == "__main__":
	Main()