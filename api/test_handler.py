import requests
import json
import ujson
import pprint


def test_api(event, context={}):
    url = f'http://localhost:7000{event["path"]}'

    # Additional headers.
    headers = {'Content-Type': 'application/json'}

    # Body
    payload = event

    # convert dict to json string by json.dumps() for body data.
    resp = requests.post(url, headers=headers, data=json.dumps(payload, indent=4))

    # Validate response headers and body contents, e.g. status code.
    # assert resp.status_code == 200
    resp_body = resp.json()
    return resp_body


def _test_register_provenance():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    provenance_definition = {
        "provenance_type": "user",
        "record_id": 'a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11',
        "name": "test_user_xtw",
        "metadata": {"contact_information": {"email": "email@example.com"}}
    }

    event = {
        "path": "/provenance/register_provenance",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"provenance": provenance_definition})
    }

    provenance_res = test_api(event=event, context={})

    print(provenance_res)


def _test_register_standard_variables():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"
    headers = {
        "X-Api-Key": api_key
    }

    standard_names = ['sn1', 'sn2', 'sn3', 'sn4', 'sn5', 'sn6']
    standard_variable_definitions = []
    for sn in standard_names:
        standard_variable_definition = {"name": sn, "ontology": "GSN", "uri": f"www.example.com/{sn}"}
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

    standard_variable_res = test_api(event=event, context={})

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

    dataset_res = test_api(event=event, context={})
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

    variables_res = test_api(event=event, context={})
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

    resources_res = test_api(event=event, context={})
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

    resources_res = test_api(event=event, context={})
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

    result = test_api(event=event, context={})
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

    result = test_api(event=event, context={})
    print(result)

    return result


def _insert_test():

    _test_register_provenance()

    sn_res = _test_register_standard_variables()

    sn_name2id = {}
    for sn in ujson.loads(sn_res['body'])['standard_variables']:
        sn_name2id[sn['name']] = sn['record_id']

    dataset_res = _test_register_datasets()
    dataset_record_id = ujson.loads(dataset_res['body'])['datasets'][0]['record_id']

    variables_res = _test_register_variables(dataset_record_id=dataset_record_id, sn_name2id=sn_name2id)

    pprint.pprint(ujson.dumps(variables_res))

    resources_res = _test_register_resources(dataset_record_id=dataset_record_id)

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
        "spatial_coverage__intersects": {"type":"Polygon","coordinates":[[[-179.95,-59.95],[-179.95,89.95],[179.95,89.95],[179.95,-59.95],[-179.95,-59.95]]]}
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

    res = test_api(event=event, context={})
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
    res = test_api(event=event, context={})
    print(res)


# def _test_find_standard_variables():
#     query = {
#         "name__in": ["sn1"],
#         # "ontology__in": ["SomeOtherOntology"],
#         # "uri__in": ["www.example.com/sn1"]
#     }
#     api_key = ujson.loads(get_session_token({}, {})['body'])['X-Api-Key']
#
#     event = {
#         'path': '/knowledge_graph/find_standard_variables',
#         'headers': {'X-Api-Key': api_key},
#         'body': ujson.dumps(query)
#     }
#
#     # res = find_standard_variables({"headers": {"X-Api-Key": api_key}, "body": ujson.dumps(query)}, {})
#     res = test_api(event=event, context={})
#     print(res)


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


    #res = dataset_standard_variables({"headers": {"X-Api-Key": api_key}, "body": ujson.dumps(payload)}, {})
    res = test_api(event=event, context={})
    print(res)


def _test_dataset_variables():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"

    # valid uuid
    dataset_id = "4e8ade31-7729-4891-a462-2dac66158512"

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

    res = test_api(event=event, context={})
    print(res)


def _test_dataset_resources():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"

    # valid uuid
    dataset_id = "4e8ade31-7729-4891-a462-2dac66158512"
    # dataset_id_ankush = "da6b6d47-7672-4e6e-a455-7bbc7e7ceb99"

    # nonexistent uuid
    # dataset_id = "c02579a9-744e-5ca9-ab34-040cb771e169"
    query = {
        "dataset_id": dataset_id
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

    # query['filter'] = {
    #     "spatial_coverage__within": sc_filter_ankush["spatial_coverage"],
    #     "start_time__lte": tc_filter_ankush["start_time__lte"],
    #     "end_time__gte": tc_filter_ankush["end_time__gte"]
    # }
    # query['filter'] = all_filter

    event = {
        'path': '/datasets/dataset_resources',
        'headers': {'X-Api-Key': api_key},
        "httpMethod": "POST",
        'body': ujson.dumps(query)
    }

    res = test_api(event=event, context={})
    print(res)


def _test_variables_standard_variables():
    api_key = "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"

    # valid uuids
    variable_ids = ["008d7302-098c-4e80-a1b2-fe72d3012cb1", "b89b96ba-14a7-4f71-a68b-0ca197e1b5d4"]
    query = {
        "variable_ids__in": variable_ids
    }

    event = {
        'path': '/variables/variables_standard_variables',
        'headers': {'X-Api-Key': api_key},
        "httpMethod": "POST",
        'body': ujson.dumps(query)
    }

    res = test_api(event=event, context={})
    print(res)


def _test_test_api():
    path = "/path/test_function"
    headers = {'X-Api-Key': 'asdfsdfadsfa'}
    body = {"key": "value"}

    event = {
        "path": path,
        "headers": headers,
        "body": ujson.dumps(body)
    }

    resp = test_api(event, {})
    pprint.pprint(ujson.dumps(resp))


def _test_get_session_token():
    path = '/get_session_token'

    event = {
        'httpMethod': 'GET',
        'path': path
    }

    resp = test_api(event=event, context={})
    pprint.pprint(ujson.dumps(resp))


def _test_get_dataset_info():
    path = '/datasets/get_dataset_info'
    body = {"dataset_id": "c8b2b335-f627-4c45-8ebc-69ebe03e4008"}
    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = test_api(event, {})
    print(resp['body'])


def _test_get_resource_info():
    path = '/resources/get_resource_info'
    body = {"resource_id": "56de4414-0e63-4481-b416-b6fc38805625"}
    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = test_api(event, {})
    print(resp['body'])


def _test_get_variable_info():
    path = '/variables/get_variable_info'
    body = {"variable_id": "cbd04f7c-51f0-4f86-b874-789c2afbf971"}
    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = test_api(event, {})
    print(resp['body'])


def _test_get_standard_variable_info():
    path = '/standard_variables/get_standard_variable_info'
    body = {"standard_variable_id": "ab426448-4636-5e46-84d0-69282b30809c"}
    event = {
        "httpMethod": "POST",
        "path": path,
        "body": ujson.dumps(body)
    }

    resp = test_api(event, {})
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

    resp = test_api(event, {})
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

    resp = test_api(event, {})
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

    resp = test_api(event, {})
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

    resp = test_api(event, {})
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

    resp = test_api(event, {})
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

    resp = test_api(event, {})
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

    resp = test_api(event, {})
    print(resp)


def _test_search_v2_query():
    path = '/datasets/search_v2'

    body1 = {
        "search_query": ["fldas"]
    }

    body2 = {
        "spatial_coverage": {"type":"Polygon","coordinates":[[[-179.95,-59.95],[-179.95,89.95],[179.95,89.95],[179.95,-59.95],[-179.95,-59.95]]]}
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

    resp = test_api(event, {})
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

    resources_res = test_api(event=registration_event, context={})
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
    res = test_api(event=event, context={})
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


    dataset_definitions = [{"provenance_id": provenance_id, "record_id": dataset_id, "name": "delete", "description": "delete test"}]


    headers = {"X-Api-Key": "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"}

    register_datasets_event = {
        "path": "/datasets/register_datasets",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"datasets": dataset_definitions})
    }

    res = test_api(event=register_datasets_event, context={})
    print(res)

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

    res = test_api(event=register_variables_event, context={})
    print(res)

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

    res = test_api(event=register_resources_event, context={})
    print(res)

    # delete_definition = {
    #         "provenance_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    #         "dataset_id": dataset_id
    #     }
    #
    # delete_definition = {
    #     #"provenance_id": "b3e79dc2-8fa1-4203-ac82-b5267925191f",
    #     "provenance_id": "a0eebc99-9c0b-4ef8-bb6d-6bb9bd380a11",
    #     # "dataset_id": "fdf6991f-118a-4028-a85e-09a51fd143da"
    #     "dataset_id": "ca18126f-950a-40fb-be32-7fcf3236f4f1"
    # }
    # event = {
    #     "path": "/datasets/delete_dataset",
    #     "headers": headers,
    #     "httpMethod": "POST",
    #     "body": ujson.dumps(delete_definition)
    # }
    # res = test_api(event=event, context={})
    # print(res)


def _test_cache_resources():
    headers = {"X-Api-Key": "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"}

    cache_resources_definition = {"resource_ids": []}
    event = {
        "path": "/resources/cache_resources",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps(cache_resources_definition)
    }

    res = test_api(event=event, context={})
    print(res)


def _test_get_dataset_temporal_coverage():
    headers = {"X-Api-Key": "mint-data-catalog:2bc0308c-ed42-4d05-b1ab-9f0a9f5caac7:30124599-a1d3-48af-a5e1-798446f83662"}

    event = {
        "path": "/datasets/get_dataset_temporal_coverage",
        "headers": headers,
        "httpMethod": "POST",
        "body": ujson.dumps({"dataset_id": '5babae3f-c468-4e01-862e-8b201468e3b5'})
    }

    res = test_api(event=event, context={})
    print(res)


if __name__ == "__main__":
    _test_register_provenance()
    _test_register_standard_variables()
    # _rafael_register_resource()
    # _insert_test()
    # _fetch_test()
    # _test_find_datasets()
    #_test_find_standard_variables()
    #_test_dataset_standard_variables()
    # _test_dataset_variables()
    # _test_request_handler()
    #_test_get_session_token()
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
    _test_delete_dataset()

    # _exec_update_dataset()
    # _test_cache_resources()

    # _test_get_dataset_temporal_coverage()
