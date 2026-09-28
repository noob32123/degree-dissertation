from pathlib import Path
import sys, re, zipfile, difflib, json, hashlib, importlib.util
sys.stdout.reconfigure(encoding='utf-8')
root=Path(r'H:\degree-dissertation\paper\MDPI_submission_source'); rev=root/'revision_round2'
spec=importlib.util.spec_from_file_location('checker',r'C:\Users\23201\.codex\skills\nature-response\scripts\check_package_consistency.py')
c=importlib.util.module_from_spec(spec); sys.modules['checker']=c; spec.loader.exec_module(c)
with zipfile.ZipFile(root.parent/'MDPI_submission_source.zip') as z:
    original=z.read('MDPI_submission_source/manuscript.tex').decode('utf-8')
current=(root/'manuscript.tex').read_text(encoding='utf-8')
mask=[False]*len(current)
for match in re.finditer(r'\\(?:revised|revisedcaption)\{',current):
    end=c.matching_brace(current,match.end()-1)
    for i in range(match.start(),end+1): mask[i]=True
for match in re.finditer(r'\\begin\{revisedblock\}.*?\\end\{revisedblock\}',current,re.S):
    for i in range(match.start(),match.end()):mask[i]=True
def tokens(s):
    a=s.index(r'\abstract{'); b=s.index(r'\authorcontributions')
    return [(m.group(),m.start()) for m in re.finditer(r'[A-Za-z]+(?:[-\u2011][A-Za-z]+)*|\d+(?:\.\d+)?',s) if a<=m.start()<b and m.group() not in {'revised','revisedblock','revisedcaption'}]
ot=tokens(original); nt=tokens(current)
uncovered=[]
for tag,a,b,x,y in difflib.SequenceMatcher(None,[t for t,_ in ot],[t for t,_ in nt],autojunk=False).get_opcodes():
    if tag in ['replace','insert']:
        for word,pos in nt[x:y]:
            if not mask[pos] and word not in ['begin','end','color','red','ifshowrevisions','fi']:
                uncovered.append({'line':current.count('\n',0,pos)+1,'token':word})
print('UNCOVERED',json.dumps(uncovered,ensure_ascii=False))
report={'baseline':'MDPI_submission_source.zip!/MDPI_submission_source/manuscript.tex','uncovered_tokens':uncovered,'status':'passed' if not uncovered else 'needs_review'}
(rev/'final_polish_source_audit.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
assert original.replace('\r\n','\n')==(root/'manuscript_pre_round2.tex').read_text(encoding='utf-8').replace('\r\n','\n')
print('Original archive and pre-round2 source agree.')
