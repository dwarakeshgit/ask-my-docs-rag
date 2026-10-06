import torch
from transformers import AutoTokenizer, AutoModelForCausalLM


MODEL_NAME = "Qwen/Qwen2.5-1.5B-Instruct"


class TransformersClient:
    def __init__(
        self,
        model_name: str = MODEL_NAME,
        max_new_tokens: int = 256,
    ):
        self.model_name = model_name
        self.max_new_tokens = max_new_tokens

        print(f"Loading tokenizer: {self.model_name}")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name
        )

        print(f"Loading model: {self.model_name}")
        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name
        )

        self.model.eval()

    def generate(
        self,
        prompt: str,
        temperature: float = 0.0,
    ) -> str:
        if not prompt or not prompt.strip():
            raise ValueError("Prompt cannot be empty.")

        messages = [
            {
                "role": "user",
                "content": prompt,
            }
        ]

        text = self.tokenizer.apply_chat_template(
            messages,
            tokenize=False,
            add_generation_prompt=True,
        )

        inputs = self.tokenizer(
            text,
            return_tensors="pt",
        )

        with torch.no_grad():
            output = self.model.generate(
                **inputs,
                max_new_tokens=self.max_new_tokens,
                do_sample=False,
            )

        generated_tokens = output[
            0
        ][inputs.input_ids.shape[1]:]

        answer = self.tokenizer.decode(
            generated_tokens,
            skip_special_tokens=True,
        ).strip()

        return answer