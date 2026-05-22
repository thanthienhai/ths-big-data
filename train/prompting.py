from __future__ import annotations


def build_prompt(instruction: str, question: str, legal_context: str | list[str] | None = None) -> str:
    if isinstance(legal_context, list):
        context = "\n".join(str(item) for item in legal_context)
    else:
        context = str(legal_context or "")
    return (
        f"### Instruction\n{instruction.strip()}\n\n"
        f"### Question\n{question.strip()}\n\n"
        f"### Legal Context\n{context.strip()}\n\n"
        "### Answer\n"
    )

