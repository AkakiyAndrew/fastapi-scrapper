from typing import Union
import os
import pathlib

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from models import *
import utils

app = FastAPI(
    title="Web Pages Saver API",
    summary="A sample application showing how to use FastAPI to add a ReST API to a MongoDB collection.",
)
client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.page_vault
page_collection = db.get_collection("pages")


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
    raw_page = {
        k: v for k, v in page.model_dump(by_alias=True).items() if v is not None
    }

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
    # response_model_by_alias=False,
)
async def get_saved_page(page_id):
    """
    Returns saved page body from database.
    """
    page = await page_collection.find_one({"_id": ObjectId(page_id)})
    return page['body']

@app.get("/items/", response_class=HTMLResponse)
async def read_items():
    return """
    <html>
        <head>
            <title>Some HTML in here</title>
        </head>
        <body>
            <h1>Look ma! HTML!</h1>
        </body>
    </html>
    """

# import os
# from fastapi import FastAPI
# from bson import ObjectId
# import motor.motor_asyncio
# from pymongo import ReturnDocument
# app = FastAPI()

# client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
# db = client.page_vault
# page_collection = db.get_collection("pages")


# @app.get("/")
# async def root():
#     return {"message": "Hello World"}