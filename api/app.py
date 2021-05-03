from flask import Flask, jsonify, request, render_template
from dcat_service.provenance import provenance_blueprint
from dcat_service.datasets import datasets_blueprint
from dcat_service.variables import variables_blueprint
from dcat_service.knowledge_graph import knowledge_graph_blueprint
from dcat_service.resources import resources_blueprint
from dcat_service.standard_variables import standard_variables_blueprint
from dcat_service.handler import request_handler, _parse_json, find_datasets_handler
from dcat_service.misc.exception import UnauthorizedException, BadRequestException, InternalServerException
import uuid
import traceback

from flask_cors import CORS
import sys

app = Flask(__name__, template_folder='frontend/public', static_folder='frontend/public', static_url_path='/frontend/public')
CORS(app)


@app.route("/api_doc.json")
def documentation():
    return app.send_static_file('api_doc.json')


@app.route("/mint_logo.png")
def render_logo():
    return app.send_static_file('mint_logo.png')


@app.route("/", defaults={'path': ''})
@app.route("/<path:path>", methods=["GET"])
def catch_all(path):
    return render_template('index.html')


@app.route('/get_session_token', methods=['GET'])
def get_session_token():
    session_key = f"mint-data-catalog:{uuid.uuid4()}:{uuid.uuid4()}"
    return jsonify({"X-Api-Key": str(session_key)}), 200


@app.route('/<path:api_endpoint>', methods=['POST'])
def handle_api_request(api_endpoint):
    event = {
        'httpMethod': 'POST',
        'path': '/' + api_endpoint,
        'body': request.get_json()
    }
    #return event
    result = request_handler(event, context=None)
    return result['body'], result['statusCode'], result['headers']
    #return request_handler(event, context=None)
    #return request_handler(event, None)


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7000, debug=True)