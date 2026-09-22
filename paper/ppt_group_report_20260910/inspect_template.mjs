import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const sourcePath = "H:\\degree-dissertation\\paper\\ppt_group_report_20260910\\template.pptx";
const outDir = "H:\\degree-dissertation\\paper\\ppt_group_report_20260910\\template-inspect";
const helperPath = "C:\\Users\\23201\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.905.11957\\skills\\presentations\\container_tools\\runtime_helpers.mjs";
const { importRuntimeModule } = await import(pathToFileURL(helperPath).href);
const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");

await fs.rm(outDir, { recursive: true, force: true });
await fs.mkdir(path.join(outDir, "source-slides"), { recursive: true });
await fs.mkdir(path.join(outDir, "layouts"), { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(sourcePath));
const slides = presentation.slides.items;
for (let i = 0; i < slides.length; i += 1) {
  const tag = String(i + 1).padStart(2, "0");
  const preview = await presentation.export({ slide: slides[i], format: "png", scale: 1 });
  await fs.writeFile(path.join(outDir, "source-slides", `source-slide-${tag}.png`), new Uint8Array(await preview.arrayBuffer()));
  const layout = await presentation.export({ slide: slides[i], format: "layout" });
  await fs.writeFile(path.join(outDir, "layouts", `source-slide-${tag}.layout.json`), await layout.text());
}
const inspection = await presentation.inspect({ kind: "slide,textbox,shape,image,table,chart,notes,layout", maxChars: 300000 });
await fs.writeFile(path.join(outDir, "template-inspect.ndjson"), inspection.ndjson ?? "", "utf8");
await fs.writeFile(path.join(outDir, "summary.json"), JSON.stringify({
  slideCount: slides.length,
  slideSize: presentation.slideSize,
  masters: presentation.masters?.items?.length ?? null,
  layouts: presentation.layouts?.items?.length ?? null,
  inspectTruncated: Boolean(inspection.truncated),
}, null, 2));
console.log(JSON.stringify({ slideCount: slides.length, slideSize: presentation.slideSize }));
