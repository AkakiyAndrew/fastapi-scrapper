from bs4 import BeautifulSoup
import requests
# from typing import Union
import logging

from scrapping.utils import get_url_domain, get_resource_type, get_url_fragment, prepare_url, strip_url
from db.db import save_page, save_static
from . import scrapper
from .chrome_scrapper import HEADLESS_HEADERS
# from ..models import Page

# TODO:
# сделать функцию для сохранения страницы в БД по URL - скраппинг body/statics, возможно рекурсивно
# сделать вторую функцию, которая принимает готовый body и тянет статику, без проверок URL (ручное сохранение одной странички)
def get_static(url: str) -> requests.Response:
    """
    Get static by url
    """
    return requests.get(url, headers=HEADLESS_HEADERS)


async def scrape_page(
    page_url: str,
    body: str=None,
    recursive: bool = False,
    statics_from_other_domains: bool = False,
    scrapped_pages: set = None,
):
    """
    Save the page to db by URL or body
    """
    
    if not body and not page_url:
        # logging.error('No body or url provided')
        raise ValueError('No body or url provided')
    
    if not page_url and recursive:
        raise ValueError('Recursive scrapping is not supported without URL. Use scrape_page_by_URL instead')

    statics = []
    scrapped_pages = scrapped_pages or set()
    if page_url:
        domain = get_url_domain(page_url)
        scrapped_pages.add(page_url)
        body, page_screenshot = await scrapper.get_body(page_url)
        page_url = strip_url(page_url)
    else:
        domain = ""
    
    soup = BeautifulSoup(body, 'html.parser')

    # TODO: parse all tags, save in list and only after - scrape them async-like? (statics first) 

    # parse statics, styles and scripts
    for tag in soup.find_all(['script', 'link', 'img', 'a']):
        if tag.get('rel') == "preconnect":
            continue

        tag_url = tag.get('src')
        key = 'src'
        if not tag_url:
            tag_url = tag.get('href')
            key = 'href'

        if not tag_url:
            logging.debug(f'No key "src" or "href" in {tag}')
            continue

        # skip in-page links
        if tag_url.startswith('#'):
            continue

        fragment = get_url_fragment(tag_url)
        if fragment:
            # if it leads to another page and no url provided - skip
            tag_url_path = strip_url(tag_url)
            if page_url and tag_url_path == page_url:
                # if its on same page - convert to anchor
                tag[key] = "#" + fragment

        tag_url = prepare_url(tag_url, page_url)
        static_type = get_resource_type(tag_url)
        if static_type == 'static':
            if not page_url and not statics_from_other_domains and get_url_domain(tag_url) == domain:
                continue
            try:
                # TODO: utilize async queue for urls
                static_response = get_static(tag_url)
                saved_static_id = await save_static(tag_url, static_response.content, static_response.headers.get('Content-Type'))
                statics.append(saved_static_id)
                tag[key] = f'/statics/{saved_static_id}'
            except Exception as e:
                logging.error(f'Failed to load static {tag_url}: {e}')
                continue
        # if link to other page - save if it's from the same domain and if recursive
        elif page_url and static_type == 'other' and recursive and get_url_domain(tag_url) == domain and tag_url not in scrapped_pages:
            new_page_id = await scrape_page(tag_url, None, recursive, statics_from_other_domains, scrapped_pages)
            tag[key] = f'/pages/{new_page_id}'

    # save the page
    title = soup.find('title')
    if title:
        title = title.text or 'No title'
    else:
        title = 'No title'
    page_body = soup.prettify()
    return await save_page(page_url, page_body, page_screenshot, title, statics)


async def scrape_page_by_url(
    url: str,
    recursive: bool = False,
    statics_from_other_domains: bool = False,
    scrapped_pages: set = set(),
):
    """
    Save the page to db by URL
    """

    return await scrape_page(url, None, recursive, statics_from_other_domains, scrapped_pages)


async def scrape_page_by_body(
    body: str,
    scrapped_pages: set = set(),
):
    """
    Save the page to db by body
    """

    return await scrape_page(None, body, False, False, scrapped_pages)