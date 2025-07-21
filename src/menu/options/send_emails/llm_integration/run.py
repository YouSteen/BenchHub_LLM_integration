from llm_core.inference import LLMRunner
from menu.options.send_emails.llm_integration.prompt_builder import build_prompt
from menu.options.send_emails.llm_integration.survey_parser import get_entries_for_unsent
from menu.options.send_emails.llm_integration.sent_log import load_sent_log

from menu.utils.config_manager import get_llm_path


def generate_llm_outputs(df) -> list[dict]:
    sent_ids = load_sent_log("sent_log.xlsx")
    entries = get_entries_for_unsent(df, sent_ids)

    if not entries:
        print("No new entries to process. All IDs are already logged.")
        return []

    llm_path = get_llm_path()
    if not llm_path:
        raise ValueError("LLM model path is not configured.")

    llm = LLMRunner(model_path=llm_path)

    results = []
    for entry in entries:
        prompt = build_prompt(entry["r1"], entry["r2"], entry["r3"])
        text = llm.run(prompt)
        results.append(
            {
                "id": entry["id"],
                "name": entry["name"],
                "email": entry["email"],
                "coach": entry["career_coach"],
                "llm_output": text.strip(),
            }
        )

    return results

