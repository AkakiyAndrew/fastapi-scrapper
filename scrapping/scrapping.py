from bs4 import BeautifulSoup
import requests
# from typing import Union
import logging

from scrapping.utils import get_domain, get_resource_type, prepare_url
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
        domain = get_domain(page_url)
        scrapped_pages.add(page_url)
        body = scrapper.get_body(page_url)
    else:
        domain = ""
    
    soup = BeautifulSoup(body, 'html.parser')

    title = soup.find('title')
    if title:
        title = title.text
    else:
        title = 'No title'

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
            # logging.warning(f'No key "src" or "href" in {tag}')
            continue

        # skip in-page links
        # TODO: incorporate this into resulting page
        # TODO: incorporate all #-like links
        if tag_url.startswith('#'):
            continue

        # TODO: skip exceptions when statics cant be loaded

        tag_url = prepare_url(tag_url, page_url)
        static_type = get_resource_type(tag_url)
        if static_type == 'static':
            if not page_url and not statics_from_other_domains and get_domain(tag_url) == domain:
                continue
            static_response = get_static(tag_url)
            saved_static_id = await save_static(tag_url, static_response.content, static_response.headers.get('Content-Type'))
            statics.append(saved_static_id)
            tag[key] = f'/statics/{saved_static_id}'
        # if link to other page - save if it's from the same domain and if recursive
        # TODO: pass driver to recursive scrapping
        elif page_url and static_type == 'other' and recursive and get_domain(tag_url) == domain and tag_url not in scrapped_pages:
            new_page_id = await scrape_page(tag_url, None, recursive, statics_from_other_domains, scrapped_pages)
            tag[key] = f'/pages/{new_page_id}'

    # save the page
    page_body = soup.prettify()
    return await save_page(page_url, page_body, title, statics)

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

# async def scrape_page_by_url(
#     url: str,
#     recursive: bool = False,
#     statics_from_other_domains: bool = False,
#     scrapped_pages: set = set(),
# ):
#     """
#     Save the page to db by URL
#     """

#     statics = []
#     domain = get_domain(url)
#     scrapped_pages.add(url)

#     soup = get_body_soup(url)
#     title = soup.find('title')
#     if title:
#         title = title.text
#     else:
#         title = 'No title'

#     # parse statics, styles and scripts
#     for tag in soup.find_all(['script', 'link', 'img', 'a']):
#         tag_url = tag.get('src')
#         key = 'src'
#         if not tag_url:
#             tag_url = tag.get('href')
#             key = 'href'

#         if not tag_url:
#             logging.warning(f'No key "src" or "href" in {tag}')
#             return None

#         tag_url = strip_url(tag_url)
#         static_type = get_resource_type(tag_url)
#         if static_type == 'static':
#             if not statics_from_other_domains and get_domain(tag_url) == domain:
#                 continue
#             saved_static = save_static(tag_url, scrapper.get_static(tag_url))
#             statics.append(saved_static)
#             tag[key] = f'/statics/{saved_static['_id']}'
#         # if link to other page - save if it's from the same domain and if recursive
#         elif static_type == 'other' and recursive and get_domain(tag_url) == domain and tag_url not in scrapped_pages:
#             recursive_page = scrape_page_by_url(tag_url, recursive, statics_from_other_domains, scrapped_pages)
#             if recursive_page:
#                 tag[key] = f'/pages/{recursive_page['_id']}'

#     # save the page
#     return save_page(url, soup.prettify(), title, statics)


# async def scrape_page_by_body(
#     body: str,
#     recursive: bool=False,
#     scrapped_pages: set = set(),
#     ):
#     """
#     Save the page to db by given body
#     """
#     statics = []

#     # if statics_from_other_domains:
#     #     for link in body.links:
#     #         # if domain == get_domain(link) or statics_from_other_domains:
#     #         #     statics.append(scrapper.get_static(link))

#     return body, statics
