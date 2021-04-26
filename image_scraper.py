import requests
import os
import cssutils
import pickle
from tqdm import tqdm
from bs4 import BeautifulSoup as bs
from urllib.parse import urljoin, urlparse


# vars
backup_filename = "image-urls.pkl"


# methods

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    valid_parse = bool(parsed.netloc) and bool(parsed.scheme)

    valid_extensions = ["jpg", "png", "gif", "jpeg"]
    contains = [(ext in url or ext.upper() in url) for ext in valid_extensions]
    return valid_parse and any(contains)

def parse_css_background(url):
    return url.replace('url(', '').replace(')', '')

def get_all_images(url):
    """
    Returns all image URLs on a single `url`
    """
    try:
        soup = bs(requests.get(url).content, "lxml")
    except requests.exceptions.ConnectionError:
        print(f"Could not connect to {url}")
        return []
    except Exception as e:
        print(f"Could request soup in {url}")
        return []

    urls = []

    def add_url(u):
        # make the URL absolute by joining domain with the URL that is just extracted
        if "https" not in u and "http" not in u:
            img_url = urljoin(url, u)
        else:
            img_url = u

        # There are some URLs that contains HTTP GET key value pairs which we don't
        # like (that ends with something like this "/image.png?c=3.2.5"),
        # let's remove them:

        try:
            pos = img_url.index("?")
            img_url = img_url[:pos]
        except ValueError:
            pass

        # finally, if the url is valid
        if is_valid(img_url):
            if img_url not in urls:
                urls.append(img_url)
            else:
                print(f"Double {img_url}")
        else:
            print("not valid ", img_url)


    for img in soup.find_all("img"):
        img_url = img.attrs.get("src")
        if not img_url:
            # if img does not contain src attribute, just skip
            continue
        add_url(img_url)

    for div in soup.find_all("div"):
        div_style = div.get("style", None)

        if div_style is not None:
            style = cssutils.parseStyle(div['style'])

            img_url = style['background-image']
            if img_url != "":
                _url = parse_css_background(img_url)
                add_url(_url)

            img_bg = style['background']
            if img_bg != "":
                _url = parse_css_background(img_bg)
                add_url(_url)

    for a in soup.find_all("a"):
        a_style = a.get("style", None)
        if a_style is not None:
            style = cssutils.parseStyle(a['style'])

            img_url = style['background-image']
            if img_url != "":
                _url = parse_css_background(img_url)
                add_url(_url)

            img_bg = style['background']
            if img_bg != "":
                _url = parse_css_background(img_bg)
                add_url(_url)

    return urls

def download(url, pathname):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)

    files = [os.path.join(pathname, f) for f in os.listdir(pathname)]
    # download the body of response by chunk, not immediately
    try:
        response = requests.get(url, stream=True)
    except Exception as e:
        print(f"Could not download image at {url}. Error: {e}")
        return

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))
    # get the file name
    idx = 1
    filename = os.path.join(pathname, url.split("/")[-1])
    while filename in files:
        filename = os.path.join(pathname, str(idx) + " - " + url.split("/")[-1])
        idx += 1
        print("got duplicate name")

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)

    with open(filename, "wb") as f:
        for data in progress:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))


def scrape(urls, result_path):

    # Get all images
    imgs = []

    for url in tqdm(urls, "Finding image urls..."):
        u_imgs = get_all_images(url)
        imgs.extend(u_imgs)

    l = len(imgs)
    imgs = list(set(imgs))
    print(f"Removed page doubles {l - len(imgs)}")

    for img in imgs:
        assert imgs.count(img) == 1

    # Save backup
    if not os.path.exists(result_path):
        os.mkdir(result_path)
    backup_path = os.path.join(result_path, backup_filename)
    with open(backup_path, "wb") as f:
        pickle.dump(imgs, f)
        print(f"Saved image URLs to {backup_path}")

    # Download
    print(f"TOTAL {len(imgs)}")
    print(imgs)
    for img in tqdm(imgs, "Downloading images..."):
        # for each image, download it
        download(img, result_path)

def load_image_urls_from_backup(path):
    backup_path = os.path.join(path, backup_filename)
    with open(backup_path, "rb") as f:
        backup_urls = pickle.load(f)
        return backup_urls

