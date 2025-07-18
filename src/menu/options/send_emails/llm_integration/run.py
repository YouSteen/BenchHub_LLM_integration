from survey_parser import load_all_form_responses
from prompt_builder import build_prompt
from inference import LLMRunner

def main():
    xlsx_path = r"C:\Users\iustanciu\OneDrive - ENDAVA\Survey\BenchHub_Engagement & Upskilling Survey.xlsx"
    model_path = r"C:\dev\BenchHub_LLM_integration\models\mistral-7b-instruct-v0.2.Q4_K_M.gguf"

    responses = load_all_form_responses(xlsx_path)
    llm = LLMRunner(model_path=model_path)

    for idx, (r1, r2, r3) in enumerate(responses, start=1):
        prompt = build_prompt(r1, r2, r3)
        email = llm.run(prompt)
        print(f"\n=== Entry #{idx} ===")
        print(email)
        print("=" * 50)

if __name__ == "__main__":
    main()
