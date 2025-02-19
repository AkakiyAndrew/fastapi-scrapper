from typing import Union
import pathlib
import scrapping.utils as utils

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, FileResponse
from bson import ObjectId

from models import *
from db import page_collection, static_collection

app = FastAPI(
    title="Web Pages Saver API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)


@app.post(
    "/pages/",
    response_description="Add new page",
    response_model=Page,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_page(page: Page = Body(...)):
    """
    Insert a new page record.

    A unique `id` will be created and provided in the response.
    """

    # TODO: if provided ONLY a URL, fetch/scrap the page and save it.
    # TODO: if provided a body - save it as is, fetch statics and save them as well.


    if page.save_time is None:
        page.save_time = datetime.datetime.now().astimezone()

    if page.body is None:
        presumptive_path = pathlib.Path(__file__).parent / "pages_example" / utils.get_domain(page.url)
        if presumptive_path.exists():
            with open(presumptive_path, mode="r", encoding="utf-8") as f:
                page.body = f.read()
        else:
            page.body = "<!DOCTYPE html><html><head></head><body>Hello, World!</body></html>"

    new_page = await page_collection.insert_one(
        page.model_dump(by_alias=True, exclude=["id"])
    )
    created_page = await page_collection.find_one(
        {"_id": new_page.inserted_id}
    )
    return created_page


@app.get(
    "/pages/",
    response_description="List all pages",
    response_model=PageCollection,
    response_model_by_alias=False,
    response_model_exclude={"pages": {"body"}},
)
async def list_pages():
    """
    List all of the pages data in the database.

    The response is unpaginated and limited to 50 results.
    """

    return PageCollection(pages=await page_collection.find().to_list(100))


@app.get(
    "/pages/{page_id}",
    response_description="Get body of saved page",
    response_class=HTMLResponse,
)
async def get_saved_page(page_id):
    """
    Returns saved page body from database.
    """
    page = await page_collection.find_one({"_id": ObjectId(page_id)})
    return page['body']


@app.get(
    "/pages/statics/{static_id}",
    response_description="Get static file",
    response_class=FileResponse,
)
async def get_saved_static_file(static_id):
    """
    Returns saved static file from database.
    """
    static = await static_collection.find_one({"_id": ObjectId(static_id)})
    return static['file']