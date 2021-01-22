from typing import *
from dcat_service.db_models import VariableDB, Base
from dcat_service.models.standard_variable import StandardVariable
from dcat_service.models.dataset import Dataset
from dcat_service.misc.validation_result import ValidationResult
from dcat_service.misc.validator import Validator, ValidateNotEmpty, ValidatorRunner, ValidateProperUUID, ValidateIsList
from dcat_service import session_scope
from sqlalchemy import bindparam, Table, tuple_
from sqlalchemy.dialects import postgresql
from uuid import uuid4


class Variable:
    def __init__(self, dataset_id: str=None, name: str=None, record_id: str=None,
                 standard_variable_ids: List[str]=None, json_metadata: dict=None):
        self.dataset_id = dataset_id
        self.name = name
        self.record_id = record_id
        self.standard_variable_ids = standard_variable_ids
        self.json_metadata = json_metadata

    def to_json(self):
        return {
            "record_id": self.record_id,
            "dataset_id": self.dataset_id,
            "name": self.name,
            "standard_variable_ids": self.standard_variable_ids,
            "metadata": self.json_metadata
        }

    def __str__(self):
        return str(self.to_json())

    @staticmethod
    def schema_validators() -> List[Validator]:
        return [
            ValidateNotEmpty(attribute="record_id"),
            ValidateProperUUID(attribute="record_id"),
            ValidateNotEmpty(attribute="dataset_id"),
            ValidateProperUUID(attribute="dataset_id"),
            ValidateNotEmpty(attribute="standard_variable_ids"),
            ValidateIsList(attribute="standard_variable_ids"),
            ValidateNotEmpty(attribute="name")
        ]

    @staticmethod
    def find_by_record_id(record_id: str, session: session_scope) -> Optional[VariableDB]:
        return session.query(VariableDB).filter(VariableDB.id == record_id).first()

    @staticmethod
    def find_by_record_ids(record_ids: Iterable[str], session: session_scope=None) -> Iterable[VariableDB]:
        if session is None:
            with session_scope() as sess:
                return sess.query(VariableDB).filter(VariableDB.id.in_(record_ids)).all()

        else:
            return session.query(VariableDB).filter(VariableDB.id.in_(record_ids)).all()

    @staticmethod
    def find_by_dataset_id_and_name(dataset_ids_and_names: Iterable[Tuple[str, str]], session: session_scope=None) -> Iterable[VariableDB]:
        if session is None:
            with session_scope() as sess:
                return sess.query(VariableDB).filter(tuple_(VariableDB.dataset_id, VariableDB.name).in_(dataset_ids_and_names)).all()

        else:
            return session.query(VariableDB).filter(tuple_(VariableDB.dataset_id, VariableDB.name).in_(dataset_ids_and_names)).all()

    @staticmethod
    def from_json(variable_definition):
        json_metadata = variable_definition.get('metadata', {})

        record_id = variable_definition.get("record_id", str(uuid4()))
        dataset_id = variable_definition.get("dataset_id")
        name = variable_definition.get("name")
        standard_variable_ids = variable_definition.get("standard_variable_ids", [])

        return Variable(dataset_id=dataset_id,
                        name=name,
                        record_id=record_id,
                        standard_variable_ids=standard_variable_ids,
                        json_metadata=json_metadata)


class VariableCollectionBuilder:
    def __init__(self, session):
        self.session = session
        self.variables: List[Variable] = []
        self.schema_validation_errors: List[ValidationResult] = []
        self.data_validation_errors: List[ValidationResult] = []
        self.db_records_references = {
            "dataset_ids": set([]),
            "standard_variable_ids": set([])
        }
        self.variables_standard_variables: List[Dict] = []

    def instantiate_variables(self, variable_definitions: List[dict]):
        for variable_definition in variable_definitions:
            variable = Variable.from_json(variable_definition)

            self.db_records_references["dataset_ids"].add(variable.dataset_id)
            self.db_records_references["standard_variable_ids"].update(variable.standard_variable_ids)
            self.variables = [Variable.from_json(variable_definition) for variable_definition in variable_definitions]

    def validate_schema(self):
        validator_runner = ValidatorRunner(validators=Variable.schema_validators())
        validation_results = validator_runner.run_validations(self.variables)

        validation_results_with_errors = []
        for validation_result in validation_results:
            if not validation_result.is_valid():
                validation_results_with_errors.append(validation_result)

        self.schema_validation_errors = validation_results_with_errors

    def build_record_associations(self):
        validation_results_with_errors = []

        datasets = Dataset.find_by_record_ids(self.db_records_references["dataset_ids"], self.session)
        standard_variables = StandardVariable.find_by_record_ids(self.db_records_references["standard_variable_ids"], self.session)

        valid_dataset_associations = {}
        for dataset in datasets:
            valid_dataset_associations[str(dataset.id)] = dataset

        valid_dataset_ids = set(valid_dataset_associations.keys())

        valid_standard_variables_associations = {}
        for standard_variable in standard_variables:
            valid_standard_variables_associations[str(standard_variable.id)] = standard_variable

        valid_standard_variable_ids = set(valid_standard_variables_associations.keys())

        # make sure that there are no duplicate dataset_id/name in the payload
        dataset_id_name_counts = {}
        for variable in self.variables:
            key = (str(variable.dataset_id), str(variable.name))
            if key not in dataset_id_name_counts:
                dataset_id_name_counts[key] = 1
            else:
                dataset_id_name_counts[key] += 1

        for variable in self.variables:
            validation_result = ValidationResult(record=variable.to_json())
            if variable.dataset_id not in valid_dataset_ids:
                validation_result.add_error(f"Invalid value for 'dataset_id': {variable.dataset_id}")

            invalid_standard_variable_ids = set(variable.standard_variable_ids) - valid_standard_variable_ids
            if len(invalid_standard_variable_ids) > 0:
                validation_result.add_error(f"Invalid value for 'standard_variable_ids': {invalid_standard_variable_ids}")

            dataset_id = str(variable.dataset_id)
            name = str(variable.name)
            key_count = dataset_id_name_counts[(dataset_id, name)]
            if key_count > 1:
                validation_result.add_error(f"Duplicate value for (dataset_id, name): ({dataset_id}), ({name})")

            if not validation_result.is_valid():
                validation_results_with_errors.append(validation_result)

        # Validate uniqueness of dataset_id/name
        if len(validation_results_with_errors) == 0:
            prelim_dataset_id_and_name_to_var = {(str(v.dataset_id), str(v.name)): v for v in self.variables}
            existing_variables = Variable.find_by_dataset_id_and_name(list(prelim_dataset_id_and_name_to_var.keys()), self.session)
            for existing_variable in existing_variables:
                record_id = str(existing_variable.id)
                dataset_id = str(existing_variable.dataset_id)
                name = existing_variable.name

                variable = prelim_dataset_id_and_name_to_var[(dataset_id, name)]
                if variable.record_id != record_id:
                    validation_result = ValidationResult(record=variable.to_json())

                    msg = f"Record already exists for variable with dataset_id '{dataset_id}' and name '{name}': '{record_id}'"
                    validation_result.add_error(msg)
                    validation_results_with_errors.append(validation_result)

        # Associate dataset
        # Associate standard_variables
        # Associate temporal_index
        # Associate spatial_index
        self.data_validation_errors = validation_results_with_errors

    def persist(self):

        variable_db_table = Table("variables", Base.metadata, autoload=True)
        insert_variables_stmt = postgresql.insert(VariableDB).values(
            id=bindparam('record_id'),
            dataset_id=bindparam('dataset_id'),
            name=bindparam('name'),
            json_metadata=bindparam('json_metadata')
            # created_at=func.now(),
            # updated_at=func.now()
        )

        do_update_variables_stmt = insert_variables_stmt.on_conflict_do_update(
            index_elements=[VariableDB.id],
            set_={'json_metadata': VariableDB.json_metadata.op('||')(insert_variables_stmt.excluded.json_metadata),
                  'name': insert_variables_stmt.excluded.name
                  # 'updated_at': insert_variables_stmt.excluded.updated_at
                  }
        )

        variables_standard_variables_table = Table("variables_standard_variables", Base.metadata, autoload=True)
        insert_variables_standard_variables_stm = postgresql.insert(variables_standard_variables_table).values(
            variable_id=bindparam('variable_id'),
            standard_variable_id=bindparam('standard_variable_id')
        )
        # do_updated_variables_standard_variables_stm = insert_variables_standard_variables_stm.

        variable_json_records = []
        variables_standard_variables_json_records = []

        for variable in self.variables:
            variable_json_records.append({
                "record_id": variable.record_id,
                "dataset_id": variable.dataset_id,
                "name": variable.name,
                "json_metadata": variable.json_metadata
            })

            for standard_variable_id in variable.standard_variable_ids:
                variables_standard_variables_json_records.append({
                    "variable_id": variable.record_id,
                    "standard_variable_id": standard_variable_id
                })

        self.session.execute(do_update_variables_stmt, variable_json_records)
        self.session.execute(insert_variables_standard_variables_stm, variables_standard_variables_json_records)

        return variable_json_records







