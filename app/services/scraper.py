import os
import time
from typing import List, Dict, Optional
from urllib import robotparser
from urllib.parse import urljoin

import logging
import requests
from bs4 import BeautifulSoup

USER_AGENT = os.getenv("SCRAPER_USER_AGENT", "WebScraper/1.0")
RATE_LIMIT = float(os.getenv("SCRAPER_RATE_LIMIT_SECONDS", "0.7"))
REQ_TIMEOUT = float(os.getenv("SCRAPER_REQUEST_TIMEOUT", "10"))
RESPECT_ROBOTS = os.getenv("SCRAPER_RESPECT_ROBOTS", "1") == "1"

BASE_URL = "https://books.toscrape.com/"

logger = logging.getLogger(__name__)


def _get_session() -> requests.Session:
    s = requests.Session()
    s.headers.update({"User-Agent": USER_AGENT})
    return s


def _load_robots(base_url: str) -> robotparser.RobotFileParser:
    rp = robotparser.RobotFileParser()
    rp.set_url(urljoin(base_url, "robots.txt"))
    try:
        rp.read()
        logger.info("robots.txt loaded")
    except Exception as e:
        logger.warning("robots.txt not available (%s) — proceeding.", e)
    return rp


def _can_fetch(rp: robotparser.RobotFileParser, url: str) -> bool:
    if not RESPECT_ROBOTS:
        return True
    try:
        return rp.can_fetch(USER_AGENT, url)
    except Exception:
        logger.warning("robots.txt check failed for %s — allowing by default.", url)
        return True


def scrape_books() -> List[Dict[str, Optional[str]]]:
    """
    Scrape 1 page of books.toscrape.com and return a list of items,
    each item is {title, description, url}
    """
    list_url = urljoin(BASE_URL, "catalogue/page-1.html")

    session = _get_session()
    rp = _load_robots(BASE_URL)

    logger.info("GET %s", list_url)
    r = session.get(list_url, timeout=REQ_TIMEOUT)
    r.raise_for_status()

    soup = BeautifulSoup(r.text, "html.parser")

    raw_links = [
        a.get("href", "")
        for a in soup.select("section ol.row article.product_pod h3 a[href]")
    ]

    product_links: List[str] = []
    for href in raw_links:
        if href.startswith("../../../"):
            href = href.replace("../../../", "catalogue/")
        product_links.append(urljoin(BASE_URL, href))

    items: List[Dict[str, Optional[str]]] = []
    skipped = 0

    for product_url in product_links:
        if "/catalogue/" not in product_url:
            product_url = urljoin(
                BASE_URL, "catalogue/" + product_url.split("/")[-2] + "/index.html"
            )

        if not _can_fetch(rp, product_url):
            logger.info("robots.txt disallows product fetch: %s", product_url)
            skipped += 1
            continue

        time.sleep(RATE_LIMIT)

        try:
            logger.info("GET %s", product_url)
            pr = session.get(product_url, timeout=REQ_TIMEOUT)
            pr.raise_for_status()
        except requests.RequestException as e:
            logger.warning("Request failed for %s: %s", product_url, e)
            skipped += 1
            continue

        psoup = BeautifulSoup(pr.text, "html.parser")

        title_tag = psoup.select_one(".product_main h1")
        title = title_tag.get_text(strip=True) if title_tag else None

        desc_tag = psoup.select_one("#product_description ~ p")
        description = desc_tag.get_text(strip=True) if desc_tag else None

        if not title:
            logger.warning("Missing title for %s — skipping.", product_url)
            skipped += 1
            continue

        items.append({"title": title, "description": description, "url": product_url})

    logger.info("Scrape finished: gathered=%s, skipped=%s", len(items), skipped)
    return items
