from typing import *
import sys
import traceback
from datetime import datetime
import uuid
import ujson

from sqlalchemy import func
from sqlalchemy import and_
from sqlalchemy.sql.expression import case, literal
from sqlalchemy import desc
from sqlalchemy import JSON, TIMESTAMP, DateTime

from dcat_service.misc.exception import BadRequestException, InternalServerException
from dcat_service.db_models import DatasetDB, StandardVariableDB, TemporalCoverageIndexDB, SpatialCoverageIndexDB, \
    VariableDB, ResourceDB
from dcat_service.models.dataset import Dataset
from dcat_service.models.resource import Resource
from dcat_service.models.variable import Variable
from dcat_service.models.standard_variable import StandardVariable

from dcat_service import session_scope
import re


def _validate_uuid(input_string: str) -> bool:
    try:
        uuid.UUID(str(input_string))
        return True
    except ValueError:
        return False


def find_datasets_old(query_definition: Dict) -> Dict:

    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': f"Query definition must not be empty; received {query_definition}"})
    # parse query operators
    # search_ops = body.pop('search_operators', "and").lower()
    # sort_by = body.pop("sort_by", None)
    # assert search_ops == "or" or search_ops == "and"
    limit = int(query_definition.pop("limit", 20))
    offset = int(query_definition.pop("offset", 0))
    fields: Dict[str, dict] = {}
    for field_w_op, value in query_definition.items():
        if field_w_op.rfind("__") == -1:
            field, op = field_w_op, None
        else:
            field, op = field_w_op.split("__")
        fields[field] = {"op": op, "value": value}

    allowed_query_words = ["dataset_names", "dataset_ids", "standard_variable_ids", "standard_variable_names",
                           "spatial_coverage", "start_time", "end_time"]

    if len(fields) == 0:
        raise BadRequestException({'Missing search field(s)': query_definition})
    elif not all([field_name in allowed_query_words for field_name in list(fields.keys())]):
        raise BadRequestException({'InvalidQueryDefinition': f"Invalid search field(s); must be either of {allowed_query_words}"})
    if "dataset_names" in fields:
        dataset_names_op = fields["dataset_names"]["op"]
        dataset_names_value = fields["dataset_names"]["value"]

        if dataset_names_op != "in":
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'dataset_names': {dataset_names_op}"})
        if not dataset_names_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'dataset_names': {dataset_names_value}"})
        if not isinstance(dataset_names_value, list):
            raise BadRequestException({'InvalidQueryDefinition':
                f"Invalid filter value type for 'dataset_names': {dataset_names_value}; must be an array of values"})

    if "dataset_ids" in fields:
        dataset_ids_op = fields["dataset_ids"]["op"]
        dataset_ids_value = fields["dataset_ids"]["value"]

        if dataset_ids_op != "in":
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'dataset_ids': {dataset_ids_op}"})
        if not dataset_ids_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'dataset_ids': {dataset_ids_value}"})
        if not isinstance(dataset_ids_value, list):
            raise BadRequestException({'InvalidQueryException':
                f"Invalid filter value for type 'dataset_ids': {dataset_ids_value}; must be an array of values"})

    if "standard_variable_ids" in fields:
        standard_variable_ids_op = fields["standard_variable_ids"]["op"]
        standard_variable_ids_value = fields["standard_variable_ids"]["value"]

        if standard_variable_ids_op != "in":
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'standard_variable_ids_op': {standard_variable_ids_op}"})
        if not standard_variable_ids_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'standard_variable_ids': {standard_variable_ids_value}"})
        if not isinstance(standard_variable_ids_value, list):
            raise BadRequestException({'InvalidQueryDefinition': 
                f"Invalid filter value type for 'standard_variable_ids': {standard_variable_ids_value}; must be an array of values"})

    if "standard_variable_names" in fields:
        standard_variable_names_op = fields["standard_variable_names"]["op"]
        standard_variable_names_value = fields["standard_variable_names"]["value"]

        if standard_variable_names_op != "in":
            raise BadRequestException({'InvalidQueryDefinition': 
                f"Invalid filter operation for 'standard_variable_names_op': {standard_variable_names_op}"})
        if not standard_variable_names_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'standard_variable_names': {standard_variable_names_value}"})
        if not isinstance(standard_variable_names_value, list):
            raise BadRequestException({'InvalidQueryDefinition': 
                f"Invalid filter value type for 'standard_variable_names': {standard_variable_names_value}; must be an array of values"})

    if "spatial_coverage" in fields:
        spatial_coverage_op = fields["spatial_coverage"]["op"]
        spatial_coverage_value = fields["spatial_coverage"]["value"]

        allowed_filter_keywords = ["within", "intersects"]

        if spatial_coverage_op not in allowed_filter_keywords:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'spatial_coverage': {spatial_coverage_op}"})
        if not spatial_coverage_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'spatial_coverage': {spatial_coverage_op}"})
        # if not isinstance(spatial_coverage_value, list):
        #     raise BadRequestException({'InvalidQueryDefinition':
        #         f"Invalid filter value type for 'spatial_coverage': {spatial_coverage_op}; must be an numeric array with [x_min, y_min, x_max, y_max]"})

    if "start_time" in fields:
        if fields["start_time"]['op'] is None:
            fields["start_time"]["op"] = "gte"

        if fields["start_time"]["op"] not in {"gte", "gt", "lte", "lt"}:
            raise BadRequestException({'InvalidQueryDefinition': 
                f"Invalid filter operation: {fields['start_time']['op']}; must be on of 'gte', 'gt', 'lte', 'lt'"})

        try:
            fields['start_time']['value'] = datetime.strptime(fields['start_time']['value'], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            help_msg = "must be formatted according to ISO8601: '%Y-%m-%dT%H:%M:%S'"
            raise BadRequestException({'InvalidQueryDefinition': 
                f"Invalid datetime format for 'start_time': {fields['start_time']['value']}; {help_msg}"})

    if "end_time" in fields:
        if fields["end_time"]['op'] is None:
            fields["end_time"]["op"] = "gte"

        if fields["end_time"]["op"] not in {"gte", "gt", "lte", "lt"}:
            raise BadRequestException({'InvalidQueryDefinition': 
                f"Invalid filter operation: {fields['end_time']['op']}; must be on of 'gte', 'gt', 'lte', 'lt'"})
        try:
            fields['end_time']['value'] = datetime.strptime(fields['end_time']['value'], "%Y-%m-%dT%H:%M:%S")
        except ValueError:
            help_msg = "must be formatted according to ISO8601: '%Y-%m-%dT%H:%M:%S'"
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid datetime format for 'end_time': {fields['end_time']['value']}; {help_msg}"})

    # execute the query
    try:
        with session_scope() as session:
            query = session.query(DatasetDB.id, DatasetDB.name, DatasetDB.description, DatasetDB.json_metadata, func.ST_AsGeoJSON(DatasetDB.spatial_coverage))

            query = query.filter(DatasetDB.provenance_id != 'e8287ea4-e6f2-47aa-8bfc-0c22852735c8')

            # query = query.filter(ResourceDB.is_queryable.is_(True))
            if "dataset_names" in fields:
                dataset_names = ['(^|\s|_|\-)' + re.escape(dataset_name).replace(r"\*", ".*") + '($|\s|_|\-)' for dataset_name in fields['dataset_names']['value']]

                query = query.filter(DatasetDB.name.op("~*")("|".join(dataset_names)))

            if "dataset_ids" in fields:
                query = query.filter(DatasetDB.id.in_(fields['dataset_ids']['value']))

            if "standard_variable_ids" in fields or "standard_variable_names" in fields:

                query = query.join(VariableDB, DatasetDB.id == VariableDB.dataset_id) \
                    .join(StandardVariableDB, VariableDB.standard_variables)

                if "standard_variable_ids" in fields:
                    query = query.filter(StandardVariableDB.id.in_(fields['standard_variable_ids']['value']))

                if "standard_variable_names" in fields:
                    standard_variable_names = ['(^|\s|_|\-)' + re.escape(sv_name).replace(r"\*", ".*") + '($|\s|_|\-)' for sv_name in fields['standard_variable_names']['value']]
                    query = query.filter(StandardVariableDB.name.op("~*")("|".join(standard_variable_names)))

            if "start_time" in fields or "end_time" in fields:
                # filter out datasets that have too many resources (based on provenance_id)

                if "start_time" in fields:
                    if fields["start_time"]["op"] == "gte":
                        query = query.filter(DatasetDB.temporal_coverage_start >= fields["start_time"]['value'])
                    elif fields["start_time"]["op"] == "gt":
                        query = query.filter(DatasetDB.temporal_coverage_start > fields["start_time"]['value'])
                    elif fields["start_time"]["op"] == "lte":
                        query = query.filter(DatasetDB.temporal_coverage_start <= fields["start_time"]['value'])
                    elif fields["start_time"]["op"] == "lt":
                        query = query.filter(DatasetDB.temporal_coverage_start < fields["start_time"]['value'])
                    # if in json metadata, but hard to index this way value
                    # elif fields["start_time"]["op"] == "lt":
                    #     query = query.filter(DatasetDB.json_metadata['temporal_coverage', 'start_time'].astext.cast(TIMESTAMP) < fields["start_time"]['value'])
                    else:
                        raise Exception("Invalid operator")
                if "end_time" in fields:
                    if fields["end_time"]["op"] == "gte":
                        query = query.filter(DatasetDB.temporal_coverage_end >= fields["end_time"]['value'])
                    elif fields["end_time"]["op"] == "gt":
                        query = query.filter(DatasetDB.temporal_coverage_end > fields["end_time"]['value'])
                    elif fields["end_time"]["op"] == "lte":
                        query = query.filter(DatasetDB.temporal_coverage_end <= fields["end_time"]['value'])
                    elif fields["end_time"]["op"] == "lt":
                        query = query.filter(DatasetDB.temporal_coverage_end < fields["end_time"]['value'])
                    else:
                        raise Exception("Invalid operator")

            if "spatial_coverage" in fields:
                # how do we represent global ? null or generate a value..?
                # filter out datasets with too many resources (based on provenance_id)

                if fields["spatial_coverage"]["op"] == "within" and isinstance(fields['spatial_coverage']['value'], list):
                    query = query.filter(DatasetDB.spatial_coverage.ST_Within(
                        func.ST_Makeenvelope(*fields['spatial_coverage']['value'],
                                             DatasetDB.LOCATION_SRID)))

                elif fields["spatial_coverage"]["op"] == "within" and isinstance(fields['spatial_coverage']['value'], dict):
                    query = query.filter(DatasetDB.spatial_coverage.ST_Within(
                            func.st_setsrid(
                                func.ST_geomfromgeojson(ujson.dumps(fields['spatial_coverage']['value'])),
                                DatasetDB.LOCATION_SRID))
                    )

                elif fields["spatial_coverage"]["op"] == "intersects" and isinstance(fields['spatial_coverage']['value'], list):
                    query = query.filter(DatasetDB.spatial_coverage.ST_Intersects(
                        func.ST_Makeenvelope(*fields['spatial_coverage']['value'],
                                             DatasetDB.LOCATION_SRID)))

                elif fields["spatial_coverage"]["op"] == "intersects" and isinstance(fields['spatial_coverage']['value'], dict):
                    query = query.filter(DatasetDB.spatial_coverage.ST_Intersects(
                        func.st_setsrid(
                            func.ST_geomfromgeojson(ujson.dumps(fields['spatial_coverage']['value'])),
                            DatasetDB.LOCATION_SRID))
                    )
            query = query.order_by(case([(DatasetDB.json_metadata.has_key('source_url'), 1)], else_=0).desc())
            query = query.limit(limit).offset(offset)
            print(query)
            results = query.all()

        results_json = []
        datasets_summary = {}
        for row in results:
            if row[4] is None:
                dataset_spatial_coverage = {}
            else:
                dataset_spatial_coverage = ujson.loads(row[4])

            dataset_id = str(row[0])
            dataset_name = str(row[1])
            dataset_description = str(row[2])
            dataset_metadata = row[3]
            combined_metadata = {
                "dataset_description": dataset_description,
                "dataset_spatial_coverage": dataset_spatial_coverage,
                **dataset_metadata
            }
            if dataset_id not in datasets_summary:
                datasets_summary[dataset_id] = {"dataset_id": dataset_id, "dataset_name": dataset_name, "dataset_metadata": combined_metadata}

            #
            # record = {
            #     "dataset_id": dataset_id,
            #     "dataset_name": dataset_name,
            #     "dataset_description": dataset_description,
            #     "dataset_metadata": row[3],
            #     "dataset_spatial_coverage": dataset_spatial_coverage,
            #     "resource_id": str(row[5]),
            #     "resource_name": str(row[6]),
            #     "resource_data_url": str(row[7]),
            #     "resource_metadata": row[8]
            # }
            # results_json.append(record)

        return {"result": "success", "datasets": list(datasets_summary.values())}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def find_datasets(query_definition: Dict) -> Dict:
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': f"Query definition must not be empty; received {query_definition}"})
    # parse query operators
    # search_ops = body.pop('search_operators', "and").lower()
    # sort_by = body.pop("sort_by", None)
    # assert search_ops == "or" or search_ops == "and"
    limit = int(query_definition.pop("limit", 20))
    offset = int(query_definition.pop("offset", 0))
    fields: Dict[str, dict] = {}
    for field_w_op, value in query_definition.items():
        if field_w_op.rfind("__") == -1:
            field, op = field_w_op, None
        else:
            field, op = field_w_op.split("__")
        fields[field] = {"op": op, "value": value}

    allowed_query_words = ["dataset_names", "dataset_ids", "standard_variable_ids", "standard_variable_names"]

    if len(fields) == 0:
        raise BadRequestException({'Missing search field(s)': query_definition})
    elif not all([field_name in allowed_query_words for field_name in list(fields.keys())]):
        raise BadRequestException({'InvalidQueryDefinition': f"Invalid search field(s); must be either of {allowed_query_words}"})
    if "dataset_names" in fields:
        dataset_names_op = fields["dataset_names"]["op"]
        dataset_names_value = fields["dataset_names"]["value"]

        if dataset_names_op != "in":
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'dataset_names': {dataset_names_op}"})
        if not dataset_names_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'dataset_names': {dataset_names_value}"})
        if not isinstance(dataset_names_value, list):
            raise BadRequestException({'InvalidQueryDefinition':
                f"Invalid filter value type for 'dataset_names': {dataset_names_value}; must be an array of values"})

    if "dataset_ids" in fields:
        dataset_ids_op = fields["dataset_ids"]["op"]
        dataset_ids_value = fields["dataset_ids"]["value"]

        if dataset_ids_op != "in":
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'dataset_ids': {dataset_ids_op}"})
        if not dataset_ids_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'dataset_ids': {dataset_ids_value}"})
        if not isinstance(dataset_ids_value, list):
            raise BadRequestException({'InvalidQueryException':
                f"Invalid filter value for type 'dataset_ids': {dataset_ids_value}; must be an array of values"})

    if "standard_variable_ids" in fields:
        standard_variable_ids_op = fields["standard_variable_ids"]["op"]
        standard_variable_ids_value = fields["standard_variable_ids"]["value"]

        if standard_variable_ids_op != "in":
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'standard_variable_ids_op': {standard_variable_ids_op}"})
        if not standard_variable_ids_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'standard_variable_ids': {standard_variable_ids_value}"})
        if not isinstance(standard_variable_ids_value, list):
            raise BadRequestException({'InvalidQueryDefinition':
                f"Invalid filter value type for 'standard_variable_ids': {standard_variable_ids_value}; must be an array of values"})

    if "standard_variable_names" in fields:
        standard_variable_names_op = fields["standard_variable_names"]["op"]
        standard_variable_names_value = fields["standard_variable_names"]["value"]

        if standard_variable_names_op != "in":
            raise BadRequestException({'InvalidQueryDefinition':
                f"Invalid filter operation for 'standard_variable_names_op': {standard_variable_names_op}"})
        if not standard_variable_names_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'standard_variable_names': {standard_variable_names_value}"})
        if not isinstance(standard_variable_names_value, list):
            raise BadRequestException({'InvalidQueryDefinition':
                f"Invalid filter value type for 'standard_variable_names': {standard_variable_names_value}; must be an array of values"})

    # execute the query
    try:
        with session_scope() as session:
            query = session.query(DatasetDB.id, DatasetDB.name, DatasetDB.description, DatasetDB.json_metadata).distinct()
            if "dataset_names" in fields:
                dataset_names = ['(^|\s|_|\-)' + re.escape(dataset_name).replace(r"\*", ".*") + '($|\s|_|\-)' for dataset_name in fields['dataset_names']['value']]

                query = query.filter(DatasetDB.name.op("~*")("|".join(dataset_names)))

            if "dataset_ids" in fields:
                query = query.filter(DatasetDB.id.in_(fields['dataset_ids']['value']))

            if "standard_variable_ids" in fields or "standard_variable_names" in fields:

                query = query.join(DatasetDB, VariableDB.dataset) \
                    .join(StandardVariableDB, VariableDB.standard_variables)

                if "standard_variable_ids" in fields:
                    query = query.filter(StandardVariableDB.id.in_(fields['standard_variable_ids']['value']))

                if "standard_variable_names" in fields:
                    standard_variable_names = ['(^|\s|_|\-)' + re.escape(sv_name).replace(r"\*", ".*") + '($|\s|_|\-)' for sv_name in fields['standard_variable_names']['value']]
                    query = query.filter(StandardVariableDB.name.op("~*")("|".join(standard_variable_names)))

            query = query.order_by(case([(DatasetDB.json_metadata.has_key('source_url'), 1)], else_=0).desc())

            query = query.limit(limit).offset(offset)
            print(query)
            results = query.all()

        results_json = []
        for row in results:
            record = {
                "dataset_id": str(row[0]),
                "dataset_name": str(row[1]),
                "dataset_description": str(row[2]),
                "dataset_metadata": row[3],
            }
            results_json.append(record)

        return {"result": "success", "datasets": results_json}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def find_standard_variables(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException({'Invalid query definition': query_definition})


    limit = int(query_definition.pop("limit", 100))
    offset = int(query_definition.pop("offset", 0))
    fields: Dict[str, dict] = {}
    for field_w_op, value in query_definition.items():
        if field_w_op.rfind("__") == -1:
            field, op = field_w_op, None
        else:
            field, op = field_w_op.split("__")
        fields[field] = {"op": op, "value": value}

    allowed_query_words = ["name", "ontology", "uri"]

    if len(fields) == 0:
        raise BadRequestException({'InvalidQueryDefinition': f"Query definition must not be empty; received {query_definition}"})
    elif not all([field_name in allowed_query_words for field_name in list(fields.keys())]):
        raise BadRequestException({'InvalidQueryDefinition': f"Invalid search field(s); must be either of {allowed_query_words}"})

    else:
        if "name" in fields:
            name_op = fields["name"]["op"]
            name_value = fields["name"]["value"]

            if name_op != "in":
                raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'name': {name_op}"})
            if not name_value:
                raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'name': {name_value}"})
            if not isinstance(name_value, list):
                raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value type for 'name': {name_value}; must be an array of values"})

        if "ontology" in fields:
            ontology_op = fields["ontology"]["op"]
            ontology_value = fields["ontology"]["value"]

            if ontology_op != "in":
                raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'ontology': {ontology_op}"})
            if not ontology_value:
                raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'ontology': {ontology_value}"})
            if not isinstance(ontology_value, list):
                raise BadRequestException({'InvalidQueryDefinition':
                    f"Invalid filter value type for 'ontology': {ontology_value}; must be an array of values"})

        if "uri" in fields:
            uri_op = fields["uri"]["op"]
            uri_value = fields["uri"]["value"]

            if uri_op != "in":
                raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operations for 'uri': {uri_op}"})
            if not uri_value:
                raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'uri': {uri_value}"})
            if not isinstance(uri_value, list):
                raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value type for 'uri': {uri_value}; must be an array of values"})

        # if "resource_variables" in fields:
        #     resource_variables_op = fields["resource_variables"]["op"]
        #     resource_variables_value = fields["resource_variables"]["value"]
        #
        #     if resource_variables_op != "in":
        #         raise BadRequestException({'InvalidQueryDefinition':f"Invalid filter operations for 'resource_variables': {resource_variables_op}"})
        #     if not resource_variables_value:
        #         raise BadRequestException({'InvalidQueryDefinition':f"Invalid filter value for 'resource_variables': {resource_variables_value}"})
        #     if not isinstance(resource_variables_value, list):
        #         raise BadRequestException({'InvalidQueryDefinition':
        #             f"Invalid filter value type for 'resource_variables': {resource_variables_value}; must be an array of values"})

        try:
            with session_scope() as session:
                query = session.query(StandardVariableDB).distinct()
                if "name" in fields:
                    standard_variable_names = ['(^|\s|_|\-)' + re.escape(name).replace(r"\*", ".*") + '($|\s|_|\-)' for name in fields['name']['value']]

                    query = query.filter(StandardVariableDB.name.op("~*")("|".join(standard_variable_names)))
                if "ontology" in fields:
                    query = query.filter(StandardVariableDB.ontology.in_(fields["ontology"]["value"]))
                if "uri" in fields:
                    query = query.filter(StandardVariableDB.uri.in_(fields["uri"]["value"]))
                # if "resource_variables" in fields:
                #     query

                query = query.limit(limit)
                print(query)
                results = query.all()

            results_json = [standard_variable.to_dict() for standard_variable in results]
            return {"result": "success", "standard_variables": results_json}

        except Exception as e:
            traceback.print_exc(file=sys.stdout)
            raise InternalServerException(e)


def dataset_standard_variables(query_definition: dict) -> dict:
    
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': query_definition})
    elif "dataset_id" not in query_definition:
        raise BadRequestException({'InvalidQueryDefinition': "Missing required key 'dataset_id'"})

    dataset_record_id = query_definition['dataset_id']

    try:
        uuid.UUID(str(dataset_record_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException({'InvalidQueryDefinition': f"'dataset_id' value must be a valid UUID v4; received {dataset_record_id}"})

    try:
        with session_scope() as session:
            query = session.query(DatasetDB.id, DatasetDB.name, StandardVariableDB.id, StandardVariableDB.name,
                                  StandardVariableDB.uri).distinct() \
                .join(VariableDB, DatasetDB.variables) \
                .join(StandardVariableDB, VariableDB.standard_variables) \
                .filter(DatasetDB.id == dataset_record_id)

            print(query)
            results = query.all()
            results_json = {
                "dataset_id": None,
                "dataset_name": None,
                "standard_variables": []
            }

            for row in results:
                # This is overwriting dataset_id and dataset_name but it's ok since those should be unique anyways
                results_json["dataset_id"] = str(row[0])
                results_json["dataset_name"] = str(row[1])
                results_json["standard_variables"].append(
                    {
                        "standard_variable_id": str(row[2]),
                        "standard_variable_name": str(row[3]),
                        "standard_variable_uri": str(row[4])
                    }
                )

            return {"result": "success", "dataset": results_json}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def dataset_variables(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': query_definition})
    elif "dataset_id" not in query_definition:
        raise BadRequestException({'InvalidQueryDefinition': "Missing required key 'dataset_id'"})

    dataset_record_id = query_definition['dataset_id']

    try:
        uuid.UUID(str(dataset_record_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'dataset_id' value must be a valid UUID v4; received {dataset_record_id}"})

    try:
        with session_scope() as session:
            query = session.query(VariableDB.id, VariableDB.name, VariableDB.json_metadata,
                                  StandardVariableDB.id, StandardVariableDB.name, StandardVariableDB.ontology,
                                  StandardVariableDB.uri, StandardVariableDB.description) \
                .join(VariableDB, DatasetDB.variables) \
                .outerjoin(StandardVariableDB, VariableDB.standard_variables) \
                .filter(VariableDB.dataset_id == dataset_record_id)

            print(query)
            results = query.all()

            variable_ids_results = {}

            for row in results:
                variable_id = str(row[0])

                if variable_id in variable_ids_results:
                    record_json = variable_ids_results[variable_id]
                else:
                    record_json = {
                        "variable_id": variable_id,
                        "variable_name": str(row[1]),
                        "dataset_id": dataset_record_id,
                        "variable_metadata": row[2],
                        "standard_variables": []
                    }

                if row[3] is not None and row[4] is not None:
                    record_json["standard_variables"].append({
                        "standard_variable_id": str(row[3]),
                        "standard_variable_name": str(row[4]),
                        "standard_variable_ontology": str(row[5]),
                        "standard_variable_uri": str(row[6]),
                        "standard_variable_description": str(row[7])
                    })

                variable_ids_results[variable_id] = record_json

            variables = list(variable_ids_results.values())
            return {"result": "success", "dataset": {"variables": variables}}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def variables_standard_variables(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': f"Query definition must not be empty; received {query_definition}"})

    # parse query operators
    # search_ops = body.pop('search_operators', "and").lower()
    # sort_by = body.pop("sort_by", None)
    # assert search_ops == "or" or search_ops == "and"
    limit = int(query_definition.pop("limit", 20))
    offset = int(query_definition.pop("offset", 0))
    fields: Dict[str, dict] = {}
    for field_w_op, value in query_definition.items():
        if field_w_op.rfind("__") == -1:
            field, op = field_w_op, None
        else:
            field, op = field_w_op.split("__")
        fields[field] = {"op": op, "value": value}

    allowed_query_words = ["variable_ids"]

    if len(fields) == 0:
        raise BadRequestException({'Missing search field(s)': query_definition})
    elif not all([field_name in allowed_query_words for field_name in list(fields.keys())]):
        raise BadRequestException({'InvalidQueryDefinition': f"Invalid search field(s); must be either of {allowed_query_words}"})
    if "variable_ids" in fields:
        variable_ids_op = fields["variable_ids"]["op"]
        variable_ids_value = fields["variable_ids"]["value"]

        if variable_ids_op != "in":
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter operation for 'variable_ids': {variable_ids_op}"})
        if not variable_ids_value:
            raise BadRequestException({'InvalidQueryDefinition': f"Invalid filter value for 'variable_ids': {variable_ids_value}"})
        if not isinstance(variable_ids_value, list):
            raise BadRequestException({'InvalidQueryDefinition':
                f"Invalid filter value type for 'variable_ids': {variable_ids_value}; must be an array of values"})
        if any([not _validate_uuid(val) for val in variable_ids_value]):
            raise BadRequestException({'InvalidQueryDefinition':
                f"Invalid values for 'variable_ids': {variable_ids_value}; must be an array of uuid strings"})

    try:
        with session_scope() as session:
            query = session.query(VariableDB.id, VariableDB.name, VariableDB.dataset_id, VariableDB.json_metadata,
                                  StandardVariableDB.id, StandardVariableDB.name, StandardVariableDB.ontology,
                                  StandardVariableDB.uri, StandardVariableDB.description)\
                .distinct() \
                .outerjoin(StandardVariableDB, VariableDB.standard_variables) \
                .filter(VariableDB.id.in_(fields['variable_ids']['value']))

            print(query)
            results = query.limit(limit).all()

            variable_ids_results = {}

            for row in results:
                variable_id = str(row[0])

                if variable_id in variable_ids_results:
                    record_json = variable_ids_results[variable_id]
                else:
                    record_json = {
                        "variable_id": variable_id,
                        "variable_name": str(row[1]),
                        "dataset_id": str(row[2]),
                        "metadata": row[3],
                        "standard_variables": []
                    }

                if row[4] is not None and row[5] is not None:
                    record_json["standard_variables"].append({
                        "standard_variable_id": str(row[4]),
                        "standard_variable_name": str(row[5]),
                        "standard_variable_ontology": str(row[6]),
                        "standard_variable_uri": str(row[7]),
                        "standard_variable_description": str(row[8])
                    })

                variable_ids_results[variable_id] = record_json

            return {"result": "success", "variables": list(variable_ids_results.values())}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def dataset_temporal_coverage(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': query_definition})
    elif "dataset_id" not in query_definition:
        raise BadRequestException({'InvalidQueryDefinition': "Missing required key 'dataset_id'"})

    dataset_record_id = query_definition['dataset_id']

    select_variables_query_part = ["MIN(start_time)", "MAX(end_time)"]
    join_query_part = ["JOIN resources ON resources.id = temporal_coverage_index.indexed_id"]
    where_query_part = [f"WHERE resources.dataset_id = '{dataset_record_id}'"]

    query = "SELECT " + ", ".join(select_variables_query_part) + " "
    query += "FROM temporal_coverage_index "
    query += " ".join(join_query_part) + " "
    query +=  " ".join(where_query_part) + " "

    try:
        with session_scope() as session:
            results = session.execute(query)

            for row in results:
                min_date = str(row[0])
                max_date = str(row[1])

            return {"result": "success", "dataset": {"dataset_id": dataset_record_id, "temporal_coverage_start": min_date, "temporal_coverage_end": max_date}}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)



def dataset_resources(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': query_definition})
    elif "dataset_id" not in query_definition:
        raise BadRequestException({'InvalidQueryDefinition': "Missing required key 'dataset_id'"})

    dataset_record_id = query_definition['dataset_id']
    limit = int(query_definition.pop("limit", 200))



    try:
        uuid.UUID(str(dataset_record_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'dataset_id' value must be a valid UUID v4; received {dataset_record_id}"})

    try:
        with session_scope() as session:
            query = session.query(ResourceDB.id, ResourceDB.name, ResourceDB.data_url, ResourceDB.created_at,
                                  ResourceDB.resource_type, ResourceDB.json_metadata)
                # .join(ResourceDB, DatasetDB.resources)

            filter_definition = query_definition.get('filter')
            # assert search_ops == "or" or search_ops == "and"

            if filter_definition is not None:
                fields: Dict[str, dict] = {}
                for field_w_op, value in filter_definition.items():
                    if field_w_op.rfind("__") == -1:
                        field, op = field_w_op, None
                    else:
                        field, op = field_w_op.split("__")
                    fields[field] = {"op": op, "value": value}

                allowed_filter_words = ["spatial_coverage", "start_time", "end_time"]

                if not all([field_name in allowed_filter_words for field_name in list(fields.keys())]):
                    raise BadRequestException(
                        {
                            'InvalidQueryDefinition': f"Invalid search field(s); must be either of {allowed_filter_words}"})

                if "spatial_coverage" in fields:
                    spatial_coverage_op = fields["spatial_coverage"]["op"]
                    spatial_coverage_value = fields["spatial_coverage"]["value"]

                    allowed_filter_keywords = ["within", "intersects"]

                    if spatial_coverage_op not in allowed_filter_keywords:
                        raise BadRequestException({
                            'InvalidQueryDefinition': f"Invalid filter operation for 'spatial_coverage': {spatial_coverage_op}"})
                    if not spatial_coverage_value:
                        raise BadRequestException(
                            {
                                'InvalidQueryDefinition': f"Invalid filter value for 'spatial_coverage': {spatial_coverage_op}"})
                    # if not isinstance(spatial_coverage_value, list):
                    #     raise BadRequestException({'InvalidQueryDefinition':
                    #         f"Invalid filter value type for 'spatial_coverage': {spatial_coverage_op}; must be an numeric array with [x_min, y_min, x_max, y_max]"})

                if "start_time" in fields:
                    if fields["start_time"]['op'] is None:
                        fields["start_time"]["op"] = "gte"

                    if fields["start_time"]["op"] not in {"gte", "gt", "lte", "lt"}:
                        raise BadRequestException({'InvalidQueryDefinition':
                                                       f"Invalid filter operation: {fields['start_time']['op']}; must be on of 'gte', 'gt', 'lte', 'lt'"})

                    try:
                        fields['start_time']['value'] = datetime.strptime(fields['start_time']['value'],
                                                                          "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        help_msg = "must be formatted according to ISO8601: '%Y-%m-%dT%H:%M:%S'"
                        raise BadRequestException({'InvalidQueryDefinition':
                                                       f"Invalid datetime format for 'start_time': {fields['start_time']['value']}; {help_msg}"})

                if "end_time" in fields:
                    if fields["end_time"]['op'] is None:
                        fields["end_time"]["op"] = "gte"

                    if fields["end_time"]["op"] not in {"gte", "gt", "lte", "lt"}:
                        raise BadRequestException({'InvalidQueryDefinition':
                                                       f"Invalid filter operation: {fields['end_time']['op']}; must be on of 'gte', 'gt', 'lte', 'lt'"})
                    try:
                        fields['end_time']['value'] = datetime.strptime(fields['end_time']['value'],
                                                                        "%Y-%m-%dT%H:%M:%S")
                    except ValueError:
                        help_msg = "must be formatted according to ISO8601: '%Y-%m-%dT%H:%M:%S'"
                        raise BadRequestException({'InvalidQueryDefinition': f"Invalid datetime format for 'end_time': {fields['end_time']['value']}; {help_msg}"})

                if "start_time" in fields or "end_time" in fields:
                    # filter out datasets that have too many resources (based on provenance_id)
                    query = query.join(TemporalCoverageIndexDB, TemporalCoverageIndexDB.indexed_id == ResourceDB.id)

                    if "start_time" in fields:
                        if fields["start_time"]["op"] == "gte":
                            query = query.filter(TemporalCoverageIndexDB.start_time >= fields["start_time"]['value'])
                        elif fields["start_time"]["op"] == "gt":
                            query = query.filter(TemporalCoverageIndexDB.start_time > fields["start_time"]['value'])
                        elif fields["start_time"]["op"] == "lte":
                            query = query.filter(TemporalCoverageIndexDB.start_time <= fields["start_time"]['value'])
                        elif fields["start_time"]["op"] == "lt":
                            query = query.filter(TemporalCoverageIndexDB.start_time < fields["start_time"]['value'])
                        # if in json metadata, but hard to index this way value
                        # elif fields["start_time"]["op"] == "lt":
                        #     query = query.filter(DatasetDB.json_metadata['temporal_coverage', 'start_time'].astext.cast(TIMESTAMP) < fields["start_time"]['value'])
                        else:
                            raise Exception("Invalid operator")
                    if "end_time" in fields:
                        if fields["end_time"]["op"] == "gte":
                            query = query.filter(TemporalCoverageIndexDB.end_time >= fields["end_time"]['value'])
                        elif fields["end_time"]["op"] == "gt":
                            query = query.filter(TemporalCoverageIndexDB.end_time > fields["end_time"]['value'])
                        elif fields["end_time"]["op"] == "lte":
                            query = query.filter(TemporalCoverageIndexDB.end_time <= fields["end_time"]['value'])
                        elif fields["end_time"]["op"] == "lt":
                            query = query.filter(TemporalCoverageIndexDB.end_time < fields["end_time"]['value'])
                        else:
                            raise Exception("Invalid operator")

                if "spatial_coverage" in fields:
                    # how do we represent global ? null or generate a value..?
                    # filter out datasets with too many resources (based on provenance_id)
                    query = query.join(SpatialCoverageIndexDB, SpatialCoverageIndexDB.indexed_id == ResourceDB.id)

                    if fields["spatial_coverage"]["op"] == "within" and isinstance(fields['spatial_coverage']['value'], list):
                        query = query.filter(SpatialCoverageIndexDB.spatial_coverage.ST_Within(
                            func.ST_Makeenvelope(*fields['spatial_coverage']['value'],
                                                 SpatialCoverageIndexDB.LOCATION_SRID)))

                    elif fields["spatial_coverage"]["op"] == "within" and isinstance(fields['spatial_coverage']['value'], dict):
                        query = query.filter(SpatialCoverageIndexDB.spatial_coverage.ST_Within(
                                func.st_setsrid(
                                    func.ST_geomfromgeojson(ujson.dumps(fields['spatial_coverage']['value'])),
                                    SpatialCoverageIndexDB.LOCATION_SRID))
                        )

                    elif fields["spatial_coverage"]["op"] == "intersects" and isinstance(fields['spatial_coverage']['value'], list):
                        query = query.filter(SpatialCoverageIndexDB.spatial_coverage.ST_Intersects(
                            func.ST_Makeenvelope(*fields['spatial_coverage']['value'],
                                                 SpatialCoverageIndexDB.LOCATION_SRID)))

                    elif fields["spatial_coverage"]["op"] == "intersects" and isinstance(fields['spatial_coverage']['value'], dict):
                        query = query.filter(SpatialCoverageIndexDB.spatial_coverage.ST_Intersects(
                            func.st_setsrid(
                                func.ST_geomfromgeojson(ujson.dumps(fields['spatial_coverage']['value'])),
                                SpatialCoverageIndexDB.LOCATION_SRID))
                        )


            ###################################3
            query = query.filter(ResourceDB.dataset_id == dataset_record_id)

            if filter_definition is not None and "end_time" in filter_definition:
                query = query.order_by(TemporalCoverageIndexDB.end_time.desc())

            query = query.limit(limit)

            print(query)
            results = query.all()
            results_json = {
                "dataset_id": dataset_record_id,
                "resources": []
            }

            for row in results:
                # This is overwriting dataset_id and dataset_name but it's ok since those should be unique anyways
                results_json["dataset_id"] = dataset_record_id
                results_json["resources"].append(
                    {
                        "resource_id": str(row[0]),
                        "resource_name": str(row[1]),
                        "resource_data_url": str(row[2]),
                        "resource_created_at": str(row[3]).split(".")[0],
                        "resource_type": str(row[4]),
                        "resource_metadata": row[5]
                    }
                )

            return {"result": "success", "dataset": results_json, "dataset_id": dataset_record_id, "resources": results_json["resources"]}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def get_dataset_info(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': query_definition})
    elif "dataset_id" not in query_definition:
        raise BadRequestException({'InvalidQueryDefinition': "Missing required key 'dataset_id'"})

    dataset_id = query_definition['dataset_id']

    try:
        uuid.UUID(str(dataset_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'dataset_id' value must be a valid UUID v4; received {dataset_id}"})

    try:
        with session_scope() as session:
            record = {}
            dataset_db_record = Dataset.find_by_record_id(dataset_id, session)
            if dataset_db_record is not None:
                record["dataset_id"] = str(dataset_db_record.id)
                record["name"] = dataset_db_record.name
                record["description"] = dataset_db_record.description
                record["metadata"] = dataset_db_record.json_metadata
                record["created_at"] = str(dataset_db_record.created_at).split(".")[0]
                if dataset_db_record.spatial_coverage_geojson is not None:
                    record["metadata"]["spatial_coverage"] = ujson.loads(dataset_db_record.spatial_coverage_geojson)
                else:
                    record["metadata"]["spatial_coverage"] = {}

            return record

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)
    

def get_resource_info(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': query_definition})
    elif "resource_id" not in query_definition:
        raise BadRequestException({'InvalidQueryDefinition': "Missing required key 'resource_id'"})

    resource_id = query_definition['resource_id']

    try:
        uuid.UUID(str(resource_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'resource_id' value must be a valid UUID v4; received {resource_id}"})

    try:
        with session_scope() as session:
            record = {}
            resource_db_record = Resource.find_by_record_id(resource_id, session)

            if resource_db_record is not None:
                record["resource_id"] = str(resource_db_record.id)
                record["name"] = resource_db_record.name
                record["dataset_id"] = str(resource_db_record.dataset_id)
                record["resource_type"] = resource_db_record.resource_type
                record["data_url"] = resource_db_record.data_url
                record["metadata"] = resource_db_record.json_metadata
                record["created_at"] = str(resource_db_record.created_at).split(".")[0]

            return record

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def get_variable_info(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': query_definition})
    elif "variable_id" not in query_definition:
        raise BadRequestException({'InvalidQueryDefinition': "Missing required key 'variable_id'"})

    variable_id = query_definition['variable_id']

    try:
        uuid.UUID(str(variable_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'variable_id' value must be a valid UUID v4; received {variable_id}"})

    try:
        with session_scope() as session:
            record = {}

            query = VariableDB
            variable_db_record = Variable.find_by_record_id(variable_id, session)

            if variable_db_record is not None:
                record["variable_id"] = str(variable_db_record.id)
                record["name"] = variable_db_record.name
                record["dataset_id"] = str(variable_db_record.dataset_id)
                record["metadata"] = variable_db_record.json_metadata

            return record

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def get_standard_variable_info(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException({'InvalidQueryDefinition': query_definition})
    elif "standard_variable_id" not in query_definition:
        raise BadRequestException({'InvalidQueryDefinition': "Missing required key 'standard_variable_id'"})

    standard_variable_id = query_definition['standard_variable_id']

    try:
        uuid.UUID(str(standard_variable_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'standard_variable_id' value must be a valid UUID v4; received {standard_variable_id}"})

    try:
        with session_scope() as session:
            record = {}
            standard_variable_db_record = StandardVariable.find_by_record_id(standard_variable_id, session)

            if standard_variable_db_record is not None:
                record["standard_variable_id"] = str(standard_variable_db_record.id)
                record["name"] = standard_variable_db_record.name
                record["ontology"] = standard_variable_db_record.ontology
                record["uri"] = standard_variable_db_record.uri
                record["description"] = standard_variable_db_record.description

            return record

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def search_datasets(query_definition: dict) -> dict:
    if len(query_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {query_definition}"})
        # parse query operators
        # search_ops = body.pop('search_operators', "and").lower()
        # sort_by = body.pop("sort_by", None)
        # assert search_ops == "or" or search_ops == "and"
    limit = int(query_definition.pop("limit", 500))
    field_names = query_definition.keys()

    allowed_query_words = frozenset(["search_query", "provenance_id"])

    if not all([field_name in allowed_query_words for field_name in list(query_definition.keys())]):
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Invalid search field(s); must be either of {allowed_query_words}"})

    search_query = query_definition.get("search_query")
    if not isinstance(search_query, list):
        raise BadRequestException({'InvalidQueryDefinition':
                                           f"Invalid filter value type for 'search_query': {search_query}; must be an array of values"})

    provenance_id = query_definition.get("provenance_id")

    if provenance_id is not None:
        try:
            uuid.UUID(str(provenance_id))
            # assert(uuid_val.version == 4)
        except ValueError:
            raise BadRequestException(
                {'InvalidQueryDefinition': f"'provenance_id' value must be a valid UUID v4; received {provenance_id}"})

        # execute the query
    try:
        with session_scope() as session:

            # Get Dataset

            datasets_query = _generate_select_datasets_query(provenance_id=provenance_id, search_query=search_query, limit=limit)
            print(datasets_query)


            # query = query.limit(limit)
            # results = query.all()
            datasets_results = session.execute(datasets_query)

            datasets_dict = {}
            for row in datasets_results:
                dataset_id = str(row[0])
                dataset_metadata = {}
                if row[3] is not None:
                    dataset_metadata = row[3]

                dataset_record = {
                    "dataset_id": dataset_id,
                    "dataset_name": str(row[1]),
                    "dataset_description": str(row[2]),
                    "dataset_metadata": dataset_metadata,
                    "variables": {}
                }

                if dataset_id not in datasets_dict:
                    datasets_dict[dataset_id] = dataset_record

            dataset_ids = list(datasets_dict.keys())
            if len(dataset_ids) > 0:
                variables_query = _generate_variable_query(dataset_ids=dataset_ids)
                print(variables_query)
                variables_results = session.execute(variables_query)

                for row in variables_results:
                    dataset_id = str(row[0])
                    variable_id = str(row[1])

                    variable_record = {
                        "variable_id": variable_id,
                        "variable_name": str(row[2]),
                        "variable_metadata": row[3],
                        "standard_variables": []
                    }

                    if variable_id not in datasets_dict[dataset_id]["variables"]:
                        datasets_dict[dataset_id]["variables"][variable_id] = variable_record

                    standard_variable_record = {
                        "standard_variable_id": str(row[4]),
                        "standard_variable_name": str(row[5]),
                        "standard_variable_uri": str(row[6]),
                    }

                    datasets_dict[dataset_id]["variables"][variable_id]["standard_variables"].append(standard_variable_record)

            results_json = []
            for dataset_id, dataset_record in datasets_dict.items():
                dataset_record["variables"] = list(dataset_record["variables"].values())
                results_json.append(dataset_record)

            return {"result": "success", "datasets": results_json}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def _generate_select_datasets_query(provenance_id=None, search_query=[], limit=20):
    select_datasets_query_part = [
        "datasets.id as dataset_id",
        "datasets.name as dataset_name",
        "datasets.description as description",
        "datasets.json_metadata as dataset_metadata"
    ]

    where_query_part = []
    order_by_query_part = []

    if provenance_id is not None:
        where_query_part.append(f"datasets.provenance_id = '{provenance_id}'")

    if search_query is not None:
        # ["a b", "c"] => "'a b' & 'c'"
        search_string = " & ".join([f"''{str(keyword)}''" for keyword in search_query])
        where_query_part.append(f"datasets.tsv @@ to_tsquery('english', '{search_string}')")
        order_by_query_part.append(f"ts_rank_cd(datasets.tsv, to_tsquery('english', '{search_string}')) DESC")

        # datasets that have 'source' field set should be displayed first
        order_by_query_part.append("(case when datasets.json_metadata -> 'source' IS NOT NULL then 1 else 0 end) DESC")

    query = "SELECT " + ", ".join(select_datasets_query_part) + " "
    query += "FROM datasets "

    if len(where_query_part) > 0:
        query += "WHERE " + " AND ".join(where_query_part) + " "

    if len(order_by_query_part) > 0:
        query += "ORDER BY " + ", ".join(order_by_query_part) + " "

    query += f"LIMIT {limit}"

    return query


def _generate_variable_query(dataset_ids=[]):
    select_variables_query_part = [
        "variables.dataset_id as dataset_id",
        "variables.id as variable_id",
        "variables.name as variable_name",
        "variables.json_metadata as variable_metadata",
        "standard_variables.id as standard_variable_id",
        "standard_variables.name as standard_variable_name",
        "standard_variables.uri as standard_variable_uri",
    ]

    join_query_part = [
        "LEFT JOIN variables_standard_variables ON variables.id = variables_standard_variables.variable_id",
        "LEFT JOIN standard_variables ON variables_standard_variables.standard_variable_id = standard_variables.id"
    ]

    query = "SELECT " + ", ".join(select_variables_query_part) + " "
    query += "FROM variables "
    query += " ".join(join_query_part) + " "

    dataset_ids_str = ", ".join([f"'{dataset_id}'" for dataset_id in dataset_ids])
    if dataset_ids_str == '':
        query += f"WHERE variables.dataset_id in (NULL)"
    else:
        query += f"WHERE variables.dataset_id in ({dataset_ids_str})"

    return query