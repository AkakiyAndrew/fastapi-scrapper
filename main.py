import io
import scrapping.scrapping as scrapping

from fastapi import FastAPI, status, Body, Response
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from bson import ObjectId

from models import DomainRepresentation, PageScrapeRequest
from db import pages_collection, static_collection, domain_collection

app = FastAPI(
    title="Web Pages Saver API",
    summary="A simple scrapping app for saving and viewing web pages, on FastAPI & MongoDB.",
)

@app.get(
    "/pages/",
    response_description="List all pages",
    response_model=DomainRepresentation,
    response_model_by_alias=False,
)
async def list_pages():
    """
    List all of the pages data in the database.

    The response is unpaginated and limited to 50 results.
    """

    # TODO: make proper pagination, with, like, ~5 page versions per page
    domains = DomainRepresentation(saved_domains=await domain_collection.find().to_list(100))
    return domains

@app.post(
    "/pages/",
    
    response_description="Add new page",
    status_code=status.HTTP_201_CREATED,
)
async def create_page(page: PageScrapeRequest = Body(...)):
    """
    Insert a new page record.

    A unique `id` will be created and provided in the response.
    """

    created_page_id = await scrapping.scrape_page(page.url, page.body)
    
    return str(created_page_id)


@app.get(
    "/pages/{page_id}",
    response_description="Get body of saved page",
    response_class=HTMLResponse,
)
async def get_saved_page(page_id):
    """
    Returns saved page body from database.
    """
    page = await pages_collection.find_one({"_id": ObjectId(page_id)})
    return page['body']


@app.get(
    "/statics/{static_id}",
    response_description="Get static file",
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


# TODO: page deletions (by page id, delete page body, remove from domain's entry)
# TODO: and reduce statics counter, maybe delete it

app.mount("/", StaticFiles(directory="static", html=True), name="static") # serve static files