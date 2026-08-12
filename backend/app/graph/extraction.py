import json
import re


EXTRACT_PROMPT = """
Extract factual triples from the text below.

Return ONLY a JSON array of objects with keys
"subject", "relation", "object".

Each triple must come from a single clear
statement in the text.

Do not guess or combine information across
different sentences.

If unsure which entity a relation refers to,
skip that triple entirely.

Text:
{text}
"""


class TripleExtractor:

    def __init__(self, llm_service):
        self.llm_service = llm_service


    def extract_triples(self, text):

        messages = [
            {
                "role": "user",
                "content": EXTRACT_PROMPT.format(
                    text=text
                )
            }
        ]

        content = self.llm_service.generate(
            messages,
            json_format=True
        )

        try:

            result = json.loads(
                content
            )

        except json.JSONDecodeError:

            return []

        if isinstance(
            result,
            dict
        ):
            return [result]

        if isinstance(
            result,
            list
        ):
            return result

        return []


    def extract_triples_from_text(
        self,
        text
    ):

        sentences = re.split(
            r'(?<=[.!?])\s+',
            text.strip()
        )

        all_triples = []

        for sentence in sentences:

            if sentence.strip():

                all_triples.extend(
                    self.extract_triples(
                        sentence
                    )
                )

        return all_triples