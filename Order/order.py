#!/usr/bin/env python3
# The above shebang (#!) operator tells Unix-like environments
# to run this file as a python3 script

import os
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

from datetime import datetime
import json

from datetime import datetime

app = Flask(__name__)
# 3308 port used here, please alter to 3306 if necessary 
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root@localhost:3306/order'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

CORS(app)  

class Order(db.Model):
    __tablename__ = 'order'

    order_id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.String(100), nullable=False)
    c_phone_number = db.Column(db.Integer, nullable=False)
    driver_id = db.Column(db.Integer, nullable=True)
    driver_name = db.Column(db.String(100), nullable=True)
    d_phone_number = db.Column(db.Integer, nullable=True)
    date_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    pickup_location = db.Column(db.String(100), nullable=False)
    destination = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(10), nullable=False, default='NEW')
    price = db.Column(db.Float(precision=2), nullable=False)

    def json(self):
        return {
            'order_id': self.order_id,
            'customer_id': self.customer_id,
            'c_phone_number': self.c_phone_number,
            'driver_id': self.driver_id,
            'driver_name': self.driver_name,
            'd_phone_number': self.d_phone_number,
            'date_time': self.date_time,
            'pickup_location': self.pickup_location,
            'destination': self.destination,
            'status': self.status,
            'price': self.price
        }

@app.route("/order")
def get_all():
    orderlist = Order.query.all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders"
        }
    ), 404

@app.route("/order/get_available_orders")
def get_available_orders():
    orderlist=Order.query.filter_by(status="NEW").all()
    if len(orderlist):
        return jsonify(
            {
                "code":200,
                "data":{
                    "customers":[order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code":404,
            "message":"There are no available orders"
        }
    ),404

@app.route("/order/<string:order_id>")
def find_by_order_id(order_id):
    order = Order.query.filter_by(order_id=order_id).first()
    if order:
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        )
    return jsonify(
        {
            "code": 404,
            "data": {
                "order_id": order_id
            },
            "message": "Order not found."
        }
    ), 404

@app.route("/order/customer/<string:customer_id>")
def find_by_customer_id(customer_id):
    orderlist = Order.query.filter_by(customer_id=customer_id).all()
    # orderlist = Order.query.all()
    if len(orderlist):
        return jsonify(
            {
                "code": 200,
                "data": {
                    "orders": [order.json() for order in orderlist]
                }
            }
        )
    return jsonify(
        {
            "code": 404,
            "message": "There are no orders"
        }
    ), 404

# @app.route("/order/delete/<string:order_id>", methods=['GET'])
# def delete_order(order_id): 
#     order = Order.query.filter_by(order_id=order_id).delete()
#     try:
#         db.session.commit()
#         return {
#             "code": 200,
#             "message": "Order id " + order_id + " has been deleted"
#         }
#     except Exception as e:
#         return jsonify(
#             {
#                 "code": 500,
#                 "message": "An error occurred while deleting order id ="+ str(order_id) +" "+ str(e)
#             }
#         ), 500
    

#     print(order)


@app.route("/order", methods=['POST'])
def create_order():
    customer_id = request.json.get('customer_id')
    c_phone_number = request.json.get('c_phone_number')
    pickup_location = request.json.get('pickup_location')
    destination = request.json.get('destination')
    price = request.json.get('price')
    order = Order(customer_id=customer_id, 
    c_phone_number=c_phone_number,
    pickup_location=pickup_location,
    destination=destination,
    price=price)
    
    try:
        db.session.add(order)
        db.session.commit()
    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "message": "An error occurred while creating new order. " + str(e)
            }
        ), 500
    
    print(json.dumps(order.json(), default=str))
    print()

    return jsonify(
        {
            "code": 201,
            "data": order.json()
        }
    ), 201


@app.route("/order/<string:order_id>", methods=['PUT'])
def update_order(order_id):
    try:
        order = Order.query.filter_by(order_id=order_id).first()

        if not order:
            return jsonify(
                {
                    "code": 404,
                    "data": {
                        "order_id": order_id
                    },
                    "message": "Order not found."
                }
            ), 404
        # update status
        data = request.get_json()
        print(data)
        if 'driver_id' in data:
            if data['driver_id']:
                order.driver_id = data['driver_id']
            if data['driver_name']:
                order.driver_name = data['driver_name']
            if data['d_phone_number']:
                order.d_phone_number = data['d_phone_number']
        if data['status']:
            order.status = data['status']
        db.session.commit()
        return jsonify(
            {
                "code": 200,
                "data": order.json()
            }
        ), 200

    except Exception as e:
        return jsonify(
            {
                "code": 500,
                "data": {
                    "order_id": order_id
                },
                "message": "An error occurred while updating the order details. " + str(e)
            }
        ), 500

if __name__ == '__main__':
    print("This is flask for " + os.path.basename(__file__) + ": manage orders ...")
    app.run(host='0.0.0.0', port=5004, debug=True)