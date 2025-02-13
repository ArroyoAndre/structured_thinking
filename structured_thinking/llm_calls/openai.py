from typing import Type, Optional
from pydantic import BaseModel
import openai


def make_structured_call(
        model_name: str, 
        prompt: list[dict], 
        output_class: Type[BaseModel], 
        max_completion_tokens: Optional[int] = None,
    ) -> tuple[BaseModel, BaseModel]:
    """
    Makes a structured call to the OpenAI API with the provided prompt and output class.

    Args:
        model_name (str): The name of the model to be used.
        prompt (list[dict]): The input prompt messages for the model.
        output_class (Type[BaseModel]): The class type of the expected output.
        max_completion_tokens (Optional[int]): The maximum number of tokens to be generated.

    Returns:
        tuple[BaseModel, BaseModel]: The parsed output and the API response.
    """
    client = openai.Client()
    response = client.beta.chat.completions.parse(
        model=model_name,
        messages=prompt,
        temperature=0,
        max_completion_tokens=max_completion_tokens,
        response_format=output_class,
    )
    # Print token statistics
    print(f"Model {model_name} - Tokens used:\n{response.usage}\n")

    output : BaseModel = response.choices[0].message.parsed
    return output, response
