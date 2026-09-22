from pathlib import Path
from pypdf import PdfReader
root=Path(r"H:\degree-dissertation\paper\MDPI_submission_source")
pdfs=[root/'manuscript_clean.pdf',root/'manuscript_marked.pdf',root/'revision_round2'/'cover_letter.pdf',root/'revision_round2'/'response_reviewer1.pdf',root/'revision_round2'/'response_reviewer2.pdf',root/'revision_round2'/'response_reviewer3.pdf']
texts={}
for p in pdfs:
    reader=PdfReader(str(p))
    text='\n'.join((page.extract_text() or '') for page in reader.pages)
    texts[p.name]=text
    bad=[token for token in ('RESULT_PENDING','PLACEHOLDER','TBD','[?]') if token in text]
    print(f'{p.name}: pages={len(reader.pages)}, chars={len(text)}, bad={bad}')
clean=texts['manuscript_clean.pdf']
marked=texts['manuscript_marked.pdf']
print('manuscript_text_equal=', clean==marked)
for required in ('1,020 trained checkpoints','3076c7949333ebcb36643fc5b011ff9db05f78dd','eight-step greedy-rollout'):
    print(required, required in clean)
if clean != marked: raise SystemExit('clean/marked text mismatch')
