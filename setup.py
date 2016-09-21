from setuptools import setup, find_packages

setup(
    name="web_crawler",
    version="0.0.1",
    author="Gus Chadney",
    author_email="angus.chadney@gmail.com",
    description=("Web Crawler"),
    packages=find_packages(exclude=['tests', 'tests.*']),
    scripts=['bin/web-crawler'],
)
