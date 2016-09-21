import os

from mock import patch
import pytest

from web_crawler.web_crawler import Crawler


@pytest.mark.parametrize('test_link, result', [
    ('None', False),
    ('/', False),
    ('/email/', False),
    ('/en/', False),
    ('/en-de/', False),
    ('http://www.thewestbayhotel.co.uk', False),
    ('/valid/', True),
    ('http://www.thewestbayhotel.co.uk/test/', True),
    ('http://google.com/', False),
])
def test_validate_link(test_link, result):
    homepage = 'http://www.thewestbayhotel.co.uk'
    assert Crawler.validate_link(homepage, test_link) == result


def test_filter_links():
    crawler = Crawler('http://www.thewestbayhotel.co.uk', 'output')
    links = ['/test1/', '/test1/', '/test2/', '/']
    filtered_links = crawler.filter_links(links)
    assert len(filtered_links) == 2
    assert filtered_links[0] == 'http://www.thewestbayhotel.co.uk/test1/'
    assert filtered_links[1] == 'http://www.thewestbayhotel.co.uk/test2/'


@patch('web_crawler.web_crawler.Page')
def test_crawl(MockPage, capsys):
    homepage = 'http://www.thewestbayhotel.co.uk'
    page = MockPage.return_value
    page.parse_page_content.side_effect = [
        {
            'links': ['/child1/', '/child2/'],
            'css': ['/css/'],
            'img': ['img.png'],
        },
        {
            'links': ['/child3/'],
            'css': ['/css/'],
            'img': ['img.png'],
        },
        {
            'links': [None],
            'css': ['/css/'],
            'img': ['img.png'],
        },
        {
            'links': [None],
            'css': ['/css/'],
            'img': ['img.png'],
        },
    ]
    crawler = Crawler(homepage, 'output')
    crawler.crawl()

    assert crawler.sitemap['top'] == {
        'img': ['img.png'], 'css': ['/css/'],
        'links': ['/child1/', '/child2/'],
        'child_links': [homepage + '/child2/', homepage + '/child1/'],
    }
    assert crawler.sitemap[homepage + '/child1/'] == {
        'img': ['img.png'], 'css': ['/css/'],
        'links': [None],
        'child_links': [],
    }
    assert crawler.sitemap[homepage + '/child2/'] == {
        'img': ['img.png'], 'css': ['/css/'],
        'links': ['/child3/'],
        'child_links': [homepage + '/child3/'],
    }
    assert crawler.sitemap[homepage + '/child3/'] == {
        'img': ['img.png'], 'css': ['/css/'],
        'links': [None],
        'child_links': [],
    }


def test_print_child_links(capsys):
    assert not Crawler.print_child_links([])

    Crawler.print_child_links(['l1', 'l2'])
    out, err = capsys.readouterr()
    assert out == '  Child links: \n  l1\n  l2\n'


output_text = '''Site: http://www.thewestbayhotel.co.uk
- Images:
  i1
- CSS:
  css1
- Child links:
    Site: http://www.thewestbayhotel.co.uk/l1/
    - CSS:
      css1
    - Child links:
        Site: http://www.thewestbayhotel.co.uk/l3/
    Site: http://www.thewestbayhotel.co.uk/l2/
    - Images:
      i1
'''


def test_print_results():
    homepage = 'http://www.thewestbayhotel.co.uk'
    outfile = './crawler_temp.txt'
    crawler = Crawler(homepage, outfile)
    crawler.sitemap = {
        'top': {
            'img': ['i1'], 'css': ['css1'],
            'child_links': [homepage + '/l1/', homepage + '/l2/'],
        },
        homepage + '/l1/': {
            'img': [], 'css': ['css1'],
            'child_links': [homepage + '/l3/'],
        },
        homepage + '/l2/': {
            'img': ['i1'], 'css': [],
            'child_links': [],
        },
        homepage + '/l3/': {
            'img': [], 'css': [],
            'child_links': [],
        },
    }
    crawler.output_results()
    with open(outfile, 'r') as fh:
        assert fh.read() == output_text
    os.remove(outfile)
