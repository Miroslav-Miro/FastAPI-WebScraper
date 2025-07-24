# app/scraper.py
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from sqlalchemy.orm import Session

from app.models import ScrapedItem

BASE_URL = "https://books.toscrape.com/"


def scrape_books(db: Session, limit: int = 10) -> int:
    """
    Scrape up to `limit` books and store them in the database.
    Returns number of new items added.
    """
    added = 0
    page_url = urljoin(BASE_URL, "catalogue/page-1.html")

    while page_url and added < limit:
        resp = requests.get(page_url, timeout=10)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for pod in soup.select("article.product_pod"):
            if added >= limit:
                break

            a = pod.h3.a
            title = a["title"].strip()
            relative = a["href"]
            product_url = urljoin(page_url, relative)  # resolves ../ etc

            # Skip if already in DB
            if db.query(ScrapedItem).filter_by(url=product_url).first():
                continue

            # Fetch description from product page
            description = ""
            try:
                prod_resp = requests.get(product_url, timeout=10)
                prod_resp.raise_for_status()
                prod_soup = BeautifulSoup(prod_resp.text, "html.parser")
                desc_tag = prod_soup.select_one("#product_description ~ p")
                if desc_tag:
                    description = desc_tag.get_text(strip=True)
            except Exception as e:
                print(f"Failed to fetch description for {product_url}: {e}")

            item = ScrapedItem(title=title, description=description, url=product_url)
            db.add(item)
            db.commit()
            added += 1
            print(f"[SCRAPER] Added: {title}")

        next_link = soup.select_one("li.next > a")
        if next_link:
            page_url = urljoin(page_url, next_link["href"])
        else:
            page_url = None

    print(f"[SCRAPER] Finished. Added {added} new items.")
    return added
