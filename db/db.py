import hashlib
from . import page_collection, static_collection

async def save_page(
    url: str,
    body: str,
    title: str,
    statics: list):
    """
    Save the page to db
    """
    # TODO: save in versioned collection & sort by 'save_time'
    page = {
        "url": url,
        "title": title,
        "body": body,
        "statics": [static for static in statics]
    }
    new_page = await page_collection.insert_one(page)
    return new_page.inserted_id


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
        static_existed["usage_count"] += 1
        static_collection.update_one({"_id": static_existed["_id"]}, {"$set": {"usage_count": static_existed["usage_count"]}})
        return static_existed["_id"]
    else:
        new_static = await static_collection.insert_one({
            "url": url,
            "file": static_raw,
            "media_type": media_type,
            "hash": static_hash,
            "usage_count": 1
        })
        return new_static.inserted_id 
    
