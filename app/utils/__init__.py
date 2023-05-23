from flask_restx.fields import List
from werkzeug.routing import BaseConverter
from sqlalchemy.orm.decl_api import DeclarativeMeta
from sqlalchemy import String, Integer, Float, Boolean, ARRAY
from flask_restx import fields
from sqlalchemy import inspect
from dataclasses import is_dataclass


TYPE_MAP = {
    str: fields.String,
    int: fields.Integer,
    float: fields.Float,
    bool: fields.Boolean,
}


SQL_TYPE_MAP = {
    String: fields.String,
    Integer: fields.Integer,
    Float: fields.Float,
    Boolean: fields.Boolean,
    ARRAY: fields.List,
}


# we need to convert both marshmallow dataclasses and sqlalchemy schemas
# to a simpler format that can be used by flask-restx to generate the
# swagger properly
def convert_schema(data):
    if isinstance(data, DeclarativeMeta):
        return convert_sqlalchemy(data)
    elif is_dataclass(data):
        return convert_marshmallow(data)
    raise TypeError("Input should be dataclass or SQLAlchemy schema")


def convert_sqlalchemy(sqla_type):
    res = {}
    inspector = inspect(sqla_type)
    for key, column in inspector.columns.items():
        key_type = type(column.type)
        if key_type in SQL_TYPE_MAP:
            res[key] = SQL_TYPE_MAP[key_type]
        elif (
            hasattr(column.type, "__args__")
            and isinstance(column.type, ARRAY)
            and type(column.type.__args__[0]) in SQL_TYPE_MAP
        ):
            res[key] = SQL_TYPE_MAP[ARRAY](
                SQL_TYPE_MAP[type(column.type.__args__[0])]
            )
    return res


# TODO : need a better way to convert from marshmallow to flask restx schema
def convert_marshmallow(marshtype):
    res = {}
    for key, key_type in marshtype.__annotations__.items():
        if key_type in TYPE_MAP:
            res[key] = TYPE_MAP[key_type]
        elif key_type.__dict__["_name"] == "List":
            res[key] = List(TYPE_MAP[key_type.__args__[0]])
    return res


class RegexConverter(BaseConverter):
    def __init__(self, url_map, *items):
        super(RegexConverter, self).__init__(url_map)
        self.regex = items[0]
