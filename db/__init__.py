import motor.motor_asyncio
from pymongo import ReturnDocument
import os

client = motor.motor_asyncio.AsyncIOMotorClient(os.environ["MONGODB_URL"])
db = client.page_vault
page_collection = db.get_collection("pages")
static_collection = db.get_collection("statics")