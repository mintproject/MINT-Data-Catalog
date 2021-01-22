from typing import *
from dcat_service.db_models import VariableDB, StandardVariableDB
from dcat_service.misc.exception import StandardVariableValidationError
from dcat_service.misc.validation_result import ValidationResult
from dcat_service.misc.validator import Validator, ValidateNotEmpty, ValidateProperUUID, ValidatorRunner
from dcat_service import session_scope
import uuid
from sqlalchemy import bindparam
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func


class StandardVariable:
    def __init__(self, record_id: str, name: str, ontology: str, uri: str, description: str):
        self.record_id = record_id
        self.ontology = ontology
        self.name = name
        self.uri = uri
        self.description = description

    def to_json(self):
        return {
            "record_id": self.record_id,
            "ontology": self.ontology,
            "name": self.name,
            "uri": self.uri,
            "description": self.description
        }

    def __str__(self):
        return str(self.to_json())

    @staticmethod
    def find_by_record_id(record_id: str, session: session_scope=None) -> Optional[StandardVariableDB]:
        if session is None:
            with session_scope() as sess:
                return sess.query(StandardVariableDB).filter(StandardVariableDB.id == record_id).first()
        else:
            return session.query(StandardVariableDB).filter(StandardVariableDB.id == record_id).first()

    @staticmethod
    def find_by_record_ids(record_ids: Iterable[str], session: session_scope=None) -> Iterable[StandardVariableDB]:
        if session is None:
            with session_scope() as sess:
                return sess.query(StandardVariableDB).filter(StandardVariableDB.id.in_(record_ids)).all()

        else:
            return session.query(StandardVariableDB).filter(StandardVariableDB.id.in_(record_ids)).all()

    @staticmethod
    def schema_validators() -> List[Validator]:
        return [
            ValidateNotEmpty(attribute="name"),
            ValidateNotEmpty(attribute="ontology"),
            ValidateNotEmpty(attribute="uri"),
            ValidateNotEmpty(attribute="record_id"),
            ValidateProperUUID(attribute="record_id")
        ]

    @staticmethod
    def from_json(standard_variable_definition):
        name = standard_variable_definition.get("name")
        ontology = standard_variable_definition.get("ontology")
        uri = standard_variable_definition.get("uri")
        description = standard_variable_definition.get("description", "")
        record_id = standard_variable_definition.get("record_id", str(uuid.uuid5(uuid.NAMESPACE_URL, str(uri))))

        return StandardVariable(record_id=record_id,
                                name=name,
                                ontology=ontology,
                                uri=uri,
                                description=description)


class StandardVariableCollectionBuilder:
    def __init__(self, session):
        self.session = session
        self.standard_variables: List[StandardVariable] = []
        self.db_records: List[StandardVariableDB] = []
        self.schema_validation_errors: List[ValidationResult] = []
        self.data_validation_errors: List[ValidationResult] = []
        self.db_records_references = {}

    def instantiate_variables(self, standard_variable_definitions: List[dict]):
        self.standard_variables = [StandardVariable.from_json(standard_variable_definition) for standard_variable_definition in standard_variable_definitions]

    def validate_schema(self):
        validator_runner = ValidatorRunner(validators=StandardVariable.schema_validators())
        validation_results = validator_runner.run_validations(self.standard_variables)

        validation_results_with_errors = []
        for validation_result in validation_results:
            if not validation_result.is_valid():
                validation_results_with_errors.append(validation_result)

        self.schema_validation_errors = validation_results_with_errors

    def build_record_associations(self):
        standard_variable_db_records = []
        self.db_records = standard_variable_db_records

    def persist(self) -> List[dict]:
        stmt = postgresql.insert(StandardVariableDB).values(
            id=bindparam('record_id'),
            ontology=bindparam('ontology'),
            name=bindparam('name'),
            uri=bindparam('uri'),
            description=bindparam('description'),
            created_at=func.now(),
            updated_at=func.now()
        )

        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=[StandardVariableDB.id],
            set_={'ontology': stmt.excluded.ontology,
                  'name': stmt.excluded.name,
                  'uri': stmt.excluded.uri,
                  'description': stmt.excluded.description,
                  'updated_at': stmt.excluded.updated_at
                  }
        )

        standard_variables_json_records = [standard_variable.to_json() for standard_variable in self.standard_variables]
        self.session.execute(do_update_stmt, standard_variables_json_records)

        return standard_variables_json_records
