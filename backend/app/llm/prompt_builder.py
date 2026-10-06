from pathlib import Path
from typing import List, Dict, Any


PROMPT_VERSION = "grounded_answer_v1.txt"


class GroundedPromptBuilder:
    def __init__(self, prompt_version: str = PROMPT_VERSION):
        self.prompt_version = prompt_version

        self.prompt_path = (
            Path(__file__).resolve().parents[1]
            / "prompts"
            / self.prompt_version
        )

        if not self.prompt_path.exists():
            raise FileNotFoundError(
                f"Prompt file not found: {self.prompt_path}"
            )

        self.template = self.prompt_path.read_text(
            encoding="utf-8"
        )

    def build(
        self,
        question: str,
        evidence: List[Dict[str, Any]],
    ) -> str:
        """
        Build a grounded prompt using the selected
        versioned prompt template.

        Source and page metadata are intentionally not
        included in the LLM prompt because citations
        are handled separately by the application.
        """

        if not question or not question.strip():
            raise ValueError("Question cannot be empty.")

        if not evidence:
            raise ValueError("Evidence cannot be empty.")

        evidence_parts = []

        for document in evidence:
            text = document.get("text", "").strip()

            if text:
                evidence_parts.append(text)

        if not evidence_parts:
            raise ValueError("Evidence contains no usable text.")

        evidence_text = "\n\n".join(evidence_parts)

        return self.template.format(
            question=question,
            evidence_text=evidence_text,
        )