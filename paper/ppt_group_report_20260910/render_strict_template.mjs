import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = "H:\\degree-dissertation\\paper\\ppt_group_report_20260910";
const PPTX = path.join(ROOT, "output", "资源耦合卫星地面调度_DQN家族_严格模板最终版.pptx");
const RENDER = path.join(ROOT, "output", "rendered-strict-template-final");
const helperPath = "C:\\Users\\23201\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.905.11957\\skills\\presentations\\container_tools\\runtime_helpers.mjs";
const { importRuntimeModule } = await import(pathToFileURL(helperPath).href);
const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");

await fs.mkdir(RENDER, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(PPTX));
for (let i = 0; i < presentation.slides.items.length; i++) {
  const blob = await presentation.export({ slide: presentation.slides.items[i], format: "png", scale: 1 });
  await fs.writeFile(path.join(RENDER, `slide-${String(i + 1).padStart(2, "0")}.png`), new Uint8Array(await blob.arrayBuffer()));
}
console.log(JSON.stringify({ slides: presentation.slides.items.length, renderDir: RENDER }));
