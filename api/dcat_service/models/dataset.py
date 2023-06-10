from typing import *
from uuid import uuid4
from dcat_service.db_models import VariableDB, DatasetDB, ResourceDB, StandardVariableDB
from dcat_service.models.standard_variable import StandardVariable
# from dcat_service.models.variable import Variable
from dcat_service.models.provenance import Provenance
from dcat_service.misc.exception import DatasetValidationError
from dcat_service.misc.validation_result import ValidationResult
from dcat_service.misc.validator import ValidatorRunner, Validator, ValidateNotEmpty, ValidateProperUUID, ValidateIsDict

from dcat_service import session_scope

from sqlalchemy import bindparam
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func


class Dataset:
    def __init__(self, provenance_id, record_id, name, description, json_metadata, variables=None):
        self.provenance_id = provenance_id
        self.record_id = record_id
        self.name = name
        self.description = description
        self.json_metadata = json_metadata
        self.variables = variables
        # self.resources = resources

    def to_json(self):
        return {
            "record_id": self.record_id,
            "provenance_id": self.provenance_id,
            "name": self.name,
            "description": self.description,
            "json_metadata": self.json_metadata
        }

    def __str__(self):
        return str(self.to_json())

    # @staticmethod
    # def register_variables(dataset_record_id, variable_definitions) -> dict:
    #     res = {}
    #     with session_scope() as session:
    #         dataset = Dataset.find_by_record_id(record_id=dataset_record_id, session=session)
    #         variables = []
    #         standard_variables_list = set([])
    #         for variable_definition in variable_definitions:
    #             standard_variables_list.update(variable_definition.get('standard_names', []))
    #             variables.append(Variable.from_json(variable_definition))
    #
    #     return {}

    @staticmethod
    def find_by_record_id(record_id: str, session: session_scope = None) -> Optional[DatasetDB]:
        attributes = [DatasetDB.id, DatasetDB.provenance_id, DatasetDB.name, DatasetDB.description,
                      DatasetDB.json_metadata, DatasetDB.created_at, func.ST_AsGeoJSON(DatasetDB.spatial_coverage).label('spatial_coverage_geojson')]
        if session is None:
            with session_scope() as sess:
                return sess.query(*attributes).filter(DatasetDB.id == record_id).first()

        else:
            return session.query(*attributes).filter(DatasetDB.id == record_id).first()

    @staticmethod
    def find_by_record_ids(record_ids: Iterable[str], session: session_scope = None) -> Iterable[DatasetDB]:
        if session is None:
            with session_scope() as sess:
                return sess.query(DatasetDB).filter(DatasetDB.id.in_(record_ids)).all()

        else:
            return session.query(DatasetDB).filter(DatasetDB.id.in_(record_ids)).all()

    @staticmethod
    def schema_validators_for_create() -> List[Validator]:
        return [
            ValidateNotEmpty(attribute='provenance_id'),
            ValidateNotEmpty(attribute='record_id'),
            ValidateProperUUID(attribute='record_id'),
            ValidateProperUUID(attribute='provenance_id'),
            ValidateNotEmpty(attribute='name'),
            ValidateNotEmpty(attribute='description'),
            ValidateIsDict(attribute='json_metadata')
        ]

    @staticmethod
    def schema_validators_for_update() -> List[Validator]:
        return [
            ValidateNotEmpty(attribute='provenance_id'),
            ValidateNotEmpty(attribute='record_id'),
            ValidateProperUUID(attribute='record_id'),
            ValidateProperUUID(attribute='provenance_id'),
            ValidateNotEmpty(attribute='name'),
            ValidateNotEmpty(attribute='description'),
            ValidateIsDict(attribute='json_metadata')
        ]

    @staticmethod
    def from_json(dataset_definition) -> 'Dataset':
        record_id = dataset_definition.get("record_id", str(uuid4()))
        provenance_id = dataset_definition.get("provenance_id")
        name = dataset_definition.get("name")
        description = dataset_definition.get("description")
        json_metadata = dataset_definition.get("metadata", {})

        return Dataset(provenance_id=provenance_id,
                       record_id=record_id,
                       name=name,
                       description=description,
                       json_metadata=json_metadata)


class DatasetCollectionBuilder:
    def __init__(self, session):
        self.session = session
        self.datasets: List[Dataset] = []
        self.db_records: List[DatasetDB] = []
        self.schema_validation_errors: List[ValidationResult] = []
        self.data_validation_errors: List[ValidationResult] = []
        self.db_records_references = {"provenance_record_ids": set([])}

    def instantiate_variables(self, dataset_definitions: List[dict]):
        for dataset_definition in dataset_definitions:
            dataset = Dataset.from_json(dataset_definition)
            self.db_records_references["provenance_record_ids"].add(
                dataset.provenance_id)
            self.datasets.append(dataset)

    def validate_schema(self):
        validator_runner = ValidatorRunner(
            validators=Dataset.schema_validators_for_create())
        validation_results = validator_runner.run_validations(self.datasets)

        validation_results_with_errors = []
        for validation_result in validation_results:
            if not validation_result.is_valid():
                validation_results_with_errors.append(validation_result)

        self.schema_validation_errors = validation_results_with_errors

    def build_record_associations(self):
        provenance_arr = Provenance.find_by_record_ids(
            self.db_records_references["provenance_record_ids"], self.session)
        valid_provenance_associations = {}
        for provenance in provenance_arr:
            valid_provenance_associations[str(provenance.id)] = provenance
        valid_provenance_record_ids = set(valid_provenance_associations.keys())

        validation_results_with_errors = []
        for dataset in self.datasets:
            if dataset.provenance_id not in valid_provenance_record_ids:
                validation_result = ValidationResult(record=dataset.to_json())
                validation_result.add_error(
                    [f"Invalid value for 'provenance_id': {dataset.provenance_id}"])
                validation_results_with_errors.append(validation_result)

        self.data_validation_errors = validation_results_with_errors

    def persist(self) -> List[str]:
        stmt = postgresql.insert(DatasetDB).values(
            provenance_id=bindparam('provenance_id'),
            id=bindparam('record_id'),
            name=bindparam('name'),
            description=bindparam('description'),
            json_metadata=bindparam('json_metadata'),
            created_at=func.now(),
            updated_at=func.now()
        )

        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=[DatasetDB.id],
            set_={'name': stmt.excluded.name,
                  'provenance_id': stmt.excluded.provenance_id,
                  'description': stmt.excluded.description,
                  'json_metadata': DatasetDB.json_metadata.op('||')(stmt.excluded.json_metadata),
                  'updated_at': stmt.excluded.updated_at
                  }
        )

        standard_variables_json_records = [
            dataset.to_json() for dataset in self.datasets]
        self.session.execute(do_update_stmt, standard_variables_json_records)

        return standard_variables_json_records


class DatasetCollectionUpdater:
    def __init__(self, session):
        self.session = session
        self.datasets: List[Dataset] = []
        self.db_records: List[DatasetDB] = []
        self.schema_validation_errors: List[ValidationResult] = []
        self.data_validation_errors: List[ValidationResult] = []
        self.db_records_references = {"provenance_record_ids": set([])}

    def instantiate_variables(self, dataset_definitions: List[dict]):
        for dataset_definition in dataset_definitions:
            dataset = Dataset.from_json(dataset_definition)
            self.db_records_references["provenance_record_ids"].add(
                dataset.provenance_id)
            self.datasets.append(dataset)

    def validate_schema(self):
        validator_runner = ValidatorRunner(
            validators=Dataset.schema_validators_for_create())
        validation_results = validator_runner.run_validations(self.datasets)

        validation_results_with_errors = []
        for validation_result in validation_results:
            if not validation_result.is_valid():
                validation_results_with_errors.append(validation_result)

        self.schema_validation_errors = validation_results_with_errors

    def build_record_associations(self):
        provenance_arr = Provenance.find_by_record_ids(self.db_records_references["provenance_record_ids"],
                                                       self.session)
        valid_provenance_associations = {}
        for provenance in provenance_arr:
            valid_provenance_associations[str(provenance.id)] = provenance
        valid_provenance_record_ids = set(valid_provenance_associations.keys())

        validation_results_with_errors = []
        for dataset in self.datasets:
            if dataset.provenance_id not in valid_provenance_record_ids:
                validation_result = ValidationResult(record=dataset.to_json())
                validation_result.add_error(
                    [f"Invalid value for 'provenance_id': {dataset.provenance_id}"])
                validation_results_with_errors.append(validation_result)

        self.data_validation_errors = validation_results_with_errors

    def persist(self) -> List[str]:
        stmt = postgresql.insert(DatasetDB).values(
            provenance_id=bindparam('provenance_id'),
            id=bindparam('record_id'),
            name=bindparam('name'),
            description=bindparam('description'),
            json_metadata=bindparam('json_metadata'),
            created_at=func.now(),
            updated_at=func.now()
        )

        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=[DatasetDB.id],
            set_={'name': stmt.excluded.name,
                  'provenance_id': stmt.excluded.provenance_id,
                  'description': stmt.excluded.description,
                  'json_metadata': DatasetDB.json_metadata.op('||')(stmt.excluded.json_metadata),
                  'updated_at': stmt.excluded.updated_at
                  }
        )

        standard_variables_json_records = [
            dataset.to_json() for dataset in self.datasets]
        self.session.execute(do_update_stmt, standard_variables_json_records)

        return standard_variables_json_records
