from pathlib import Path
from pypdf import PdfReader
from PIL import Image,ImageDraw
import re,unicodedata,json,sys,subprocess
sys.stdout.reconfigure(encoding='utf-8')
root=Path(r'H:\degree-dissertation\paper\MDPI_submission_source'); rev=root/'revision_round2'; out=rev/'qa_final_delivery';out.mkdir(exist_ok=True)
files=[root/'manuscript_clean.pdf',root/'manuscript_marked.pdf']+[rev/(n+'.pdf') for n in ['cover_letter','response_reviewer1','response_reviewer2','response_reviewer3']]
texts={p.stem:[x.extract_text() or '' for x in PdfReader(p).pages] for p in files}
def norm(t):return re.sub('[^a-z]','',unicodedata.normalize('NFKC',t).lower())
report={'pdf_pages':{n:len(ts) for n,ts in texts.items()},'quotes':[]}
for n,ts in texts.items():
 assert not any('??' in t for t in ts),n+' unresolved reference'
 assert not any('nasa2026' in t or 'tab:parameters' in t for t in ts),n+' literal internal reference'
clean=texts['manuscript_clean']; cover=norm('\n'.join(texts['cover_letter']))
for i in range(1,4):
 t='\n'.join(texts[f'response_reviewer{i}'])
 # Remove isolated footer page numbers before matching across pages.
 t=re.sub(r'(?m)^\d+\s*$','',t)
 chunks=re.findall(r'Revised manuscript text\.\s*(.*?)Location in the revised manuscript PDF\.\s*Quoted text: p\.\s*(\d+)',t,re.S)
 assert len(chunks)=={1:5,2:4,3:2}[i],(i,len(chunks))
 for j,(excerpt,page) in enumerate(chunks,1):
  normalized=norm(excerpt); hits=[k+1 for k,p in enumerate(clean) if normalized in norm(p)]
  if int(page) not in hits: raise AssertionError((i,j,page,hits,excerpt[:100]))
  assert normalized in cover,(i,j,'not in cover')
  report['quotes'].append({'reviewer':i,'comment':j,'page':int(page),'verbatim_pdf_match':True})
 # Compare Comments and Responses separately, ignoring visual linebreaks/hyphenation.
 for segment in re.findall(r'Comment\.\s*(.*?)Revised manuscript text\.',t,re.S):
  assert norm(segment) in cover,(i,'comment/response not identical in cover')
report['status']='passed'
(rev/'final_pdf_consistency.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
poppler=Path(r'C:\Users\23201\.cache\codex-runtimes\codex-primary-runtime\dependencies\native\poppler\Library\bin\pdftoppm.exe')
for p in files:
 folder=out/p.stem;folder.mkdir(exist_ok=True)
 subprocess.run([str(poppler),'-png','-r','85',str(p),str(folder/'page')],check=True)
 pages=sorted(folder.glob('page-*.png'))
 for start in range(0,len(pages),8):
  sheet=Image.new('RGB',(1520,1100),'#dddddd')
  for idx,path in enumerate(pages[start:start+8]):
   im=Image.open(path).convert('RGB');im.thumbnail((365,515))
   x=idx%4*380;y=idx//4*550;sheet.paste(im,(x,y));ImageDraw.Draw(sheet).text((x+8,y+520),path.stem,fill='black')
  sheet.save(out/f'{p.stem}_{start//8+1}.jpg',quality=90)
print('Rendered all final pages and contact sheets.')
