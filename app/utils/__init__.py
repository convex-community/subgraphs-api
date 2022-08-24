from flask_restx.fields import Integer, String, List, Float, Boolean


TYPE_MAP = {str: String(),
 int: Integer(),
 float: Float(),
 bool: Boolean()}


# TODO : need a better way to convert from marshmallow to flask restx schema
def convert_marshmallow(marshtype):
    res = {}
    for key, key_type in marshtype.__annotations__.items():
        if key_type in TYPE_MAP:
            res[key] = TYPE_MAP[key_type]
        elif key_type.__dict__['_name'] == 'List':
            res[key] = List(TYPE_MAP[key_type.__args__[0]])
    return res
