from app import create_app
from flask_cors import CORS
from flask import Flask, jsonify, request, make_response


app = create_app()

CORS(app, origins=["http://localhost:5173"])

@app.before_request
def handle_preflight():
    if request.method == "OPTIONS":
        response = make_response()
        response.headers.add('Access-Control-Allow-Origin', 'http://localhost:5173')
        response.headers.add('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type, Authorization')
        return response


if __name__ == '_main_':
    app.run(debug=True,host="0.0.0.0", port=5000)