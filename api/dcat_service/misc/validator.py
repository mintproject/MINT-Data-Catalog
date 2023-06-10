from typing import *

from dcat_service.misc.validation_result import ValidationResult
import uuid


class Validator:
    def validate(self, record: Any, validation_result: ValidationResult):
        raise NotImplementedError


class ValidateNotEmpty(Validator):
    def __init__(self, attribute: str, empty_values: List[Any] = None):
        self.attribute = attribute

        default_empty_values = [None, "", [], {}, set([])]
        self.empty_values = empty_values or default_empty_values

    def validate(self, record: Any, validation_result: ValidationResult):
        attribute_value = getattr(record, self.attribute)

        value_considered_empty = [attribute_value ==
                                  empty_value for empty_value in self.empty_values]
        if any(value_considered_empty):
            validation_result.add_error(
                f"{self.attribute} must not be empty; received {attribute_value}")


class ValidateIsList(Validator):
    def __init__(self, attribute: str):
        self.attribute = attribute

    def validate(self, record: Any, validation_result: ValidationResult):
        attribute_value = getattr(record, self.attribute)

        if type(attribute_value) != list:
            help_msg = "must be a list of values"
            validation_result.add_error(
                f"Invalid format for '{self.attribute}': '{attribute_value}'; {help_msg}")


class ValidateIsDict(Validator):
    def __init__(self, attribute: str):
        self.attribute = attribute

    def validate(self, record: Any, validation_result: ValidationResult):
        attribute_value = getattr(record, self.attribute)

        if type(attribute_value) != dict:
            help_msg = "must be a JSON object"
            validation_result.add_error(
                f"Invalid format for '{self.attribute}': '{attribute_value}'; {help_msg}")


class ValidateProperUUID(Validator):
    def __init__(self, attribute: str):
        self.attribute = attribute

    def validate(self, record: Any, validation_result: ValidationResult):
        attribute_value = getattr(record, self.attribute)
        try:
            uuid_val = uuid.UUID(str(attribute_value))
            # assert(uuid_val.version == 4)
        except ValueError:
            validation_result.add_error(
                f"{self.attribute} must be a valid UUID v4; received {attribute_value}")
        except AssertionError:
            validation_result.add_error(
                f"{self.attribute} must be a valid UUID v4; received {attribute_value}")


class ValidateTemporalCoverage(Validator):
    def __init__(self, attribute: str, ignore_empty_values: bool):
        self.attribute = attribute
        self.ignore_empty_values = ignore_empty_values
        self.iso8601_format = "%Y-%m-%dT%H:%M:%S"

    def validate(self, record: Any, validation_result: ValidationResult):
        from datetime import datetime

        attribute_value = getattr(record, self.attribute)
        if not self.ignore_empty_values and not attribute_value:
            validation_result.add_error(
                f"{self.attribute} must not be empty; received {attribute_value}")
        elif self.ignore_empty_values and not attribute_value:
            return True
        elif not isinstance(attribute_value, dict):
            help_msg = "must be a dictionary with keys 'type' and 'value'"
            validation_result.add_error(
                f"Invalid format for 'spatial_coverage': {attribute_value}; {help_msg}")
        else:
            if "start_time" not in attribute_value:
                validation_result.add_error(
                    f"{self.attribute} must contain 'start_time' key")
            else:
                start_time = attribute_value['start_time']
                try:
                    datetime.strptime(start_time, self.iso8601_format)
                except ValueError:
                    validation_result.add_error(
                        f"{start_time} does not match ISO8601 datetime format '{self.iso8601_format}'")

            if "end_time" not in attribute_value:
                validation_result.add_error(
                    f"{self.attribute} must contain 'end_time' key")
            else:
                end_time = attribute_value['end_time']
                try:
                    datetime.strptime(end_time, self.iso8601_format)
                except ValueError:
                    validation_result.add_error(
                        f"{end_time} does not match ISO8601 datetime format '{self.iso8601_format}'")


class ValidateSpatialCoverage:
    def __init__(self, attribute: str, ignore_empty_values: bool):
        import re
        self.attribute = attribute
        self.ignore_empty_values = ignore_empty_values
        self.supported_types = set(["WKT_POLYGON", "BoundingBox", "Point"])
        self.wkt_polygon_regex = re.compile(
            "POLYGON\s(\(\((-?\d+(.\d+)?\s-?\d+(.\d+)?,?\s?)+\)\))+")

    def validate(self, record: Any, validation_result: ValidationResult):
        attribute_value = getattr(record, self.attribute)
        if not self.ignore_empty_values and not attribute_value:
            validation_result.add_error(
                f"{self.attribute} must not be empty; received {attribute_value}")
        elif self.ignore_empty_values and not attribute_value:
            return True
        elif not isinstance(attribute_value, dict):
            help_msg = "must be a dictionary with keys 'type' and 'value'"
            validation_result.add_error(
                f"Invalid format for 'spatial_coverage': {attribute_value}; {help_msg}")
        else:
            if 'type' not in attribute_value:
                validation_result.add_error(
                    f"Missing required key 'type' in {self.attribute}")

            if 'value' not in attribute_value:
                validation_result.add_error(
                    f"Missing required key 'value' in {self.attribute}")

            spatial_coverage_type = attribute_value['type']
            spatial_coverage_value = attribute_value['value']

            if spatial_coverage_type not in self.supported_types:
                help_msg = f"must be one of the supported types: {self.supported_types}"
                msg = f"Invalid spatial coverage type: {spatial_coverage_type}; {help_msg}"
                validation_result.add_error(msg)

            if spatial_coverage_type == "WKT_POLYGON" and not self._is_valid_wkt_polygon(spatial_coverage_value):
                help_msg = f"must match the following regex: '{self.wkt_polygon_regex.pattern}'"
                msg = f"Invalid value for {spatial_coverage_type} type: {spatial_coverage_value}; {help_msg}"
                validation_result.add_error(msg)

            elif spatial_coverage_type == "BoundingBox" and not self._is_valid_bounding_box(spatial_coverage_value):
                help_msg = f"must be a dictionary containing 'xmin', 'ymin', 'xmax', 'ymax' keys with numeric values"
                msg = f"Invalid value for {spatial_coverage_type} type: {spatial_coverage_value}; {help_msg}"
                validation_result.add_error(msg)

            elif spatial_coverage_type == "Point" and not self._is_valid_wkt_point(spatial_coverage_value):
                help_msg = f"must be a dictionary containing 'x' and 'y' keys with numeric values"
                msg = f"Invalid value for {spatial_coverage_type} type: {spatial_coverage_value}; {help_msg}"
                validation_result.add_error(msg)

    def _is_valid_wkt_polygon(self, spatial_coverage_value: str) -> bool:
        match = self.wkt_polygon_regex.match(str(spatial_coverage_value))
        return match is not None

    def _is_valid_bounding_box(self, spatial_coverage_value: dict) -> bool:
        if not isinstance(spatial_coverage_value, dict):
            return False
        else:
            return all([
                self._is_numeric(spatial_coverage_value.get('xmin', '')),
                self._is_numeric(spatial_coverage_value.get('ymin', '')),
                self._is_numeric(spatial_coverage_value.get('xmax', '')),
                self._is_numeric(spatial_coverage_value.get('ymax', ''))
            ])

    def _is_valid_wkt_point(self, spatial_coverage_value: dict) -> bool:
        if not isinstance(spatial_coverage_value, dict):
            return False
        else:
            return all([
                self._is_numeric(spatial_coverage_value.get('x', '')),
                self._is_numeric(spatial_coverage_value.get('y', ''))
            ])

    def _is_numeric(self, string: str) -> bool:
        try:
            float(string)
            return True
        except ValueError:
            return False


class ValidatorRunner:
    def __init__(self, validators=List[Validator]):
        self.validators = validators

    def run_validations(self, records: List[Any]) -> List[ValidationResult]:
        validation_results = []
        for record in records:
            validation_result = ValidationResult(record=record.to_json())
            for validator in self.validators:
                validator.validate(record, validation_result=validation_result)

            validation_results.append(validation_result)

        return validation_results
