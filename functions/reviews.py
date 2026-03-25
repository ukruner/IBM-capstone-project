from cloudant.client import Cloudant
from cloudant.query import Query
from flask import Flask, jsonify, request, abort
from ibm_cloud_sdk_core import ApiException
import requests
import time
import atexit

#Add your Cloudant service credentials here
cloudant_username = "7aa5ee38-cc9d-4038-8268-a931081002b2-bluemix"
cloudant_api_key = "FA83yCzfYzrd0XRoNkHYpyqoX_L_jEIFjYoQmbUX97Dk"
cloudant_url = "https://7aa5ee38-cc9d-4038-8268-a931081002b2-bluemix.cloudantnosqldb.appdomain.cloud"
client = Cloudant.iam(cloudant_username, cloudant_api_key, connect=True, url=cloudant_url)

session = client.session()
print('Databases:', client.all_dbs())

db = client['reviews']

app = Flask(__name__)

@app.route('/api/review', methods=['GET'])
def get_reviews():
    dealership_id = request.args.get('id')

    # Check if "id" parameter is missing
    if dealership_id is None:
        return jsonify({"error": "Missing 'id' parameter in the URL"}), 400

    # Convert the "id" parameter to an integer (assuming "id" should be an integer)
    try:
        dealership_id = int(dealership_id)
    except ValueError:
        return jsonify({"error": "'id' parameter must be an integer"}), 400

    # Define the query based on the 'dealership' ID
    selector = {
        "dealership": dealership_id
    }

    # Execute the query using the query method
    result = db.get_query_result(selector)
        # Create a list to store the documents
    data_list = []
        # Iterate through the results and add documents to the list
    for doc in result:
        data_list.append(doc)
        # Return the data as JSON
    if (data_list):
        return jsonify(data_list)
    else:
        return None
    # else:
    #     return jsonify({"error": "Dealer ID does not exist"}), 404
            

    
@app.route('/api/review', methods=['POST'])
def post_review():
    if not request.json:
        abort(400, description='Invalid JSON data')
    
    # Your further processing logic here
    review_data=request.json

    # Validate that the required fields are present in the review data
    required_fields = ['dealership', 'review', 'purchase', 'purchase_date']
    for field in required_fields:
        if field not in review_data:
            abort(400, description=f'Missing required field: {field}')
    
    db.create_document(review_data)
    return jsonify({"message": "Review posted successfully"}), 201
   
@app.errorhandler(500)
def internal_server_error(error):
    return jsonify({"error": "Something went wrong on the server"}), 500    

if __name__ == '__main__':
    app.run(debug=True)