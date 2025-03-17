import datetime
from typing import Optional, List
from typing_extensions import Annotated

from pydantic import ConfigDict, BaseModel, Field, AwareDatetime
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


class PageBody(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    body: str

    model_config = ConfigDict(
        populate_by_name=True,
        json_encoders={ObjectId: str},
    )


class PageVersionStaticless(BaseModel):
    """
    Single version of saved page
    """

    page_body: PyObjectId
    save_time: datetime # TODO: MongoDB hates this??
    title: str
    preview: PyObjectId
    
    model_config = ConfigDict(
        json_encoders={ObjectId: str},
        arbitrary_types_allowed=True,
    )


class PageVersion(PageVersionStaticless):
    statics: List[PyObjectId]


class Page(BaseModel):
    """
    Page versions holder
    """
    url: str
    versions: List[PageVersion]


class Domain(BaseModel):
    """
    URL Domain, holds scrapped pages and their versions
    """

    domain: str
    pages: List[Page]

class SavedStatic(BaseModel):
    url: str
    file: bytes
    media_type: str
    hash: str
    usage_count: int


# response classes

class PageStaticless(Page):
    versions: List[PageVersionStaticless]


class DomainStaticLess(Domain):
    pages: List[PageStaticless]


class DomainRepresentation(BaseModel):
    saved_domains: List[DomainStaticLess]