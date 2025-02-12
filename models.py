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

class Page(BaseModel):
    """
    Single saved page (without statics)
    """

    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    url: str = Field(...)
    save_time: Optional[NaiveDatetime] = None
    body: Optional[str] = None
    statics: Optional[list] = None

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
        # arbitrary_types_allowed=True,
        json_schema_extra={
            "example": {
                "url": "https://example.com/home",
                "save_time": "2032-04-23T10:20:30.400",
                "body": "<!DOCTYPE html><html><head></head><body>Hello, World!</body></html>",
                "statics": [],
            }
        },
    )


class PageCollection(BaseModel):
    """
    A container holding a list of `Page` ID's, without content.

    """
    
    pages: List[Page]