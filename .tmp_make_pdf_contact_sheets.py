from pathlib import Path
from PIL import Image, ImageOps, ImageDraw
root = Path(r"H:\degree-dissertation\paper\MDPI_submission_source\revision_round2\qa_final")
for folder in sorted(p for p in root.iterdir() if p.is_dir()):
    pages = sorted(folder.glob("page-*.png"))
    for start in range(0, len(pages), 12):
        batch = pages[start:start+12]
        thumbs=[]
        for path in batch:
            im=Image.open(path).convert("RGB")
            im.thumbnail((360,510))
            canvas=Image.new("RGB", (380,550), "white")
            canvas.paste(im, ((380-im.width)//2,20))
            ImageDraw.Draw(canvas).text((10,530), path.stem, fill="black")
            thumbs.append(canvas)
        sheet=Image.new("RGB", (380*4,550*3), (225,225,225))
        for i,im in enumerate(thumbs):
            sheet.paste(im, ((i%4)*380,(i//4)*550))
        out=root/f"{folder.name}_contact_{start//12+1:02d}.jpg"
        sheet.save(out, quality=88)
        print(out)
