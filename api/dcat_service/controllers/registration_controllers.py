from typing import *
from sqlalchemy import or_, func
from dcat_service.db_models import DatasetDB, StandardVariableDB, TemporalCoverageIndexDB, SpatialCoverageIndexDB, \
    VariableDB, ResourceDB
# End for search query
import ujson
import sys
import traceback

from dcat_service.models.provenance import ProvenanceCollectionBuilder
from dcat_service.models.standard_variable import StandardVariableCollectionBuilder
from dcat_service.models.dataset import DatasetCollectionBuilder
from dcat_service.models.variable import VariableCollectionBuilder
from dcat_service.models.resource import ResourceCollectionBuilder

from dcat_service.misc.exception import BadRequestException
from dcat_service import session_scope


def register_provenance(provenance_definition: Dict) -> Dict:

    if len(provenance_definition) == 0:
        raise BadRequestException(
            {'Missing parameter or its value is empty': "provenance"})

    with session_scope() as session:
        builder = ProvenanceCollectionBuilder(session)
        builder.instantiate_provenance_arr([provenance_definition])
        builder.validate_schema()
        if len(builder.schema_validation_errors) > 0:
            raise BadRequestException(
                {"ProvenanceSchemaValidationError": builder.schema_validation_errors})
        builder.build_record_associations()
        provenance_arr = builder.persist()

    return {"provenance": provenance_arr[0]}


def register_standard_variables(standard_variable_definitions: list) -> dict:

    if len(standard_variable_definitions) == 0:
        raise BadRequestException(
            {'Missing parameter or its value is empty': "standard_variables"})
    elif len(standard_variable_definitions) > 500:
        raise BadRequestException({
            'NumRecordsExceedsThresholdError':
                f"Maximum number of records per call cannot exceed 500; received {len(standard_variable_definitions)}"
        })

    with session_scope() as session:
        builder = StandardVariableCollectionBuilder(session)
        builder.instantiate_variables(standard_variable_definitions)
        builder.validate_schema()
        if len(builder.schema_validation_errors) > 0:
            raise BadRequestException(
                {"StandardVariableSchemaValidationError": builder.schema_validation_errors})
        builder.build_record_associations()
        standard_variables = builder.persist()

    return {"result": "success", "standard_variables": standard_variables}


def register_datasets(dataset_definitions: list) -> dict:
    if len(dataset_definitions) == 0:
        raise BadRequestException(
            'Missing parameter or its value is empty: "datasets"')
    elif len(dataset_definitions) > 500:
        raise BadRequestException({
            "NumRecordsExceedsThresholdError":
                f"Maximum number of records per call cannot exceed 500; received {len(dataset_definitions)}"
        })

    with session_scope() as session:
        builder = DatasetCollectionBuilder(session)
        builder.instantiate_variables(dataset_definitions)
        builder.validate_schema()
        if len(builder.schema_validation_errors) > 0:
            raise BadRequestException(
                {"DatasetSchemaValidationError": builder.schema_validation_errors})

        builder.build_record_associations()
        if len(builder.data_validation_errors) > 0:
            raise BadRequestException(
                {"DatasetDataValidationError": builder.data_validation_errors})

        datasets = builder.persist()

    return {"result": "success", "datasets": datasets}


# def update_datasets(dataset_definitions: list) -> dict:
#     if len(dataset_definitions) == 0:
#         raise BadRequestException('Missing parameter or its value is empty: "datasets"')
#     elif len(dataset_definitions) > 500:
#         raise BadRequestException({
#             "NumRecordsExceedsThresholdError":
#                 f"Maximum number of records per call cannot exceed 500; received {len(dataset_definitions)}"
#         })
#
#     with session_scope() as session:
#         builder = DatasetCollectionBuilder(session)
#         builder.instantiate_variables(dataset_definitions)
#         builder.validate_schema()
#         if len(builder.schema_validation_errors) > 0:
#             raise BadRequestException({"DatasetSchemaValidationError": builder.schema_validation_errors})
#
#         builder.build_record_associations()
#         if len(builder.data_validation_errors) > 0:
#             raise BadRequestException({"DatasetDataValidationError": builder.data_validation_errors})
#
#         datasets = builder.persist()
#
#     return {"result": "success", "datasets": datasets}


def register_variables(variable_definitions: list) -> dict:
    if len(variable_definitions) == 0:
        raise BadRequestException(
            {"Missing parameter or its value is empty": 'variables'})
    elif len(variable_definitions) > 500:
        raise BadRequestException({
            "NumRecordsExceedsThresholdError":
                f"Maximum number of records per call cannot exceed 500; received {len(variable_definitions)}"
        })

    with session_scope() as session:
        builder = VariableCollectionBuilder(session)
        builder.instantiate_variables(variable_definitions)
        builder.validate_schema()
        if len(builder.schema_validation_errors) > 0:
            raise BadRequestException(
                {"VariableSchemaValidationError": builder.schema_validation_errors})

        builder.build_record_associations()
        if len(builder.data_validation_errors) > 0:
            raise BadRequestException(
                {"DataValidationError": builder.data_validation_errors})

        variables = builder.persist()

    return {"result": "success", "variables": variables}


def register_resources(resource_definitions: list) -> dict:
    if len(resource_definitions) == 0:
        raise BadRequestException(
            {"Missing parameter or its value is empty": 'resources'})
    elif len(resource_definitions) > 500:
        raise BadRequestException({
            "NumRecordsExceedsThresholdError":
                f"Maximum number of records per call cannot exceed 500; received {len(resource_definitions)}"
        })

    with session_scope() as session:
        builder = ResourceCollectionBuilder(session)
        builder.instantiate_resources(resource_definitions)
        builder.validate_schema()
        if len(builder.schema_validation_errors) > 0:
            raise BadRequestException(
                {"VariableSchemaValidationError": builder.schema_validation_errors})

        builder.build_record_associations()
        if len(builder.data_validation_errors) > 0:
            raise BadRequestException(
                {"DataValidationError": builder.data_validation_errors})

        resources = builder.persist()

    return {"result": "success", "resources": resources}
