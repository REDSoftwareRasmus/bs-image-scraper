from link_scraper import get_links
from image_scraper import scrape


if __name__ == "__main__":

    BLOCKED_IMAGES = [
        "http://www.stjorgengk.com/Images/logo.png"
    ]

    PATH = r"/Users/RasmusEnglund/Desktop/Scraper/result"
    bURL = "http://www.stjorgengk.com"

    links, _ = get_links(bURL)
    scrape(links, PATH, BLOCKED_IMAGES)


