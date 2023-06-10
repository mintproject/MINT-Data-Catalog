from flask import Blueprint, jsonify, request
from dcat_service.handler import _parse_json, \
    find_standard_variables_handler, register_standard_variables_handler
from dcat_service.misc.exception import UnauthorizedException, BadRequestException, InternalServerException
import sys
import traceback

knowledge_graph_blueprint = Blueprint(
    'knowledge_graph', __name__, url_prefix='/knowledge_graph')


@knowledge_graph_blueprint.route('/test', methods=['GET'])
def test_knowledge_graph_api():
    return "WE R INSIDE knowledge_graph API"


@knowledge_graph_blueprint.route('/register_standard_variables', methods=['POST'])
def register_standard_variables_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = register_standard_variables_handler(event)
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


@knowledge_graph_blueprint.route('/find_standard_variables', methods=['POST'])
def find_standard_variables_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = find_standard_variables_handler(event)
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
