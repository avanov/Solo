import logging

from enum import Enum as PythonEnum

import sqlalchemy.types as sa_types
from sqlalchemy.ext.asyncio import AsyncEngine

from solo.configurator.config.sums import SumType


log = logging.getLogger(__name__)

SQLEngine = AsyncEngine


class PythonMappedEnum(sa_types.TypeDecorator):
    """ Implements mapping between Postgres' Enums and Python Enums.
    """
    impl = sa_types.Enum

    def __init__(self, python_enum_type: SumType, **kwargs):
        self.python_enum_type = python_enum_type
        self.kwargs = kwargs
        enum_args = [x.value for x in python_enum_type]
        super().__init__(*enum_args, **self.kwargs)

    def process_bind_param(self, value: PythonEnum, dialect):
        """ Convert to postgres value
        """
        return value.value

    def process_result_value(self, value: str, dialect):
        """ Convert to python value
        """
        for case in self.python_enum_type:
            if case.value == value:
                return case
        raise TypeError("Cannot map Enum value '{}' to Python's {}".format(
            value, self.python_enum_type
        ))

    def copy(self):
        return PythonMappedEnum(self.python_enum_type, **self.kwargs)
