import requests
import os
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse


def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)


if __name__ == "__main__":

    BLOCKED = [
        "http://www.stjorgengk.com/Images/logo.png"
    ]

    URLs = [
        "http://www.stjorgengk.com",
        "http://www.stjorgengk.com/banan"
    ]

    PATH = r"/Users/RasmusEnglund/Desktop/Scraper/result"

    scrape(URLs, PATH)




