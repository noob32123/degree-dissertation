from pathlib import Path

from PIL import Image


ROOT = Path(r"H:\degree-dissertation\paper\ppt_uavgen_cvpr2026")
PAGES = ROOT / "source" / "pages_240dpi"
OUT = ROOT / "assets" / "figures"
OUT.mkdir(parents=True, exist_ok=True)


def crop(page: int, box: tuple[int, int, int, int], name: str) -> Path:
    image = Image.open(PAGES / f"page-{page:02d}.png").convert("RGB")
    target = OUT / name
    image.crop(box).save(target, quality=96)
    return target


def fit_on_white(image: Image.Image, size: tuple[int, int]) -> Image.Image:
    image = image.copy()
    image.thumbnail(size, Image.Resampling.LANCZOS)
    canvas = Image.new("RGB", size, "white")
    x = (size[0] - image.width) // 2
    y = (size[1] - image.height) // 2
    canvas.paste(image, (x, y))
    return canvas


crop(1, (1055, 855, 1875, 1075), "fig1_general.png")
crop(1, (1055, 1080, 1880, 1310), "fig1_uavgen.png")
crop(3, (185, 225, 1835, 1425), "fig2_architecture.png")
crop(3, (245, 610, 1800, 1405), "fig2_vpcdm.png")
crop(3, (250, 1000, 1180, 1395), "fig2_visual_prototypes.png")
crop(6, (390, 340, 1645, 960), "table1_main.png")
crop(6, (390, 340, 1645, 755), "table1_visdrone.png")
crop(6, (390, 755, 1645, 960), "table1_uavdt.png")
crop(6, (190, 990, 920, 1815), "fig3_categories.png")
crop(7, (270, 225, 1770, 805), "fig4_qualitative.png")
crop(7, (855, 225, 1480, 805), "fig4_baselines.png")
crop(7, (565, 225, 875, 445), "fig4_gt_top.png")
crop(7, (1170, 225, 1475, 445), "fig4_aerogen_top.png")
crop(7, (1475, 225, 1780, 445), "fig4_uavgen_top.png")
crop(7, (260, 1235, 925, 1560), "table2_remdet.png")
crop(8, (190, 450, 1830, 1225), "ablation_combined.png")
crop(8, (1050, 235, 1840, 1015), "fig5_data_scale.png")

remdet = Image.open(OUT / "table2_remdet.png").convert("RGB")
scale = Image.open(OUT / "fig5_data_scale.png").convert("RGB")
combined = Image.new("RGB", (1800, 900), "white")
combined.paste(fit_on_white(remdet, (760, 860)), (20, 20))
combined.paste(fit_on_white(scale, (980, 860)), (800, 20))
combined.save(OUT / "table2_fig5_transfer_efficiency.png", quality=96)

print(f"Created {len(list(OUT.glob('*.png')))} figure assets in {OUT}")
