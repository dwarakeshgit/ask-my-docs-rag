import re
import requests


class OllamaClient:
    def __init__(
        self,
        model_name: str = "qwen3:4b",
        base_url: str = "http://localhost:11434",
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")

    @staticmethod
    def _clean_response(response_text: str) -> str:
        """
        Clean the raw response returned by Qwen3 through Ollama.

        Qwen3 may expose its internal reasoning inside the response
        even when thinking is disabled. This method extracts only
        the final answer before it is returned to the RAG pipeline.
        """
        if not response_text:
            return ""

        cleaned = response_text.strip()

        # ---------------------------------------------------------
        # 1. If Qwen3 returns a closing </think> marker, everything
        #    before it is reasoning. Keep only the content after it.
        # ---------------------------------------------------------
        think_end_matches = list(
            re.finditer(
                r"</think>",
                cleaned,
                flags=re.IGNORECASE,
            )
        )

        if think_end_matches:
            last_think_end = think_end_matches[-1]
            cleaned = cleaned[last_think_end.end():].strip()

        # ---------------------------------------------------------
        # 2. Remove any complete <think>...</think> blocks that
        #    remain in the response.
        # ---------------------------------------------------------
        cleaned = re.sub(
            r"<think>.*?</think>",
            "",
            cleaned,
            flags=re.DOTALL | re.IGNORECASE,
        ).strip()

        # ---------------------------------------------------------
        # 3. Remove a leftover opening <think> tag.
        # ---------------------------------------------------------
        cleaned = re.sub(
            r"<think>",
            "",
            cleaned,
            flags=re.IGNORECASE,
        ).strip()

        # ---------------------------------------------------------
        # 4. If Qwen3 follows our FINAL_ANSWER format, use the
        #    LAST FINAL_ANSWER marker.
        #
        #    Qwen3 can sometimes repeat FINAL_ANSWER while
        #    reasoning, so using the first occurrence is unsafe.
        # ---------------------------------------------------------
        final_answer_matches = list(
            re.finditer(
                r"FINAL_ANSWER:\s*",
                cleaned,
                flags=re.IGNORECASE,
            )
        )

        if final_answer_matches:
            last_match = final_answer_matches[-1]
            cleaned = cleaned[last_match.end():].strip()

            # -----------------------------------------------------
            # 5. The actual answer is normally the first paragraph
            #    after FINAL_ANSWER:. Remove any extra reasoning
            #    that Qwen3 may have produced afterward.
            # -----------------------------------------------------
            paragraphs = re.split(r"\n\s*\n", cleaned)

            if paragraphs:
                cleaned = paragraphs[0].strip()

        # ---------------------------------------------------------
        # 6. Remove accidental answer tags if Qwen3 produces them.
        # ---------------------------------------------------------
        cleaned = re.sub(
            r"^<answer>\s*",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        cleaned = re.sub(
            r"\s*</answer>$",
            "",
            cleaned,
            flags=re.IGNORECASE,
        )

        return cleaned.strip()

    def generate(
        self,
        prompt: str,
        temperature: float = 0.1,
    ) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model_name,
                "prompt": prompt,
                "stream": False,
                "think": False,
                "options": {
                    "temperature": temperature,
                    "num_predict": 512,
                    "repeat_penalty": 1.05,
                },
            },
            timeout=120,
        )

        response.raise_for_status()

        data = response.json()

        raw_answer = data.get("response", "").strip()

        print("\n===== RAW QWEN RESPONSE =====")
        print(raw_answer)
        print("===== END RAW QWEN RESPONSE =====\n")

        return self._clean_response(raw_answer)