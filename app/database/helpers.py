from typing import (
    Type,
    Dict,
    Any
)
from app.database import (
    MongoModel
)


def generate_bson_schema(model_cls: Type[MongoModel]) -> Dict[str, Any]:
    """
    Generate BSON schema for the validation of the MongoDB
    collection models.

    Args:
        model_cls (Type[MongoModel]): The Collection class for
        which to create the BSON schema.

    Returns:
        Dict[str, Any]: Generated BSON validation schema.
    """
    type_map = {
        int: 'int',
        str: 'string',
        float: 'double',
        bool: 'bool'
    }
    required = []
    properties = {}

    for field, type in model_cls.model_fields.items():
        required.append(field)
        properties[field] = {
            'bsonType': type_map.get(type.annotation, 'string')
        }

    return {
        '$jsonSchema': {
            'bsonType': 'object',
            'required': required,
            'properties': properties
        }
    }


def field(
        model_cls: Type[MongoModel],
        field: str
) -> str:
    """
    Retrieves the name of the field or the alias - if it exists.
    Raises an error if the field does not exist.

    It is the responsiblity of the invoker to ensure the field
    exists in the mongoDB collection.

    Args:
        model_cls (Type[MongoModel]): The MongoDB collection class.
        field (str): The field for which to retrieve the name or alias.

    Raises:
        ValueError: If the field does not exist in the MongoDB
        collection.

    Returns:
        str: The field or alias name.
    """
    fields = list(model_cls.model_fields.keys())
    aliases = [
        field.alias
        for field in model_cls.model_fields.values()
        if field.alias is not None
    ]
    if field not in (fields + aliases):
        raise ValueError('Field Name Mismatch')

    return model_cls.model_fields[field].alias or field


def get_other_fields(
        model_cls: Type[MongoModel],
        inserted_field: str
) -> Dict[str, Any]:
    """
    Retrieves the other fields and their associated BSON types.
    This is for the purposes of '$setOnInsert' mongoDB command.

    Args:
        model_cls (Type[MongoModel]): The collection from which to retrieve
        the fields from.

        inserted_field (str): The field to exclude from the '$setOnInsert'
        command.

    Returns:
        Dict[str, Any]: Field data to feed into '$setOnInsert' command.
    """
    default_map = {
        int: 0,
        float: 0.0,
        str: '',
        bool: False
    }
    other_fields = {}
    for field, info in model_cls.model_fields.items():
        if info.is_required() and field != inserted_field:
            other_fields[
                info.alias or field
            ] = default_map.get(info.annotation, None)

    return other_fields
