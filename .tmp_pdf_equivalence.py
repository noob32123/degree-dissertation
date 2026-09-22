from collections import Counter
from pathlib import Path
import re
import unicodedata

from pypdf import PdfReader

root = Path(r"H:\degree-dissertation\paper\MDPI_submission_source")
paths = [root / "manuscript_clean.pdf", root / "manuscript_marked.pdf"]
readers = [PdfReader(str(path)) for path in paths]

def tokens(page):
    text = unicodedata.normalize("NFKC", page.extract_text() or "")
    return Counter(re.findall(r"[A-Za-z0-9]+(?:[.'-][A-Za-z0-9]+)*", text.lower()))

print(f"page_counts={[len(reader.pages) for reader in readers]}")
mismatches = []
for i, (clean_page, marked_page) in enumerate(zip(readers[0].pages, readers[1].pages), 1):
    clean_tokens = tokens(clean_page)
    marked_tokens = tokens(marked_page)
    if clean_tokens != marked_tokens:
        mismatches.append({
            "page": i,
            "clean_only": list((clean_tokens - marked_tokens).items())[:20],
            "marked_only": list((marked_tokens - clean_tokens).items())[:20],
        })
print(f"token_multiset_mismatches={mismatches}")

def all_text(reader):
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    text = unicodedata.normalize("NFKC", text)
    text = re.sub(r"([A-Za-z])-\s*\n\s*([A-Za-z])", r"\1\2", text)
    return Counter(re.findall(r"[A-Za-z0-9]+(?:[.'-][A-Za-z0-9]+)*", text.lower()))

clean_all, marked_all = map(all_text, readers)
print(f"global_clean_only={list((clean_all - marked_all).items())[:50]}")
print(f"global_marked_only={list((marked_all - clean_all).items())[:50]}")
