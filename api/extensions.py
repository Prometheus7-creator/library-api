from flask_pymongo import MongoClient
from .settings import MONGO_URI

# mongo = PyMongo()
mongo = MongoClient(MONGO_URI)