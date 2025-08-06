from llama_cpp import Llama
from typing import Optional


class LLMRunner:
    def __init__(self, model_path: str, n_ctx: int = 2048, n_threads: int = 6):
        self.model_path = model_path
        self.n_ctx = n_ctx
        self.n_threads = n_threads
        self._llm: Optional[Llama] = None

    def _load_model(self):
        if self._llm is None:
            self._llm = Llama(
                model_path=self.model_path, n_ctx=self.n_ctx, n_threads=self.n_threads
            )

    def run(
        self, prompt: str, max_tokens: int = 150, stop: Optional[list[str]] = None
    ) -> str:
        if not prompt.strip():
            raise ValueError("Prompt is empty.")
        self._load_model()
        stop = stop or ["</s>"]
        output = self._llm(prompt, max_tokens=max_tokens, stop=stop)
        return output["choices"][0]["text"].strip()
