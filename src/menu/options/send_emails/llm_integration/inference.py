from llama_cpp import Llama


class LLMRunner:
    def __init__(self, model_path: str, n_ctx: int = 4096, n_threads: int = 6):
        self._llm = Llama(
            model_path=model_path, n_ctx=n_ctx, n_threads=n_threads, verbose=False
        )

    def run(self, prompt: str, max_tokens: int = 512) -> str:
        output = self._llm(prompt, max_tokens=max_tokens)
        return output.get("choices", [{}])[0].get("text", "").strip()
