import requests
import pickle
import os
from urllib.parse import urlparse, urljoin
from bs4 import BeautifulSoup

# vars
MAX_URLS = 30
REPORT_THRESHOLD = 100
backup_filename = "links.pkl"

# initialize the set of links (unique links)
blocked_urls = set()
blocked_url_paths = set()

internal_urls = set()
visited_urls = set()

# number of urls visited so far will be stored here
total_urls_visited = 0





# methods

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and \
           bool(parsed.scheme) and \
           "tel" not in url and \
           "mailto" not in url

def get_all_website_links(url):
    """
    Returns all URLs that is found on `url` in which it belongs to the same website
    """

    urls = set()  # all URLs of `url`
    domain_name = urlparse(url).netloc  # domain name of the URL without the protocol

    try:
        soup = BeautifulSoup(requests.get(url).content, "lxml")
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {url}")
        return []

    for a_tag in soup.findAll("a"):
        href = a_tag.attrs.get("href")
        if href == "" or href is None:
            # href empty tag
            continue

        # join the URL if it's relative (not absolute link)
        href = urljoin(url, href)
        parsed_href = urlparse(href)
        # remove URL GET parameters, URL fragments, etc.
        href = parsed_href.scheme + "://" + parsed_href.netloc + parsed_href.path

        if not is_valid(href):
            continue
        if domain_name not in href:
            continue
        if href in blocked_urls:
            continue
        if href in internal_urls:
            continue
        if any([blocked_url_path in href for blocked_url_path in blocked_url_paths]):
            continue

        urls.add(href)
        internal_urls.add(href)
        if len(internal_urls) % REPORT_THRESHOLD == 0:
            print("Got ", len(internal_urls), " urls")
    return urls

def crawl(url):
    """
    Crawls a web page and extracts all links.
    You'll find all links in `external_urls` and `internal_urls` global set variables.
    """
    global total_urls_visited
    total_urls_visited += 1

    links = get_all_website_links(url)
    for link in links:
        if total_urls_visited > MAX_URLS:
            break
        crawl(link)

def get_links(url: str, _blocked_urls, _blocked_url_paths, result_path):
    global blocked_urls, blocked_url_paths
    blocked_urls = set(_blocked_urls)
    blocked_url_paths = set(_blocked_url_paths)

    crawl(url)
    print("[+] Total Internal links:", len(internal_urls))

    # Save backup
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    backup_path = os.path.join(result_path, backup_filename)
    with open(backup_path, "wb") as f:
        pickle.dump(internal_urls, f)
        print(f"Saved URLs to {backup_path}")

    return internal_urls

def load_urls_from_backup(path):
    backup_path = os.path.join(path, backup_filename)
    with open(backup_path, "rb") as f:
        backup_urls = pickle.load(f)
        return backup_urls


