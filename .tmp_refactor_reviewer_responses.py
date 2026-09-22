from pathlib import Path


ROOT = Path(r"H:\degree-dissertation\paper\MDPI_submission_source\revision_round2")

LOCATIONS = {
    1: [
        "p.~1, Abstract and Highlights; p.~3, Introduction; p.~23, Section~5.1; p.~24, Conclusions.",
        "p.~11, Section~3.4.1; pp.~17--18, Tables~7--8 and accompanying Results text; p.~23, Section~5.1.",
        "pp.~2--3, Introduction and Related Work; pp.~12--13, Section~3.4.4; pp.~20--21, Section~4.6 and Table~12; p.~23, Section~5.2.",
        "p.~14, Section~3.4.5; pp.~19--20, Sections~4.4--4.5 and Figures~6--7.",
        "p.~22, Section~5; p.~23, Sections~5.1--5.2.",
    ],
    2: [
        "pp.~2--3, Introduction; p.~23, Section~5.1; p.~24, Conclusions.",
        "pp.~2--3, Related Work; pp.~20--21, Section~4.6 and Table~12; p.~23, Section~5.2.",
        "p.~11, Section~3.4.1; pp.~17--18, Tables~7--8; p.~23, Sections~5.1--5.2.",
        "pp.~12--13, Section~3.4.4; p.~16, Figure~5 caption; p.~21, Section~4.6; p.~22, Discussion.",
    ],
    3: [
        "pp.~12--13, Section~3.4.4; p.~18, Table~10; pp.~20--21, Section~4.6 and Table~12.",
        "pp.~6--7, Section~3.1.2 and Table~3; p.~23, Sections~5.1--5.2; p.~24, Conclusions.",
    ],
}


def matching_brace(text: str, opening: int) -> int:
    depth = 0
    for index in range(opening, len(text)):
        char = text[index]
        if char == "{" and (index == 0 or text[index - 1] != "\\"):
            depth += 1
        elif char == "}" and (index == 0 or text[index - 1] != "\\"):
            depth -= 1
            if depth == 0:
                return index
    raise ValueError("unmatched brace")


def add_locations(body: str, locations: list[str]) -> str:
    marker = r"\RevisedExcerpt{"
    cursor = 0
    pieces: list[str] = []
    count = 0
    while True:
        start = body.find(marker, cursor)
        if start < 0:
            pieces.append(body[cursor:])
            break
        pieces.append(body[cursor:start])
        opening = start + len(marker) - 1
        closing = matching_brace(body, opening)
        pieces.append(body[start : closing + 1])
        if count >= len(locations):
            raise ValueError("more excerpts than locations")
        pieces.append("\n\\ManuscriptLocation{" + locations[count] + "}")
        count += 1
        cursor = closing + 1
    if count != len(locations):
        raise ValueError(f"expected {len(locations)} excerpts, found {count}")
    return "".join(pieces).strip() + "\n"


for reviewer, locations in LOCATIONS.items():
    source_path = ROOT / f"response_reviewer{reviewer}.tex"
    source = source_path.read_text(encoding="utf-8")
    first = source.index(r"\ReviewerComment{")
    end = source.rindex(r"\end{document}")
    header = source[:first]
    body = source[first:end]
    shared = add_locations(body, locations)
    shared_path = ROOT / f"reviewer{reviewer}_points.tex"
    shared_path.write_text(shared, encoding="utf-8", newline="\n")
    replacement = header + f"\\input{{reviewer{reviewer}_points.tex}}\n\n\\end{{document}}\n"
    source_path.write_text(replacement, encoding="utf-8", newline="\n")
    print(f"reviewer={reviewer} points={len(locations)} shared={shared_path.name}")
