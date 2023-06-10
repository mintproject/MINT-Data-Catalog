from typing import *

from sqlalchemy.ext.declarative import declarative_base

from sqlalchemy.dialects.postgresql import JSONB, TSVECTOR
from sqlalchemy.sql import func

from sqlalchemy import Index, PrimaryKeyConstraint, UniqueConstraint, Table, Column, String, ForeignKey, DateTime, orm, Boolean
from sqlalchemy.orm import relationship

from sqlalchemy.dialects import postgresql
from geoalchemy2 import Geometry


Base = declarative_base()


class ProvenanceDB(Base):
    __tablename__ = "provenance"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    name = Column(String)
    provenance_type = Column(String)  # Person, Organization
    json_metadata = Column(JSONB)

    datasets = relationship("DatasetDB", back_populates="provenance")


class DatasetDB(Base):
    __tablename__ = "datasets"

    LOCATION_SRID = 4326

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    provenance_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(
        "provenance.id"), index=True, nullable=False)
    # provenance_record_id = Column(String, ForeignKey("provenance.record_id"), index=True, nullable=False)
    name = Column(String, nullable=False, index=True)
    description = Column(String, nullable=False)
    json_metadata = Column(JSONB, nullable=False)
    variables = relationship("VariableDB",
                             back_populates="dataset",
                             cascade="all, delete, delete-orphan")

    created_at = Column(DateTime, nullable=False,
                        index=True, server_default=func.now())
    updated_at = Column(DateTime, nullable=False,
                        server_default=func.now(), server_onupdate=func.now())

    tsv = Column(TSVECTOR, nullable=True)
    spatial_coverage = Column(Geometry(srid=LOCATION_SRID))
    temporal_coverage_start = Column(DateTime)
    temporal_coverage_end = Column(DateTime)

    provenance = relationship("ProvenanceDB", back_populates="datasets")

    resources = relationship("ResourceDB",
                             back_populates='dataset',
                             cascade="all, delete, delete-orphan")
    # Things to include in json
    # variables, example, sample data


# Associative relationship between resources and variables in that file
resource_variables = Table("resources_variables", Base.metadata,
                           Column("resource_id", postgresql.UUID(as_uuid=True), ForeignKey(
                               "resources.id", ondelete='CASCADE'), primary_key=True),
                           Column("variable_id", postgresql.UUID(as_uuid=True), ForeignKey("variables.id", ondelete='CASCADE'), primary_key=True))

# resource_variables_r = Table("resources_variables_r", Base.metadata,
#                                      Column("resource_record_id", String, ForeignKey("resources.record_id", ondelete='CASCADE'), primary_key=True),
#                                      Column("variable_record_id", String, ForeignKey("variables.record_id", ondelete='CASCADE'), primary_key=True))


class ResourceDB(Base):
    __tablename__ = "resources"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    dataset_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(
        "datasets.id"), index=True, nullable=False)
    provenance_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(
        "provenance.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    data_url = Column(String, nullable=False)
    resource_type = Column(String, nullable=False, default="")
    json_metadata = Column(JSONB, nullable=False)
    layout = Column(JSONB, nullable=False)

    created_at = Column(DateTime, nullable=False,
                        index=True, server_default=func.now())
    updated_at = Column(DateTime, nullable=False,
                        server_default=func.now(), server_onupdate=func.now())
    is_queryable = Column(Boolean, nullable=False)

    dataset = relationship("DatasetDB", back_populates='resources')

    variables = relationship(
        "VariableDB", secondary="resources_variables", back_populates="resources")

    def to_dict(self):
        return {
            "id": str(self.id),
            "dataset_id": str(self.dataset_id),
            "provenance_id": str(self.provenance_id),
            "name": self.name,
            "data_url": self.data_url,
            "resource_type": self.resource_type,
            "json_metadata": self.json_metadata,
            "layout": self.layout
        }


# Associative relationship between variables and standard_variables
variables_standard_variables = Table("variables_standard_variables", Base.metadata,
                                     Column("variable_id", postgresql.UUID(as_uuid=True), ForeignKey(
                                         "variables.id", ondelete='CASCADE'), primary_key=True),
                                     Column("standard_variable_id", postgresql.UUID(as_uuid=True), ForeignKey("standard_variables.id", ondelete='CASCADE'), primary_key=True))


class QueryableResourceDB(Base):
    __tablename__ = "queryable_resources"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    dataset_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(
        "datasets.id"), index=True, nullable=False)
    provenance_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(
        "provenance.id"), index=True, nullable=False)
    name = Column(String, nullable=False)
    data_url = Column(String, nullable=False)
    resource_type = Column(String, nullable=False, default="")
    json_metadata = Column(JSONB, nullable=False)

    created_at = Column(DateTime, nullable=False,
                        index=True, server_default=func.now())

    def to_dict(self):
        return {
            "id": str(self.id),
            "dataset_id": str(self.dataset_id),
            "provenance_id": str(self.provenance_id),
            "name": self.name,
            "data_url": self.data_url,
            "resource_type": self.resource_type,
            "json_metadata": self.json_metadata
        }


class VariableDB(Base):

    __tablename__ = "variables"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    dataset_id = Column(postgresql.UUID(as_uuid=True), ForeignKey(
        "datasets.id", ondelete='CASCADE'), index=True, nullable=False)
    name = Column(String, nullable=False)
    # spatial_coverage = Column(Geometry(srid=LOCATION_SRID))
    # start_time = Column(DateTime, index=True)
    # end_time = Column(DateTime, index=True)
    dataset = relationship("DatasetDB", back_populates='variables')
    resources = relationship(
        "ResourceDB", secondary="resources_variables", back_populates="variables")
    standard_variables = relationship(
        "StandardVariableDB", secondary="variables_standard_variables", back_populates="variables")
    json_metadata = Column(JSONB, nullable=False)

    __table_args__ = (UniqueConstraint('dataset_id', 'name',
                      name="variables_dataset_id_name_unique_constraint"), )

    standard_variables_ids = []


class StandardVariableDB(Base):
    __tablename__ = "standard_variables"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    ontology = Column(String, nullable=False)
    name = Column(String, nullable=False, index=True)
    uri = Column(String, nullable=False, unique=True)
    description = Column(String)
    created_at = Column(DateTime, nullable=False,
                        index=True, server_default=func.now())
    updated_at = Column(DateTime, nullable=False,
                        server_default=func.now(), server_onupdate=func.now())

    variables = relationship(
        "VariableDB", secondary="variables_standard_variables", back_populates="standard_variables")

    def to_dict(self):
        return {
            "id": str(self.id),
            "ontology": str(self.ontology),
            "name": str(self.name),
            "uri": self.uri,
            "description": self.description
        }


class SpatialCoverageIndexDB(Base):
    __tablename__ = "spatial_coverage_index"

    # For postgis; corresponds to WGS 84 projection
    LOCATION_SRID = 4326

    indexed_type = Column(String, nullable=False)
    indexed_id = Column(postgresql.UUID(as_uuid=True), nullable=False)
    spatial_coverage = Column(Geometry(srid=LOCATION_SRID))

    __table_args__ = (PrimaryKeyConstraint(
        indexed_type, indexed_id, name="indexed_spatial_coverage_constraint"), )

    # variables = relationship("VariableDB", back_populates="")


class TemporalCoverageIndexDB(Base):
    __tablename__ = "temporal_coverage_index"

    indexed_type = Column(String, nullable=False)
    indexed_id = Column(postgresql.UUID(as_uuid=True), nullable=False)
    start_time = Column(DateTime, nullable=False, index=True)
    end_time = Column(DateTime, nullable=False, index=True)

    __table_args__ = (PrimaryKeyConstraint(
        indexed_type, indexed_id, name="indexed_temporal_coverage_constraint"), )


class EventDB(Base):
    __tablename__ = "events"

    id = Column(postgresql.UUID(as_uuid=True), primary_key=True)
    timestamp = Column(DateTime(timezone=False), nullable=False,
                       index=True, server_default=func.now())
    event_type = Column(String, nullable=False, index=True)
    event_value = Column(JSONB)
