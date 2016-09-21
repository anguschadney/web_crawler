# Web Crawler

A script and module to crawl a webpage and determine it's sitemap

## Requirements
- Linux
- Python 2.7.10
- pip 8.1.2

## Project contents
```
bin/
  web-crawler
web_crawler/
  __init__.py
  web_crawler.py
README.md
requirements.txt
setup.py
test/
  test_web_craw ler.py
```

## Installation instructions
```python
pip install -e .
pip install -r requirements.txt
```

## Testing
```python
py.test
```

## Usage
```
web-crawler -h
```
```
usage: web-crawler [-h] -w WEBSITE [-o OUTFILE]

Crawl a website and save the sitemap to an output file

optional arguments:
  -h, --help            show this help message and exit
  -w WEBSITE, --website WEBSITE
                        website (http://www.thewestbayhotel.co.uk)
  -o OUTFILE, --outfile OUTFILE
                        output file (results.txt)
```

## Example
```
web-crawler -w http://www.thewestbayhotel.co.uk -o results.txt
```
