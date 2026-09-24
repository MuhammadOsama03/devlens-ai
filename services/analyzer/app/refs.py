import re


SAFE_REF = re.compile(r"^(?![./])(?!.*(?:\.\.|//|@\{|\\))[A-Za-z0-9._/-]{1,255}(?<![./])$")


def validate_git_ref(value: str) -> str:
    candidate = value.strip()
    if not SAFE_REF.fullmatch(candidate):
        raise ValueError("invalid Git reference")
    if any(part.endswith(".lock") for part in candidate.split("/")):
        raise ValueError("invalid Git reference")
    return candidate
