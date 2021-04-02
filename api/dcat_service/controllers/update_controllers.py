from typing import *

import uuid
import sys
import traceback
import json

from dcat_service import session_scope
from dcat_service.models.dataset import Dataset
from dcat_service.models.resource import Resource
from dcat_service.models.variable import Variable
from dcat_service.models.standard_variable import StandardVariable

from dcat_service.misc.exception import BadRequestException, InternalServerException
from sqlalchemy.orm.attributes import flag_modified


def update_dataset_viz_status(update_definition: Dict) -> Dict:
    if len(update_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {update_definition}"})

    if "dataset_id" not in update_definition:
        raise BadRequestException({'MissingRequiredParameter': "dataset_id"})

    if "viz_config_id" not in update_definition:
        raise BadRequestException({'MissingRequiredParameter': "viz_config_id"})

    viz_config_id = update_definition["viz_config_id"]

    dataset_id = update_definition["dataset_id"]
    try:
        uuid.UUID(str(dataset_id))
    except Exception:
        raise BadRequestException({'InvalidParameter': f"'dataset_id' must be proper uuid; received {dataset_id}"})

    with session_scope() as session:

        dataset = Dataset.find_by_record_id(dataset_id, session=session)

        if viz_config_id not in dataset.json_metadata:
            raise BadRequestException({'InvalidParameter': f"Dataset {dataset_id} does not have viz_config with id {viz_config_id}"})


        # update dataset metadata
        dataset.json_metadata[viz_config_id]["visualized"] = True
        flag_modified(dataset, "json_metadata")

    return {"success": True}


def update_dataset_viz_config(update_definition: Dict) -> Dict:
    if len(update_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {update_definition}"})

    if "dataset_id" not in update_definition:
        raise BadRequestException({'MissingRequiredParameter': "dataset_id"})

    if "viz_config_id" not in update_definition:
        raise BadRequestException({'MissingRequiredParameter': "viz_config_id"})

    if "$set" not in update_definition:
        raise BadRequestException({'MissingRequiredParameter': "$set"})

    viz_config_id = update_definition["viz_config_id"]
    dataset_id = update_definition["dataset_id"]
    new_viz_config_vals = update_definition["$set"]

    try:
        uuid.UUID(str(dataset_id))
    except Exception:
        raise BadRequestException({'InvalidParameter': f"'dataset_id' must be proper uuid; received {dataset_id}"})

    with session_scope() as session:

        dataset = Dataset.find_by_record_id(dataset_id, session=session)

        if viz_config_id not in dataset.json_metadata:
            raise BadRequestException(
                {'InvalidParameter': f"Dataset {dataset_id} does not have viz_config with id {viz_config_id}"})

        # update dataset metadata
        dataset.json_metadata[viz_config_id].update(new_viz_config_vals)
        flag_modified(dataset, "json_metadata")

    return {"success": True}


def update_dataset(update_definition: Dict) -> Dict:
    if len(update_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {update_definition}"})

    if "dataset_id" not in update_definition:
        raise BadRequestException({'MissingRequiredParameter': "dataset_id"})

    dataset_id = update_definition["dataset_id"]
    try:
        uuid.UUID(str(dataset_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'dataset_id' value must be a valid UUID v4; received {dataset_id}"})

    name = update_definition.get("name")

    description = update_definition.get("description")
    json_metadata = update_definition.get('metadata')

    if json_metadata is not None and not isinstance(json_metadata, dict):
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'metadata' value must be a JSON object; received {json_metadata}"})
    
    changes = {}
    try:
        with session_scope() as session:
            dataset = Dataset.find_by_record_id(dataset_id, session)
            update_query_arr = ['UPDATE datasets SET']
            set_query_part_arr = []

            if name is not None:
                # dataset.name
                current_name = dataset.name
                # dataset.name = name
                set_query_part_arr.append(f"name = '{name}'")
                changes["name"] = _get_change_record(current_name, name)
                
            if description is not None:
                current_description = dataset.description
                set_query_part_arr.append(f"description = '{description}'")
                changes["description"] = _get_change_record(current_description, description)

            if json_metadata is not None and isinstance(json_metadata, dict):
                metadata = dataset.json_metadata
                if metadata is None:
                    metadata = {}

                current_metadata = {k: v for k, v in metadata.items()}
                metadata.update(json_metadata)

                keys_to_delete = []
                for k, v in metadata.items():
                    if v is None:
                        keys_to_delete.append(k)

                for k in keys_to_delete:
                    del metadata[k]

                set_query_part_arr.append(f"json_metadata = $${json.dumps(metadata)}$$::json")

                changes["metadata"] = _get_change_record(current_metadata, metadata)

            if len(set_query_part_arr) > 0:
                set_query_part = ', '.join(set_query_part_arr)
                update_query_arr.append(set_query_part)
                update_query_arr.append(f"WHERE datasets.id = '{dataset_id}'")
                update_query = " ".join(update_query_arr)

                print(update_query)
                session.execute(update_query)

        return {"success": True, "dataset_id": dataset_id, "changes": changes}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def update_resource(update_definition: Dict) -> Dict:
    if len(update_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {update_definition}"})

    if "resource_id" not in update_definition:
        raise BadRequestException({'MissingRequiredParameter': "resource_id"})

    resource_id = update_definition["resource_id"]
    try:
        uuid.UUID(str(resource_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'dataset_id' value must be a valid UUID v4; received {resource_id}"})

    name = update_definition.get("name")
    json_metadata = update_definition.get('metadata')
    resource_type = update_definition.get('resource_type')
    data_url = update_definition.get('data_url')

    if json_metadata is not None and not isinstance(json_metadata, dict):
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'metadata' value must be a JSON object; received {json_metadata}"})

    changes = {}

    try:
        with session_scope() as session:
            resource = Resource.find_by_record_id(resource_id, session)
            update_query_arr = ['UPDATE resources SET']
            set_query_part_arr = []

            if name is not None:
                current_name = resource.name
                set_query_part_arr.append(f"name = '{name}'")

                changes["name"] = _get_change_record(current_name, name)

            if resource_type is not None:
                current_resource_type = resource.resource_type
                set_query_part_arr.append(f"resource_type = '{resource_type}'")

                changes["resource_type"] = _get_change_record(current_resource_type, resource_type)

            if data_url is not None:
                current_data_url = resource.data_url
                set_query_part_arr.append(f"data_url = '{data_url}'")

                changes["data_url"] = _get_change_record(current_data_url, data_url)
                
            if json_metadata is not None and isinstance(json_metadata, dict):
                metadata = resource.json_metadata
                if metadata is None:
                    metadata = {}

                current_metadata = {k: v for k, v in metadata.items()}
                metadata.update(json_metadata)

                keys_to_delete = []
                for k, v in metadata.items():
                    if v is None:
                        keys_to_delete.append(k)

                for k in keys_to_delete:
                    del metadata[k]

                set_query_part_arr.append(f"json_metadata = $${json.dumps(metadata)}$$::json")
                changes["metadata"] = _get_change_record(current_metadata, metadata)

            if len(set_query_part_arr) > 0:
                set_query_part = ', '.join(set_query_part_arr)
                update_query_arr.append(set_query_part)
                update_query_arr.append(f"WHERE resources.id = '{resource_id}'")
                update_query = " ".join(update_query_arr)

                print(update_query)
                session.execute(update_query)

        return {"success": True, "resource_id": resource_id, "changes": changes}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def update_variable(update_definition: Dict) -> Dict:
    if len(update_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {update_definition}"})

    if "variable_id" not in update_definition:
        raise BadRequestException({'MissingRequiredParameter': "variable_id"})

    variable_id = update_definition["variable_id"]
    try:
        uuid.UUID(str(variable_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'dataset_id' value must be a valid UUID v4; received {variable_id}"})

    name = update_definition.get("name")
    json_metadata = update_definition.get('metadata')

    if json_metadata is not None and not isinstance(json_metadata, dict):
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'metadata' value must be a JSON object; received {json_metadata}"})

    changes = {}

    try:
        with session_scope() as session:
            variable = Variable.find_by_record_id(variable_id, session)
            update_query_arr = ['UPDATE variables SET']
            set_query_part_arr = []

            if name is not None:
                current_name = variable.name
                set_query_part_arr.append(f"name = '{name}'")
                changes["name"] = _get_change_record(current_name, name)

            if json_metadata is not None and isinstance(json_metadata, dict):
                metadata = variable.json_metadata
                if metadata is None:
                    metadata = {}

                current_metadata = {k: v for k, v in metadata.items()}
                metadata.update(json_metadata)

                keys_to_delete = []
                for k, v in metadata.items():
                    if v is None:
                        keys_to_delete.append(k)

                for k in keys_to_delete:
                    del metadata[k]

                set_query_part_arr.append(f"json_metadata = $${json.dumps(metadata)}$$::json")
                changes["metadata"] = _get_change_record(current_metadata, metadata)

            if len(set_query_part_arr) > 0:
                set_query_part = ', '.join(set_query_part_arr)
                update_query_arr.append(set_query_part)
                update_query_arr.append(f"WHERE variables.id = '{variable_id}'")
                update_query = " ".join(update_query_arr)

                print(update_query)
                session.execute(update_query)

        return {"success": True, "variable_id": variable_id, "changes": changes}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def update_standard_variable(update_definition: Dict) -> Dict:
    if len(update_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {update_definition}"})

    if "standard_variable_id" not in update_definition:
        raise BadRequestException({'MissingRequiredParameter': "standard_variable_id"})

    standard_variable_id = update_definition["standard_variable_id"]
    try:
        uuid.UUID(str(standard_variable_id))
        # assert(uuid_val.version == 4)
    except ValueError:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"'dataset_id' value must be a valid UUID v4; received {standard_variable_id}"})

    name = update_definition.get("name")
    ontology = update_definition.get("ontology")
    uri = update_definition.get("uri")
    description = update_definition.get("description")

    changes = {}

    try:
        with session_scope() as session:
            standard_variable = StandardVariable.find_by_record_id(standard_variable_id, session)
            update_query_arr = ['UPDATE standard_variables SET']
            set_query_part_arr = []

            if name is not None:
                current_name = standard_variable.name
                set_query_part_arr.append(f"name = '{name}'")

                changes["name"] = _get_change_record(current_name, name)

            if ontology is not None:
                current_ontology = standard_variable.ontology
                set_query_part_arr.append(f"ontology = '{ontology}'")

                changes["ontology"] = _get_change_record(current_ontology, ontology)

            if uri is not None:
                current_uri = standard_variable.uri
                set_query_part_arr.append(f"uri = '{uri}'")
                changes["uri"] = _get_change_record(current_uri, uri)

            if description is not None:
                current_description = standard_variable.description
                set_query_part_arr.append(f"description = '{description}'")
                changes["description"] = _get_change_record(current_description, ontology)

            if len(set_query_part_arr) > 0:
                set_query_part = ', '.join(set_query_part_arr)
                update_query_arr.append(set_query_part)
                update_query_arr.append(f"WHERE standard_variables.id = '{standard_variable_id}'")
                update_query = " ".join(update_query_arr)

                print(update_query)
                session.execute(update_query)

        return {"success": True, "standard_variable_id": standard_variable_id, "changes": changes}

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def sync_datasets_metadata() -> List[Dict]:
    responses = []
    responses.append(_update_polygon_spatial_coverage_query())
    responses.append(_update_polygon_point_coverage())
    responses.append(_update_temporal_coverage())
    responses.append(_update_resource_summary())
    responses.append(_update_variables_list())
    responses.append(_update_standard_variables_list())

    return responses


def _update_polygon_spatial_coverage_query():
    with session_scope() as session:
        update_polygon_spatial_coverage_query = """
            with spatial_coverage as (
    	            select 
    	                dataset_id, 
    	                ST_MakePolygon(ST_ExteriorRing(ST_union(ST_Simplify(spatial_coverage_index.spatial_coverage,0.5)))) as dataset_spatial_coverage 
    	            from resources
    	            inner join spatial_coverage_index on resources.id = spatial_coverage_index.indexed_id 
    	            where st_geometrytype(spatial_coverage_index.spatial_coverage) not like '%Point'

    	        --and resources.is_queryable is TRUE
    	        group by dataset_id
            )
            update datasets 
            SET spatial_coverage = sc.dataset_spatial_coverage
            from spatial_coverage sc
            where sc.dataset_id = datasets.id"""

        try:
            session.execute(update_polygon_spatial_coverage_query)
            return {"updated_polygon_spatial_coverage": True}
        except Exception as e:
            return {"updated_polygon_spatial_coverage": False, "error": e}


def _update_polygon_point_coverage():
    with session_scope() as session:
        query = """
                with spatial_coverage as (
        	        select 
        	            dataset_id, 
        	            ST_union(ST_Simplify(st_buffer(spatial_coverage_index.spatial_coverage, 0.5), 0.5)) as dataset_spatial_coverage 
        	        from resources
        	        inner join spatial_coverage_index on resources.id = spatial_coverage_index.indexed_id 
        	        --and resources.is_queryable is TRUE
        	        where st_geometrytype(spatial_coverage_index.spatial_coverage) like '%Point'
        	        group by dataset_id
                )
                update datasets
                SET spatial_coverage = sc.dataset_spatial_coverage
                from spatial_coverage sc 
                where sc.dataset_id = datasets.id"""

        try:
            session.execute(query)
            return {"updated_point_spatial_coverage": True}
        except Exception as e:
            return {"updated_point_spatial_coverage": False, "error": e}


def _update_temporal_coverage():
    with session_scope() as session:
        query = """
                WITH temporal_coverage as (
        	        select resources.dataset_id, 
        	            min(temporal_coverage_index.start_time) as start_time, 
        	            max(temporal_coverage_index.end_time) as end_time 
        	        from temporal_coverage_index 
        	        JOIN resources on resources.id = temporal_coverage_index.indexed_id 
        	        --and resources.is_queryable is TRUE
        	        group by resources.dataset_id
                )
                update datasets 
                SET temporal_coverage_start = tc.start_time,
                    temporal_coverage_end = tc.end_time,
                    json_metadata = datasets.json_metadata ||
        	        jsonb_build_object(
        		        'temporal_coverage',
        			    jsonb_build_object(
        				    'start_time', tc.start_time,
        				    'end_time', tc.end_time
        		        )
        	        )
                from temporal_coverage tc 
                where datasets.id = tc.dataset_id"""

        try:
            session.execute(query)
            return {"updated_temporal_coverage": True}
        except Exception as e:
            return {"updated_temporal_coverage": False, "error": e}


def _update_resource_summary():
    with session_scope() as session:
        query = """
                WITH resource_summary as (
        	        select dataset_id, 
        	            count(id) as resource_count 
        	        from resources 
        	        group by dataset_id
                )
                update datasets 
                SET json_metadata = jsonb_build_object(
        	        'resource_count', rs.resource_count
                ) || datasets.json_metadata
                from resource_summary rs
                where rs.dataset_id = datasets.id"""

        try:
            session.execute(query)
            return {"updated_resource_summary": True}
        except Exception as e:
            return {"updated_resource_summary": False, "error": e}


def _update_variables_list():
    with session_scope() as session:
        query = """
                with variables_summary as (
        	        select variables.dataset_id as dataset_id, 
        	            string_agg(variables.name, ',') as variables_list 
        	        from variables 
        	        group by dataset_id
                )
                UPDATE datasets
                set variables_list = variables_summary.variables_list
                from variables_summary 
                where datasets.id = variables_summary.dataset_id"""

        try:
            session.execute(query)
            return {"updated_variables_list": True}
        except Exception as e:
            return {"updated_variables_list": False, "error": e}


def _update_standard_variables_list():
    with session_scope() as session:
        query = """
                with standard_variables_summary as (
        	        select variables.dataset_id as dataset_id, 
        	            string_agg(standard_variables.name, ',') as standard_variables_list 
        	        from variables 
        	        join variables_standard_variables on variables.id = variables_standard_variables.variable_id
        	        join standard_variables on standard_variables.id = variables_standard_variables.standard_variable_id
        	        group by dataset_id
                )
                UPDATE datasets
                set standard_variables_list = standard_variables_summary.standard_variables_list
                from standard_variables_summary 
                where datasets.id = standard_variables_summary.dataset_id"""

        try:
            session.execute(query)
            return {"updated_standard_variables_list": True}
        except Exception as e:
            return {"updated_standard_variables_list": False, "error": e}


def _get_change_record(old_value, new_value):
    return {"from": old_value, "to": new_value}
