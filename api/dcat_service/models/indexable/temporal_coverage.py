from typing import *
from datetime import datetime


class TemporalCoverage:
    def __init__(self, indexed_type: str = None, indexed_id: str = None, start_time: datetime = None, end_time: datetime = None):
        self.indexed_type = indexed_type
        self.indexed_id = indexed_id
        self.start_time = start_time
        self.end_time = end_time

    def to_json(self):
        start_time_str = self.start_time.strftime(
            "%Y-%m-%dT%H:%M:%S") if self.start_time else None
        end_time_str = self.end_time.strftime(
            "%Y-%m-%dT%H:%M:%S") if self.end_time else None

        return {
            "indexed_type": self.indexed_type,
            "indexed_id": self.indexed_id,
            "start_time": start_time_str,
            "end_time": end_time_str,
        }

    @staticmethod
    def from_json(temporal_coverage_definition):
        indexed_type = temporal_coverage_definition['indexed_type']
        indexed_id = temporal_coverage_definition['indexed_id ']
        start_time = temporal_coverage_definition['start_time ']
        end_time = temporal_coverage_definition['end_time ']

        return TemporalCoverage(
            indexed_type=indexed_type,
            indexed_id=indexed_id,
            start_time=start_time,
            end_time=end_time,
        )
