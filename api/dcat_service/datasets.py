from flask import Blueprint, jsonify, request
from dcat_service.handler import _parse_json, \
    register_datasets_handler, register_variables_handler, register_resources_handler, \
    dataset_standard_variables_handler, dataset_variables_handler, dataset_resources_handler, \
    jataware_search_handler, search_handler, search_v2_handler, \
    update_dataset_viz_status_handler, update_dataset_viz_config_handler, \
    update_dataset_handler, get_dataset_info_handler, get_dataset_temporal_coverage_handler, \
    delete_dataset_handler
from dcat_service.misc.exception import UnauthorizedException, BadRequestException, InternalServerException
import sys
import traceback

datasets_blueprint = Blueprint('datasets', __name__, url_prefix='/datasets')


@datasets_blueprint.route('/test', methods=['GET'])
def test_datasets_api():
    return "WE R INSIDE datasets API"


@datasets_blueprint.route('/register_datasets', methods=['POST'])
def register_datasets_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = register_datasets_handler(event)
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


@datasets_blueprint.route('/register_variables', methods=['POST'])
def register_variables_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = register_variables_handler(event)
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


@datasets_blueprint.route('/register_resources', methods=['POST'])
def register_resources_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = register_resources_handler(event)
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


@datasets_blueprint.route('/dataset_standard_variables', methods=['POST'])
def dataset_standard_variables_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = dataset_standard_variables_handler(event)
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


@datasets_blueprint.route('/dataset_variables', methods=['POST'])
def dataset_variables_api():
    event = request.get_json()
    if 'body' in event:
        event['body'] = _parse_json(event.get('body', ''))
    else:
        event = {
            "body": event
        }
    try:
        result = dataset_variables_handler(event)
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


@datasets_blueprint.route('/dataset_resources', methods=['POST'])
def dataset_resources_api():
    event = request.get_json()
    if 'body' in event:
        event['body'] = _parse_json(event.get('body', ''))
    else:
        event = {
            "body": event
        }
    try:
        result = dataset_resources_handler(event)
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


@datasets_blueprint.route('/jataware_search', methods=['POST'])
def jataware_search_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = jataware_search_handler(event)
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


@datasets_blueprint.route('/search', methods=['POST'])
def search_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = search_handler(event)
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


@datasets_blueprint.route('/search_v2', methods=['POST'])
def search_v2_api():
    event = request.get_json()
    if 'body' in event:
        event['body'] = _parse_json(event.get('body', ''))
    else:
        event = {
            "body": event
        }
    try:
        result = search_v2_handler(event)
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


@datasets_blueprint.route('/update_dataset_viz_status', methods=['POST'])
def update_dataset_viz_status_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = update_dataset_viz_status_handler(event)
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


@datasets_blueprint.route('/update_dataset_viz_config', methods=['POST'])
def update_dataset_viz_config_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = update_dataset_viz_config_handler(event)
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


@datasets_blueprint.route('/update_dataset', methods=['POST'])
def update_dataset_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = update_dataset_handler(event)
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


@datasets_blueprint.route('/get_dataset_info', methods=['POST'])
def get_dataset_info_api():
    event = request.get_json()
    if 'body' in event:
        event['body'] = _parse_json(event.get('body', ''))
    else:
        event = {
            "body": event
        }
    try:
        result = get_dataset_info_handler(event)
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


@datasets_blueprint.route('/get_dataset_temporal_coverage', methods=['POST'])
def get_dataset_temporal_coverage_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = get_dataset_temporal_coverage_handler(event)
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


@datasets_blueprint.route('/delete_dataset', methods=['POST'])
def delete_dataset_api():
    event = request.get_json()
    event['body'] = _parse_json(event.get('body', ''))
    try:
        result = delete_dataset_handler(event)
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


