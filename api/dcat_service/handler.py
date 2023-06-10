import functools
import pprint
import sys
import traceback
import uuid

import ujson
from dcat_service.controllers.delete_controller import delete_resource, delete_dataset
from dcat_service.controllers.query_controllers import find_datasets_old, find_datasets, \
    find_standard_variables, dataset_standard_variables, dataset_variables, variables_standard_variables, \
    dataset_resources, get_dataset_info, get_resource_info, get_variable_info, get_standard_variable_info, \
    search_datasets, dataset_temporal_coverage
from dcat_service.controllers.query_controllers_v2 import search_datasets_v2
from dcat_service.controllers.registration_controllers import register_provenance, register_datasets, \
    register_standard_variables, register_variables, register_resources
from dcat_service.controllers.update_controllers import update_dataset_viz_status, update_dataset_viz_config, \
    update_dataset, update_resource, update_variable, update_standard_variable, sync_datasets_metadata, sync_dataset_metadata
from dcat_service.misc.exception import UnauthorizedException, BadRequestException, InternalServerException


# For search query


def authenticate(func):
    @functools.wraps(func)
    def wrapper(event, **kwargs):
        if not _is_api_key_valid(event.get('headers', {}).get('X-Api-Key')):
            raise UnauthorizedException("Invalid X-Api-Key")

        print(f"Wrapper: {event}")
        return func(event, **kwargs)

    return wrapper


GET_SESSION_TOKEN_PATH = '/get_session_token'
REGISTER_PROVENANCE_PATH = '/provenance/register_provenance'
REGISTER_STANDARD_VARIABLES_PATH = '/knowledge_graph/register_standard_variables'
REGISTER_DATASETS_PATH = '/datasets/register_datasets'
REGISTER_VARIABLES_PATH = '/datasets/register_variables'
REGISTER_RESOURCES_PATH = '/datasets/register_resources'
FIND_DATASETS_PATH = '/find_datasets'
DATASETS_FIND_PATH_OLD = '/datasets/find'
FIND_STANDARD_VARIABLES_PATH = '/knowledge_graph/find_standard_variables'
DATASET_STANDARD_VARIABLES_PATH = '/datasets/dataset_standard_variables'
DATASET_VARIABLES_PATH = '/datasets/dataset_variables'
DATASET_RESOURCES_PATH = '/datasets/dataset_resources'
VARIABLES_STANDARD_VARIABLES_PATH = '/variables/variables_standard_variables'
JATAWARE_SEARCH_PATH = '/datasets/jataware_search'
SEARCH_PATH = '/datasets/search'
SEARCH_PATH_V2 = '/datasets/search_v2'

UPDATE_DATASET_VIZ_STATUS_PATH = '/datasets/update_dataset_viz_status'
UPDATE_DATASET_VIZ_CONFIG_PATH = '/datasets/update_dataset_viz_config'
UPDATE_DATASET_PATH = "/datasets/update_dataset"
UPDATE_RESOURCE_PATH = "/resources/update_resource"
UPDATE_VARIABLE_PATH = "/variables/update_variable"
UPDATE_STANDARD_VARIABLE_PATH = "/standard_variables/update_standard_variable"
SYNC_DATASETS_METADATA_PATH = "/datasets/sync_datasets_metadata"
SYNC_DATASET_METADATA_PATH = "/datasets/sync_dataset_metadata"
GET_DATASET_INFO_PATH = '/datasets/get_dataset_info'
GET_RESOURCE_INFO_PATH = '/resources/get_resource_info'
GET_VARIABLE_INFO_PATH = '/variables/get_variable_info'
GET_STANDARD_VARIABLE_INFO_PATH = '/standard_variables/get_standard_variable_info'
GET_DATASET_TEMPORAL_COVERAGE_PATH = '/datasets/get_dataset_temporal_coverage'

DELETE_RESOURCE_PATH = '/resources/delete_resource'
DELETE_DATASET_PATH = '/datasets/delete_dataset'

CACHE_RESOURCES_PATH = '/resources/cache_resources'

PATHS = frozenset([
    GET_SESSION_TOKEN_PATH,
    REGISTER_PROVENANCE_PATH,
    REGISTER_STANDARD_VARIABLES_PATH,
    REGISTER_DATASETS_PATH,
    REGISTER_VARIABLES_PATH,
    REGISTER_RESOURCES_PATH,
    FIND_DATASETS_PATH,
    DATASETS_FIND_PATH_OLD,
    FIND_STANDARD_VARIABLES_PATH,
    DATASET_STANDARD_VARIABLES_PATH,
    DATASET_VARIABLES_PATH,
    DATASET_RESOURCES_PATH,
    VARIABLES_STANDARD_VARIABLES_PATH,
    JATAWARE_SEARCH_PATH,
    SEARCH_PATH,
    SEARCH_PATH_V2,
    UPDATE_DATASET_VIZ_STATUS_PATH,
    UPDATE_DATASET_VIZ_CONFIG_PATH,
    UPDATE_DATASET_PATH,
    UPDATE_DATASET_PATH,
    UPDATE_RESOURCE_PATH,
    UPDATE_VARIABLE_PATH,
    UPDATE_STANDARD_VARIABLE_PATH,
    SYNC_DATASETS_METADATA_PATH,
    SYNC_DATASET_METADATA_PATH,
    GET_DATASET_INFO_PATH,
    GET_RESOURCE_INFO_PATH,
    GET_VARIABLE_INFO_PATH,
    GET_STANDARD_VARIABLE_INFO_PATH,
    GET_DATASET_TEMPORAL_COVERAGE_PATH,
    DELETE_RESOURCE_PATH,
    DELETE_DATASET_PATH,
    CACHE_RESOURCES_PATH
])


def request_handler(event, context):
    path = event.get('path')
    http_method = event.get('httpMethod')

    print(path)
    if path not in PATHS:
        return _not_found()

    # headers = event.get('headers')
    if http_method and http_method == 'POST':
        try:
            event['body'] = _parse_json(event.get('body', ''))
        except BadRequestException as e:
            return _bad_request(e)

    try:
        if path == GET_SESSION_TOKEN_PATH:
            result = get_session_token()
        elif path == REGISTER_PROVENANCE_PATH:
            result = register_provenance_handler(event)
        elif path == REGISTER_STANDARD_VARIABLES_PATH:
            result = register_standard_variables_handler(event)
        elif path == REGISTER_DATASETS_PATH:
            result = register_datasets_handler(event)
        elif path == REGISTER_VARIABLES_PATH:
            result = register_variables_handler(event)
        elif path == REGISTER_RESOURCES_PATH:
            result = register_resources_handler(event)
        elif path == DATASET_STANDARD_VARIABLES_PATH:
            result = dataset_standard_variables_handler(event)
        elif path == DATASET_VARIABLES_PATH:
            result = dataset_variables_handler(event)
        elif path == DATASET_RESOURCES_PATH:
            result = dataset_resources_handler(event)
        elif path == VARIABLES_STANDARD_VARIABLES_PATH:
            result = variables_standard_variables_handler(event)
        elif path == DATASETS_FIND_PATH_OLD:
            result = find_datasets_old_handler(event)
        elif path == FIND_DATASETS_PATH:
            result = find_datasets_handler(event)
        elif path == FIND_STANDARD_VARIABLES_PATH:
            result = find_standard_variables_handler(event)
        elif path == JATAWARE_SEARCH_PATH:
            result = jataware_search_handler(event)
        elif path == SEARCH_PATH:
            result = search_handler(event)
        elif path == SEARCH_PATH_V2:
            result = search_v2_handler(event)
        elif path == UPDATE_DATASET_VIZ_STATUS_PATH:
            result = update_dataset_viz_status_handler(event)
        elif path == UPDATE_DATASET_VIZ_CONFIG_PATH:
            result = update_dataset_viz_config_handler(event)
        elif path == UPDATE_DATASET_PATH:
            result = update_dataset_handler(event)
        elif path == UPDATE_RESOURCE_PATH:
            result = update_resource_handler(event)
        elif path == UPDATE_VARIABLE_PATH:
            result = update_variable_handler(event)
        elif path == UPDATE_STANDARD_VARIABLE_PATH:
            result = update_standard_variable_handler(event)
        elif path == GET_DATASET_INFO_PATH:
            result = get_dataset_info_handler(event)
        elif path == GET_RESOURCE_INFO_PATH:
            result = get_resource_info_handler(event)
        elif path == GET_VARIABLE_INFO_PATH:
            result = get_variable_info_handler(event)
        elif path == GET_STANDARD_VARIABLE_INFO_PATH:
            result = get_standard_variable_info_handler(event)
        elif path == GET_DATASET_TEMPORAL_COVERAGE_PATH:
            result = get_dataset_temporal_coverage_handler(event)
        elif path == DELETE_RESOURCE_PATH:
            result = delete_resource_handler(event)
        elif path == DELETE_DATASET_PATH:
            result = delete_dataset_handler(event)
        elif path == SYNC_DATASETS_METADATA_PATH:
            result = sync_datasets_metadata_handler(event)
        elif path == SYNC_DATASET_METADATA_PATH:
            result = sync_dataset_metadata_handler(event)
        elif path == CACHE_RESOURCES_PATH:
            result = cache_resources_handler(event)
        else:
            return _not_found()

        return _request_succeeded(result)

    except UnauthorizedException as e:
        return _unauthorized(str(e))
    except BadRequestException as e:
        return _bad_request(str(e))
    except InternalServerException as e:
        traceback.print_exc(file=sys.stdout)
        return _internal_error()
    except Exception as e:
        traceback.print_exc(file=sys.stdout)

        return _internal_error()


def _parse_json(payload):
    try:
        if isinstance(payload, str):
            return ujson.loads(payload)
        else:
            return payload
    except Exception:
        raise BadRequestException(f"Not a valid json object: {payload}")


@authenticate
def test_function(event):
    payload = event['body']['key']
    return {"results": ["some", "results"], "payload": payload}


def get_session_token():
    session_key = f"mint-data-catalog:{uuid.uuid4()}:{uuid.uuid4()}"
    return {"X-Api-Key": str(session_key)}


@authenticate
def register_provenance_handler(event):
    provenance_definition = event.get('body', {}).get('provenance', {})
    return register_provenance(provenance_definition)


@authenticate
def register_datasets_handler(event):
    dataset_definitions = event.get('body', {}).get('datasets', [])

    return register_datasets(dataset_definitions)


@authenticate
def register_standard_variables_handler(event):
    standard_variable_definitions = event.get(
        'body', {}).get('standard_variables', [])

    return register_standard_variables(standard_variable_definitions)


@authenticate
def register_variables_handler(event):
    variable_definitions = event.get('body', {}).get('variables', [])

    return register_variables(variable_definitions)


@authenticate
def register_resources_handler(event):
    resource_definitions = event.get('body', {}).get('resources', [])

    return register_resources(resource_definitions)


@authenticate
def find_datasets_old_handler(event):
    query_definition = event.get('body', {})
    return find_datasets_old(query_definition)


@authenticate
def find_datasets_handler(event):
    query_definition = event.get('body', {})
    return find_datasets(query_definition)


@authenticate
def find_standard_variables_handler(event):
    query_definition = event.get('body', {})
    return find_standard_variables(query_definition)


@authenticate
def dataset_standard_variables_handler(event):
    query_definition = event.get('body', {})
    return dataset_standard_variables(query_definition)


@authenticate
def dataset_variables_handler(event):
    query_definition = event.get('body', {})
    return dataset_variables(query_definition)


@authenticate
def dataset_resources_handler(event):
    query_definition = event.get('body', {})
    return dataset_resources(query_definition)


def jataware_search_handler(event):
    query_definition = event.get('body', {})
    query_definition["provenance_id"] = "3831a57f-a372-424a-b310-525b5441581b"
    return search_datasets(query_definition)


def search_handler(event):
    query_definition = event.get('body', {})
    return search_datasets(query_definition)


def search_v2_handler(event):
    query_definition = event.get('body', {})
    return search_datasets_v2(query_definition)


@authenticate
def variables_standard_variables_handler(event):
    query_definition = event.get('body', {})
    return variables_standard_variables(query_definition)


def update_dataset_viz_status_handler(event):
    update_definition = event.get('body', {})
    return update_dataset_viz_status(update_definition)


def update_dataset_viz_config_handler(event):
    update_definition = event.get('body', {})
    return update_dataset_viz_config(update_definition)


def update_dataset_handler(event):
    update_definition = event.get('body', {})
    return update_dataset(update_definition)


def update_resource_handler(event):
    update_definition = event.get('body', {})
    return update_resource(update_definition)


def update_variable_handler(event):
    update_definition = event.get('body', {})
    return update_variable(update_definition)


def update_standard_variable_handler(event):
    update_definition = event.get('body', {})
    return update_standard_variable(update_definition)


def sync_datasets_metadata_handler(event):
    return sync_datasets_metadata()


def sync_dataset_metadata_handler(event):
    dsid = event.get('body', {}).get('dataset_id', None)
    if dsid is not None:
        return sync_dataset_metadata(dsid)


def get_dataset_info_handler(event):
    query_definition = event.get('body', {})
    return get_dataset_info(query_definition)


def get_resource_info_handler(event):
    query_definition = event.get('body', {})
    return get_resource_info(query_definition)


def get_variable_info_handler(event):
    query_definition = event.get('body', {})
    return get_variable_info(query_definition)


def get_standard_variable_info_handler(event):
    query_definition = event.get('body', {})
    return get_standard_variable_info(query_definition)


def get_dataset_temporal_coverage_handler(event):
    query_definition = event.get('body', {})
    return dataset_temporal_coverage(query_definition)


def delete_resource_handler(event):
    delete_definition = event.get('body', {})
    return delete_resource(delete_definition)


def delete_dataset_handler(event):
    delete_definition = event.get('body', {})
    return delete_dataset(delete_definition)


def cache_resources_handler(event):
    cache_resources_definition = event.get('body', {})
    return {"job_id": str(uuid.uuid4()), "status": "pending"}


def _enable_sqlalchemy_logging():
    import logging

    logging.basicConfig()
    logging.getLogger('sqlalchemy.engine').setLevel(logging.INFO)


def _is_api_key_valid(api_key: str):
    return True
    if api_key is None:
        return False
    try:
        api_key_components = str(api_key).split(':')
        if len(api_key_components) != 3:
            return False
        if api_key_components[0] != "mint-data-catalog":
            return False
        if not _is_uuid(api_key_components[1]):
            return False
        if not _is_uuid(api_key_components[2]):
            return False

        return True
    except:
        return False


def _is_uuid(uuid_str: str) -> bool:
    try:
        uuid.UUID(str(uuid_str))
        return True
    except ValueError:
        return False


def _default_response_headers():
    return {
        "Access-Control-Allow-Methods": "GET, POST, DELETE, PUT",
        "Access-Control-Allow-Headers": "X-Requested-With, Content-Type, X-HTTP-Method-Override, X-Api-Key",
        "Access-Control-Allow-Origin": "*"
    }


def _request_succeeded(payload: dict) -> dict:
    return {
        "headers": _default_response_headers(),
        "statusCode": 200,
        "body": ujson.dumps(payload)
    }


def _bad_request(message: str) -> dict:
    return {
        "headers": _default_response_headers(),
        "statusCode": 400,
        "body": ujson.dumps({"error": message})
    }


def _unauthorized(message: str) -> dict:
    return {
        "headers": _default_response_headers(),
        "statusCode": 403,
        "body": ujson.dumps({"error": message})
    }


def _not_found():
    return {
        "headers": _default_response_headers(),
        "statusCode": 404,
        "body": ujson.dumps({"error": "Not Found"})
    }


def _internal_error():
    return {
        "headers": _default_response_headers(),
        "statusCode": 500,
        "body": ujson.dumps({"error": "Internal Error"})
    }


def _test_register_provenance():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    provenance_definition = {
        "provenance_type": "user",
        "record_id": 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        "name": "change my name",
        "metadata": {"contact_information": {"email": "email@example.com"}}
    }

    event = {
        "path": "/provenance/register_provenance",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"provenance": provenance_definition})
    }

    provenance_res = request_handler(event=event, context={})

    print(provenance_res)


def _test_register_standard_variables():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    standard_names = ['sn1', 'sn2', 'sn3', 'sn4', 'sn5', 'sn6']
    standard_variable_definitions = []
    for sn in standard_names:
        standard_variable_definition = {
            "name": sn, "ontology": "GSN", "uri": f"www.example.com/{sn}"}
        if sn == 'sn3':
            standard_variable_definition['record_id'] = '7529c859-83cb-563f-8cb8-3d6449fe237c'
            standard_variable_definition['ontology'] = 'OtherUPDSDFG'

        standard_variable_definitions.append(standard_variable_definition)

    event = {
        "path": "/knowledge_graph/register_standard_variables",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"standard_variables": standard_variable_definitions})
    }

    standard_variable_res = request_handler(event=event, context={})

    print(standard_variable_res)
    return standard_variable_res


def _test_register_datasets():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    dataset_record_id = "4e8ade31-7729-4891-a462-2dac66158512"
    datasets_definitions = [{
        "record_id": dataset_record_id,
        "provenance_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "metadata": {"variables": [{"@id": "blah"}, {"@id": "blah1"}], "new_metadata": 9},
        "description": "Test dataset desription blag blah blah blah",
        "name": "Test dataset name"
    }]

    event = {
        "path": "/datasets/register_datasets",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"datasets": datasets_definitions})
    }

    dataset_res = request_handler(event=event, context={})
    print(dataset_res)

    return dataset_res


# sn_name2id - a dictionary that maps standard_names created in #_test_register_standard_names to their record_ids
def _test_register_variables(dataset_record_id: str, sn_name2id: dict):
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    variable_definitions = [{
        "record_id": '008d7302-098c-4e80-a1b2-fe72d3012cb1',
        "dataset_id": dataset_record_id,
        "name": "var1-test",
        "metadata": {"unit": "mm s-1"},
        "standard_variable_ids": [sn_name2id[name] for name in ["sn2", "sn3"]]
    }, {
        "record_id": 'b89b96ba-14a7-4f71-a68b-0ca197e1b5d4',
        "dataset_id": dataset_record_id,
        "name": "var2-test",
        "metadata": {"unit": "mm s-2"},
        "standard_variable_ids": [sn_name2id[name] for name in ["sn2", "sn5", "sn3"]]
    }, {
        "record_id": '01379f9c-7d2a-4c4a-b818-fd947f767467',
        "dataset_id": dataset_record_id,
        "name": "var3-test",
        "metadata": {"unit": "mm s-3"},
        "standard_variable_ids": [sn_name2id[name] for name in ["sn1"]]
    }
    ]

    event = {
        "path": "/datasets/register_variables",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"variables": variable_definitions})
    }

    variables_res = request_handler(event=event, context={})
    print(variables_res)

    return variables_res


def _test_register_resources(dataset_record_id):
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    resource_definitions = [{
        "record_id": "0722f1c9-0df4-4cb1-a8b2-7612df33ac00",
        "dataset_id": dataset_record_id,
        "provenance_id": '6f57d0df-8570-4f7e-93c8-ef71361e6cfe',
        "variable_ids": ['b89b96ba-14a7-4f71-a68b-0ca197e1b5d4', '01379f9c-7d2a-4c4a-b818-fd947f767467'],
        "name": "2-variables file",
        "resource_type": "csv",
        "data_url": "www.data_url_1.com",
        "metadata": {
            "spatial_coverage": {
                "type": "BoundingBox",
                "value": {"xmin": 5, "ymin": -5, "xmax": "-56.5", "ymax": "-5.5"},
            },
            "temporal_coverage": {
                "start_time": "2018-01-01T14:40:30",
                "end_time": "2018-02-01T14:40:30"
            }
            # "some_key": {
            #     "some_key2": "value2"
            # }
        },
        "layout": {}
    }, {
        "record_id": "656432da-8f55-4327-98bb-3242ba8f2a95",
        "dataset_id": dataset_record_id,
        "provenance_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "variable_ids": [],
        "name": "0-variables file",
        "resource_type": "netcdf",
        "data_url": "www.data_url_2.com",
        "metadata": {
            "spatial_coverage": {
                "type": "Point",
                "value": {"x": -118.47, "y": 34.00}
            },
            #     "temporal_coverage": {
            #         "start_time": "2018-04-01T14:40:31",
            #         "end_time": "2018-03-01T14:40:30"
            #     }
        },
        # "metadata": {},
        "layout": {}
    }]

    event = {
        "path": "/datasets/register_resources",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"resources": resource_definitions})
    }

    resources_res = request_handler(event=event, context={})
    print(resources_res)

    return resources_res


def _test_register_resources_dan():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    resource_definitions = [
        {
            "dataset_id": "90db5c2f-ab2d-4086-8e07-72edb43545cd",
            "provenance_id": "7abe6e06-6f12-47b5-8844-3ad3f659e64c",
            "variable_ids": ["46877064-ba75-4b62-8984-f97bfcc64a04"],
            "name": "South Sudan Population Density (2015)",
            "resource_type": "GeoTIFF",
            "data_url": "https://s3.amazonaws.com/mint-data-catalog-public-datasets/south_sudan/ssudan_pop_density.tif.zip",
            "metadata": {
                    "is_zip": "true",
                    "spatial_coverage": {
                        "type": "BoundingBox",
                        "value": {
                            "xmin": 23.5073392908950041,
                            "ymin": 3.4863541890203287,
                            "xmax": 35.9476749908950097,
                            "ymax": 12.2385040890203332
                        }
                    },
                "temporal_coverage": {
                        "start_time": "2015-01-01T00:00:00",
                        "end_time": "2015-12-31T23:59:59"
                    }
            }
        },
        {
            "dataset_id": "d33b9035-581c-43bd-bd1c-d7b723231a2b",
            "provenance_id": "7abe6e06-6f12-47b5-8844-3ad3f659e64c",
            "variable_ids": ["3a5be2bc-efac-48bb-b70e-411ca4ae258a"],
            "name": "Road Network",
            "resource_type": "GeoJSON",
            "data_url": "https://s3.amazonaws.com/mint-data-catalog-public-datasets/south_sudan/ssudan_roads.geojson.zip",
            "metadata": {
                    "is_zip": "true",
                    "spatial_coverage": {
                        "type": "BoundingBox",
                        "value": {
                            "xmin": 23.8040498000000014,
                            "ymin": 3.1338895999999998,
                            "xmax": 36.2339556000000016,
                            "ymax": 13.1332734000000002
                        }
                    },
                "temporal_coverage": {
                        "start_time": "2017-12-31T00:00:00",
                        "end_time": "2017-12-31T23:59:59"
                    }
            }
        }
    ]

    event = {
        "path": "/datasets/register_resources",
        "httpMethod": "POST",
        "headers": headers,
        "body": ujson.dumps({"resources": resource_definitions})
    }

    resources_res = request_handler(event=event, context={})
    print(resources_res)

    return resources_res


def _test_update_dataset_viz_status():
    dataset_id = "d33b9035-581c-43bd-bd1c-d7b723231a2b"
    viz_config_id = "viz_config_1"

    headers = {
        "X-Api-Key": "don't need this"
    }

    event = {
        "path": "/datasets/update_dataset_viz_status",
        "httpMethod": "POST",
        "headers": headers,
        "body": ujson.dumps({"dataset_id": dataset_id, "viz_config_id": viz_config_id})
    }

    result = request_handler(event=event, context={})
    print(result)

    return result


def _test_update_dataset_viz_config():
    dataset_id = "d33b9035-581c-43bd-bd1c-d7b723231a2b"
    viz_config_id = "viz_config_1"

    headers = {
        "X-Api-Key": "don't need this"
    }

    payload = {
        "dataset_id": dataset_id,
        "viz_config_id": viz_config_id,
        "$set": {"visualized": "true"}
    }
    event = {
        "path": "/datasets/update_dataset_viz_config",
        "httpMethod": "POST",
        "headers": headers,
        "body": ujson.dumps(payload)
    }

    result = request_handler(event=event, context={})
    print(result)

    return result


def _insert_test():

    _test_register_provenance()

    sn_res = _test_register_standard_variables()
    print("BLAGHVLAG:")
    print(sn_res)
    sn_name2id = {}
    for sn in ujson.loads(sn_res['body'])['standard_variables']:
        sn_name2id[sn['name']] = sn['record_id']

    dataset_res = _test_register_datasets()
    dataset_record_id = ujson.loads(dataset_res['body'])[
        'datasets'][0]['record_id']

    variables_res = _test_register_variables(
        dataset_record_id=dataset_record_id, sn_name2id=sn_name2id)

    pprint.pprint(ujson.dumps(variables_res))

    # resources_res = _test_register_resources(dataset_record_id=dataset_record_id)

    print("DONE")


def _fetch_test():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    query = {"standard_variable_names__in": ["atmosphere_air_water~vapor__min_of_relative_saturation",
                                             "land_surface~horizontal_radiation~incoming~shortwave__energy_flux",
                                             "land_surface_wind__speed",
                                             "atmosphere_water__time_integral_of_precipitation_leq_volume_flux",
                                             "air__daily_max_of_temperature", "air__daily_min_of_temperature"],
             "spatial_coverage__intersects": [-98.9177253733141, 28.928792181820924, -95.16497400496687,
                                              33.800469405778045],
             "end_time__gte": "2000-01-01T00:00:00",
             "start_time__lte": "2018-12-31T00:00:00",
             "limit": 5000
             }

    query = {
        "spatial_coverage__intersects": {"type": "Polygon", "coordinates": [[[-179.95, -59.95], [-179.95, 89.95], [179.95, 89.95], [179.95, -59.95], [-179.95, -59.95]]]}
    }

    query = {
        "end_time__gte": "2000-01-01T00:00:00",
        "start_time__lte": "2018-12-31T00:00:00",
    }

    query = {
        "spatial_coverage__intersects": [-98.9177253733141, 28.928792181820924, -95.16497400496687,
                                         33.800469405778045]
    }

    query = {
        "standard_variable_names__in": ["atmosphere_water__precipitation_leq_volume_flux"],
        "dataset_names__in": ["BARO GPM data 2008 - 2018"],
        "end_time__gte": "2018-01-01T00:00:00",
        "start_time__lte": "2019-01-01T00:00:00"
    }
    query = {
        "dataset_ids__in": ["adfca6fb-ad82-4be3-87d8-8f60f9193e43"]
    }

    event = {
        'path': '/datasets/find',
        'httpMethod': 'POST',
        'headers': headers,
        'body': ujson.dumps(query)
    }

    res = request_handler(event=event, context={})
    print(res)


def _test_find_datasets():
    query = {
        "dataset_names__in": ["*"],
        "limit": 10
    }

    event = {
        'path': '/find_datasets',
        'headers': {'X-Api-Key': 'mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662'},
        'httpMethod': 'POST',
        'body': ujson.dumps(query)
    }

    # res = find_standard_variables({"headers": {"X-Api-Key": api_key}, "body": ujson.dumps(query)}, {})
    res = request_handler(event=event, context={})
    print(res)


def _test_find_standard_variables():
    query = {
        "name__in": ["sn1"],
        # "ontology__in": ["SomeOtherOntology"],
        # "uri__in": ["www.example.com/sn1"]
    }
    api_key = ujson.loads(get_session_token({}, {})['body'])['X-Api-Key']

    event = {
        'path': '/knowledge_graph/find_standard_variables',
        'headers': {'X-Api-Key': api_key},
        'body': ujson.dumps(query)
    }

    # res = find_standard_variables({"headers": {"X-Api-Key": api_key}, "body": ujson.dumps(query)}, {})
    res = request_handler(event=event, context={})
    print(res)


def _test_dataset_standard_variables():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"

    # valid uuid
    dataset_id = "f335e62c-a38b-5549-bd22-dd7b81f1b17c"

    # nonexistent uuid
    # dataset_id = "c02579a9-744e-5ca9-ab34-040cb771e169"
    query = {
        "dataset_id": dataset_id
    }

    event = {
        'path': '/datasets/dataset_standard_variables',
        'headers': {'X-Api-Key': api_key},
        'body': ujson.dumps(query)
    }

    # res = dataset_standard_variables({"headers": {"X-Api-Key": api_key}, "body": ujson.dumps(payload)}, {})
    res = request_handler(event=event, context={})
    print(res)


def _test_dataset_variables():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"

    # valid uuid
    dataset_id = "7a6c1b5c-5b09-4cf9-9921-f70c1d496e8a"

    # nonexistent uuid
    # dataset_id = "c02579a9-744e-5ca9-ab34-040cb771e169"
    query = {
        "dataset_id": dataset_id
    }

    event = {
        'path': '/datasets/dataset_variables',
        'headers': {'X-Api-Key': api_key},
        "httpMethod": "POST",
        'body': ujson.dumps(query)
    }

    res = request_handler(event=event, context={})
    print(res)


def _test_dataset_resources():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"

    # valid uuid
    dataset_id = "7a6c1b5c-5b09-4cf9-9921-f70c1d496e8a"
    dataset_id_ankush = "da6b6d47-7672-4e6e-a455-7bbc7e7ceb99"

    # nonexistent uuid
    # dataset_id = "c02579a9-744e-5ca9-ab34-040cb771e169"
    query = {
        "dataset_id": dataset_id_ankush
    }

    bounding_box = [41.468759, 3.775651, 42.024722, 4.126743]
    start_time = "2018-01-01T00:00:00"
    end_time = "2018-12-31T23:59:59"

    sc_filter = {
        "spatial_coverage__intersects": {"type": "Polygon", "coordinates": [
            [[-179.95, -59.95], [-179.95, 89.95], [179.95, 89.95], [179.95, -59.95], [-179.95, -59.95]]]}
    }

    tc_filter = {
        "end_time__gte": "2019-01-01T00:00:00",
        "start_time__lte": "2019-12-31T00:00:00"
    }

    tc_filter_ankush = {
        "end_time__gte": "2018-01-01T00:00:00",
        "start_time__lte": "2018-12-31T23:59:59"
    }
    sc_filter_ankush = {
        "spatial_coverage": {"type": "Polygon", "coordinates": [[[41.47, 3.77], [42, 3.77], [42, 4.12], [41.47, 4.12], [41.47, 3.77]]]}
    }

    all_filter = {
        "spatial_coverage__intersects": {"type": "Polygon", "coordinates": [
            [[-179.95, -59.95], [-179.95, 89.95], [179.95, 89.95], [179.95, -59.95], [-179.95, -59.95]]]},
        "end_time__gte": "2010-01-01T00:00:00",
        "start_time__lte": "2018-12-31T00:00:00"
    }

    query['filter'] = {
        "spatial_coverage__within": sc_filter_ankush["spatial_coverage"],
        "start_time__lte": tc_filter_ankush["start_time__lte"],
        "end_time__gte": tc_filter_ankush["end_time__gte"]
    }
    # query['filter'] = all_filter

    event = {
        'path': '/datasets/dataset_resources',
        'headers': {'X-Api-Key': api_key},
        "httpMethod": "POST",
        'body': ujson.dumps(query)
    }

    res = request_handler(event=event, context={})
    print(res)


def _test_variables_standard_variables():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"

    # valid uuids
    variable_ids = ["008d7302-098c-4e80-a1b2-fe72d3012cb1",
                    "b89b96ba-14a7-4f71-a68b-0ca197e1b5d4"]
    query = {
        "variable_ids__in": variable_ids
    }

    event = {
        'path': '/variables/variables_standard_variables',
        'headers': {'X-Api-Key': api_key},
        "httpMethod": "POST",
        'body': ujson.dumps(query)
    }

    res = request_handler(event=event, context={})
    print(res)


def _test_request_handler():
    path = "/path/test_function"
    headers = {'X-Api-Key': 'asdfsdfadsfa'}
    body = {"key": "value"}

    event = {
        "path": path,
        "headers": headers,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    pprint.pprint(ujson.dumps(resp))


def _test_get_session_token():
    path = '/get_session_token'

    event = {
        'httpMethod': 'GET',
        'path': path
    }

    resp = request_handler(event=event, context={})
    pprint.pprint(ujson.dumps(resp))


def _test_get_dataset_info():
    path = '/datasets/get_dataset_info'
    body = {"dataset_id": "c8b2b335-f627-4c45-8ebc-69ebe03e4008"}
    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp['body'])


def _test_get_resource_info():
    path = '/resources/get_resource_info'
    body = {"resource_id": "56de4414-0e63-4481-b416-b6fc38805625"}
    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp['body'])


def _test_get_variable_info():
    path = '/variables/get_variable_info'
    body = {"variable_id": "cbd04f7c-51f0-4f86-b874-789c2afbf971"}
    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp['body'])


def _test_get_standard_variable_info():
    path = '/standard_variables/get_standard_variable_info'
    body = {"standard_variable_id": "ab426448-4636-5e46-84d0-69282b30809c"}
    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp['body'])


def _test_update_dataset():
    path = '/datasets/update_dataset'
    body = {
        "dataset_id": "4e8ade31-7729-4891-a462-2dac66158512",
        "name": "new_name",
        "metadata": {
            "new_metadata": "test"
        }
    }

    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp['body'])


def _exec_update_dataset():
    path = '/datasets/update_dataset'
    body = {
        "dataset_id": "insert-here",
        "metadata": {}
    }

    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp['body'])


def _test_update_resource():
    path = '/resources/update_resource'
    body = {
        "resource_id": "656432da-8f55-4327-98bb-3242ba8f2a95",
        "resource_type": "NetCDF",
        "metadata": {
            "new_metadata": 23
        }
    }

    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp['body'])


def _test_update_variable():
    path = '/variables/update_variable'
    body = {
        "variable_id": "008d7302-098c-4e80-a1b2-fe72d3012cb1",
        "name": "new variable name",
        "metadata": {
            "new_metadata": 23,
            "new_field": 343
        }
    }

    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp['body'])


def _test_update_standard_variable():
    path = '/standard_variables/update_standard_variable'
    body = {
        "standard_variable_id": "3fb35cc2-56e5-540a-94a2-fab02f5139ce",
        "name": "new name",
        "description": "update description"
    }

    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp['body'])


def _test_jataware_search_query():
    path = '/datasets/jataware_search'

    body = {
        "search_query": ["data"]
    }

    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp)
    # print(resp['body'])


def _test_search_query():
    path = '/datasets/search'

    body = {
        "search_query": ["data"]
    }

    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp)


def _test_search_v2_query():
    path = '/datasets/search_v2'

    body1 = {
        "search_query": ["fldas"]
    }

    body2 = {
        "spatial_coverage": {"type": "Polygon", "coordinates": [[[-179.95, -59.95], [-179.95, 89.95], [179.95, 89.95], [179.95, -59.95], [-179.95, -59.95]]]}
    }

    body3 = {
        "temporal_coverage": {
            "start_time": "2000-01-01T00:00:00",
            "end_time": "2010-12-31T23:59:59"
        }
    }

    body = {**body1, **body2, **body3}

    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = request_handler(event, {})
    print(resp)


def _test_delete_resource():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    resource_definitions = [{
        "record_id": "dda6cda7-aec4-4f4a-9fda-4740cfe123dc",
        "dataset_id": "4e8ade31-7729-4891-a462-2dac66158512",
        "provenance_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "variable_ids": ['b89b96ba-14a7-4f71-a68b-0ca197e1b5d4', '01379f9c-7d2a-4c4a-b818-fd947f767467'],
        "name": "2-variables file",
        "resource_type": "csv",
        "data_url": "www.data_url_1.com",
        "metadata": {
            "spatial_coverage": {
                "type": "BoundingBox",
                "value": {"xmin": 5, "ymin": -5, "xmax": "-56.5", "ymax": "-5.5"},
            },
            "temporal_coverage": {
                "start_time": "2018-01-01T14:40:30",
                "end_time": "2018-02-01T14:40:30"
            }
        }
    }]

    registration_event = {
        "path": "/datasets/register_resources",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"resources": resource_definitions})
    }

    resources_res = request_handler(event=registration_event, context={})
    print(resources_res)

    delete_definition = {
        "provenance_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
        "resource_id": "dda6cda7-aec4-4f4a-9fda-4740cfe123dc"
    }

    event = {
        "path": "/resources/delete_resource",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps(delete_definition)
    }
    res = request_handler(event=event, context={})
    print(res)


def _test_delete_dataset():
    provenance_id = "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11"

    resource_id1 = "7fc07e3b-3d34-42aa-8ce0-c394d5542eaa"
    resource_id2 = "e99ac19c-b75a-4684-a0aa-17c6af735557"
    variable_id1 = "7152584f-0819-4c7d-8522-a09c20b925b6"
    variable_id2 = "0313fd35-74dd-41c2-9208-b39d1baf4ff5"
    dataset_id = "ca18126f-950a-40fb-be32-7fcf3236f4f1"

    sn3 = "7529c859-83cb-563f-8cb8-3d6449fe237c"
    sn4 = "6cede7e3-927f-5c2c-b67e-2d7dccc622b4"
    sn5 = "3c3601a7-1c36-5dfa-8aac-12d07fd93258"
    sn6 = "7370308c-2e57-5a15-ae54-ead6e195835c"

    dataset_definitions = [{"provenance_id": provenance_id,
                            "record_id": dataset_id, "name": "delete", "description": "delete test"}]

    headers = {
        "X-Api-Key": "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"}

    register_datasets_event = {
        "path": "/datasets/register_datasets",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"datasets": dataset_definitions})
    }

    # res = request_handler(event=register_datasets_event, context={})
    # print(res)

    variable_definitions = [{
        "record_id": variable_id1,
        "dataset_id": dataset_id,
        "name": "var1-test",
        "metadata": {"unit": "mm s-1"},
        "standard_variable_ids": [sn3, sn4, sn5]
    }, {
        "record_id": variable_id2,
        "dataset_id": dataset_id,
        "name": "var2-test",
        "metadata": {"unit": "mm s-2"},
        "standard_variable_ids": [sn6]
    }]

    register_variables_event = {
        "path": "/datasets/register_variables",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"variables": variable_definitions})
    }

    # res = request_handler(event=register_variables_event, context={})
    # print(res)

    resource_definitions = [{
        "record_id": resource_id1,
        "dataset_id": dataset_id,
        "provenance_id": provenance_id,
        "variable_ids": [variable_id1, variable_id2],
        "name": "2-variables file",
        "resource_type": "csv",
        "data_url": "www.data_url_1.com",
        "metadata": {
            "spatial_coverage": {"type": "BoundingBox", "value": {"xmin": 5, "ymin": -5, "xmax": "-56.5", "ymax": "-5.5"}},
            "temporal_coverage": {"start_time": "2018-01-01T14:40:30", "end_time": "2018-02-01T14:40:30"}
        }
    }, {
        "record_id": resource_id2,
        "dataset_id": dataset_id,
        "provenance_id": provenance_id,
        "variable_ids": [variable_id1],
        "name": "1-variables file",
        "resource_type": "netcdf",
        "data_url": "www.data_url_2.com",
        "metadata": {"spatial_coverage": {"type": "Point", "value": {"x": -118.47, "y": 34.00}}}
    }]

    register_resources_event = {
        "path": "/datasets/register_resources",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"resources": resource_definitions})
    }

    # res = request_handler(event=register_resources_event, context={})
    # print(res)

    # delete_definition = {
    #         "provenance_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    #         "dataset_id": dataset_id
    #     }

    delete_definition = {
        "provenance_id": "b3e79dc2-8fa1-4203-ac82-b5267925191f",
        "dataset_id": "fdf6991f-118a-4028-a85e-09a51fd143da"
    }
    event = {
        "path": "/datasets/delete_dataset",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps(delete_definition)
    }
    res = request_handler(event=event, context={})
    print(res)


def _test_cache_resources():
    headers = {
        "X-Api-Key": "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"}

    cache_resources_definition = {"resource_ids": []}
    event = {
        "path": "/resources/cache_resources",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps(cache_resources_definition)
    }

    res = request_handler(event=event, context={})
    print(res)


def _test_get_dataset_temporal_coverage():
    headers = {
        "X-Api-Key": "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"}

    event = {
        "path": "/datasets/get_dataset_temporal_coverage",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"dataset_id": '5babae3f-c468-4e01-862e-8b201468e3b5'})
    }

    res = request_handler(event=event, context={})
    print(res)


if __name__ == "__main__":
    # _rafael_register_resource()
    _insert_test()
    # _fetch_test()
    # _test_find_datasets()
    # _test_find_standard_variables()
    # _test_dataset_standard_variables()
    # _test_dataset_variables()
    # _test_request_handler()
    # _test_get_session_token()
    # _test_register_provenance()
    # _test_register_resources_dan()
    # _test_register_resources("4e8ade31-7729-4891-a462-2dac66158512")
    # _test_update_dataset_viz_status()
    # _test_update_dataset_viz_config()
    # _test_variables_standard_variables()
    # _test_dataset_resources()
    # _test_get_dataset_info()
    # _test_get_resource_info()
    # _test_get_variable_info()
    # _test_get_standard_variable_info()

    # _test_update_dataset()
    # _test_update_resource()
    # _test_update_variable()
    # _test_update_standard_variable()

    # _test_jataware_search_query()
    # _test_search_query()
    # _test_search_v2_query()
    # _test_delete_resource()
    # _test_delete_dataset()

    # _exec_update_dataset()
    # _test_cache_resources()

    # _test_get_dataset_temporal_coverage()
