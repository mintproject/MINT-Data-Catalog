from flask import Blueprint, jsonify, request
from dcat_service.handler import _parse_json, \
    variables_standard_variables_handler, update_variable_handler, get_variable_info_handler
from dcat_service.misc.exception import UnauthorizedException, BadRequestException, InternalServerException
import sys
import traceback

variables_blueprint = Blueprint('variables', __name__, url_prefix='/variables')


@variables_blueprint.route('/test', methods=['GET'])
def test_variables_api():
    return "WE R INSIDE VARIABLES API"


@variables_blueprint.route('/variables_standard_variables', methods=['POST'])
def variables_standard_variables_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = variables_standard_variables_handler(event)
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


@variables_blueprint.route('/update_variable', methods=['POST'])
def update_variable_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = update_variable_handler(event)
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


@variables_blueprint.route('/get_variable_info', methods=['POST'])
def get_variable_info_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = get_variable_info_handler(event)
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