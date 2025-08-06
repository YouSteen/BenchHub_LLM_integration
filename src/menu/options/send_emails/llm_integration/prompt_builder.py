def build_prompt(r1: str, r2: str, r3: str) -> str:
    return (
        f"You are an assistant at Endava writing internal communication to employees.\n\n"
        "This section will be inserted into a pre-written email template.\n\n"
        "You must follow these rules:\n\n"
        "Here are the employee's survey responses:\n"
        f"- Areas of interest: {r1}\n"
        f"- Motivation: {r2}\n"
        f"- Currently in training: {r3}\n\n"
        "Here is an example of the tone and structure you should match:\n\n"
        "You can explore various upskilling paths by visiting our Collaboration & Knowledge Hub. "
        "There, you'll find a range of options to suit your interests, such as Automation, AI and Performance. "
        "To guide you towards areas with strong demand, prioritizing Automation and AI is recommended, "
        "as these skills are currently highly valued in the industry.\n\n"
        "Now generate only the middle paragraph of the email."
    )
