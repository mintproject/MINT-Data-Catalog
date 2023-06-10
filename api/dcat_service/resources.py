from flask import Blueprint, jsonify, request
from dcat_service.handler import _parse_json, \
    update_resource_handler, get_resource_info_handler, delete_resource_handler, cache_resources_handler
from dcat_service.misc.exception import UnauthorizedException, BadRequestException, InternalServerException
import sys
import traceback

resources_blueprint = Blueprint('resources', __name__, url_prefix='/resources')


@resources_blueprint.route('/test', methods=['GET'])
def test_resources_api():
    return "WE R INSIDE resources API"


@resources_blueprint.route('/update_resource', methods=['POST'])
def update_resource_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = update_resource_handler(event)
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


@resources_blueprint.route('/get_resource_info', methods=['POST'])
def get_resource_info_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = get_resource_info_handler(event)
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


@resources_blueprint.route('/delete_resource', methods=['POST'])
def delete_resource_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = delete_resource_handler(event)
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


@resources_blueprint.route('/cache_resources', methods=['POST'])
def cache_resources_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = cache_resources_handler(event)
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
