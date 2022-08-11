from dataclasses import dataclass
from typing import Optional

@dataclass
class CodeBlock:
    code: str
    lang: Optional[str]

def extract_code_block(message: str) -> Optional[CodeBlock]:
    lang = None
    code_lines = []
    in_code_block = False
    lines = message.split("\n")
    for line in lines:
        if in_code_block:
            if line.startswith("```"):
                break
            code_lines.append(line)
        elif line.startswith("```"):
            lang = line[3:]
            in_code_block = True

    if not in_code_block:
        return None

    if lang == "":
        lang = None

    return CodeBlock("\n".join(code_lines), lang)
