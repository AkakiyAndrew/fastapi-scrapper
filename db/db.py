import hashlib
import datetime
from bson import ObjectId
from . import domain_collection, static_collection, pages_collection
from models import PageVersion, Domain, Page, SavedStatic, PageBody


async def save_page(
    url: str,
    body: str,
    page_screenshot: bytes,
    title: str,
    statics: list):
    """
    Save the page to db
    """

    # add new page version to db
    new_page = PageBody(
        body=body,
    )

    # save preview as simple static, obtaiable by its id
    # dummy url
    new_preview_static = save_static("/statics/preview/", page_screenshot, "image/png") 

    new_page = pages_collection.insert_one(new_page.model_dump(exclude=["id"])) # TODO: await?
    preview_static_id = await new_preview_static
    new_page_id = (await new_page).inserted_id
    statics.append(preview_static_id)
    # TODO: Convert ObjectId to string?
    new_page_version = PageVersion(
        url=url,
        page_body= new_page_id,
        save_time=datetime.datetime.now(tz=datetime.UTC),
        title=title,
        preview=preview_static_id,
        statics=[static for static in statics],
    )

    domain = url.split('/')[2]
    page_url = url.split(domain)[1]
    
    # TODO: use mongodb operator 'setOnInsert' to update in single query and remove 'else' block?
    domain_existed = await domain_collection.find_one({"domain": domain})
    if domain_existed:
        page_existed = False
        for page in domain_existed["pages"]:
            if page["url"] == page_url:
                page_existed = True
                await domain_collection.update_one(
                    {"domain": domain, "pages.url": page_url},
                    {"$push": {"pages.$.versions": new_page_version.model_dump(exclude_none=True)}},
                )
                break
        if not page_existed:
            await domain_collection.update_one(
                {"domain": domain},
                {"$push": {"pages": Page(url=page_url, versions=[new_page_version]).model_dump(exclude_none=True)}},
            )
    else:
        await domain_collection.insert_one(
            Domain(domain=domain, pages=[Page(url=page_url, versions=[new_page_version])]).model_dump(exclude_none=True)
        )

    return new_page_id


async def save_static(
    url: str,
    static_raw: bytes,
    media_type: str):
    """
    Save the static to db
    """
    # check if static is already in db by hash
    static_hash = hashlib.sha256(static_raw).hexdigest()
    static_existed = await static_collection.find_one({"hash": static_hash})

    if static_existed:
        # if static already exist - just increment 'usage_count' and return its id
        static_collection.update_one({"_id": static_existed["_id"]}, {"$inc": {"usage_count": 1}})
        return static_existed["_id"]
    else:
        new_static = await static_collection.insert_one(
            SavedStatic(
                url=url,
                file=static_raw,
                media_type=media_type,
                hash=static_hash,
                usage_count=1,
            ).model_dump()
        )
        return new_static.inserted_id 
