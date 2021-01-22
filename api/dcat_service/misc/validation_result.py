from typing import *


class ValidationResult:
    def __init__(self, record=None):
        self.record = record
        self.errors = []

    def is_valid(self) -> bool:
        return len(self.errors) == 0

    def add_error(self, error):
        self.errors.append(error)

    def __repr__(self):
        return str({"record": self.record, "errors": self.errors})
