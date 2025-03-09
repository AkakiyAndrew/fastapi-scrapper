import datetime
from typing import Optional, List
from typing_extensions import Annotated

from fastapi import FastAPI, Body, HTTPException, status
from fastapi.responses import Response
from pydantic import ConfigDict, BaseModel, Field, NaiveDatetime
from pydantic.functional_validators import BeforeValidator

from bson import ObjectId

# Represents an ObjectId field in the database.
# It will be represented as a `str` on the model so that it can be serialized to JSON.
PyObjectId = Annotated[str, BeforeValidator(str)]


class PageScrapeRequest(BaseModel):
    """
    Request for scraping a page.
    """

    url: str = Field(..., description="The URL of the page to scrape.")
    body: Optional[str] = Field(
        None,
        description="The body of the page to save. If not provided, the page will be scraped.",
    )
    recursive: Optional[bool] = Field(
        False, description="If true, scrape all URLs on page from same domain recursively."
    )
    statics_from_other_domains: Optional[bool] = Field(
        False, description="If true, save statics from other domains."
    )

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        json_schema_extra={
            "example": {
                "url": "https://example.com/home",
                "recursive": False,
                "statics_from_other_domains": False,
                "body": "<!DOCTYPE html><html><head></head><body>Hello, World!</body></html>",
            }
        },
    )

class Page(BaseModel):
    """
    Single saved page
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    url: str = Field(...)
    body: Optional[str] = None
    save_time: Optional[NaiveDatetime] = None
    title: Optional[str] = None
    preview: bytes
    statics: List[PyObjectId]

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        # arbitrary_types_allowed=True,
    )


class PageCollection(BaseModel):
    """
    A container holding a list of `Page`s.

    """
    pages: List[Page]