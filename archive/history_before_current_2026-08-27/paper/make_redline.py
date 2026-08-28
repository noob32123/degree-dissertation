"""Create a line-level red manuscript from the state-completeness baseline."""

from __future__ import annotations

import difflib
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parent
BASELINE = ROOT / "source_pre_state_complete_revision_2026-08-27.tex"
CLEAN = ROOT / "source.tex"
MARKED = ROOT / "source_marked_state_complete_revision_2026-08-27.tex"


def main() -> None:
    before = BASELINE.read_text(encoding="utf-8").splitlines(keepends=True)
    after = CLEAN.read_text(encoding="utf-8").splitlines(keepends=True)
    matcher = difflib.SequenceMatcher(a=before, b=after, autojunk=False)
    output: list[str] = []
    in_document = False
    for tag, _i1, _i2, j1, j2 in matcher.get_opcodes():
        if tag == "equal":
            output.extend(after[j1:j2])
            if any(r"\begin{document}" in line for line in after[j1:j2]):
                in_document = True
        elif tag in {"replace", "insert"}:
            if in_document:
                output.append("\\color{red}% BEGIN STATE-COMPLETE REVISION\n")
                output.extend(after[j1:j2])
                output.append("\\color{black}% END STATE-COMPLETE REVISION\n")
            else:
                # Preamble commands are kept structurally unchanged. Visible
                # revised content after \begin{document} carries the red mark.
                output.extend(after[j1:j2])
                if any(r"\begin{document}" in line for line in after[j1:j2]):
                    in_document = True
        elif tag == "delete":
            continue
    marked = "".join(output)
    marked = marked.replace("\\showrevisionsfalse", "\\showrevisionstrue", 1)
    MARKED.write_text(marked, encoding="utf-8")


if __name__ == "__main__":
    main()
