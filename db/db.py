import hashlib
from . import page_collection, static_collection

async def save_page(
    url: str,
    body: str,
    statics: list):
    """
    Save the page to db
    """
    # TODO: save in versioned collection & sort by 'save_time'
    page = {
        "original_url": url,
        "body": body,
        "statics": [static['_id'] for static in statics]
    }
    return page_collection.insert_one(page)


async def save_static(
    url: str,
    static: bytes):
    """
    Save the static to db
    """
    # check if static is already in db by hash
    static_hash = hashlib.sha256(static).hexdigest()
    static = static_collection.find_one({"hash": static_hash})
    if static:
        return static
    else:
        return static_collection.insert_one({
        "original_url": url,
        "static": static,
        "hash": static_hash
    })
    
