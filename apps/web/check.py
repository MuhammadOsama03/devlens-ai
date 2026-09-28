from html.parser import HTMLParser
from pathlib import Path


class DocumentParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.has_viewport = False

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        if tag == "meta" and attributes.get("name") == "viewport":
            self.has_viewport = True


document = Path(__file__).with_name("index.html").read_text(encoding="utf-8")
parser = DocumentParser()
parser.feed(document)

assert parser.has_viewport, "index.html must include a viewport meta tag"
assert {"content", "analyze", "repository", "result"} <= parser.ids
assert "innerHTML" not in document, "render API content with safe DOM methods"
assert "\\n" not in document, "index.html contains a literal escaped newline"
