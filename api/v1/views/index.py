#!/usr/bin/python3
"""Entry point of views"""
from flask import jsonify
from api.v1.views import app_views
from models import storage


@app_views.route('/status', strick_slashes=False)
def status():
    """Returns the status of the app"""
    return jsonify({"status": "OK"})


@app_views.route('/stats', strick_slashes=False)
def stats():
    """Returns the numberf of each instance type"""
    return jsonify(amenities=storage.count("Amenity"),
                   cities=storage.count("City"),
                   places=storage.count("Place"),
                   reviews=storage.count("Review"),
                   states=storage.count("State"),
                   users=storage.count("User")
                   )
