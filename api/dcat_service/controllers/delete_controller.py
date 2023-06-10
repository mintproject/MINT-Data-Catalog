from typing import *

import uuid
import sys
import traceback

from dcat_service import session_scope
from dcat_service.models.dataset import Dataset
from dcat_service.models.resource import Resource

from dcat_service.misc.exception import BadRequestException, InternalServerException


def delete_resource(delete_definition: Dict) -> Dict:
    if len(delete_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {delete_definition}"})

    if "provenance_id" not in delete_definition:
        raise BadRequestException(
            {'MissingRequiredParameter': "provenance_id"})

    if "resource_id" not in delete_definition:
        raise BadRequestException({'MissingRequiredParameter': "resource_id"})

    provenance_id = delete_definition["provenance_id"]
    resource_id = delete_definition["resource_id"]

    try:
        uuid.UUID(str(provenance_id))
    except Exception:
        raise BadRequestException(
            {'InvalidParameter': f"'provenance_id' must be proper uuid; received {provenance_id}"})

    try:
        uuid.UUID(str(resource_id))
    except Exception:
        raise BadRequestException(
            {'InvalidParameter': f"'resource_id' must be proper uuid; received {resource_id}"})

    with session_scope() as session:
        resource = Resource.find_by_record_id(resource_id, session)

        if resource is None:
            raise BadRequestException(
                {'InvalidParameter': f"'Resource does not exist: '{str(resource_id)}'"})

        elif str(resource.provenance_id) != str(provenance_id):
            raise BadRequestException(
                {'InvalidParameter': f"provenance_id '{str(provenance_id)}' does not match"})

        else:

            session.execute(
                f"DELETE FROM spatial_coverage_index WHERE indexed_id = '{str(resource_id)}'")
            session.execute(
                f"DELETE FROM temporal_coverage_index WHERE indexed_id = '{str(resource_id)}'")
            session.execute(
                f"DELETE FROM resources_variables WHERE resource_id = '{str(resource_id)}'")
            session.execute(
                f"DELETE FROM resources WHERE id = '{str(resource_id)}'")

            return {"result": "success"}


def delete_dataset(delete_definition: Dict) -> Dict:
    if len(delete_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {delete_definition}"})

    if "provenance_id" not in delete_definition:
        raise BadRequestException(
            {'MissingRequiredParameter': "provenance_id"})

    if "dataset_id" not in delete_definition:
        raise BadRequestException({'MissingRequiredParameter': "dataset_id"})

    provenance_id = delete_definition["provenance_id"]
    dataset_id = delete_definition["dataset_id"]

    try:
        uuid.UUID(str(provenance_id))
    except Exception:
        raise BadRequestException(
            {'InvalidParameter': f"'provenance_id' must be proper uuid; received {provenance_id}"})

    try:
        uuid.UUID(str(dataset_id))
    except Exception:
        raise BadRequestException(
            {'InvalidParameter': f"'dataset_id' must be proper uuid; received {dataset_id}"})

    with session_scope() as session:
        dataset = Dataset.find_by_record_id(dataset_id, session)

        if dataset is None:
            raise BadRequestException(
                {'InvalidParameter': f"'Dataset does not exist: '{str(dataset_id)}'"})

        elif str(dataset.provenance_id) != str(provenance_id):
            raise BadRequestException(
                {'InvalidParameter': f"provenance_id '{str(provenance_id)}' does not match"})

        else:
            # create temp table to hold variable_ids that need to be deleted for variables, resources_variables, and
            # variables_standard_variables tables
            session.execute("DROP TABLE IF EXISTS delete_variables")
            session.execute(
                f"CREATE TEMPORARY TABLE delete_variables AS SELECT variables.id AS variable_id FROM variables WHERE dataset_id = '{dataset_id}'")
            session.execute(
                "CREATE index idx_variable_id ON delete_variables (variable_id)")

            # create temp table to hold resource_ids that need to be deleted for resources, spatial_coverage_index,
            # and temporal_coverage_index tables
            session.execute("DROP TABLE IF EXISTS delete_resources")
            session.execute(
                f"CREATE TEMPORARY TABLE delete_resources AS SELECT resources.id AS resource_id FROM resources WHERE dataset_id = '{dataset_id}'")
            session.execute(
                "CREATE index idx_resource_id ON delete_resources (resource_id)")

            # Delete variables_standard_variables
            session.execute(
                "DELETE FROM variables_standard_variables USING delete_variables WHERE variables_standard_variables.variable_id = delete_variables.variable_id")

            # Delete resources_variables
            session.execute(
                "DELETE FROM resources_variables USING delete_variables WHERE resources_variables.variable_id = delete_variables.variable_id")

            # Delete variables
            session.execute(
                f"DELETE FROM variables WHERE dataset_id = '{str(dataset_id)}'")

            # Delete temporal_coverage_index
            session.execute(
                "DELETE FROM temporal_coverage_index USING delete_resources WHERE temporal_coverage_index.indexed_id = delete_resources.resource_id")

            # Delete spatial_coverage_index
            session.execute(
                "DELETE FROM spatial_coverage_index USING delete_resources WHERE spatial_coverage_index.indexed_id = delete_resources.resource_id")

            # Delete resources
            session.execute(
                f"DELETE FROM resources WHERE dataset_id = '{str(dataset_id)}'")

            # Delete dataset
            session.execute(
                f"DELETE FROM datasets WHERE id = '{str(dataset_id)}'")

            return {"result": "success"}
