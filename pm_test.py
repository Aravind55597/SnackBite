# Test pm composite microservice 
from invokes import invoke_http

# Run Order, customer, payment and payment management on flask first

# json = {"order_id":2, "pickup_location": "Jurong East", "destination": "Pasir Ris Singapore", "customer_id": 1}
json = {"order_id": 3, "status":"completed"}
results = invoke_http("http://localhost:5300/order_completed", method='PUT', json=json)


print( type(results) )
print()
print( results )