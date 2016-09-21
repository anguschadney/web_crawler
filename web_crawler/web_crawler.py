from __future__ import print_function

from collections import deque
from lxml import html
import re
from urllib import urlopen
from urlparse import urljoin
from urlparse import urlparse


INDENT = 4


class Page(object):
    """Object to parse a webpage and return details (links, css, etc...)

    Args:
        url (str): page url (e.g. 'http://www.thewestbayhotel.co.uk')
    """

    def __init__(self, url):
        self.url = url

    def parse_page_content(self):
        """Fetch page data and parse relevant tags

        Returns:
            page_data (dict): dict containing page data information:
                              {
                                  'links': list of parsed links
                                  'css': list of parsed css links
                                  'img': list of parsed images
                              }
        """
        page_data = {}
        # TODO: improve error handling
        try:
            response = urlopen(self.url)
        except Exception:
            return

        content = html.fromstring(response.read())

        page_data['links'] = self.get_page_data(
            content, '//a', 'href'
        )
        page_data['css'] = self.get_page_data(
            content, '//link', 'href', 'stylesheet'
        )
        page_data['img'] = self.get_page_data(
            content, '//img', 'src'
        )
        return page_data

    @staticmethod
    def get_page_data(content, tag, attribute, rel=None):
        """Parse page for specific tags

        Args:
            content (html obj):  parsed html content
            tag (string):  tag of interest (e.g. //a)
            attribute (string):  attribute of tag to extract (e.g. 'href')
            rel (string):  used to filter out a specified 'rel' attribute if
                           necessary

        Returns:
            values (list): list of strings of parsed values
        """
        values = []
        data = content.xpath(tag)

        for item in data:
            value = item.get(attribute)
            # dont want None values
            if not value:
                continue
            # filter out items that have a matching rel attribute
            if rel and item.get('rel') != rel:
                continue
            values.append(value)
        return values


class Crawler(object):
    """Object to figure out a sitemap by crawling a page and it's descendant
    links within the same domain.

    Args:
        homepage (str): base url (e.g. 'http://www.thewestbayhotel.co.uk')
        outfile (str): file to output results in

    Attributes:
        sitemap (dict): dict corresponding to page information for each page
                        {
                            'img': []  - list of image resources found on page
                            'css': []  - list of css resources found on page
                            'links': []  - list of unparsed links
                            'child_links': []  - list of parsed links
                        }
        all_links (list): list of all links found (so we don't double count)
    """

    def __init__(self, homepage, outfile):
        self.homepage = homepage
        self.outfile = outfile
        self.sitemap = {}
        self.all_links = []

    @staticmethod
    def validate_link(homepage, link):
        # home domain or None
        if not link or len(link) == 1:
            return False
        # get rid of email links
        if 'email' in link:
            return False
        # hack to get rid of language links
        if re.match('/[a-z]{2}(-[a-z]{2})?/', link):
            return False
        # check its not a circular link
        if link.strip('/') == homepage.strip('/'):
            return False
        # extension link
        if link[0] == '/':
            return True
        # probably full url, check domain
        domain = urlparse(homepage).netloc
        if urlparse(link).netloc == domain:
            return True
        return False

    def filter_links(self, link_list):
        # remove junk
        filtered_links = [
            link for link in link_list
            if self.validate_link(self.homepage, link)
        ]
        # remove dupes
        filtered_links = set(filtered_links)
        # check not already in list
        return [
            urljoin(self.homepage, link) for link in filtered_links
            if urljoin(self.homepage, link) not in self.all_links
        ]

    @staticmethod
    def print_child_links(links):
        if links:
            print('  Child links: ')
            for link in links:
                print('  ' + link)

    def crawl(self):
        self.all_links = []
        homepage = Page(self.homepage)
        print('Crawling domain ' + self.homepage)
        page_data = homepage.parse_page_content()

        # No information returned for main webpage, therefore just exit
        if not page_data:
            print('Invalid hostname')
            return

        filtered_links = self.filter_links(page_data['links'])
        self.print_child_links(filtered_links)
        page_data['child_links'] = list(filtered_links)

        self.sitemap['top'] = page_data

        self.all_links = filtered_links
        unvisited_links = deque(filtered_links)

        while len(unvisited_links):
            print('Number to sites to visit: ' + str(len(unvisited_links)))
            current_link = unvisited_links.popleft()
            print('Crawling page ' + current_link)
            page = Page(current_link)
            page_data = page.parse_page_content()

            filtered_links = self.filter_links(page_data['links'])
            self.print_child_links(filtered_links)
            page_data['child_links'] = list(filtered_links)

            self.all_links.extend(filtered_links)
            unvisited_links.extend(filtered_links)

            self.sitemap[current_link] = page_data

    @staticmethod
    def _print_details(fh, link, site_dict, indent):
        print(' ' * indent + 'Site: ' + link, file=fh)

        if len(site_dict['img']):
            print(' ' * indent, end='', file=fh)
            print('- Images:', file=fh)
            for img in site_dict['img']:
                print(' ' * indent, end='', file=fh)
                print('  ' + img, file=fh)

        if len(site_dict['css']):
            print(' ' * indent, end='', file=fh)
            print('- CSS:', file=fh)
            for css in site_dict['css']:
                print(' ' * indent, end='', file=fh)
                print('  ' + css, file=fh)

    def _print_site(self, fh, site, indent=''):
        indent += INDENT
        sm = self.sitemap
        child_links = sm[site]['child_links']
        if len(child_links):
            print(' ' * (indent - INDENT) + '- Child links:', file=fh)
            for child in child_links:
                self._print_details(fh, child, sm[child], indent=indent)
                self._print_site(fh, child, indent=indent)
        indent += -INDENT

    def output_results(self):
        if not self.sitemap:
            return
        print('\nWriting to file: ' + self.outfile)
        fh = open(self.outfile, 'w')
        indent = 0
        self._print_details(fh, self.homepage, self.sitemap['top'], indent)
        self._print_site(fh, 'top', indent)
        fh.close()
