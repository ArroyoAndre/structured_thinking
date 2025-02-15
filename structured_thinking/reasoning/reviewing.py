from pydantic import BaseModel
from typing import Optional, Type
from dataclasses import dataclass

from structured_thinking.llm_calls.openai import make_structured_call
from structured_thinking.llm_calls.utils import find_text_chunks, CHUNKING_WARNING_PRE, CHUNKING_WARNING_POST
from structured_thinking.reasoning.reasoning import load_template, Template


DEFAULT_REVIEWING_TEMPLATE = "transcription_reviewing"


REVIEWING_SYSTEM_MESSAGE = """
You should review the text provided by the user, making corrections and clarifications to ensure that it is faithful to what the user probably said.
The text might contain transcription errors, such as missing words, wrong words, words that do not make sense, missing punctuation, missing or wrong prepositions, typos and misspellings, etc.
Short and uncommon words are more likely to be transcribed incorrectly. Pay attention to phrases that sound strange or do not make sense.
You should fix transcription problems, without adding or removing information. If you are unsure about what was said, you can leave the original text.
Break the text into paragraphs, and make corrections to each paragraph separately. Paragraphs should not be too long.
In case the text contains dialogs, always break the paragraphs when it is likely the speaker changed.
The language of the text must be preserved.
Make sure all text is present in the final version, even if it is not clear or if it is incorrect. No parts should be missing or repeated. The order of the parts must be kept unchanged.
"""

@dataclass
class ReviewingOutput:
    output: str
    reasoning: list[BaseModel]
    full_response: list[BaseModel]


def reviewing_call(
        model_name: str,
        text: str,
        template: Template | str = DEFAULT_REVIEWING_TEMPLATE,
        additional_messages: list[dict] = [], # Optional messages to be added before the user input
        max_chunk_size: int = 16000,
        max_completion_tokens: Optional[int] = None,
    ) -> ReviewingOutput:
    """
    Calls a llm model with a structured output and a reviewing template, to review the text for transcription errors.
    The processing can happen in chunks to avoid exceeding the token limits.
    """

    if isinstance(template, str):
        template = load_template(template)

    text_chunks = find_text_chunks(text, max_chunk_size)

    responses = []
    outputs = []
    for previous, current, next in text_chunks:
        if previous or next:
            messages = [
                {"role": "system", "content": CHUNKING_WARNING_PRE.format(previous=previous)},
                {"role": "user", "content": current},
                {"role": "system", "content": CHUNKING_WARNING_POST.format(next=next)},
            ]
        else:
            messages = [{"role": "user", "content": current}]
        messages = [{"role": "system", "content": REVIEWING_SYSTEM_MESSAGE}] + messages
        if additional_messages:
            messages = additional_messages + messages
        thinking_output, response = make_structured_call(model_name, messages, template.output_class, max_completion_tokens)
        outputs.append(thinking_output)
        responses.append(response)
    
    output_text = _assemble_output(outputs)
    return ReviewingOutput(
        output=output_text,
        reasoning=outputs,
        full_response=responses,
    )


def _assemble_output(outputs: list[BaseModel]) -> str:
    text = ""
    for output in outputs:
        for paragraph in output.paragraphs:
            text += paragraph.corrected_paragraph + "\n"
    return text.strip()
