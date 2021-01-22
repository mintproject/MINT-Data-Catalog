from flask import Flask, jsonify, request, render_template
from dcat_service.provenance import provenance_blueprint
from dcat_service.datasets import datasets_blueprint
from dcat_service.variables import variables_blueprint
from dcat_service.knowledge_graph import knowledge_graph_blueprint
from dcat_service.resources import resources_blueprint
from dcat_service.standard_variables import standard_variables_blueprint
from dcat_service.handler import _parse_json, find_datasets_handler
from dcat_service.misc.exception import UnauthorizedException, BadRequestException, InternalServerException
import uuid
import traceback

from flask_cors import CORS
import sys

app = Flask(__name__, template_folder='frontend/public', static_folder='frontend/public', static_url_path='/frontend/public')
app.register_blueprint(provenance_blueprint)
app.register_blueprint(datasets_blueprint)
app.register_blueprint(variables_blueprint)
app.register_blueprint(knowledge_graph_blueprint)
app.register_blueprint(resources_blueprint)
app.register_blueprint(standard_variables_blueprint)
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


@app.route('/find_datasets', methods=['POST'])
def find_datasets():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = find_datasets_handler(event)
        return jsonify(result), 200
    except UnauthorizedException as e:
        return jsonify(error=str(e)), 403
    except BadRequestException as e:
        return jsonify(error=str(e)), 400
    except InternalServerException as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify(error="Internal Error"), 500
    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        return jsonify(error="Internal Error"), 500


if __name__ == "__main__":
    app.run(host='0.0.0.0', port=7000, debug=True)
