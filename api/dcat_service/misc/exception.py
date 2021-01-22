#!/usr/bin/python
# -*- coding: utf-8 -*-


class DataInvalidException(Exception):
    pass


class QueryInvalidException(Exception):
    pass


class ProvenanceValidationError(Exception):
    pass


class VariableValidationError(Exception):
    pass


class StandardVariableValidationError(Exception):
    pass


class DatasetValidationError(Exception):
    pass


class DatasetFileValidationError(Exception):
    pass


# For request handling in the main function
class UnauthorizedException(Exception):
    pass


class BadRequestException(Exception):
    pass


class InternalServerException(Exception):
    pass


class NotFoundException(Exception):
    pass
