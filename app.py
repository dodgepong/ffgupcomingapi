import os
import atexit

from flask import Flask, jsonify, json, request
from lxml import html
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import requests

app = Flask(__name__)

mongo_client = MongoClient(os.environ.get('MONGODB_URI'))

@app.route("/")
def upcoming():
    upcoming_db = mongo_client.upcoming
    products_collection = upcoming_db.products

    to_return = []
    for result in products_collection.find(request.args):
        to_return.append(result)

    return jsonify(to_return)

def update_upcoming():
    page = requests.get('https://www.fantasyflightgames.com/en/upcoming/')
    tree = html.fromstring(page.content)
    scripts = tree.xpath('//script/text()')

    for script in scripts:
        if 'upcoming_data = [{' in script:
            lines = script.split(';')
            upcoming = json.loads(lines[0].split(' = ')[1])

            upcoming_db = mongo_client.upcoming
            products_collection = upcoming_db.products

            # wipe the table and completely replace it
            products_collection.delete_many({})
            products_collection.drop_indexes()
            products_collection.create_index('root_collection')
            products_collection.create_index('collection')
            products_collection.create_index('name')
            products_collection.create_index('product')
            products_collection.insert_many(upcoming)

            break

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=update_upcoming,
    trigger=IntervalTrigger(minutes=1),
    id='store_updater',
    name='Update the cache of upcoming products',
    replace_existing=True)

atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True)
