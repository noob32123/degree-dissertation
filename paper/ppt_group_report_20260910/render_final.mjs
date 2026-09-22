import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = "H:\\degree-dissertation\\paper\\ppt_group_report_20260910";
const PPTX = path.join(ROOT, "output", "DQN_Satellite_Ground_Group_Meeting_CN_Ready.pptx");
const RENDER = path.join(ROOT, "output", "rendered-ready");
const helperPath = "C:\\Users\\23201\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.905.11957\\skills\\presentations\\container_tools\\runtime_helpers.mjs";
const { importRuntimeModule } = await import(pathToFileURL(helperPath).href);
const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");

await fs.mkdir(RENDER, { recursive: true });
const p = await PresentationFile.importPptx(await FileBlob.load(PPTX));
for (let i = 0; i < p.slides.items.length; i++) {
  const blob = await p.export({ slide: p.slides.items[i], format: "png", scale: 1 });
  const out = path.join(RENDER, `slide-${String(i + 1).padStart(2, "0")}.png`);
  await fs.writeFile(out, new Uint8Array(await blob.arrayBuffer()));
}
console.log(JSON.stringify({ slides: p.slides.items.length, renderDir: RENDER }));
