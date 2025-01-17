from typing import Union
import os

from fastapi import FastAPI
from pydantic import BaseModel

from bson import ObjectId
import motor.motor_asyncio
from pymongo import ReturnDocument

from .models import *

app = FastAPI(
    title="Student Course API",
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
)
async def list_pages():
    """
    List all of the pages data in the database.

    The response is unpaginated and limited to 50 results.
    """
    return PageCollection([page.id for page in await page_collection.find().to_list(100)])


@app.get(
    "/pages/{page_id}",
    response_description="List all pages",
    response_model=Page,
    response_model_by_alias=False,
)
async def get_saved_page(page_id):
    """
    Returns saved page body from database.
    """
    return await page_collection.find_one({"_id": ObjectId(page_id)}).body 