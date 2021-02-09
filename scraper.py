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

def get_all_images(url):
    """
    Returns all image URLs on a single `url`
    """
    soup = bs(requests.get(url).content, "html.parser")
    urls = []
    for img in tqdm(soup.find_all("img"), "Extracting images"):
        img_url = img.attrs.get("src")
        if not img_url:
            # if img does not contain src attribute, just skip
            continue
        # make the URL absolute by joining domain with the URL that is just extracted
        img_url = urljoin(url, img_url)

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
            if img_url in BLOCKED:
                print(f"Blocked {img_url}")
                continue

            if img_url not in urls:
                urls.append(img_url)
            else:
                print(f"Double {img_url}")

    return urls

def download(url, pathname):
    """
    Downloads a file given an URL and puts it in the folder `pathname`
    """
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)
    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))
    # get the file name
    filename = os.path.join(pathname, url.split("/")[-1])
    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for data in progress:
            # write data read to the file
            f.write(data)
            # update the progress bar manually
            progress.update(len(data))


def scrape(urls, path):
    # get all images
    imgs = []

    for url in urls:
        u_imgs = get_all_images(url)
        imgs.extend(u_imgs)

    l = len(imgs)
    imgs = list(set(imgs))
    print(f"Removed page doubles {l - len(imgs)}")

    for img in imgs:
        assert imgs.count(img) == 1

    print(f"TOTAL {len(imgs)}")
    return
    for img in imgs:
        # for each image, download it
        download(img, path)


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




