from link_scraper import get_links, load_urls_from_backup
from image_scraper import scrape


if __name__ == "__main__":

    BLOCKED_URLS = [
        "http://dk.tribotec.se/",
        "https://en.tribotec.se/"
    ]

    BLOCKED_URL_PATHS = [
        "/wp-content/uploads"
    ]

    PATH = r"/Users/RasmusEnglund/Desktop/Scraper/result2"
    bURL = "https://tribotec.se/"

    #links = get_links(bURL, BLOCKED_URLS, BLOCKED_URL_PATHS, PATH)
    links = load_urls_from_backup(PATH)
    print(len(list(links)))
    scrape(links, PATH)


