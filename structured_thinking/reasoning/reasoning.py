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


def load_template(template_name: str) -> Template:
    templates_dir = os.path.join(os.path.dirname(__file__), "templates")
    fname = os.path.join(templates_dir, f"{template_name}.yaml")
    with open(fname, "r") as f:
        schema_dict = yaml.safe_load(f)
    loaded_classes = []
    for custom_class in schema_dict["classes"]:
        class_name = custom_class["name"]
        cls = class_from_schema(Schema(**custom_class), loaded_classes)
        # Reconstrói o modelo para resolver referências pendentes
        globals()[class_name] = cls
        loaded_classes.append(globals()[class_name])
#    for cls in loaded_classes:
#        cls.model_rebuild()
    return Template(
        name=template_name,
        classes=loaded_classes,
        output_class=globals()[schema_dict["output_class"]],
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
