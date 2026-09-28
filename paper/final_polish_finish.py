from pathlib import Path
import re, zipfile, json, sys, difflib
sys.stdout.reconfigure(encoding='utf-8')
root=Path(r'H:\degree-dissertation\paper\MDPI_submission_source')
rev=root/'revision_round2'
before=rev/'final_polish_baseline'
before.mkdir(exist_ok=True)
for f in rev.glob('*points.tex'):
    dest=before/f.name
    if not dest.exists(): dest.write_bytes(f.read_bytes())
s=(root/'manuscript.tex').read_text(encoding='utf-8')
s=s.replace(r'\newcommand{\revisedcaption}[1]{\color{red}\caption{#1}\color{black}}',r'\newcommand{\revisedcaption}[1]{\captionsetup{labelfont+={color=red},textfont+={color=red}}\caption{#1}}')
# Mark the small new edit outside an existing revision block.
s=s.replace('The uncentered full-action, immediate-advantage, and Double-DQN auxiliary variants inherited',r'The uncentered full-action, immediate-advantage, and \revised{Double-DQN} auxiliary variants inherited')
s=s.replace('Their individual contributions from centering and bootstrapping therefore remain descriptive rather than factorially identified.','These comparisons therefore cannot isolate the individual contributions of centering and bootstrapping.')
# Holm adjusts tests, not percentile intervals; preserve reported numerical evidence.
s=s.replace('Across all four discount factors, every DQN--MPC-4 interval remained below zero after a separate 24-comparison Holm correction.','Across all four discount factors, every DQN--MPC-4 interval remained below zero, and all sign tests remained supported after a separate 24-comparison Holm correction.')
(root/'manuscript.tex').write_text(s,encoding='utf-8')
(root/'manuscript_marked.tex').write_text('\\def\\ShowRevisions{1}\n'+s,encoding='utf-8')
# The standalone response must show actual manuscript numbering, not internal keys.
mapping=r'''% Resolved against the final manuscript; citations and labels are shared by all letters.
\makeatletter
\def\responsecite#1{[\def\responseseparator{}\@for\responsekey:=#1\do{\responseseparator\csname responsecite@\responsekey\endcsname\def\responseseparator{,}}]}
\expandafter\def\csname responsecite@nasa2026avionics\endcsname{26}
\expandafter\def\csname responsecite@nasa2026ground\endcsname{27}
\expandafter\def\csname responsecite@ccsds122\endcsname{28}
\def\responseref#1{\csname responseref@#1\endcsname}
\expandafter\def\csname responseref@tab:parameters\endcsname{3}
\makeatother
\AtBeginDocument{\let\cite\responsecite\let\ref\responseref}
'''
(rev/'manuscript_reference_numbers.tex').write_text(mapping,encoding='utf-8')
for name in ['response_preamble.tex','cover_letter.tex']:
    f=rev/name; t=f.read_text(encoding='utf-8')
    a=t.index('% Reviewer excerpts') if '% Reviewer excerpts' in t else t.index('% Render manuscript')
    b=t.index(r'\newcommand{\ReviewerComment}',a)
    t=t[:a]+r'\input{manuscript_reference_numbers.tex}'+'\n'+t[b:]
    f.write_text(t,encoding='utf-8')
# Exact excerpt location first, followed by other supporting edits.
locations={
1:[r'Quoted text: p.~1, Abstract. Related changes: p.~1, Highlights; pp.~2--3, Introduction; p.~23, Section~5.1; p.~24, Conclusions.',
r'Quoted text: p.~11, Section~3.4.1. Related changes: pp.~17--18, Tables~7--8 and accompanying Results; p.~23, Section~5.1.',
r'Quoted text: p.~21, Section~4.6. Related changes: p.~3, Related Work; pp.~12--13, Section~3.4.3; pp.~20--21, Section~4.6 and Table~12; pp.~23--24, Section~5.2.',
r'Quoted text: p.~20, Section~4.5. Related changes: p.~14, Section~3.4.6; pp.~19--20, Sections~4.4--4.5 and Figures~6--7.',
r'Quoted text: p.~23, Section~5.1. Related changes: pp.~23--24, Section~5.2.'],
2:[r'Quoted text: p.~3, Introduction. Related changes: pp.~2--3, Introduction; p.~23, Section~5.1; p.~24, Conclusions.',
r'Quoted text: p.~21, Section~4.6. Related changes: p.~3, Related Work; pp.~20--21, Section~4.6 and Table~12; pp.~23--24, Section~5.2.',
r'Quoted text: p.~11, Section~3.4.1. Related changes: pp.~17--18, Tables~7--8; p.~23, Sections~5.1--5.2.',
r'Quoted text: p.~13, Section~3.4.3. Related changes: pp.~12--13, Section~3.4.3; pp.~20--21, Section~4.6 and Table~12; p.~22, Discussion.'],
3:[r'Quoted text: p.~21, Section~4.6. Related changes: pp.~12--13, Section~3.4.3; p.~18, Table~10; pp.~20--21, Section~4.6 and Table~12.',
r'Quoted text: p.~6, Section~3.1.2. Related changes: p.~7, Table~3; pp.~23--24, Sections~5.1--5.2 and Conclusions.']}
for i, vals in locations.items():
    f=rev/f'reviewer{i}_points.tex'; t=f.read_text(encoding='utf-8'); it=iter(vals)
    t=re.sub(r'\\ManuscriptLocation\{[^\n]*\}',lambda m:r'\ManuscriptLocation{'+next(it)+'}',t)
    f.write_text(t,encoding='utf-8')
print('Final caption coloring, citation numbers, and explicit excerpt locations updated.')
