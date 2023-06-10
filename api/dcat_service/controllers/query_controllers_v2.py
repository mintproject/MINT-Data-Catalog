from typing import *
import sys
import traceback
from datetime import datetime
import uuid
import ujson

from dcat_service.misc.exception import BadRequestException, InternalServerException
from dcat_service import session_scope

from dcat_service.db_models import DatasetDB
from sqlalchemy import func


def search_datasets_v2(query_definition: dict) -> list:
    if len(query_definition) == 0:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty; received {query_definition}"})
        # parse query operators
        # search_ops = body.pop('search_operators', "and").lower()
        # sort_by = body.pop("sort_by", None)
        # assert search_ops == "or" or search_ops == "and"
    limit = int(query_definition.pop("limit", 500))
    field_names = query_definition.keys()

    allowed_query_words = frozenset(
        ["search_query", "spatial_coverage", "temporal_coverage", "provenance_id"])

    if query_definition == {}:
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Query definition must not be empty"})

    if not all([field_name in allowed_query_words for field_name in list(query_definition.keys())]):
        raise BadRequestException(
            {'InvalidQueryDefinition': f"Invalid search field(s); must be either of {allowed_query_words}"})

    search_query = query_definition.get("search_query")

    if search_query is not None and not isinstance(search_query, list):
        raise BadRequestException({'InvalidQueryDefinition':
                                   f"Invalid value type for 'search_query': {search_query}; must be an array"})

    provenance_id = query_definition.get("provenance_id")

    if provenance_id is not None:
        try:
            uuid.UUID(str(provenance_id))
            # assert(uuid_val.version == 4)
        except ValueError:
            raise BadRequestException(
                {'InvalidQueryDefinition': f"'provenance_id' value must be a valid UUID v4; received {provenance_id}"})

    spatial_coverage = query_definition.get("spatial_coverage")
    # if spatial_coverage is not None:
    temporal_coverage = query_definition.get("temporal_coverage")

    # execute the query
    try:
        with session_scope() as session:

            # Get Dataset

            datasets_query = _generate_select_datasets_query(
                provenance_id=provenance_id, search_query=search_query, spatial_coverage=spatial_coverage, temporal_coverage=temporal_coverage, limit=limit)
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
                    "dataset_spatial_coverage": ujson.loads(row[4])
                }

                if dataset_id not in datasets_dict:
                    datasets_dict[dataset_id] = dataset_record

            # dataset_ids = list(datasets_dict.keys())

            results_json = []
            for dataset_id, dataset_record in datasets_dict.items():
                # dataset_record["variables"] = list(dataset_record["variables"].values())
                results_json.append(dataset_record)

            return results_json

    except Exception as e:
        traceback.print_exc(file=sys.stdout)
        raise InternalServerException(e)


def _generate_select_datasets_query(provenance_id=None, search_query=[], spatial_coverage=None, temporal_coverage=None, limit=20):
    select_datasets_query_part = [
        "datasets.id as dataset_id",
        "datasets.name as dataset_name",
        "datasets.description as description",
        "datasets.json_metadata as dataset_metadata",
        "COALESCE(ST_AsGeoJSON(datasets.spatial_coverage), '{}') as dataset_spatial_coverage"
    ]

    where_query_part = []
    order_by_query_part = []

    if provenance_id is not None:
        where_query_part.append(f"datasets.provenance_id = '{provenance_id}'")

    if search_query is not None:
        # ["a b", "c"] => "'a b' & 'c'"
        search_string = " & ".join(
            [f"''{str(keyword)}''" for keyword in search_query])
        where_query_part.append(
            f"datasets.tsv @@ to_tsquery('english', '{search_string}')")
        order_by_query_part.append(
            f"ts_rank_cd(datasets.tsv, to_tsquery('english', '{search_string}')) DESC")

        # datasets that have 'source' field set should be displayed first
        order_by_query_part.append(
            "(case when datasets.json_metadata -> 'source' IS NOT NULL then 1 else 0 end) DESC")

    if spatial_coverage is not None:
        where_query_part.append(
            f"ST_Intersects(datasets.spatial_coverage, ST_SetSRID(ST_GeomFromGeoJSON('{ujson.dumps(spatial_coverage)}'), {DatasetDB.LOCATION_SRID}))")

    if temporal_coverage is not None:
        requested_coverage_start_time = temporal_coverage.get('start_time')
        requested_coverage_end_time = temporal_coverage.get('end_time')

        if requested_coverage_start_time is not None:
            where_query_part.append(
                f"datasets.temporal_coverage_end >= '{requested_coverage_start_time}'")
        if requested_coverage_end_time is not None:
            where_query_part.append(
                f"datasets.temporal_coverage_start <= '{requested_coverage_end_time}'")

    query = "SELECT " + ", ".join(select_datasets_query_part) + " "
    query += "FROM datasets "

    if len(where_query_part) > 0:
        query += "WHERE " + " AND ".join(where_query_part) + " "

    if len(order_by_query_part) > 0:
        query += "ORDER BY " + ", ".join(order_by_query_part) + " "

    query += f"LIMIT {limit}"

    return query
