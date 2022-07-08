import os
import urllib

password = urllib.parse.quote_plus('Quit@777')

MONGO_URI = 'mongodb+srv://ansh:{}@cluster0.klout.mongodb.net/?retryWrites=true&w=majority'.format(password)