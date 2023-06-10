from typing import *
from dcat_service.db_models import ProvenanceDB
from dcat_service.misc.exception import ProvenanceValidationError
from dcat_service.misc.validation_result import ValidationResult
from dcat_service.misc.validator import Validator, ValidateNotEmpty, ValidateProperUUID, ValidatorRunner

from dcat_service import session_scope
import uuid
from sqlalchemy import bindparam
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import func


class Provenance:
    def __init__(self, record_id: str, name: str, provenance_type: str, json_metadata: dict):
        self.record_id = record_id
        self.name = name
        self.provenance_type = provenance_type
        self.json_metadata = json_metadata

    def to_json(self):
        return {
            "record_id": self.record_id,
            "name": self.name,
            "provenance_type": self.provenance_type,
            "json_metadata": self.json_metadata
        }

    @staticmethod
    def find_by_record_id(record_id: str, session: session_scope = None) -> Optional[ProvenanceDB]:
        record_id = uuid.uuid3(uuid.NAMESPACE_DNS, record_id)
        if session is None:
            with session_scope() as sess:
                return sess.query(ProvenanceDB).filter(ProvenanceDB.id == record_id).first()
        else:
            return session.query(ProvenanceDB).filter(ProvenanceDB.id == record_id).first()

    @staticmethod
    def find_by_record_ids(record_ids: Iterable[str], session: session_scope = None) -> Iterable[ProvenanceDB]:
        if session is None:
            with session_scope() as sess:
                return sess.query(ProvenanceDB).filter(ProvenanceDB.id.in_(record_ids)).all()

        else:
            return session.query(ProvenanceDB).filter(ProvenanceDB.id.in_(record_ids)).all()

    @staticmethod
    def from_json(provenance_definition):
        record_id = provenance_definition.get("record_id", str(uuid.uuid4()))
        name = provenance_definition.get("name")
        provenance_type = provenance_definition.get("provenance_type")
        json_metadata = provenance_definition.get("metadata")

        return Provenance(record_id=record_id,
                          name=name,
                          provenance_type=provenance_type,
                          json_metadata=json_metadata)

    @staticmethod
    def schema_validators() -> List[Validator]:
        return [
            ValidateNotEmpty(attribute="name"),
            ValidateNotEmpty(attribute="provenance_type"),
            ValidateNotEmpty(attribute="record_id"),
            ValidateProperUUID(attribute="record_id")
        ]


class ProvenanceCollectionBuilder:
    def __init__(self, session):
        self.session = session
        self.provenance_arr: List[Provenance] = []
        self.schema_validation_errors: List[ValidationResult] = []
        self.data_validation_errors: List[ValidationResult] = []
        self.db_records = []

    def instantiate_provenance_arr(self, provenance_definitions: List[dict]):
        self.provenance_arr = [Provenance.from_json(
            provenance_definition) for provenance_definition in provenance_definitions]

    def validate_schema(self):
        validator_runner = ValidatorRunner(
            validators=Provenance.schema_validators())
        validation_results = validator_runner.run_validations(
            self.provenance_arr)

        validation_results_with_errors = []
        for validation_result in validation_results:
            if not validation_result.is_valid():
                validation_results_with_errors.append(validation_result)

        self.schema_validation_errors = validation_results_with_errors

    def build_record_associations(self):
        provenance_db_records = []
        self.db_records = provenance_db_records

    def persist(self) -> List[dict]:
        stmt = postgresql.insert(ProvenanceDB).values(
            id=bindparam('record_id'),
            name=bindparam('name'),
            provenance_type=bindparam('provenance_type'),
            json_metadata=bindparam('json_metadata')
        )

        do_update_stmt = stmt.on_conflict_do_update(
            index_elements=[ProvenanceDB.id],
            set_={'provenance_type': stmt.excluded.provenance_type,
                  'name': stmt.excluded.name,
                  'json_metadata': stmt.excluded.json_metadata
                  }
        )

        provenance_json_records = [provenance.to_json()
                                   for provenance in self.provenance_arr]
        self.session.execute(do_update_stmt, provenance_json_records)

        return provenance_json_records
