import io
import datetime
from typing import Union
import pathlib
import scrapping.utils as utils
import scrapping.scrapping as scrapping

from fastapi import FastAPI, status, Body, Response
from fastapi.responses import HTMLResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from bson import ObjectId

from models import Page, PageCollection, PageScrapeRequest
from db import page_collection, static_collection

app = FastAPI(
    title="Web Pages Saver API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)

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

@app.post(
    "/pages/",
    
    response_description="Add new page",
    response_model=Page,
    status_code=status.HTTP_201_CREATED,
    response_model_by_alias=False,
)
async def create_page(page: PageScrapeRequest = Body(...)):
    """
    Insert a new page record.

    A unique `id` will be created and provided in the response.
    """

    # page = {}

    # if page.save_time is None:
    #     page.save_time = datetime.datetime.now().astimezone()

    created_page_id = await scrapping.scrape_page(page.url, page.body)
    
    return await page_collection.find_one({"_id": created_page_id})


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
    "/statics/{static_id}",
    response_description="Get static file",
    # response_class=FileResponse,
)
async def get_saved_static_file(static_id):
    """
    Returns saved static file from database.
    """
    static = await static_collection.find_one({"_id": ObjectId(static_id)})
    # return static['file']
    if not static:
        return Response("Not found", status_code=status.HTTP_404_NOT_FOUND)

    return StreamingResponse(content=io.BytesIO(static['file']), media_type=static["media_type"])


app.mount("/", StaticFiles(directory="static", html=True), name="static") # serve static files