#!/usr/bin/python3
"""
route for handling Place objects and operations
"""
from flask import jsonify, abort, request
from api.v1.views import app_views, storage
from models.place import Place


@app_views.route("/cities/<city_id>/places", methods=["GET"],
                 strict_slashes=False)
def places_by_city(city_id):
    """
    retrieves all Place objects by city
    :return: json of all Places
    """
    place_list = []
    city_obj = storage.get("City", str(city_id))
    for obj in city_obj.places:
        place_list.append(obj.to_dict())

    return jsonify(place_list)


@app_views.route("/cities/<city_id>/places", methods=["POST"],
                 strict_slashes=False)
def place_create(city_id):
    """
    create place route
    :return: newly created Place obj
    """
    place_json = request.get_json(silent=True)
    if place_json is None:
        abort(400, 'Not a JSON')
    if not storage.get("User", place_json["user_id"]):
        abort(404)
    if not storage.get("City", city_id):
        abort(404)
    if "user_id" not in place_json:
        abort(400, 'Missing user_id')
    if "name" not in place_json:
        abort(400, 'Missing name')

    place_json["city_id"] = city_id

    new_place = Place(**place_json)
    new_place.save()
    resp = jsonify(new_place.to_dict())
    resp.status_code = 201

    return resp


@app_views.route("/places/<place_id>",  methods=["GET"],
                 strict_slashes=False)
def place_by_id(place_id):
    """
    gets a specific Place object by ID
    :param place_id: place object id
    :return: place obj with the specified id or error
    """

    fetched_obj = storage.get("Place", str(place_id))

    if fetched_obj is None:
        abort(404)

    return jsonify(fetched_obj.to_dict())


@app_views.route("/places/<place_id>",  methods=["PUT"],
                 strict_slashes=False)
def place_put(place_id):
    """
    updates specific Place object by ID
    :param place_id: Place object ID
    :return: Place object and 200 on success, or 400 or 404 on failure
    """
    place_json = request.get_json(silent=True)

    if place_json is None:
        abort(400, 'Not a JSON')

    fetched_obj = storage.get("Place", str(place_id))

    if fetched_obj is None:
        abort(404)

    for key, val in place_json.items():
        if key not in ["id", "created_at", "updated_at", "user_id", "city_id"]:
            setattr(fetched_obj, key, val)

    fetched_obj.save()

    return jsonify(fetched_obj.to_dict())


@app_views.route("/places/<place_id>",  methods=["DELETE"],
                 strict_slashes=False)
def place_delete_by_id(place_id):
    """
    deletes Place by id
    :param place_id: Place object id
    :return: empty dict with 200 or 404 if not found
    """

    fetched_obj = storage.get("Place", str(place_id))

    if fetched_obj is None:
        abort(404)

    storage.delete(fetched_obj)
    storage.save()

    return jsonify({})


def places_search():
    """
    Retrieves all Place objects depending of
    the JSON in the body of the request
    """
    body_r = request.get_json()
    if body_r is None:
        abort(400, "Not a JSON")

    if not body_r or (
            not body_r.get('states') and
            not body_r.get('cities') and
            not body_r.get('amenities')
    ):
        places = storage.all(Place)
        return jsonify([place.to_dict() for place in places.values()])

    places = []

    if body_r.get('states'):
        states = [storage.get("State", id) for id in body_r.get('states')]

        for state in states:
            for city in state.cities:
                for place in city.places:
                    places.append(place)

    if body_r.get('cities'):
        cities = [storage.get("City", id) for id in body_r.get('cities')]

        for city in cities:
            for place in city.places:
                if place not in places:
                    places.append(place)

    if not places:
        places = storage.all(Place)
        places = [place for place in places.values()]

    if body_r.get('amenities'):
        ams = [storage.get("Amenity", id) for id in body_r.get('amenities')]
        i = 0
        limit = len(places)
        HBNB_API_HOST = getenv('HBNB_API_HOST')
        HBNB_API_PORT = getenv('HBNB_API_PORT')

        port = 5000 if not HBNB_API_PORT else HBNB_API_PORT
        first_url = "http://0.0.0.0:{}/api/v1/places/".format(port)
        while i < limit:
            place = places[i]
            url = first_url + '{}/amenities'
            req = url.format(place.id)
            response = requests.get(req)
            am_d = json.loads(response.text)
            amenities = [storage.get("Amenity", o['id']) for o in am_d]
            for amenity in ams:
                if amenity not in amenities:
                    places.pop(i)
                    i -= 1
                    limit -= 1
                    break
            i += 1
    return jsonify([place.to_dict() for place in places])
