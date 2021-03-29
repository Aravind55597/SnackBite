from flask import Flask, request, jsonify
from flask_cors import CORS

import os, sys
from os import environ

import requests
from invokes import invoke_http

#import amqp_setup
import pika
import json

app = Flask(__name__)
CORS(app)

driver_URL = environ.get('driver_URL')  or "http://localhost:5001/driver"
#activity_log_URL = "http://localhost:5003/activity_log"
#error_URL = "http://localhost:5004/error

@app.route("/display_order", methods=['GET'])
def display_orders():
    # 1. Get order info {customer_id, pickup_location, destination}
    order_URL = "http://localhost:5004/order/get_available_orders"
    # Invoke the order microservice
    print('\n-----Invoking order microservice-----')
    order_result = invoke_http(order_URL, method='GET')
    print('order_result:', order_result)

    # 2. Check the order result; if a failure, send it to the error microservice.
    code = order_result["code"]
    if code not in range(200, 300):
        # Inform the error microservice
        #print('\n\n-----Invoking error microservice as pricing fails-----')
        print('\n\n-----Publishing the (order error) message with routing_key=order.error-----')

        # invoke_http(error_URL, method="POST", json=price_result)

        # amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error", 
        #     body=message, properties=pika.BasicProperties(delivery_mode = 2)) 

        # make message persistent within the matching queues until it is received by some receiver 
        # (the matching queues have to exist and be durable and bound to the exchange)

        # - reply from the invocation is not used;
        # continue even if this invocation fails        
        print("\nOrder status ({:d}) published to the RabbitMQ Exchange:".format(
        code), order_result)

        # 7. Return error
        return {
            "code": 500,
            "data": {"order_result": order_result},
            "message": "Retrieval of new orders failure sent for error handling."
        }

    else:
    # 3. Get all drivers using driver microservice
    # Invoke driver microservice
        return {
            "code": 201,
            "data": {
            "order_result": order_result
            }
        }
@app.route("/update_order", methods=['POST'])
def update_order():
    if request.is_json:
        try:
            order_accept = request.get_json()
            print("\nOrder accepted, received order id and driver details in JSON:", order_accept)
            # do the actual work# 
            # 1. Update the order details using order microservice
            # Invoke the order microservice
            order_URL = f"http://localhost:5004/order/{order_accept['order_id']}"
            result = invoke_http(order_URL, method='PUT', json=order_accept)
            
            # 2. Check the order update result; if a failure, send it to the error microservice.
            code = result["code"]
            if code not in range(200, 300): 
                # Inform the error microservice
                #print('\n\n-----Invoking error microservice as pricing fails-----')
                print('\n\n-----Publishing the (order update error) message with routing_key=order.error-----')

                # invoke_http(error_URL, method="POST", json=price_result)

                # amqp_setup.channel.basic_publish(exchange=amqp_setup.exchangename, routing_key="order.error", 
                #     body=message, properties=pika.BasicProperties(delivery_mode = 2)) 

                # make message persistent within the matching queues until it is received by some receiver 
                # (the matching queues have to exist and be durable and bound to the exchange)

                # - reply from the invocation is not used;
                # continue even if this invocation fails        
                print("\nOrder update status ({:d}) published to the RabbitMQ Exchange:".format(
                code), result)

                # Return error
                return {
                    "code": 500,
                    "data": {"result": result},
                    "message": "Update of accept order failure sent for error handling."
                }           
            else:
                # 3. Update the Driver UI 
                delivery_URL = "http://localhost:5200/display_order" 
                order_result = invoke_http(delivery_URL, method='GET')
                return {
                    "code": 201,
                    "data": {
                    "order_result": order_result
                    }
                }
        except Exception as e:
            # Unexpected error in code
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + " at " + str(exc_type) + ": " + fname + ": line " + str(exc_tb.tb_lineno)
            print(ex_str)

            return jsonify({
                "code": 500,
                "message": "order_management.py internal error: " + ex_str
            }), 500

        # if reached here, not a JSON request.
        return jsonify({
            "code": 400,
            "message": "Invalid JSON input: " + str(request.get_data())
        }), 400


    # Execute this program if it is run as a main script (not by 'import')
if __name__ == "__main__":
    print("This is flask " + os.path.basename(__file__) + " for delivery management...")
    app.run(host="0.0.0.0", port=5200, debug=True)
    # Notes for the parameters: 
    # - debug=True will reload the program automatically if a change is detected;
    #   -- it in fact starts two instances of the same flask program, and uses one of the instances to monitor the program changes;
    # - host="0.0.0.0" allows the flask program to accept requests sent from any IP/host (in addition to localhost),
    #   -- i.e., it gives permissions to hosts with any IP to access the flask program,
    #   -- as long as the hosts can already reach the machine running the flask program along the network;
    #              