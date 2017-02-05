# API for FFG Upcoming Products

This is a simple API to give easier insight into the content of the [FFG Upcoming Products](https://www.fantasyflightgames.com/en/upcoming/) page.

## How to use

This API is currently live on a free Heroku dyno at this location: `https://ffgupcomingapi.herokuapp.com/`

With no filtering, this endpoint will return a list of all items on the upcoming list.

A typical result entry looks like this:

    {
      "category": "Living Card Games®",
      "collection": "The Dunwich Legacy",
      "collection_crumbs": "Arkham Horror: The Card Game - The Dunwich Legacy",
      "css_class": "shipping",
      "expected_by": 1487203200000,
      "expected_by_override": "",
      "is_reprint": false,
      "last_updated": 1486166400000,
      "name": "Shipping Now",
      "order_index": 30,
      "price": 14.95,
      "product": "The Miskatonic Museum",
      "product_image_url": "https://images-cdn.fantasyflightgames.com/filer_public/79/c1/79c12dcc-4f75-4b8d-9059-91456a1436ad/ahc03_main.png",
      "product_url": "/en/products/arkham-horror-the-card-game/products/miskatonic-museum",
      "root_collection": "Arkham Horror: The Card Game",
      "status_image_url": "https://images-cdn.fantasyflightgames.com/filer_public/11/98/1198b4c7-c06b-4217-828b-21bf4ff7256b/status_shipping_sm.png"
    }

You can filter on any of the fields by adding `field=value` to the URL query. For example, to find all upcoming products for Android: Netrunner, the URL will look like this: `https://ffgupcomingapi.herokuapp.com/?root_collection=Android:%20Netrunner%20The%20Card%20Game`

The `expected_by` and `last_updated` fields are in milliseconds since the Unix Epoch. Just divide by 1000 for standard Unix timestamps.

Queries against this API actually hit a cache that is updated every minute, rather than querying directly against the FFG-hosted page and scraping on every request.