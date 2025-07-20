from llm_integration.survey_parser import get_entries_for_unsent
from llm_integration.prompt_builder import build_prompt
from llm_integration.inference import LLMRunner

def generate_llm_outputs(xlsx_path: str) -> list[dict]:
    entries = get_entries_for_unsent(xlsx_path)
    llm = LLMRunner(model_path="C:\\dev\\BenchHub_LLM_integration\\models\\mistral-7b-instruct-v0.2.Q4_K_M.gguf")

    results = []
    for entry in entries:
        prompt = build_prompt(entry["r1"], entry["r2"], entry["r3"])
        text, _ = llm.run(prompt)
        results.append({
            "name": entry["name"],
            "email": entry["email"],
            "coach": entry["career_coach"],
            "llm_output": text.strip()
        })

    return results
