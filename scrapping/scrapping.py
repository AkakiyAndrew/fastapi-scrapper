from bs4 import BeautifulSoup
import requests

from scrapping.utils import get_domain, get_resource_type, strip_url
from db.db import save_page, save_static
from . import scrapper
from . import HEADLESS_HEADERS

# TODO:
# сделать функцию для сохранения страницы в БД по URL - скраппинг body/statics, возможно рекурсивно
# сделать вторую функцию, которая принимает готовый body и тянет статику, без проверок URL (ручное сохранение одной странички)
def get_static(url: str) -> bytes:
    """
    Get static by url
    """
    return requests.get(url, headers=HEADLESS_HEADERS).content


async def scrape_page_by_url(
    url: str,
    recursive: bool = False,
    statics_from_other_domains: bool = False,
    scrapped_pages: set = set(),

) -> None:
    """
    Save the page to db
    """

    statics = []
    domain = get_domain(url)

    scrapped_pages.add(url)
    body = scrapper.get_body(url)
    soup = BeautifulSoup(body, 'html.parser')

    # parse statics, styles and scripts
    for tag in soup.find_all(['script', 'link', 'img', 'a']):
        tag_url = tag.get('src')
        key = 'src'
        if not tag_url:
            tag_url = tag.get('href')
            key = 'href'

        if tag_url:
            tag_url = strip_url(tag_url)
            static_type = get_resource_type(tag_url)
            if static_type == 'static':
                if not statics_from_other_domains and get_domain(tag_url) == domain:
                    continue
                saved_static = save_static(tag_url, scrapper.get_static(tag_url))
                statics.append(saved_static)
                tag[key] = f'/statics/{saved_static['_id']}'
            # if link to other page - save if it's from the same domain and if recursive
            elif static_type == 'other' and recursive and get_domain(tag_url) == domain and tag_url not in scrapped_pages:
                recursive_page = scrape_page_by_url(tag_url, recursive, statics_from_other_domains, scrapped_pages)
                tag[key] = f'/pages/{recursive_page['_id']}'

    # save the page
    return save_page(url, soup.prettify(), statics)


# async def scrape_page_by_body(
#     body: str,
#     statics_from_other_domains: bool=False
#     ) -> None:
#     """
#     Save the page to db
#     """
#     statics = []
#     domain = get_domain(url)

#     # if statics_from_other_domains:
#     #     for link in body.links:
#     #         # if domain == get_domain(link) or statics_from_other_domains:
#     #         #     statics.append(scrapper.get_static(link))

#     return body, statics
