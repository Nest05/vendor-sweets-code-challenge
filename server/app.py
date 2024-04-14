#!/usr/bin/env python3

from models import db, Sweet, Vendor, VendorSweet
from flask_migrate import Migrate
from flask import Flask, request, make_response
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
            "error": "Vendor not found."
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
            "error": "Sweet not found."
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
            "error": "VendorSweet not found."
        }
        response = make_response(response_body, 404)  # Use 404 status code for not found
        return response

    if request.method == 'DELETE':
        db.session.delete(vendor_sweet)
        db.session.commit()
        
        response_body = {}
        response = make_response(
        response_body,
        200
        )
        return response

@app.route('/vendor_sweets', methods=['GET', 'POST'])
def vendor_sweets():
    if request.method == 'GET':
        vendor_sweets = [vendor_sweets.to_dict() for vendor_sweets in VendorSweet.query.all()]
        return make_response( vendor_sweets, 200 )
    
    elif request.method == 'POST':
        price=request.form.get("price")
        vendor_id=request.form.get("vendor_id")
        sweet_id=request.form.get("sweet_id")

       
        if vendor_id and sweet_id:
            new_sweet_vendor = VendorSweet(
                price=price,
                vendor_id=vendor_id,
                sweet_id=sweet_id
            )

            db.session.add(new_sweet_vendor)
            db.session.commit()


            vendor = Vendor.query.get(vendor_id)  # Fetch the vendor details based on vendor_id
            sweet = Sweet.query.get(sweet_id)
            # Check if vendor exists and prepare the response data
            next_id = len(VendorSweet.query.all())

            if vendor and sweet:
                response_data = {
                    'id': next_id,
                    'price': price,
                    'sweet': {
                        'id': sweet.id,
                        'name': sweet.name
                    },
                    'sweet_id': sweet_id,
                    'vendor': {
                        'id': vendor.id,
                        'name': vendor.name
                    },
                    'vendor_id': vendor_id
                }
                return make_response(response_data, 201)
            else:
                response_data = {
                    'errors': ['Vendor not found']
                }
                return make_response(response_data, 404)
        else:
            response_data = {
                'errors': ['Validation errors']
            }
        
            return make_response(response_data, 400)


if __name__ == '__main__':
    app.run(port=5555, debug=True)
