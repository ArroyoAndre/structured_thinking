from typing import Any, Type
from pydantic import BaseModel, Field
from io import TextIOBase

import yaml


class FieldSchema(BaseModel):
    name: str = Field(description="The name of the field")
    type: Any = Field(description="The type of the field")
    description: str = Field(description="A description of the field")


class Schema(BaseModel):
    name: str = Field(description="The name of the schema")
    fields: list[FieldSchema] = Field(description="The fields of the schema")


def class_from_schema(schema: Schema) -> Type[BaseModel]:
    fields = schema.fields
    field_definitions = {field.name: Field(description=field.description) for field in fields}
    field_types = {field.name: field.type for field in fields}
    field_definitions["__annotations__"] = field_types
    return type(schema.name, (BaseModel,), field_definitions)


def schema_from_class(cls: Type[BaseModel]) -> Schema:
    fields = []
    for name, field in cls.model_fields.items():
        fields.append({
            "name": name, 
            "type": field.annotation.__name__,
            "description": field.description
        })
    return Schema(name=cls.__name__, fields=fields)


def load_schema_class(source: str | TextIOBase) -> Type[BaseModel]:
    if isinstance(source, str):
        with open(source, "r") as f:
            schema_dict = yaml.safe_load(f)
    else:
        schema_dict = yaml.safe_load(source)
    return class_from_schema(Schema(**schema_dict))


def save_schema_class(cls: Type[BaseModel], fname: str | TextIOBase):
    if isinstance(fname, str):
        with open(fname, "w", encoding='utf-8') as f:
            yaml.dump(schema_from_class(cls).model_dump(), f, allow_unicode=True)
    else:
        yaml.dump(schema_from_class(cls).model_dump(), fname, allow_unicode=True)