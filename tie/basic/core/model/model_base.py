"""Model Definition"""

import logging

from pydantic import BaseModel, ConfigDict

# logger
logger = logging.getLogger('tcex')


def snake_to_camel(snake_string: str) -> str:
    """Convert snake_case to camelCase

    Args:
        snake_string: The snake case input string.
    """
    components = snake_string.split('_')
    return components[0] + ''.join(x.title() for x in components[1:])


class GenericModelBase(BaseModel):
    """Generic Model Definition"""

    model_config = ConfigDict(
        alias_generator=snake_to_camel,
        populate_by_name=True,
        extra='forbid',
        validate_default=True,
        validate_assignment=True,
    )


class ModelBase(BaseModel):
    """Model Definition"""

    model_config = ConfigDict(
        alias_generator=snake_to_camel,
        populate_by_name=True,
        extra='forbid',
        validate_default=True,
        validate_assignment=True,
    )
