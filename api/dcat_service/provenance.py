from flask import Blueprint, jsonify, request
from dcat_service.handler import _parse_json, register_provenance_handler
from dcat_service.misc.exception import UnauthorizedException, BadRequestException, InternalServerException
import sys
import traceback

provenance_blueprint = Blueprint(
    'provenance', __name__, url_prefix='/provenance')


# NOTE: need error handler
# need parser


@provenance_blueprint.route('/test_provenance', methods=['GET'])
def test_provenance_api():
    return "WE R INSIDE PROVENANCE API"


@provenance_blueprint.route('/register_provenance', methods=['POST'])
def register_provenance_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = register_provenance_handler(event)
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
