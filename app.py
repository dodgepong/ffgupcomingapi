import os
import atexit

from flask import Flask, jsonify, json, request
from lxml import html
from pymongo import MongoClient
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import requests

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler())

app = Flask(__name__)

mongo_client = MongoClient(os.environ.get('MONGODB_URI'))

@app.route("/")
def upcoming():
    upcoming_db = mongo_client[os.environ.get('DB_NAME')]
    products_collection = upcoming_db.products

    results = []
    for result in products_collection.find(request.args):
        result.pop('_id')
        results.append(result)

    return jsonify({
        'count': len(results),
        'results': results
    })

def update_upcoming():
    logger.info('Starting upcoming data update process')
    page = requests.get('https://www.fantasyflightgames.com/en/upcoming/')
    tree = html.fromstring(page.content)
    scripts = tree.xpath('//script/text()')

    for script in scripts:
        if 'upcoming_data = [{"' in script:
            lines = script.split(';')
            upcoming_data = json.loads(lines[0].split(' = ')[1])
            logger.info('Found %d items in latest fetch, updating...', len(upcoming_data))

            upcoming_db = mongo_client[os.environ.get('DB_NAME')]
            products_collection = upcoming_db.products

            for product in products_collection.find():
                product_name = product.get('product', None)
                if not product_name:
                    continue
                new_data_for_existing_product = next((x for x in upcoming_data if x.get('product', None) == product_name), None)
                if new_data_for_existing_product:
                    # replace the product in the db with this product
                    logger.debug('Updating item %s in database', product_name)
                    products_collection.replace_one({'product': product_name}, new_data_for_existing_product)
                else:
                    # the product was not in the upcoming list, so remove it from the cache
                    logger.info('Deleting item %s from database', product_name)
                    products_collection.delete_on({'product': product_name})

            # there has to be a better way to do this, after the above
            for new_upcoming_product in upcoming_data:
                existing_product = products_collection.find_one({'product': new_upcoming_product.get('product')})
                if not existing_product:
                    logger.info('Adding new item %s to database', new_upcoming_product.get('product'))
                    products_collection.insert_one(new_upcoming_product)

            logger.info('Finished adding items to the database.')
            return
    logger.warning('Upcoming data not found!')

scheduler = BackgroundScheduler()
scheduler.start()
scheduler.add_job(
    func=update_upcoming,
    trigger=IntervalTrigger(minutes=5),
    id='store_updater',
    name='Update the cache of upcoming products',
    replace_existing=True)

atexit.register(lambda: scheduler.shutdown())

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
