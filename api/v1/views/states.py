#!/usr/bin/python3
"""For State Objects"""
from models import storage
from models.state import State
from api.v1.views import app_views
from flask import jsonify, make_response, abort, request


@app_views.route('/state', methods=['GET'], strict_slashes=False)
def state():
    """get the list of all state object"""
    d_states = storage.all(State)
    return jsonify([obj.to_dict() for obj in d_states.values()])


@app_views.route('/state/<state_id>', methods=['GET'], strict_slashes=False)
def state_spec(staet_id):
    """returns the state with the given state_id"""
    state = storage.get("State", state_id)
    if not state:
        abort(404)

    return jsonify(state.to_dict())


@app_views.route('/state/<state_id>', methods=['DELETE'], strict_slashes=False)
def del_state(state_id):
    """delete state of the given state_id"""
    state = storage.get("State", state_id)
    if not state:
        abort(404)

    state.delete()
    storage.save()
    return make_response(jsonify({}), 200)


@app_views.route('/state', methods=['POST'], strict_slashes=False)
def post_state():
    """creates a neww state"""
    body = request.get_json()
    if not body:
        abort(400, 'Not a JSON')

    if "name" not in body:
        abort(400, "Missing name")

    state = State(**body)
    storage.new(state)
    storage.save()
    return make_response(jsonify(state.to_dict()), 201)


@app_views.route('/state/<state_id>', methods=['PUT'], strict_slashes=False)
def put_state(state_id):
    """update the state with the given state_id"""
    state = storage.get("State", state_id)
    if not state:
        abort(404)

    body = request.get_json()
    if not body:
        abort(400, 'Not a JSON')

    for k, v in body.items():
        if k != 'id' and k != 'created_at' and k != 'updated_at':
            setattr(state, k, v)

    storage.save()
    return make_response(jsonify(state.todict()), 200)
