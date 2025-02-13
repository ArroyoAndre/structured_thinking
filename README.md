# structured_thinking

This pakage uses LLM strctured outputs to foster thinking.
It is still under development. The completion API can already be used.

## Installation

```bash
pip install .
```

## Usage

OPENAI_API_KEY must be set in your environment and you must have a valid OpenAI account.

```python
from structured_thinking.structure import class_from_schema, Schema
from structured_thinking.reasoning import completion_call


MODEL = "gpt-4o"  # Choose your model. No need for reasoning ones.


def find_fields(text: str):
    messages = [
        {
            "role": "system", 
            "content": """
You will receive some text from the user about XXX. You should fill the template based on that text.
""",  # Customize your prompt
        },
        {
            "role": "user",
            "content": text,
        },
    ]

    template = class_from_schema(Schema(name="my_questions", fields=[
        {"name": "subject", "type": str, "description": "What title would you give to the text"},
        {"name": "striking_point", "type": str, "description": "Most unnusual fact stated in the text. Don't be politically correct"},
    ]))
    return completion_call(MODEL, messages, output_class, max_completion_tokens=5000)

# load your text
input_text = ...
response = find_fields(text)
print(response.output)


```

## Contributing

Feel free to submit issues or pull requests on GitHub.