# Guest Post Relevancy Grader

RGA — Relevancy Grader Assistant is a script that helps with grading guest posts opportunities.

Basically, it scrapes the number of pages in the index of Google for very specific search phrases, allowing us to determine the relevancy of a website by analyzing the ratio of the number of pages correlated to a search term to the total number of pages in the index of Google.

It's very gentle with Google and tries to be as natural as possible to avoid triggering the numerous protections in place.

## Usage

** Important Note: ** This script is useless on its own, it aims to complete a streamlined process.[Read the article for more information] (https://thomaslecoz.com/improving-guest-post-efficiency/)

1. Copy the links from your Google Sheets into links.txt (or `LINKS_FILENAME` value)
2. Execture RGA : `./RGA.py`
3. Once finished, copy and paste the content of results.txt (or `RESULTS_FILENAME` value) into the appropriate column on Sheets

[Click here for detailed instructions](https://thomaslecoz.com/improving-guest-post-efficiency/)