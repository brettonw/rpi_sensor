#! /usr/bin/env python3

# to test:
# curl -H "Content-Type: application/json" -X POST -d '{"name": "John", "age": 30}' http://localhost:8081/

from flask import Flask, request, jsonify
import json

app = Flask(__name__)

@app.route('/', methods=["POST"])
def process_request():
    req_data = request.get_json()
    # do some processing with the request data

    #with open("/usvc/files/test.json", "r") as file:
    #    data = json.load(file)
    data = {'message': 'success'}

    return jsonify(data)

if __name__ == "__main__":
    app.run(host="0.0.0.0")
