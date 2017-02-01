from flask import Flask, jsonify, json, request
from lxml import html
import requests

app = Flask(__name__)

@app.route("/")
def upcoming():
    collection = request.args.get('collection', None)
    page = requests.get('https://www.fantasyflightgames.com/en/upcoming/')
    tree = html.fromstring(page.content)
    scripts = tree.xpath('//script/text()')

    for script in scripts:
        if 'upcoming_data = [{' in script:
            lines = script.split(';')
            upcoming = json.loads(lines[0].split(' = ')[1])
            if collection:
                collection_upcoming = []
                for entry in upcoming:
                    if entry['root_collection'] == collection:
                        collection_upcoming.append(entry)
                upcoming = collection_upcoming
            return jsonify({
                'upcoming': upcoming
            })
        continue
    return "There was an error retreiving the data."

if __name__ == "__main__":
    app.run(port=80)
