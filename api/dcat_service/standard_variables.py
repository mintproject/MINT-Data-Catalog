from flask import Blueprint, jsonify, request
from dcat_service.handler import _parse_json, \
    update_standard_variable_handler, get_standard_variable_info_handler
from dcat_service.misc.exception import UnauthorizedException, BadRequestException, InternalServerException
import sys
import traceback

standard_variables_blueprint = Blueprint(
    'standard_variables', __name__, url_prefix='/standard_variables')


@standard_variables_blueprint.route('/test', methods=['GET'])
def test_standard_variables_api():
    return "WE R INSIDE standard_variables API"


@standard_variables_blueprint.route('/update_standard_variable', methods=['POST'])
def update_standard_variable_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = update_standard_variable_handler(event)
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


@standard_variables_blueprint.route('/get_standard_variable_info', methods=['POST'])
def get_standard_variable_info_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = get_standard_variable_info_handler(event)
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
