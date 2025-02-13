from pydantic import BaseModel
from typing import Optional, Type

from structured_thinking.llm_calls.openai import make_structured_call
from structured_thinking.structure.schema import class_from_schema, schema_from_class, Schema, FieldSchema
from structured_thinking.reasoning.reasoning import Template, ReasoningOutput, load_template


DEFAULT_COMPLETION_TEMPLATE = "considered_completion"


def completion_call(
        model_name: str, 
        messages: list[dict],
        output_class: BaseModel, 
        template: Template | str = DEFAULT_COMPLETION_TEMPLATE,
        max_completion_tokens: Optional[int] = None,
    ) -> ReasoningOutput:
    """   
    Calls a llm model with a structured output and a thinking template.

    Args:
        model_name (str): The name of the model to be used.
        messages (list[dict]): The input messages for the model.
        output_class (BaseModel): The class type of the expected output. Field descriptions are important.
        template (Template or str): The template used for the completion.
        max_completion_tokens (int): The maximum number of tokens to be generated in the completion, including structured thinking.

    Returns:
        ReasoningOutput: The the structured output, tokens usage and the reasoning output.
    """
    output_schema = schema_from_class(output_class)
    if isinstance(template, str):
        template = load_template(template)
    if template.descriptions_dict:
        descriptions_message = (
            "Consider the following instructions for the output fields:\n"
            + "\n".join([f"- {field}: {description}" for field, description in template.descriptions_dict.items()])
        )
        messages.append({"role": "system", "content": descriptions_message})
    
    thinking_schema = Schema(
        name="Thinking",
        fields=[_replace_type_for_thinking(field, template.output_class) for field in output_schema.fields],
    )
    final_key = list(template.output_class.model_fields.keys())[-1]
    thinking_class = class_from_schema(thinking_schema)
    
    thinking_output, response = make_structured_call(model_name, messages, thinking_class, max_completion_tokens)

    final_output = _assemble_output(thinking_output, output_class, final_key)

    return ReasoningOutput(
        output=final_output,
        reasoning=thinking_output,
        full_response=response,
    )


def _replace_type_for_thinking(field: FieldSchema, thinking_class: Type[BaseModel]) -> FieldSchema:
    return FieldSchema(name=field.name, type=thinking_class, description=field.description)


def _assemble_output(thinking_output: BaseModel, output_class: BaseModel, final_key: str) -> BaseModel:
    output_dict = thinking_output.model_dump()
    final_output = {}
    for field_name, field_value in output_dict.items():
        final_output[field_name] = field_value[final_key]
    return output_class(**final_output)
