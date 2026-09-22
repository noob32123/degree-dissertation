import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = "H:\\degree-dissertation\\paper\\ppt_group_report_20260910";
const TEMPLATE = path.join(ROOT, "template.pptx");
const OUTDIR = path.join(ROOT, "output");
const ASSET = path.join(OUTDIR, "assets", "figures");
const MEDIA = path.join(ROOT, "template-media");
const SKILL_DIR = "C:\\Users\\23201\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.905.11957\\skills\\presentations";
const RUNTIME_PYTHON = "C:\\Users\\23201\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
const FINAL = path.join(OUTDIR, "DQN_Satellite_Ground_Group_Meeting_CN_Ready.pptx");

const helperPath = path.join(SKILL_DIR, "container_tools", "runtime_helpers.mjs");
const { importRuntimeModule } = await import(pathToFileURL(helperPath).href);
const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");
const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools", "artifact_tool_utils.mjs")).href);

await fs.mkdir(OUTDIR, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(TEMPLATE));
const blankLayout = presentation.layouts.items.find((x) => x.name === "空白") ?? presentation.layouts.items[1];
for (const oldSlide of [...presentation.slides.items]) oldSlide.delete();

const W = 1280;
const H = 720;
const FONT = "Microsoft YaHei";
const NAVY = "#244D77";
const TEAL = "#087D96";
const BLUE = "#2A6F9E";
const PALE = "#EAF2F6";
const PALE2 = "#F5F8FA";
const RED = "#B83324";
const DARK = "#17242D";
const GRAY = "#5E6B74";
const LIGHT = "#D7E2E8";
const WHITE = "#FFFFFF";

const bytes = async (p) => new Uint8Array(await fs.readFile(p));
const logoHit = await bytes(path.join(MEDIA, "image3.png"));
const logoLab = await bytes(path.join(MEDIA, "image4.png"));
const coverBg = await bytes(path.join(MEDIA, "image5.png"));
const fig = {};
for (const name of [
  "fig_system_paths.png", "fig_physical_generator.png", "fig_reviewer_primary.png",
  "fig_main_family.png", "fig_dqn_family.png", "fig_sensitivity_planning.png",
  "fig_training_diagnostics.png",
]) fig[name] = await bytes(path.join(ASSET, name));

function addShape(slide, cfg) {
  return slide.shapes.add({ line: { fill: "none", width: 0 }, ...cfg });
}

function addText(slide, text, x, y, w, h, opts = {}) {
  const s = addShape(slide, {
    geometry: "textbox",
    position: { left: x, top: y, width: w, height: h },
    fill: opts.fill ?? "none",
    line: opts.line ?? { fill: "none", width: 0 },
    ...(opts.radius ? { borderRadius: opts.radius } : {}),
  });
  s.text = text;
  s.text.style = {
    typeface: opts.typeface ?? FONT,
    fontSize: opts.size ?? 24,
    bold: opts.bold ?? false,
    color: opts.color ?? DARK,
    alignment: opts.align ?? "left",
    verticalAlignment: opts.valign ?? "middle",
    autoFit: opts.autoFit ?? "none",
    wrap: true,
  };
  return s;
}

function addRect(slide, x, y, w, h, fill, lineFill = "none", lineWidth = 0, radius = 0) {
  return addShape(slide, {
    geometry: "rect",
    position: { left: x, top: y, width: w, height: h },
    fill,
    line: { style: "solid", fill: lineFill, width: lineWidth },
    ...(radius ? { borderRadius: radius } : {}),
  });
}

function addLine(slide, x, y, w, h, color = TEAL, width = 2) {
  return addShape(slide, {
    geometry: "line",
    position: { left: x, top: y, width: w, height: h },
    fill: "none",
    line: { style: "solid", fill: color, width },
  });
}

function addImage(slide, blob, alt, x, y, w, h, fit = "contain") {
  return slide.images.add({ blob, contentType: "image/png", alt, fit, position: { left: x, top: y, width: w, height: h } });
}

function newSlide(section, title, index, takeaway = "") {
  const slide = presentation.slides.add({ layoutId: blankLayout.id });
  slide.shapes.deleteAll();
  slide.background.fill = WHITE;
  addText(slide, section, 42, 12, 510, 28, { size: 18, bold: true, color: TEAL });
  addText(slide, title, 42, 39, 890, 50, { size: 34, bold: true, color: DARK });
  addLine(slide, 42, 96, 1196, 0, TEAL, 3);
  addImage(slide, logoLab, "卫星数据智能计算技术实验室标识", 1092, 17, 55, 55, "contain");
  addImage(slide, logoHit, "哈尔滨工业大学（深圳）标识", 1153, 21, 87, 37, "contain");
  addText(slide, String(index).padStart(2, "0"), 1174, 678, 60, 20, { size: 13, color: GRAY, align: "right" });
  if (takeaway) {
    addRect(slide, 204, 642, 872, 38, RED, RED, 0, 4);
    addText(slide, takeaway, 216, 646, 848, 29, { size: 18, bold: true, color: WHITE, align: "center" });
  }
  return slide;
}

function addNotes(slide, text) {
  slide.speakerNotes.textFrame.setText(text);
}

function addMetric(slide, value, label, x, y, w, color = NAVY) {
  addText(slide, value, x, y, w, 54, { size: 37, bold: true, color, align: "center" });
  addText(slide, label, x, y + 53, w, 38, { size: 17, color: GRAY, align: "center" });
}

function addNumberedPoint(slide, no, heading, body, x, y, w) {
  addText(slide, no, x, y, 65, 60, { size: 32, bold: true, color: WHITE, align: "center", fill: TEAL, radius: 4 });
  addText(slide, heading, x + 84, y - 2, w - 84, 32, { size: 24, bold: true, color: NAVY });
  addText(slide, body, x + 84, y + 28, w - 84, 55, { size: 18, color: DARK, valign: "top" });
}

// 1. Cover
{
  const slide = presentation.slides.add({ layoutId: blankLayout.id });
  slide.shapes.deleteAll();
  slide.background.fill = NAVY;
  addImage(slide, coverBg, "卫星与地球背景图（来自用户提供模板）", 0, 171, W, 269, "cover");
  addRect(slide, 0, 171, W, 269, "#17324FCC", "none", 0);
  addImage(slide, logoHit, "哈尔滨工业大学（深圳）标识", 28, 28, 305, 75, "contain");
  addImage(slide, logoLab, "卫星数据智能计算技术实验室标识", 1170, 35, 72, 72, "contain");
  addText(slide, "卫星数据智能计算技术实验室", 760, 88, 420, 38, { size: 20, bold: true, color: WHITE, align: "right" });
  addText(slide, "资源耦合卫星地面调度中\nDQN 家族优势的统计证据", 105, 205, 1070, 128, { size: 43, bold: true, color: WHITE, align: "center" });
  addText(slide, "Statistical Evidence for a DQN-Family Advantage in a Resource-Coupled Satellite-Ground Scheduling Benchmark", 142, 340, 996, 58, { size: 19, color: "#DCEAF2", align: "center" });
  addText(slide, "汇报人：杨博丞", 160, 477, 960, 50, { size: 27, bold: true, color: WHITE, align: "center" });
  addText(slide, "哈尔滨工业大学（深圳）空天科技学院\n卫星数据智能计算技术实验室", 160, 545, 960, 74, { size: 21, color: "#E5EFF5", align: "center" });
  addText(slide, "2026.09.10", 1015, 668, 205, 24, { size: 15, color: "#CADBE6", align: "right" });
  addNotes(slide, "开场：本报告介绍当前论文的核心问题、方法、统计证据与适用边界。题目和作者信息来自 manuscript.tex；视觉风格及标识来自用户指定模板。建议用 30 秒说明研究对象不是一般任务分配，而是带持续资源状态的卫星—地面序贯调度。" );
}

// 2. Agenda
{
  const slide = newSlide("汇报提纲", "目录", 2);
  const items = [
    ["01", "研究背景与问题"], ["02", "基准与方法"],
    ["03", "实验结果与统计证据"], ["04", "边界与结论"],
  ];
  items.forEach(([n, t], i) => {
    const y = 164 + i * 102;
    addText(slide, n, 270, y, 94, 61, { size: 30, bold: true, color: WHITE, align: "center", fill: i % 2 ? NAVY : TEAL, radius: 4 });
    addText(slide, t, 390, y, 550, 61, { size: 27, bold: true, color: DARK, fill: i % 2 ? PALE2 : PALE, radius: 4 });
  });
  addNotes(slide, "汇报分为四部分：先界定资源耦合调度问题，再说明可复现基准与六种 DQN 目标，随后展示跨场景、跨随机种子的统计证据，最后讨论边界和结论。" );
}

// 3. Background
{
  const slide = newSlide("一、研究背景与问题", "一次调度动作会同时改变多个持续资源状态", 3,
    "关键难点不是单步代价，而是当前动作对后续可行性与累积成本的长期影响。");
  addText(slide, "三种处理路径", 55, 125, 220, 34, { size: 22, bold: true, color: NAVY });
  const actions = [["星上处理", "onboard"], ["地面处理", "ground"], ["星地协同", "collaborative"]];
  actions.forEach(([cn, en], i) => {
    const x = 58 + i * 242;
    addText(slide, cn, x, 172, 200, 48, { size: 23, bold: true, color: WHITE, align: "center", fill: i === 2 ? TEAL : NAVY, radius: 4 });
    addText(slide, en, x, 222, 200, 24, { size: 14, color: GRAY, align: "center" });
  });
  addText(slide, "持续演化的六类资源", 55, 302, 260, 34, { size: 22, bold: true, color: NAVY });
  const resources = ["热状态", "能量", "任务队列", "计算利用率", "链路带宽", "接触时长"];
  resources.forEach((r, i) => {
    const col = i % 3, row = Math.floor(i / 3);
    addText(slide, r, 62 + col * 222, 350 + row * 76, 186, 48, { size: 21, bold: true, color: DARK, align: "center", fill: PALE, line: { style: "solid", fill: LIGHT, width: 1 }, radius: 4 });
  });
  addRect(slide, 790, 145, 405, 393, PALE2, LIGHT, 1, 6);
  addText(slide, "资源耦合", 835, 180, 315, 46, { size: 30, bold: true, color: TEAL, align: "center" });
  addText(slide, "动作会改变热、能量、队列和链路状态；\n这些状态又共同决定后续动作的代价。", 840, 248, 305, 110, { size: 22, color: DARK, align: "center" });
  addLine(slide, 875, 388, 235, 0, TEAL, 2);
  addText(slide, "长期价值学习用于显式处理\n跨时段影响与软约束惩罚", 840, 410, 305, 86, { size: 23, bold: true, color: NAVY, align: "center" });
  addNotes(slide, "对应 manuscript.tex 的 System Model 与 Introduction。强调资源是持久状态而不是独立任务属性。三个动作共同作用于六类资源，因此贪心选择可能把代价推迟到后续时段。" );
}

// 4. Gap and contributions
{
  const slide = newSlide("一、研究背景与问题", "研究问题与三项贡献", 4,
    "研究目标：在匹配训练预算和交互数据的条件下，检验 DQN 家族相对短视规划的稳定优势。");
  addText(slide, "现有证据缺口", 55, 125, 230, 34, { size: 22, bold: true, color: NAVY });
  addText(slide, "许多调度研究在算法、训练预算、测试轨迹和统计检验上并不完全可比，\n难以区分“算法优势”与“实验配置优势”。", 55, 165, 1140, 72, { size: 23, color: DARK, fill: PALE2, line: { style: "solid", fill: LIGHT, width: 1 }, radius: 5 });
  addNumberedPoint(slide, "01", "可复现资源耦合基准", "统一任务生成、资源状态、软约束和评测轨迹。", 78, 282, 1100);
  addNumberedPoint(slide, "02", "匹配条件下比较六种 DQN 目标", "共享网络结构、训练交互和测试场景，仅改变学习目标。", 78, 386, 1100);
  addNumberedPoint(slide, "03", "用联合统计证据界定结论", "跨 20 个模型种子与共享轨迹，报告联合区间、符号检验与敏感性结果。", 78, 490, 1100);
  addNotes(slide, "对应 Introduction 末尾现版本保留的三项贡献。第四点已按作者要求删除，因此本页不新增额外贡献。讲述时突出“匹配条件”和“联合统计证据”，避免把结论泛化到真实飞行环境。" );
}

// 5. System and actions
{
  const slide = newSlide("二、基准与方法", "系统模型：动作路径与六类后置资源", 5,
    "同一任务在三种处理路径之间选择；每条路径对应不同的资源消耗与后续状态。");
  addImage(slide, fig["fig_system_paths.png"], "三种调度动作及六类后置资源的系统示意图", 60, 126, 1160, 475, "contain");
  addText(slide, "图源：论文 Fig. 1（manuscript.tex）", 62, 605, 430, 22, { size: 14, color: GRAY });
  addNotes(slide, "对应论文 Fig. 1。上方是 onboard、ground、collaborative 三种动作，下方是动作后持续演化的资源量。建议按从任务输入到动作、再到资源状态的顺序讲图。" );
}

// 6. Generator
{
  const slide = newSlide("二、基准与方法", "合成任务生成器：保留任务属性间的物理一致性", 6,
    "生成器用于受控统计比较；它体现一致性约束，但不声称拟合真实在轨任务分布。");
  addImage(slide, fig["fig_physical_generator.png"], "合成任务生成器的散点关系与相关性热图", 55, 130, 825, 455, "contain");
  addMetric(slide, "20,000", "独立物理审计任务", 920, 175, 255, TEAL);
  addMetric(slide, "0.660", "数据量—工作量相关系数", 920, 302, 255, NAVY);
  addText(slide, "设计原则", 930, 432, 235, 30, { size: 21, bold: true, color: NAVY, align: "center" });
  addText(slide, "任务属性相关\n资源转换可解释\n随机性可复现", 930, 470, 235, 105, { size: 20, color: DARK, align: "center", fill: PALE, radius: 5 });
  addText(slide, "图源：论文 Fig. 2", 62, 606, 250, 22, { size: 14, color: GRAY });
  addNotes(slide, "对应论文任务生成器审计图。20,000 个独立任务用于检查生成关系，数据量与工作量相关系数为 0.660。需要主动说明：该生成器是可控、可复现的合成基准，不是对真实飞行分布的经验拟合。" );
}

// 7. DQN objective family table
{
  const slide = newSlide("二、基准与方法", "六种 DQN 学习目标及匹配训练条件", 7,
    "统一网络、训练交互和评测轨迹，使差异尽可能归因于目标构造。");
  const values = [
    ["目标变体", "事实动作 Bellman", "全动作辅助", "Double 目标"],
    ["Standard DQN", "是", "否", "否"],
    ["Full-action Q", "是", "Q 值监督", "否"],
    ["Immediate advantage", "是", "即时优势", "否"],
    ["Centered", "是", "中心化优势", "否"],
    ["Double", "是", "否", "是"],
    ["Double + centered", "是", "中心化优势", "是"],
  ];
  const table = slide.tables.add({ rows: values.length, columns: 4, left: 92, top: 145, width: 1096, height: 410, columnWidths: [330, 245, 285, 236], values });
  table.borders.assign({ style: "solid", fill: LIGHT, width: 1 });
  table.cells.block({ row: 0, column: 0, rowCount: 1, columnCount: 4 }).assign({ fill: NAVY, textStyle: { typeface: FONT, fontSize: 19, bold: true, color: WHITE }, anchor: "middle" });
  table.cells.block({ row: 1, column: 0, rowCount: 6, columnCount: 4 }).assign({ textStyle: { typeface: FONT, fontSize: 18, color: DARK }, anchor: "middle", margins: { left: 8, right: 8, top: 4, bottom: 4 } });
  for (let r = 1; r < 7; r++) {
    table.cells.block({ row: r, column: 0, rowCount: 1, columnCount: 4 }).fill = r % 2 ? WHITE : PALE2;
    table.getCell(r, 0).text.style = { typeface: FONT, fontSize: 18, bold: r === 4 || r === 6, color: r === 4 || r === 6 ? TEAL : DARK };
  }
  addText(slide, "注：六个变体均使用相同状态、动作、网络容量、训练交互与评测协议。", 94, 578, 1090, 28, { size: 17, color: GRAY, align: "center" });
  addNotes(slide, "对应 DQN Objective Family。Standard 为事实动作 Bellman；Full-action Q、Immediate advantage、Centered 引入不同的全动作辅助；Double 使用解耦选择与评估；Double + centered 组合两者。这里不把辅助监督表述为额外环境交互，因为它来自同一状态下的模型化动作评价。" );
}

// 8. Evaluation design
{
  const slide = newSlide("二、基准与方法", "评测设计：共享轨迹、独立模型种子与联合推断", 8,
    "支持判据预先固定：均值差为负、95% 区间排除 0，并报告多重比较校正。");
  addMetric(slide, "20", "独立模型种子", 70, 145, 210, TEAL);
  addMetric(slide, "20", "每种子共享测试轨迹", 318, 145, 250, NAVY);
  addMetric(slide, "5", "完全耦合场景", 606, 145, 210, TEAL);
  addMetric(slide, "30", "DQN–MPC-4 对比", 854, 145, 250, NAVY);
  addMetric(slide, "10,000", "联合 bootstrap 重采样", 1090, 145, 150, TEAL);
  addLine(slide, 84, 275, 1110, 0, LIGHT, 2);
  addText(slide, "比较对象", 75, 306, 220, 32, { size: 22, bold: true, color: NAVY });
  const comps = ["Argmin", "MPC-4", "Contextual bandit", "Threshold", "6× DQN"];
  comps.forEach((c, i) => addText(slide, c, 76 + i * 225, 352, 190, 48, { size: 19, bold: true, color: i === 4 ? WHITE : DARK, align: "center", fill: i === 4 ? TEAL : PALE, radius: 4 }));
  addText(slide, "统计证据链", 75, 446, 220, 32, { size: 22, bold: true, color: NAVY });
  const stats = [["①", "逐对配对均值差"], ["②", "联合 95% 区间"], ["③", "Holm 校正符号检验"]];
  stats.forEach(([n, t], i) => {
    const x = 78 + i * 365;
    addText(slide, n, x, 498, 48, 48, { size: 22, bold: true, color: WHITE, align: "center", fill: NAVY, radius: 24 });
    addText(slide, t, x + 58, 495, 270, 54, { size: 20, color: DARK });
  });
  addNotes(slide, "对应 Experimental Design。五个完全耦合场景是 nominal、burst、link-limited、energy-limited、thermal-stress。每个模型种子在 20 条共享 held-out 轨迹上评测。30 个对比来自 6 个 DQN 目标乘 5 个场景。联合 bootstrap 使用 10,000 次重采样，符号检验按 Holm 校正。" );
}

// 9. Performance
{
  const slide = newSlide("三、实验结果与统计证据", "七类场景中的总体表现", 9,
    "在五个完全耦合场景中，DQN 家族均低于所有非 DQN 基线；数值越低越好。");
  addImage(slide, fig["fig_reviewer_primary.png"], "七类场景中各调度器平均成本的比较", 55, 128, 1168, 462, "contain");
  addText(slide, "图源：论文 Fig. 3；Static 与 Reduced 用于诊断，五个 Full regimes 用于主要结论。", 62, 600, 1100, 24, { size: 15, color: GRAY });
  addNotes(slide, "对应论文主结果图。静态和 reduced 场景用于诊断模型在耦合减弱时的行为，主要结论只基于右侧五个 fully coupled regimes。不要把 DQN 在所有七种场景中的排序笼统表述为无条件最优。" );
}

// 10. 30 contrasts
{
  const slide = newSlide("三、实验结果与统计证据", "30/30 个 DQN–MPC-4 对比支持家族优势", 10,
    "最不利比较仍为 −5.92；同时 95% 上界为 −5.03，保持在零以下。");
  addImage(slide, fig["fig_main_family.png"], "30 个 DQN–MPC-4 配对差异及联合区间", 50, 128, 840, 475, "contain");
  addMetric(slide, "30 / 30", "平均差均低于 0", 925, 164, 260, TEAL);
  addMetric(slide, "−5.92", "最不利均值差", 925, 286, 260, NAVY);
  addMetric(slide, "−5.03", "同时 95% 上界", 925, 408, 260, RED);
  addText(slide, "Holm 校正后最大 p = 5.722×10⁻⁵", 915, 535, 280, 40, { size: 17, bold: true, color: DARK, align: "center", fill: PALE, radius: 4 });
  addText(slide, "图源：论文 Fig. 4", 62, 606, 300, 22, { size: 14, color: GRAY });
  addNotes(slide, "核心结论页。差值定义为 DQN 成本减 MPC-4 成本，因此负值表示 DQN 更好。30 个均值差全部为负，且每个配对 95% 区间排除 0。跨全部比较的同时 95% 上界为 −5.03；最不利均值差为 −5.92；Holm 校正符号检验最大 p 值为 5.722e−05。" );
}

// 11. Within family
{
  const slide = newSlide("三、实验结果与统计证据", "DQN 家族内部差异随场景变化", 11,
    "证据支持的是“DQN 家族相对 MPC-4”的稳定优势，而非某一目标在所有场景中绝对占优。");
  addImage(slide, fig["fig_dqn_family.png"], "六种 DQN 目标在五个完全耦合场景中的成本及目标间区间", 50, 132, 870, 455, "contain");
  addText(slide, "Nominal 场景", 955, 180, 235, 30, { size: 21, bold: true, color: NAVY, align: "center" });
  addText(slide, "77.66–78.40", 945, 225, 255, 62, { size: 37, bold: true, color: TEAL, align: "center" });
  addText(slide, "六种 DQN 的成本范围", 945, 287, 255, 28, { size: 17, color: GRAY, align: "center" });
  addLine(slide, 970, 345, 205, 0, LIGHT, 2);
  addText(slide, "Centered", 955, 375, 235, 34, { size: 24, bold: true, color: NAVY, align: "center" });
  addText(slide, "在多个场景中数值最低，\n但领先幅度小且并非处处显著。", 945, 421, 255, 87, { size: 19, color: DARK, align: "center", fill: PALE2, radius: 4 });
  addText(slide, "图源：论文 Fig. 5", 62, 606, 300, 22, { size: 14, color: GRAY });
  addNotes(slide, "对应论文 DQN-family 细分结果。Nominal 下六种目标范围为 77.66–78.40，远小于它们与 MPC-4（90.83）的差距。Centered 在若干场景中最低，但家族内部区间显示差异较小且依场景变化，因此不要宣称 centered 普遍最优。" );
}

// 12. Planning depth native table
{
  const slide = newSlide("三、实验结果与统计证据", "规划深度：成本下降伴随显著运行时间增长", 12,
    "更深的精确规划继续降低成本，但从 H=1 到 H=6，运行时间增长约 327 倍。");
  const values = [
    ["规划深度 H", "枚举序列数", "平均成本", "单步运行时间 (ms)"],
    ["1", "3", "99.33", "0.13"],
    ["2", "9", "92.80", "0.50"],
    ["4", "81", "90.83", "4.82"],
    ["6", "729", "89.35", "42.50"],
  ];
  const table = slide.tables.add({ rows: 5, columns: 4, left: 70, top: 160, width: 770, height: 332, columnWidths: [180, 180, 180, 230], values });
  table.borders.assign({ style: "solid", fill: LIGHT, width: 1 });
  table.cells.block({ row: 0, column: 0, rowCount: 1, columnCount: 4 }).assign({ fill: NAVY, textStyle: { typeface: FONT, fontSize: 18, bold: true, color: WHITE }, anchor: "middle" });
  table.cells.block({ row: 1, column: 0, rowCount: 4, columnCount: 4 }).assign({ textStyle: { typeface: FONT, fontSize: 20, color: DARK }, anchor: "middle" });
  for (let r = 1; r < 5; r++) table.cells.block({ row: r, column: 0, rowCount: 1, columnCount: 4 }).fill = r % 2 ? WHITE : PALE2;
  table.cells.block({ row: 4, column: 0, rowCount: 1, columnCount: 4 }).textStyle.bold = true;
  table.getCell(4, 2).fill = "#D9F0EA";
  table.getCell(4, 3).fill = "#F6DED9";
  addText(slide, "成本", 900, 168, 250, 28, { size: 19, bold: true, color: NAVY, align: "center" });
  addText(slide, "99.33 → 89.35", 890, 207, 270, 55, { size: 31, bold: true, color: TEAL, align: "center" });
  addText(slide, "−10.0%", 930, 264, 190, 28, { size: 18, color: GRAY, align: "center" });
  addLine(slide, 925, 318, 200, 0, LIGHT, 2);
  addText(slide, "运行时间", 900, 342, 250, 28, { size: 19, bold: true, color: NAVY, align: "center" });
  addText(slide, "0.13 → 42.50 ms", 875, 383, 300, 55, { size: 28, bold: true, color: RED, align: "center" });
  addText(slide, "约 327×", 930, 439, 190, 28, { size: 18, color: GRAY, align: "center" });
  addText(slide, "基于 400 条 held-out 轨迹；本文未进行匹配的 DQN 推理延迟测量。", 74, 535, 1095, 32, { size: 17, color: GRAY, align: "center", fill: PALE2, radius: 4 });
  addNotes(slide, "对应规划深度消融。H=1、2、4、6 的成本分别为 99.33、92.80、90.83、89.35，运行时间为 0.13、0.50、4.82、42.50 ms。该表基于 400 条 held-out 轨迹。必须保留限定：没有在同一硬件和实现条件下测量 DQN 推理延迟，因此不能据此声称 DQN 在墙钟时间上快于 MPC。" );
}

// 13. Sensitivity
{
  const slide = newSlide("三、实验结果与统计证据", "参数敏感性与预览误差", 13,
    "参数剖面支持 8/8；预览缩放 ±15% 时各仅支持 3/5 个场景，应按边界而非失败解读。");
  addImage(slide, fig["fig_sensitivity_planning.png"], "参数敏感性及规划预览误差结果", 55, 130, 850, 455, "contain");
  addMetric(slide, "8 / 8", "参数剖面区间低于 0", 940, 170, 250, TEAL);
  addMetric(slide, "0.50–1.66%", "Centered 相对 Standard 改善", 920, 298, 290, NAVY);
  addText(slide, "预览缩放", 950, 434, 230, 28, { size: 19, bold: true, color: NAVY, align: "center" });
  addText(slide, "0.85：3/5 场景支持\n1.15：3/5 场景支持", 930, 472, 270, 82, { size: 19, color: DARK, align: "center", fill: PALE2, radius: 4 });
  addText(slide, "图源：论文 Fig. 6", 62, 606, 300, 22, { size: 14, color: GRAY });
  addNotes(slide, "左侧参数敏感性覆盖 8 个剖面，Centered 相对 Standard 的改善约 0.50%–1.66%，所有配对区间低于 0。右侧预览误差把规划输入统一缩放为 0.85 或 1.15，两种情况下都只有 3/5 场景满足原支持判据，因此只能称部分稳健，不能称对预览误差完全鲁棒。" );
}

// 14. Training + engineering
{
  const slide = newSlide("三、实验结果与统计证据", "训练稳定性与工程指标", 14,
    "成本优势主要来自更少的延迟惩罚；工程指标改善伴随热峰值略高这一权衡。");
  addImage(slide, fig["fig_training_diagnostics.png"], "Standard DQN 与 Centered 目标的训练诊断曲线", 48, 130, 790, 440, "contain");
  addText(slide, "约 220 episodes", 880, 153, 305, 48, { size: 29, bold: true, color: TEAL, align: "center" });
  addText(slide, "Standard 与 Centered 曲线趋于稳定", 875, 202, 315, 48, { size: 17, color: GRAY, align: "center" });
  const eng = [["延迟惩罚", "更低"], ["建模能耗", "更低"], ["时延", "更低"], ["传输数据量", "更低"]];
  eng.forEach(([k, v], i) => {
    const y = 286 + i * 58;
    addText(slide, k, 885, y, 170, 40, { size: 19, color: DARK });
    addText(slide, v, 1060, y, 105, 40, { size: 19, bold: true, color: TEAL, align: "center", fill: PALE, radius: 3 });
  });
  addText(slide, "边界：两者都触及 clipped energy=0；DQN 最大热状态略高。", 850, 535, 360, 55, { size: 16, color: RED, align: "center", fill: "#FAEEEB", radius: 4 });
  addText(slide, "图源：论文 Fig. 7", 62, 606, 300, 22, { size: 14, color: GRAY });
  addNotes(slide, "对应训练诊断和工程分解。曲线在约 220 episodes 后趋于稳定。与 MPC-4 相比，Standard DQN 在五个 fully coupled regimes 中具有更低的延迟惩罚、建模能耗、时延和传输数据量。两者 clipped energy 都到 0，DQN 最大热状态略高，因此应作为资源权衡而不是全面占优来呈现。" );
}

// 15. Scope and reproducibility
{
  const slide = newSlide("四、边界与结论", "适用边界与可复现性", 15,
    "当前结果建立受控基准证据；真实任务标定、硬约束安全性与在轨验证是下一步。");
  addText(slide, "当前证据边界", 72, 132, 310, 38, { size: 23, bold: true, color: NAVY });
  const bounds = [
    "合成任务与固定的无量纲权重",
    "软约束与截断资源状态",
    "全部模型在耦合系数 c=1 下训练",
    "规划器使用完美短期预览",
    "未测量匹配条件下的 DQN 推理延迟",
  ];
  bounds.forEach((t, i) => {
    addRect(slide, 76, 186 + i * 69, 17, 17, i < 2 ? TEAL : NAVY, "none", 0, 8);
    addText(slide, t, 108, 174 + i * 69, 495, 44, { size: 19, color: DARK });
  });
  addRect(slide, 646, 145, 2, 410, LIGHT);
  addText(slide, "可复现材料", 700, 132, 310, 38, { size: 23, bold: true, color: NAVY });
  addText(slide, "公开代码与结果包", 710, 198, 430, 38, { size: 22, bold: true, color: TEAL });
  addText(slide, "github.com/noob32123/\ndqn_family_satellite_ground", 710, 245, 450, 70, { size: 21, color: DARK, fill: PALE, radius: 4 });
  addText(slide, "下一步验证", 710, 360, 430, 38, { size: 22, bold: true, color: TEAL });
  ["真实任务分布标定", "硬约束与安全屏蔽", "不完美预览与分布漂移", "匹配硬件上的端到端时延"].forEach((t, i) => {
    addRect(slide, 716, 416 + i * 35, 10, 10, TEAL, "none", 0, 5);
    addText(slide, t, 738, 402 + i * 35, 420, 34, { size: 18, color: DARK });
  });
  addNotes(slide, "对应 Discussion 和 Data Availability。公开仓库地址来自论文数据可用性声明。边界措辞按当前稿件的审慎表述，不把合成基准结果外推为真实在轨性能。这里可用 45 秒说明后续验证路线。" );
}

// 16. Conclusion
{
  const slide = newSlide("四、边界与结论", "结论", 16);
  addNumberedPoint(slide, "01", "家族级证据稳定", "五个完全耦合场景中的 30 个 DQN–MPC-4 对比全部支持 DQN 家族。", 92, 160, 1070);
  addNumberedPoint(slide, "02", "目标内部差异有限", "不同 DQN 目标的差异较小且依场景变化，不支持“单一目标普遍最优”。", 92, 282, 1070);
  addNumberedPoint(slide, "03", "计算与性能存在权衡", "更深规划继续降低成本，但运行时间快速增长；推理延迟仍需匹配测量。", 92, 404, 1070);
  addLine(slide, 220, 547, 840, 0, TEAL, 2);
  addText(slide, "谢谢聆听 · 敬请批评指正", 240, 568, 800, 55, { size: 31, bold: true, color: NAVY, align: "center" });
  addNotes(slide, "收束在三点：一是家族相对 MPC-4 的统计优势；二是家族内部没有普遍赢家；三是规划质量与计算代价的权衡。最后邀请讨论真实数据标定、硬约束和在线部署评测。" );
}

const workspaceDir = "H:\\degree-dissertation";
const stagingDir = path.join(ROOT, ".codex-finalizer");
await fs.mkdir(stagingDir, { recursive: true });
const candidatePath = path.join(stagingDir, "candidate.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const result = await finalizePresentation({
  explicitTotalSlideCount: 16,
  sourceTemplatePath: TEMPLATE,
  workspaceDir,
  candidatePath,
  finalPath: FINAL,
  pythonExecutable: RUNTIME_PYTHON,
  integrityValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_package_integrity.py"),
  layoutValidatorPath: path.join(SKILL_DIR, "container_tools", "inspect_presentation_layout_geometry.py"),
  layoutArgs: [
    "--expected-slide-size-emu", "12192000,6858000",
    "--validate-heading-fit",
    "--require-native-table-slide", "7",
    "--require-native-table-slide", "12",
  ],
  requiredNativeTableOwnerSlides: [7, 12],
  requiredNativeChartOwnerSlides: [],
  fontPolicy: {
    basis: "design",
    families: [FONT],
  },
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "DQN_Satellite_Ground_Group_Meeting_CN_Ready.validation.json"),
});

console.log(JSON.stringify({ final: FINAL, slides: presentation.slides.items.length, result }, null, 2));
