from flask import Flask 
from pymongo import MongoClient
from .extensions import mongo


def create_app():

	app = Flask(__name__)

	from .views import main 
	app.register_blueprint(main)

	return app