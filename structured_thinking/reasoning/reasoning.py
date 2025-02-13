from dataclasses import dataclass
from pydantic import BaseModel, Field
from typing import Any, Type
import os
import yaml

from structured_thinking.structure.schema import class_from_schema, schema_from_class, Schema


@dataclass
class ReasoningOutput:
    output: BaseModel
    reasoning: BaseModel
    full_response: BaseModel


class Template(BaseModel):
    name: str = Field(description="The name of the template")
    classes: list[Type[BaseModel]] = Field(description="The schema classes of the template, following creation order")
    output_class: Type[BaseModel] = Field(description="The type of the output class")
    descriptions_dict: dict = Field(default_factory=dict, description="A dictionary with descriptions for each field")


def load_template(template_name: str) -> Template:
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    fname = os.path.join(templates_dir, f"{template_name}.yaml")
    with open(fname, "r") as f:
        schema_dict = yaml.safe_load(f)
    descriptions_dict = {}
    for custom_class in schema_dict["classes"]:
        globals()[custom_class['name']] = class_from_schema(Schema(**custom_class))
    return Template(
        name=template_name,
        classes=[globals()[custom_class['name']] for custom_class in schema_dict["classes"]],
        output_class=globals()[schema_dict["output_class"]],
        descriptions_dict=descriptions_dict,
    )


def save_template(template: Template):
    name = template.name
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    fname = os.path.join(templates_dir, f"{name}.yaml")
    schema_dict = dict(name=name)
    classes = []
    for custom_class in template.classes:
        classes.append(schema_from_class(custom_class).model_dump())
    schema_dict["classes"] = classes
    schema_dict["output_class"] = template.output_class.__name__
    with open(fname, "w", encoding='utf-8') as f:
        yaml.dump(schema_dict, f, allow_unicode=True)


def compress_descriptions(descriptions_dict: dict, custom_class: Type[BaseModel]) -> Type[BaseModel]:
    for field_name, field in custom_class.model_fields.items():
        if field_name not in descriptions_dict:
            key = field_name
        else:
            i = 1
            while f"{field_name}_{i}" in descriptions_dict:
                i += 1
            key = f"{field_name}_{i}"
        descriptions_dict[key] = field.description
        field.description = f"See {key}"
    print(custom_class.model_fields)
    return custom_class
