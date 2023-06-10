from typing import *
from dcat_service.db_models import ResourceDB, TemporalCoverageIndexDB, SpatialCoverageIndexDB, Base
from dcat_service.models.dataset import Dataset
from dcat_service.models.variable import Variable
from dcat_service.models.provenance import Provenance
from dcat_service.misc.validation_result import ValidationResult
from dcat_service.misc.validator import Validator, ValidateNotEmpty, ValidatorRunner, ValidateProperUUID, \
    ValidateTemporalCoverage, ValidateSpatialCoverage, ValidateIsList

from dcat_service import session_scope
from sqlalchemy import bindparam, Table, func
from sqlalchemy.dialects import postgresql
from uuid import uuid4


class Resource:
    def __init__(self, dataset_id: str = None, record_id: str = None, provenance_id: str = None, name: str = None,
                 data_url: str = None, resource_type: str = None, variable_ids: List[str] = None, json_metadata: dict = None,
                 layout: dict = None, temporal_coverage: dict = None, spatial_coverage: dict = None):

        self.dataset_id = dataset_id
        self.provenance_id = provenance_id
        self.name = name
        self.record_id = record_id
        self.variable_ids = variable_ids
        self.resource_type = resource_type
        self.data_url = data_url
        self.json_metadata = json_metadata
        self.layout = layout
        self.temporal_coverage = temporal_coverage
        self.spatial_coverage = spatial_coverage

    def to_json(self):
        return {
            "dataset_id": self.dataset_id,
            "provenance_id": self.provenance_id,
            "name": self.name,
            "record_id": self.record_id,
            "variable_ids": self.variable_ids,
            "resource_type": self.resource_type,
            "data_url": self.data_url,
            "json_metadata": self.json_metadata,
            "layout": self.layout,
            "temporal_coverage": self.temporal_coverage,
            "spatial_coverage": self.spatial_coverage
        }

    def __str__(self):
        return str(self.to_json())

    @staticmethod
    def find_by_record_id(record_id: str, session: session_scope = None) -> Optional[ResourceDB]:
        if session is None:
            with session_scope() as sess:
                return sess.query(ResourceDB).filter(ResourceDB.id == record_id).first()

        else:
            return session.query(ResourceDB).filter(ResourceDB.id == record_id).first()

    @staticmethod
    def find_by_record_ids(record_ids: Iterable[str], session: session_scope = None) -> Iterable[ResourceDB]:
        if session is None:
            with session_scope() as sess:
                return sess.query(ResourceDB).filter(ResourceDB.id.in_(record_ids)).all()

        else:
            return session.query(ResourceDB).filter(ResourceDB.id.in_(record_ids)).all()

    @staticmethod
    def schema_validators() -> List[Validator]:
        return [
            ValidateNotEmpty(attribute="record_id"),
            ValidateProperUUID(attribute="record_id"),

            ValidateNotEmpty(attribute="dataset_id"),
            ValidateProperUUID(attribute="dataset_id"),

            ValidateNotEmpty(attribute="provenance_id"),
            ValidateProperUUID(attribute="provenance_id"),

            ValidateIsList(attribute="variable_ids"),
            ValidateNotEmpty(attribute="name"),
            ValidateNotEmpty(attribute="resource_type"),
            ValidateNotEmpty(attribute="data_url"),

            ValidateTemporalCoverage(
                attribute="temporal_coverage", ignore_empty_values=True),
            ValidateSpatialCoverage(
                attribute="spatial_coverage", ignore_empty_values=True)
        ]

    @staticmethod
    def from_json(resource_definition):
        json_metadata = resource_definition.get('metadata', {})
        layout = resource_definition.get('layout', {})

        record_id_candidate = resource_definition.get("record_id")
        record_id = record_id_candidate if record_id_candidate else str(
            uuid4())

        dataset_id = resource_definition.get("dataset_id")
        provenance_id = resource_definition.get("provenance_id")
        name = resource_definition.get("name")
        variable_ids = resource_definition.get("variable_ids", [])
        resource_type = resource_definition.get("resource_type")
        data_url = resource_definition.get("data_url")

        temporal_coverage = resource_definition.get(
            "metadata", {}).get("temporal_coverage")
        spatial_coverage = resource_definition.get(
            "metadata", {}).get("spatial_coverage")

        return Resource(record_id=record_id,
                        dataset_id=dataset_id,
                        provenance_id=provenance_id,
                        variable_ids=variable_ids,
                        name=name,
                        resource_type=resource_type,
                        data_url=data_url,
                        json_metadata=json_metadata,
                        layout=layout,
                        temporal_coverage=temporal_coverage,
                        spatial_coverage=spatial_coverage)


class ResourceCollectionBuilder:
    def __init__(self, session):
        self.session = session
        self.resources: List[Resource] = []
        self.schema_validation_errors: List[ValidationResult] = []
        self.data_validation_errors: List[ValidationResult] = []
        self.db_records_references = {
            "dataset_ids": set([]),
            "provenance_ids": set([]),
            "variable_ids": set([])
        }
        self.resources_variables: List[Dict] = []

    def instantiate_resources(self, resource_definitions: List[dict]):
        for resource_definition in resource_definitions:
            resource = Resource.from_json(resource_definition)

            self.db_records_references["dataset_ids"].add(resource.dataset_id)
            self.db_records_references["provenance_ids"].add(
                resource.provenance_id)
            self.db_records_references["variable_ids"].update(
                resource.variable_ids)
            self.resources = [Resource.from_json(
                resource_definition) for resource_definition in resource_definitions]

    def validate_schema(self):
        validator_runner = ValidatorRunner(
            validators=Resource.schema_validators())
        validation_results = validator_runner.run_validations(self.resources)

        validation_results_with_errors = []
        for validation_result in validation_results:
            if not validation_result.is_valid():
                validation_results_with_errors.append(validation_result)

        self.schema_validation_errors = validation_results_with_errors

    def build_record_associations(self):
        validation_results_with_errors = []

        datasets = Dataset.find_by_record_ids(
            self.db_records_references["dataset_ids"], self.session)
        provenance_arr = Provenance.find_by_record_ids(
            self.db_records_references["provenance_ids"], self.session)
        variables = Variable.find_by_record_ids(
            self.db_records_references["variable_ids"], self.session)

        valid_dataset_associations = {}
        for dataset in datasets:
            valid_dataset_associations[str(dataset.id)] = dataset

        valid_dataset_ids = set(valid_dataset_associations.keys())

        valid_provenance_associations = {}
        for provenance in provenance_arr:
            valid_provenance_associations[str(provenance.id)] = provenance

        valid_provenance_ids = set(valid_provenance_associations.keys())

        valid_variable_associations = {}
        for variable in variables:
            valid_variable_associations[str(variable.id)] = variable

        valid_variable_ids = set(valid_variable_associations.keys())

        resource_record_ids = set([])
        for resource in self.resources:
            validation_result = ValidationResult(record=resource.to_json())

            resource_record_id = str(resource.record_id)

            if resource_record_id in resource_record_ids:
                validation_result.add_error(
                    f"Duplicate record_id '{resource_record_id}' found in this batch; record_ids must be unique")
            else:
                resource_record_ids.add(resource_record_id)

            if resource.dataset_id not in valid_dataset_ids:
                validation_result.add_error(
                    f"Invalid value for 'dataset_id': {resource.dataset_id}")

            if resource.provenance_id not in valid_provenance_ids:
                validation_result.add_error(
                    f"Invalid value for 'provenance_id': {resource.provenance_id}")

            invalid_variable_ids = set(
                resource.variable_ids) - valid_variable_ids
            if len(invalid_variable_ids) > 0:
                validation_result.add_error(
                    f"Invalid value for 'variable_ids': {invalid_variable_ids}")

            if not validation_result.is_valid():
                validation_results_with_errors.append(validation_result)

        # Associate dataset
        # Associate standard_variables
        # Associate temporal_index
        # Associate spatial_index
        self.data_validation_errors = validation_results_with_errors

    def persist(self):
        resource_db_table = Table("resources", Base.metadata, autoload=True)
        insert_resources_stmt = postgresql.insert(ResourceDB).values(
            id=bindparam('record_id'),
            dataset_id=bindparam('dataset_id'),
            provenance_id=bindparam('provenance_id'),
            name=bindparam('name'),
            resource_type=bindparam('resource_type'),
            data_url=bindparam('data_url'),
            json_metadata=bindparam('json_metadata'),
            layout=bindparam('layout'),
            is_queryable=bindparam('is_queryable')
            # created_at=func.now(),
            # updated_at=func.now()
        )

        do_update_resources_stmt = insert_resources_stmt.on_conflict_do_update(
            index_elements=[ResourceDB.id],
            set_={'name': insert_resources_stmt.excluded.name,
                  'resource_type': insert_resources_stmt.excluded.resource_type,
                  'data_url': insert_resources_stmt.excluded.data_url,
                  'json_metadata': ResourceDB.json_metadata.op('||')(insert_resources_stmt.excluded.json_metadata),
                  'layout': insert_resources_stmt.excluded.layout,
                  'is_queryable': insert_resources_stmt.excluded.is_queryable
                  # 'updated_at': insert_resources_stmt.excluded.updated_at
                  }
        )

        resources_variables_table = Table(
            "resources_variables", Base.metadata, autoload=True)
        insert_resources_variables_stmt = postgresql.insert(resources_variables_table).values(
            resource_id=bindparam('resource_id'),
            variable_id=bindparam('variable_id')
        )

        # temporal_coverage_index_table = Table("temporal_coverage_index", Base.metadata, autoload=True)
        insert_temporal_coverage_index_stmt = postgresql.insert(TemporalCoverageIndexDB).values(
            indexed_type=bindparam('indexed_type'),
            indexed_id=bindparam('indexed_id'),
            start_time=bindparam('start_time'),
            end_time=bindparam('end_time')
        )
        do_update_temporal_coverage_index_stmt = insert_temporal_coverage_index_stmt.on_conflict_do_update(
            index_elements=[TemporalCoverageIndexDB.indexed_type,
                            TemporalCoverageIndexDB.indexed_id],
            set_={'start_time': insert_temporal_coverage_index_stmt.excluded.start_time,
                  'end_time': insert_temporal_coverage_index_stmt.excluded.end_time}
        )

        insert_spatial_coverage_index_stmt = postgresql.insert(SpatialCoverageIndexDB).values(
            indexed_type=bindparam('indexed_type'),
            indexed_id=bindparam('indexed_id'),
            spatial_coverage=bindparam('spatial_coverage')
        )
        do_update_spatial_coverage_index_stmt = insert_spatial_coverage_index_stmt.on_conflict_do_update(
            index_elements=[TemporalCoverageIndexDB.indexed_id],
            set_={
                'spatial_coverage': insert_spatial_coverage_index_stmt.excluded.spatial_coverage}
        )
        # do_updated_resources_standard_resources_stm = insert_resources_standard_resources_stm.

        resource_json_records = []
        resources_variables_json_records = []
        temporal_coverage_json_records = []
        spatial_coverage_json_records = []

        def is_queryable(provenance_id):
            return True
            # Original:
            # if provenance_id == '6f57d0df-8570-4f7e-93c8-ef71361e6cfe':
            #     return False
            # else:
            #     return True

        for resource in self.resources:
            resource_json_records.append({
                "record_id": resource.record_id,
                "provenance_id": resource.provenance_id,
                "dataset_id": resource.dataset_id,
                "name": resource.name,
                "resource_type": resource.resource_type,
                "data_url": resource.data_url,
                "layout": resource.layout,
                "json_metadata": resource.json_metadata,
                "is_queryable": is_queryable(resource.provenance_id)
            })

            for variable_id in resource.variable_ids:
                resources_variables_json_records.append({
                    "resource_id": resource.record_id,
                    "variable_id": variable_id
                })

            if resource.temporal_coverage:
                temporal_coverage_json_records.append({
                    "indexed_type": 'RESOURCE',
                    "indexed_id": resource.record_id,
                    "start_time": resource.temporal_coverage['start_time'],
                    "end_time": resource.temporal_coverage['end_time']
                })

            if resource.spatial_coverage:
                spatial_coverage_json_records.append({
                    "indexed_type": 'RESOURCE',
                    "indexed_id": resource.record_id,
                    "spatial_coverage": self._as_wkt(resource.spatial_coverage)
                })

        def get_query(arr):
            keys = ["indexed_type", "indexed_id", "start_time", "end_time"]
            query = [
                f"INSERT INTO temporal_coverage_index ({(', '.join(keys))})"]

            values_arr = []
            for record in arr:
                values_arr.append(
                    "(" + ", ".join(["'"+record[k]+"'" for k in keys]) + ")")

            query.append(f"VALUES {', '.join(values_arr)}")

            query.append(
                "ON CONFLICT (indexed_type, indexed_id) DO UPDATE SET start_time = excluded.start_time, end_time = excluded.end_time")
            return "\n".join(query)

        # Get session's connection to perform bulk inserts, but still within self.session's transaction
        connection = self.session.connection()
        print(resource_json_records)
        connection.execute(do_update_resources_stmt, resource_json_records)
        if len(resources_variables_json_records) > 0:
            connection.execute(insert_resources_variables_stmt,
                               resources_variables_json_records)

        if len(temporal_coverage_json_records) > 0:
            self.session.execute(get_query(temporal_coverage_json_records))
        # connection.execute(do_update_temporal_coverage_index_stmt, temporal_coverage_json_records)
        if len(spatial_coverage_json_records) > 0:
            connection.execute(
                do_update_spatial_coverage_index_stmt, spatial_coverage_json_records)

        for record in resource_json_records:
            del record['is_queryable']

        return resource_json_records

    # TODO: This should be in SpatialCoverage class
    def _as_wkt(self, spatial_coverage: dict):
        spatial_coverage_str = ""
        if spatial_coverage['type'] == "WKT_POLYGON":
            spatial_coverage_str = spatial_coverage['value']
        elif spatial_coverage['type'] == "BoundingBox":
            xmin = spatial_coverage['value']['xmin']
            ymin = spatial_coverage['value']['ymin']
            xmax = spatial_coverage['value']['xmax']
            ymax = spatial_coverage['value']['ymax']

            spatial_coverage_str = f"POLYGON (({xmin} {ymin}, {xmin} {ymax}, {xmax} {ymax}, {xmax} {ymin}, {xmin} {ymin}))"
        elif str(spatial_coverage['type']).lower() == "point":
            x = spatial_coverage['value']['x']
            y = spatial_coverage['value']['y']
            spatial_coverage_str = f"POINT ({x} {y})"

        return f"SRID={SpatialCoverageIndexDB.LOCATION_SRID};{spatial_coverage_str}"
