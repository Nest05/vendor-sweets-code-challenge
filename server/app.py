#!/usr/bin/env python3

from models import db, Sweet, Vendor, VendorSweet
from flask_migrate import Migrate
from flask import Flask, request, make_response, jsonify
from flask_restful import Api, Resource
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Code challenge</h1>'

@app.route('/vendors')
def vendors():
    vendors = [vendor.to_dict() for vendor in Vendor.query.all()]
    return make_response(  vendors,   200  )

@app.route('/vendors/<int:id>')
def vendors_by_id(id):
    vendor = Vendor.query.filter_by(id=id).first()
    if vendor is None:
        # Create a response for a non-existent vendor
        response_body = {
            "error": "Vendor not found"
        }
        response = make_response(response_body, 404)  # Use 404 status code for not found
        return response

    if request.method == 'GET':
        vendor_serialized = vendor.to_dict()

        response = make_response ( 
            vendor_serialized, 
            200  
        )

        return response

@app.route('/sweets')
def sweets():
    sweets = [sweet.to_dict() for sweet in Sweet.query.all()]
    return make_response(  sweets,   200  )

@app.route('/sweets/<int:id>')
def sweets_by_id(id):
    sweet = Sweet.query.filter_by(id=id).first()
    if sweet is None:
        # Create a response for a non-existent sweet
        response_body = {
            "error": "Sweet not found"
        }
        response = make_response(response_body, 404)  # Use 404 status code for not found
        return response

    if request.method == 'GET':
        sweet_serialized = sweet.to_dict()

        response = make_response ( 
            sweet_serialized, 
            200  
        )

        return response

@app.route('/vendor_sweets/<int:id>', methods=['DELETE'])
def delete_vendor_sweet(id):
    vendor_sweet = VendorSweet.query.filter_by(id=id).first()

    if vendor_sweet is None:
        # Create a response for a non-existent VendorSweet
        response_body = {
            "error": "VendorSweet not found"
        }
        response = make_response(response_body, 404)  # Use 404 status code for not found
        return response

    if request.method == 'DELETE':
        db.session.delete(vendor_sweet)
        db.session.commit()
        
        response_body = {}
        response = make_response(
        response_body,
        204
        )
        return response

@app.route('/vendor_sweets', methods=['GET', 'POST'])
def vendor_sweets():
    if request.method == 'GET':
        vendor_sweets = [vendor_sweet.to_dict() for vendor_sweet in VendorSweet.query.all()]
        return make_response(jsonify(vendor_sweets), 200)

    elif request.method == 'POST':
        price = request.json.get("price")
        vendor_id = request.json.get("vendor_id")
        sweet_id = request.json.get("sweet_id")

        if price and vendor_id and sweet_id:
            vendor = Vendor.query.get(vendor_id)
            sweet = Sweet.query.get(sweet_id)

            if vendor and sweet:
                if price > 0:  # Perform validation check for price
                    new_sweet_vendor = VendorSweet(
                        price=price,
                        vendor_id=vendor_id,
                        sweet_id=sweet_id
                    )

                    db.session.add(new_sweet_vendor)
                    db.session.commit()

                    response_data = {
                        'price': price,
                        'vendor_id': vendor_id,
                        'sweet_id': sweet_id,
                        'id': new_sweet_vendor.id,
                        'sweet': {
                            'id': sweet.id,
                            'name': sweet.name
                        },
                        'vendor': {
                            'id': vendor.id,
                            'name': vendor.name
                        }
                    }

                    return make_response(jsonify(response_data), 201)
                else:
                    response_data = {
                        'errors': ['validation errors']
                    }
                    return make_response(jsonify(response_data), 400)
            else:
                response_data = {
                    'errors': ['Vendor not found']
                }
                return make_response(jsonify(response_data), 404)
        else:
            response_data = {
                'errors': ['validation errors']
            }
            return make_response(jsonify(response_data), 400)

if __name__ == '__main__':
    app.run(port=5555, debug=True)
