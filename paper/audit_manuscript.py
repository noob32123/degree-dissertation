"""Lightweight prose and consistency audit for the LaTeX manuscript."""

from __future__ import annotations

import re
from pathlib import Path


SOURCE = Path(__file__).with_name("source.tex")
BIBLIOGRAPHY = Path(__file__).with_name("ref.bib")


def strip_latex(text: str) -> str:
    if r"\begin{abstract}" in text:
        text = text.split(r"\begin{abstract}", 1)[1]
    text = re.sub(r"(?m)(?<!\\)%.*$", " ", text)
    for environment in ("equation", "align", "tikzpicture", "figure", "table"):
        text = re.sub(
            rf"\\begin\{{{environment}\*?\}}.*?\\end\{{{environment}\*?\}}",
            ". ", text, flags=re.S
        )
    text = re.sub(r"\$.*?\$", " ", text, flags=re.S)
    text = re.sub(r"\\(?:cite|ref|eqref|label|input|includegraphics)"
                  r"(?:\[[^]]*\])?\{[^}]*\}", " ", text)
    text = re.sub(r"\\(?:section|subsection|subsubsection)\*?\{[^}]*\}", ". ", text)
    text = text.replace(r"\item", ". ")
    text = re.sub(r"\\[A-Za-z]+\*?(?:\[[^]]*\])?", " ", text)
    text = text.replace("{", " ").replace("}", " ")
    return re.sub(r"\s+", " ", text)


def main() -> None:
    source = SOURCE.read_text(encoding="utf-8")
    prose = strip_latex(source)
    sentences = re.split(r"(?<=[.!?])\s+", prose)
    long_sentences = []
    for sentence in sentences:
        words = re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", sentence)
        if len(words) > 30:
            long_sentences.append((len(words), sentence[:180]))

    sections = re.split(r"(?=\\section\{)", source)
    section_counts = {}
    for section in sections:
        match = re.search(r"\\section\{([^}]+)\}", section)
        name = match.group(1) if match else "front matter"
        section_counts[name] = len(
            re.findall(r"\b[A-Za-z][A-Za-z'-]*\b", strip_latex(section))
        )

    print("section_word_counts=", section_counts)
    print("sentences_over_30_words=", len(long_sentences))
    for count, sentence in long_sentences:
        print(f"  {count}: {sentence}")
    print("em_dash_count=", source.count("—"))
    citation_keys = {
        key.strip()
        for group in re.findall(r"\\cite\{([^}]+)\}", source)
        for key in group.split(",")
    }
    bibliography_keys = set(
        re.findall(r"@[A-Za-z]+\s*\{\s*([^,\s]+)",
                   BIBLIOGRAPHY.read_text(encoding="utf-8"))
    )
    missing_citations = sorted(citation_keys - bibliography_keys)
    labels = set(re.findall(r"\\label\{([^}]+)\}", source))
    references = set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", source))
    missing_references = sorted(references - labels)
    print("missing_citations=", missing_citations)
    print("missing_cross_references=", missing_references)

    if long_sentences or "—" in source:
        raise SystemExit(1)
    if missing_citations or missing_references:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
