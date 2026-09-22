import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = "H:\\degree-dissertation\\paper\\ppt_uavgen_cvpr2026";
const TEMPLATE = "C:\\Users\\23201\\Desktop\\组会报告26.7.5.pptx";
const OUTPUT = path.join(ROOT, "output", "UAVGen_CVPR2026_组会汇报_严格模板版.pptx");
const FIG = path.join(ROOT, "assets", "figures");
const SKILL = "C:\\Users\\23201\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.909.12148\\skills\\presentations";
const PYTHON = "C:\\Users\\23201\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";

const { importRuntimeModule } = await import(pathToFileURL(path.join(SKILL, "container_tools", "runtime_helpers.mjs")).href);
const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");
const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL, "container_tools", "artifact_tool_utils.mjs")).href);
const presentation = await PresentationFile.importPptx(await FileBlob.load(TEMPLATE));
if (presentation.slides.items.length !== 12) throw new Error("Template is not 12 slides");

const img = async (name) => new Uint8Array(await fs.readFile(path.join(FIG, name)));
function setText(id, value) {
  presentation.resolve(id).text = value;
}
async function replaceImage(id, name, alt) {
  const image = presentation.resolve(id);
  const properties = {
    frame: image.frame,
    geometry: image.geometry,
    borderRadius: image.borderRadius,
    rotation: image.rotation,
    flipHorizontal: image.flipHorizontal,
    flipVertical: image.flipVertical,
    lockAspectRatio: image.lockAspectRatio,
  };
  image.replace({ blob: await img(name), contentType: "image/png", alt, fit: "contain" });
  image.frame = properties.frame;
  image.crop = { left: 0, top: 0, right: 0, bottom: 0 };
  image.geometry = properties.geometry;
  image.borderRadius = properties.borderRadius;
  image.rotation = properties.rotation;
  image.flipHorizontal = properties.flipHorizontal;
  image.flipVertical = properties.flipVertical;
  image.lockAspectRatio = properties.lockAspectRatio;
}
function notes(slide, value) {
  presentation.slides.getItem(slide - 1).speakerNotes.textFrame.setText(value);
}

// 1. Cover: template background and logos are intentionally untouched.
setText("sh/65g3298r", "视觉原型条件化的无人机目标检测数据生成");
setText("sh/sryl4zqx", "CVPR 2026 论文汇报：UAVGen");
setText("sh/0bmd476t", "原文作者：Wenhao Li、Zimeng Wu、Yu Wu、Zehua Fu、Jiaxin Chen\n北京航空航天大学");
setText("sh/utg3698n", "Visual Prototype Conditioned Focal Region Generation");
notes(1, "论文：Visual Prototype Conditioned Focal Region Generation for UAV-Based Object Detection，CVPR 2026，3772–3782。汇报结构严格沿用原始12页组会模板。原文：https://openaccess.thecvf.com/content/CVPR2026/papers/Li_Visual_Prototype_Conditioned_Focal_Region_Generation_for_UAV-Based_Object_Detection_CVPR_2026_paper.pdf");

// 2. Agenda: three original agenda rows are retained.
setText("sh/9072xkry", "目    录");
setText("sh/a10jqpsj", "  问题背景与研究动机");
setText("sh/q5wjelsz", "  UAVGen 方法与数据流程");
setText("sh/9wnqhczy", "  实验结果与结论");
notes(2, "第一部分讲无人机目标检测的标注数据不足及通用生成方法的问题；第二部分讲 VPC-DM 和 FRE-DP；第三部分讲 VisDrone、UAVDT 的结果与消融。");

// 3. Background: two original picture slots compare existing synthesis and its UAV difficulty.
setText("sh/d0jax03i", "一、问题背景与研究动机");
setText("sh/943mhgre", "无人机目标检测的数据瓶颈");
setText("sh/cza94vmx", "无人机图像中的目标常小而密集，并伴随遮挡与尺度变化。标注数据有限，使检测器难以覆盖复杂场景。");
setText("sh/x8nml0ra", "通用布局到图像生成依赖类别与框位置，却常在小目标边界产生模糊或漏生成；不一致的合成标签还可能伤害检测训练。");
setText("sh/obq90bml", "核心问题：怎样生成更可信、标签更一致的无人机训练图像？");
await replaceImage("im/o32dw321", "fig4_baselines.png", "图4：GeoDiffusion 和 AeroGen 在密集目标上的生成问题");
await replaceImage("im/n2tc3y1g", "fig1_general.png", "图1a：常规布局到图像生成流程");
notes(3, "左图取自论文图4的两个基线方法，黄虚线表示与布局不一致或模糊的区域；右图是论文图1(a)所示常规布局到图像生成。不要将个例视作总体统计结果。");

// 4. Core idea: keep the original two-picture comparison composition.
setText("sh/0ba143al", "一、问题背景与研究动机");
setText("sh/p0batw72", "从整图生成转向焦点区域生成");
setText("sh/1cj2d8b6", "UAVGen 将类别对应的高质量视觉原型融入布局条件，在目标密集区优先生成，再把局部图像拼回整图，并以检测器修正漏生成、多生成和框偏移。");
setText("sh/doj29oba", "核心思路：提高小目标保真度，同时控制图像—标签不一致");
await replaceImage("im/83apgj29", "fig1_general.png", "图1a：常规生成仅依赖布局信息");
await replaceImage("im/n2187e1o", "fig1_uavgen.png", "图1b：UAVGen 引入焦点区域、视觉原型及标签修正");
notes(4, "两图来自原论文图1。左为常规数据生成，右为 UAVGen。VPC-DM 提升生成条件质量，FRE-DP 侧重目标密集区域并执行标签修正。");

// 5. Full architecture.
setText("sh/dgbulwnm", "二、UAVGen 方法与数据流程");
setText("sh/cf2tcr61", "UAVGen：整体架构");
setText("sh/n6dcr65o", "1、VPC-DM：筛选清晰且定位可靠的视觉原型，联合布局和文本条件生成图像。\n2、FRE-DP：聚类目标中心，生成焦点区域并拼接；最后修正标签。");
setText("sh/m5kbi1oj", "两个模块分别提升生成保真度与合成数据的训练可用性");
await replaceImage("im/rqdw7qls", "fig2_architecture.png", "图2：UAVGen 的 VPC-DM 与 FRE-DP 总体架构");
notes(5, "论文图2。上半部分是 FRE-DP，下半部分是 VPC-DM。讲述顺序建议先 VPC-DM 条件构建，再讲 FRE-DP 区域生成及标签修正。图中的 trainable/frozen 由原论文给出。");

// 6. Mechanism details.
setText("sh/yhg7epsj", "二、UAVGen 方法与数据流程");
setText("sh/zi98nu94", "VPC-DM：视觉原型与多源条件");
setText("sh/oryp8fah", "从检测候选中按定位、置信度和类别内特征筛选原型；图像编码器构成视觉原型布局，文本与位置编码补充场景和对象语义。");
setText("sh/pc76hkr2", "视觉原型＋布局语义共同约束扩散生成，使小目标外观更稳定");
await replaceImage("im/6xcbq9cz", "fig2_vpcdm.png", "图2下半部分：视觉原型条件化扩散模型");
notes(6, "VPC-DM：预训练检测器获取可靠候选；同类原型经聚合形成增强布局；全局文本、对象文本和位置编码共同注入生成网络。训练时对目标区域赋予更高损失权重。原论文图2与第3.2节。");

// 7. Evaluation: three original picture slots use one fixed VisDrone example.
setText("sh/cb2tkvap", "三、实验结果与结论");
setText("sh/dcbud0ra", "实验数据与评估方式");
setText("sh/xcz2l03q", "VisDrone：6471 张训练图、10 类目标；UAVDT：24143 张训练图。\n生成质量用 FID↓，检测性能用 mAP、AP50 和尺度分组 AP↑。\n主实验使用 GFL-ResNet50；另用 RemDet-X 检查迁移效果。");
setText("sh/eh4jil4r", "同一 VisDrone 样例：真实图、AeroGen、UAVGen");
setText("sh/n6x0fqlo", "FID 衡量图像分布接近程度；AP 衡量合成数据对检测训练的实际价值");
await replaceImage("im/gb25wj6t", "fig4_gt_top.png", "图4第一行：VisDrone 真实图像");
await replaceImage("im/hcbmpone", "fig4_aerogen_top.png", "图4第一行：AeroGen 生成图像");
await replaceImage("im/vat4ne5o", "fig4_uavgen_top.png", "图4第一行：UAVGen 生成图像");
notes(7, "VisDrone：6471 train/548 val/1580 test；UAVDT：24143 train/16592 test。扩散模型以 FLUX 为基础，512×512 分辨率训练与生成。图片来自论文图4第一行，依次是真实、AeroGen、UAVGen；它们只是定性样例。");

// 8. Template's edge-to-edge standalone image slide: replace only its one picture.
setText("sh/18byd4zy", "三、实验结果与结论");
setText("sh/g72x4zyd", "生成图像的定性对比");
setText("sh/m5gvmhwn", "图4显示，UAVGen 对小而密集的目标具有更清晰的外观与更好的布局一致性。");
setText("sh/0jydkreh", "原论文图4：黄色虚线标出模糊或与布局不符的目标");
await replaceImage("im/ep47m9kn", "fig4_qualitative.png", "原论文图4：Layout、GT、GeoDiffusion、AeroGen、UAVGen 三组定性对比");
notes(8, "此页保留模板原有通栏图片版式，仅替换成论文图4的完整对照主体。图4仅用于展示生成质量，不作为 FID 或 AP 的统计替代。左右列依次是布局、真值、GeoDiffusion、AeroGen、UAVGen。");

// 9. Main quantitative findings.
setText("sh/1cfmhgne", "三、实验结果与结论");
setText("sh/0b65obm9", "主结果：生成质量与检测精度");
setText("sh/98ji147e", "VisDrone：mAP 24.5→25.9，FID 48.04→34.34。\nUAVDT：mAP 14.5→16.6，FID 31.99→29.73。");
setText("sh/ml8j6p8n", "UAVGen 在两组数据上同时改善 FID 与检测 mAP");
await replaceImage("im/aho72lwb", "table1_main.png", "表1：VisDrone 与 UAVDT 的 FID、mAP 及分尺度 AP 对比");
notes(9, "原论文表1。FID 对比中的 AeroGen 与 UAVGen 分别为：VisDrone 48.04、34.34；UAVDT 31.99、29.73。检测 mAP 与真实数据基线对比：VisDrone 24.5 到25.9，UAVDT 14.5 到16.6。FID 仅使用 VPC-DM 评估，检测训练使用完整 UAVGen 管线，注意二者设置不同。");

// 10. Component ablation.
setText("sh/xc3mho32", "三、实验结果与结论");
setText("sh/cbu58j2h", "消融：两个模块均有贡献");
setText("sh/xwnupgvy", "仅加入生成图像：mAP 24.5→23.8。\nVPC-DM 完整：25.2；再加入 FRE-DP：25.9。\n焦点区域 256 分辨率表现最佳。");
setText("sh/atwbelcn", "VPC-DM 与 FRE-DP 各带来约 0.7 个 mAP 点提升");
await replaceImage("im/u5obql8f", "ablation_combined.png", "表3、表4及图5：模块、区域分辨率和数据量消融");
notes(10, "原论文表3、表4和图5。表3：真实数据24.5；仅生成23.8；视觉原型+布局编码25.2；完整管线25.9。表4：焦点区域分辨率1024/512/256对应mAP 25.3/25.6/25.9。右图为不同合成图像数量表现。");

// 11. Cross-detector transfer and efficiency, with an explicit boundary.
setText("sh/xcryxg7y", "三、实验结果与结论");
setText("sh/wbih4b6d", "迁移效果、数据效率与边界");
setText("sh/tsnip0ny", "RemDet-X：mAP 29.8→30.2。\n仅增 100 张合成图，mAP 25.0，接近 AeroGen 用 6474 张图的 24.9。\n跨高度与视角变化仍待验证。");
setText("sh/65wzelo7", "结论适用于所测数据与检测器；真实场景泛化仍是后续问题");
await replaceImage("im/6hkrqp43", "table2_fig5_transfer_efficiency.png", "表2与图5：RemDet-X 迁移效果和合成图像数量消融");
notes(11, "原论文表2：RemDet-X 在 VisDrone 上，真实数据29.8，UAVGen 30.2；对照方法 mAP 不高于29.4。图5：100张UAVGen合成图像对应mAP25.0，AeroGen 6474张对应24.9。论文结论提到真实无人机场景的视角和高度变化仍是未来研究方向，因此不能宣称已验证全面泛化。");

// 12. Closing: background image and template composition are unchanged.
setText("sh/q903ad4n", "感谢聆听！\n欢迎批评指正！");
notes(12, "感谢聆听。原文与代码地址见第一页讲稿备注；图表均来自原论文。");

const staging = path.join(ROOT, ".finalizer");
await fs.mkdir(staging, { recursive: true });
await fs.mkdir(path.dirname(OUTPUT), { recursive: true });
const candidatePath = path.join(staging, "candidate-uavgen.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);
const result = await finalizePresentation({
  explicitTotalSlideCount: 12,
  sourceTemplatePath: TEMPLATE,
  workspaceDir: "H:\\degree-dissertation",
  candidatePath,
  finalPath: OUTPUT,
  pythonExecutable: PYTHON,
  integrityValidatorPath: path.join(SKILL, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: ["--expected-slide-size-emu", "12192000,6858000", "--validate-heading-fit"],
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
  verifyArtifactToolImport: true,
  receiptPath: path.join(staging, "validation.json"),
});
console.log(JSON.stringify({ output: OUTPUT, slideCount: presentation.slides.items.length, result }, null, 2));
