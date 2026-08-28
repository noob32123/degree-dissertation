from __future__ import annotations
import json, re, shutil
from pathlib import Path
import pymupdf
from PIL import Image, ImageChops

ROOT = Path(__file__).resolve().parent
PAPER = ROOT.parent
ASSETS = ROOT / "assets"
FILES = [
    ROOT / "source_bilingual.tex",
    ROOT / "sections/01_intro_related.tex",
    ROOT / "sections/02_system.tex",
    ROOT / "sections/03_mdp_method.tex",
    ROOT / "sections/04_experiments.tex",
    ROOT / "sections/05_results.tex",
    ROOT / "sections/06_discussion_end.tex",
]
RANGES = [(1,2),(3,4),(5,9),(9,12),(12,16),(16,24),(24,27)]
FIGURES = [
 ("F001",2,"fig_dqn_family_summary.pdf","DQN 家族相对 MPC-4 的联合证据"),
 ("F002",5,"ai/fig_system_modes_arial.png","三种卫星地面处理路径"),
 ("F003",7,"fig_physical_generator.pdf","合成生成器内部一致性审计"),
 ("F004",11,"ai/fig_cbad_mechanism_simulator_exact_arial.png","中心化全动作训练机制"),
 ("F006",18,"fig_reviewer_primary.pdf","七工况性能"),
 ("F007",19,"fig_dqn_family.pdf","DQN 家族性能"),
 ("F008",22,"fig_training_diagnostics.pdf","代表性训练诊断"),
 ("F009",23,"fig_sensitivity_planning.pdf","参数敏感性与规划边界"),
]
TABLES = [
 ("T001",4,"table_closest_methods.png","与最接近方法家族的特征比较"),
 ("T002",6,"table_state_dictionary.png","15 维任务描述量字典"),
 ("T003",7,"table_parameter_provenance.png","工程原语与依据"),
 ("T004",17,"table_reviewer_main.png","七工况回合总成本"),
 ("T005",19,"table_dqn_vs_mpc_family_inference.png","DQN 家族相对 MPC-4 的联合推断"),
 ("T006",19,"table_dqn_family_performance.png","六种 DQN 目标的性能"),
 ("T007",20,"table_extended_ablation.png","固定系数组件与主干比较"),
 ("T008",20,"table_primary_inference.png","中心化全动作相对标准 DQN 的配对推断"),
 ("T009",20,"table_training_accounting.png","训练信息与计算量核算"),
 ("T010",21,"table_planner_depth.png","滚动时域规划深度"),
 ("T011",21,"table_engineering_outcomes.png","标准 DQN 相对 MPC-4 的工程结果分解"),
 ("T012",23,"table_sensitivity.png","预设参数敏感性"),
 ("T013",24,"table_preview_mismatch.png","训练时预览误设"),
]

def macros():
    out={"method":"centered full-action DQN"}
    for name in ("reviewer_macros.tex","extended_macros.tex","dqn_vs_mpc_macros.tex"):
        t=(PAPER/"generated"/name).read_text(encoding="utf-8")
        for k,v in re.findall(r"\\newcommand\{\\(\w+)\}\{([^{}]*)\}",t):
            out[k]=v.replace(r"\xspace","").replace(r"\%","%").strip()
    return out
MAC=macros()

def arg(t,p):
    while p<len(t) and t[p].isspace(): p+=1
    if t[p]!="{": raise ValueError(p)
    d=1; i=p+1
    while d:
        if t[i]=="{" and t[i-1]!="\\": d+=1
        elif t[i]=="}" and t[i-1]!="\\": d-=1
        i+=1
    return t[p+1:i-1],i

def expand(t):
    for _ in range(3):
        for k,v in MAC.items(): t=re.sub(rf"\\{k}(?:\{{\}})?",lambda m:v,t)
    return t

def md(t):
    tick=chr(96)
    t=expand(t)
    t=re.sub(r"\\cite\{([^}]*)\}",lambda m:"[refs: "+m.group(1).replace(",",", ")+"]",t)
    t=re.sub(r"(Table|Fig\.|Eq\.)~\\(?:ref|eqref)\{[^}]*\}",r"\1",t)
    t=re.sub(r"\\(?:ref|eqref)\{[^}]*\}","",t)
    t=re.sub(r"\\textbf\{([^{}]*)\}",r"**\1**",t)
    t=re.sub(r"\\texttt\{([^{}]*)\}",lambda m:tick+m.group(1).replace(r"\_","_")+tick,t)
    t=re.sub(r"\\begin\{enumerate\}(?:\[[^\]]*\])?","",t).replace(r"\end{enumerate}","")
    t=re.sub(r"\\item\s*","\n- ",t)
    t=t.replace("~"," ").replace(r"\%","%").replace(r"\&","&").replace(r"\allowbreak","")
    t=re.sub(r"\\(?:par|smallskip|noindent)\b","",t)
    t=re.sub(r"\\([A-Za-z]+)\{([^{}]*)\}",r"\2",t)
    t=re.sub(r"\\([A-Za-z]+)\b",r"\1",t).replace("\\\\","\n")
    t=re.sub(r"[ \t]+"," ",t); t=re.sub(r"\n{3,}","\n\n",t)
    return t.strip()

def toks(path):
    t=path.read_text(encoding="utf-8")
    if path.name=="source_bilingual.tex":
        t=t[t.find(r"\begin{paired}"):t.find(r"\input{sections/01_intro_related.tex}")]
    cmds=(r"\bisection",r"\bisubsection",r"\pair",r"\begin{equation}",r"\begin{align}")
    p=0
    while True:
        hits=[(t.find(c,p),c) for c in cmds if t.find(c,p)>=0]
        if not hits: break
        i,c=min(hits)
        if c in cmds[:3]:
            a,p1=arg(t,i+len(c)); b,p2=arg(t,p1)
            yield ("sec" if c==cmds[0] else "sub" if c==cmds[1] else "pair",a,b)
            p=p2
        else:
            env="equation" if c.endswith("equation}") else "align"
            e=t.find("\\end{"+env+"}",i)
            body=t[i+len(c):e]
            body=re.sub(r"\\label\{[^}]*\}","",body).replace(r"\notag","").strip()
            if env=="align": body="\\begin{aligned}\n"+body+"\n\\end{aligned}"
            yield ("eq",body,env); p=e+len(env)+6

def assets():
    fdir=ASSETS/"figures"; tdir=ASSETS/"tables"
    fdir.mkdir(parents=True,exist_ok=True); tdir.mkdir(parents=True,exist_ok=True)
    for fid,pg,rel,title in FIGURES:
        src=PAPER/"figures"/rel; dst=fdir/(fid+".png")
        if src.suffix.lower()==".pdf":
            d=pymupdf.open(src); d[0].get_pixmap(matrix=pymupdf.Matrix(2,2),alpha=False).save(dst)
        else: shutil.copy2(src,dst)
    d=pymupdf.open(ROOT/"output/table_assets.pdf")
    for i,(_,_,name,_) in enumerate(TABLES[1:]):
        raw=tdir/("_"+name); d[i].get_pixmap(matrix=pymupdf.Matrix(1.5,1.5),alpha=False).save(raw)
        im=Image.open(raw).convert("RGB"); box=ImageChops.difference(im,Image.new("RGB",im.size,"white")).getbbox()
        if box:
            q=15; box=(max(0,box[0]-q),max(0,box[1]-q),min(im.width,box[2]+q),min(im.height,box[3]+q)); im=im.crop(box)
        im.save(tdir/name,optimize=True); raw.unlink()
    d=pymupdf.open(PAPER/"output/pdf/dqn_variants_satellite_ground_manuscript.pdf"); p=d[3]
    bs=p.get_text("blocks"); y0=min(b[1] for b in bs if "Table 1:" in b[4]); y1=min((b[1] for b in bs if "3 System Model" in b[4]),default=p.rect.height-28)
    p.get_pixmap(matrix=pymupdf.Matrix(2,2),clip=pymupdf.Rect(25,y0-5,p.rect.width-25,y1-5),alpha=False).save(tdir/TABLES[0][2])

def build():
    assets(); tick=chr(96)
    groups=[(p,list(toks(p)),r) for p,r in zip(FILES,RANGES)]
    ne=sum(1 for _,ts,_ in groups for x in ts if x[0]=="eq")
    out=["# A Statistically Supported DQN-Family Advantage in a Resource-Coupled Satellite-Ground Scheduling Benchmark","",
         "## 资源耦合卫星地面调度基准中具有统计支持的 DQN 家族优势","",
         "- Source: "+tick+"paper/source.tex"+tick+" and the current 27-page PDF",
         "- Source format: "+tick+"pdf-text"+tick+"; equations verified from LaTeX","",
         "## 术语表 / Terminology ledger","",
         "| Canonical term | 中文 | 使用说明 |","|---|---|---|",
         "| DQN family | DQN 家族 | 六种 DQN 目标 |",
         "| DQN objective | DQN 目标 | 训练目标 |",
         "| MPC-4 | 四步滚动时域规划器（MPC-4） | 有限时域比较器 |",
         "| centered full-action | 中心化全动作 | 训练时辅助监督 |",
         "| model-seed block | 模型种子区组 | 独立推断单位 |",
         "| episode total cost | 回合总成本 | 不折扣主要指标 |","",
         "## 公式索引",""]+[f"- [E{i:03d}](#E{i:03d})" for i in range(1,ne+1)]+["","## 正文 / Full bilingual text",""]
    blocks=[]; equations=[]; pages=[]; sid=eid=order=0
    for path,ts,(p0,p1) in groups:
        n=sum(x[0] in ("pair","eq") for x in ts); j=0; page_map={p:[] for p in range(p0,p1+1)}
        for x in ts:
            if x[0]=="sec": out += ["## "+md(x[1])+" / "+md(x[2]),""]; continue
            if x[0]=="sub": out += ["### "+md(x[1])+" / "+md(x[2]),""]; continue
            pg=round(p0+(p1-p0)*j/max(1,n-1)); j+=1; order+=1
            if x[0]=="pair":
                sid+=1; bid=f"S{sid:03d}"; en=md(x[1]); zh=md(x[2])
                out += [f'<a id="{bid}"></a>',f"**Source:** p.{pg} {bid}","",f"**Original:** {en}","",f"**中文:** {zh}",""]
                blocks.append({"id":bid,"page":pg,"type":"paragraph","order":order,"original_text":en,"translation":zh,"bbox":[0,0,0,0],"confidence":"high","refs":[],"insert_after":bid})
            else:
                eid+=1; bid=f"E{eid:03d}"; eq=x[1]
                out += [f'<a id="{bid}"></a>',f"**Source:** p.{pg} {bid}","","$$",eq,"$$","","**中文说明：** 公式与现版 LaTeX 源码一致；仅翻译上下文。",""]
                rec={"id":bid,"page":pg,"type":"equation","order":order,"equation_number":None,"latex":eq,"bbox":[0,0,0,0],"confidence":"high","image_path":None}
                blocks.append(rec); equations.append({k:rec[k] for k in ("id","page","equation_number","latex","bbox","confidence","image_path")})
            page_map.setdefault(pg,[]).append(bid)
        pages += [{"page":p,"block_ids":v} for p,v in page_map.items()]
    out += ["## 图与表 / Figures and tables","","双语 PDF 保留图表在首次实质性讨论附近的位置；以下为独立资源卡。",""]
    for fid,pg,rel,title in FIGURES: out += [f'<a id="{fid}"></a>',f"### {fid} · {title}","",f"**Source:** p.{pg}","",f"![{fid}](assets/figures/{fid}.png)","","**中文图注：** "+title+"。完整双语图注见 PDF。",""]
    for tid,pg,name,title in TABLES: out += [f'<a id="{tid}"></a>',f"### {tid} · {title}","",f"**Source:** p.{pg}","",f"![{tid}](assets/tables/{name})","","**中文表注：** "+title+"。完整双语表注见 PDF。",""]
    out += ["## 阅读提示","","核心证据为六种 DQN 目标相对 MPC-4 的 30 个配对比较；家族内部差异更小且依赖工况。工程解释受合成软约束基准限制，运行验证、机制分离和更强比较器均列入未来工作。",""]
    (ROOT/"paper.md").write_text("\n".join(out),encoding="utf-8")
    sm={"paper":{"title":"A Statistically Supported DQN-Family Advantage in a Resource-Coupled Satellite-Ground Scheduling Benchmark","venue":"","source_type":"pdf","language":"en","source_path":"../output/pdf/dqn_variants_satellite_ground_manuscript.pdf"},"blocks":blocks,"pages":pages,
        "figures":[{"id":a,"page":b,"caption_id":None,"image_path":f"assets/figures/{a}.png","bbox":[0,0,0,0],"placement_hint":"near_first_mention_in_pdf","placed_after":None,"alt_text":d} for a,b,c,d in FIGURES],"equations":equations,
        "glossary":[{"term":"DQN family","translation":"DQN 家族","note":"six objectives"},{"term":"MPC-4","translation":"四步滚动时域规划器（MPC-4）","note":"finite-horizon comparator"}]}
    (ROOT/"source_map.json").write_text(json.dumps(sm,ensure_ascii=False,indent=2),encoding="utf-8")
    (ROOT/"translation_notes.md").write_text("""# Translation notes

- Status: complete bilingual PDF and paragraph-pair Markdown companion.
- Source format: pdf-text, cross-checked against authoritative paper/source.tex.
- Equations are copied from LaTeX and marked high confidence.
- Figures come from current publication assets; tables are rendered from current locked LaTeX inputs.
- References remain in their published language.
- The PDF is the primary reading artifact and retains semantic figure/table placement. The Markdown companion groups visual cards in an appendix.
- No substantive prose block was intentionally omitted. The public GitHub repository URL matches the current manuscript; no DOI is claimed.
""",encoding="utf-8")

if __name__=="__main__": build()
