import { pathToFileURL } from "node:url";
const hp="C:\\Users\\23201\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.905.11957\\skills\\presentations\\container_tools\\runtime_helpers.mjs";
const {importRuntimeModule}=await import(pathToFileURL(hp).href);
const {FileBlob,PresentationFile}=await importRuntimeModule("@oai/artifact-tool");
const p=await PresentationFile.importPptx(await FileBlob.load("H:\\degree-dissertation\\paper\\ppt_group_report_20260910\\output\\DQN_Satellite_Ground_Group_Meeting_CN_Final.pptx"));
const x=await p.inspect({kind:"shape,textbox,image",slide:15,maxChars:30000});
console.log(x.ndjson);
