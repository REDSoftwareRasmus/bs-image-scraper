from link_scraper import get_links
from image_scraper import scrape


if __name__ == "__main__":

    BLOCKED_IMAGES = [
    ]

    PATH = r"/Users/RasmusEnglund/Desktop/Scraper/result2"
    bURL = "http://www.gardajohan.se/"

    links, _ = get_links(bURL)
    scrape(links, PATH, BLOCKED_IMAGES)


