
CHUNKING_WARNING_PRE = """
The user text is too long to be processed in a single call. The user input will be an excerpt of the full text. 
Only for your context, the end of the preceding text is:

{previous}
"""


CHUNKING_WARNING_POST = """
Only for your context, the beginning of the following text is:

{next}
"""


def find_text_chunks(text: str, chunk_target_size: int, context_size: int = 50) -> list[tuple[str, str, str]]:
    """
    This function splits the text into chunks of near to a target size. The split is done by finding the nearest period to the target size.
    It returns a tuple containing the chunk, the end of text before the chunk and the beginning of text after the chunk.
    """
    chunks = []
    previous = ''
    while len(text) > chunk_target_size:
        if len(text) < 1.6 * chunk_target_size:
            chunk_target_size = len(text) // 2
        end = text[:chunk_target_size].rfind('.')
        if end == -1:
            end = chunk_target_size
        chunk = text[:end]
        text = text[end:]
        chunks.append((previous, chunk, text[:context_size]))
        previous = chunk[-context_size:]
    chunks.append((previous, text, ''))
    return chunks
