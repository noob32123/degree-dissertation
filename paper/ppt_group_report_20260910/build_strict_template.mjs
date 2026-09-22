import fs from "node:fs/promises";
import path from "node:path";
import { pathToFileURL } from "node:url";

const ROOT = "H:\\degree-dissertation\\paper\\ppt_group_report_20260910";
const TEMPLATE = path.join(ROOT, "template.pptx");
const OUTDIR = path.join(ROOT, "output");
const ASSET = path.join(OUTDIR, "assets", "figures");
const SKILL_DIR = "C:\\Users\\23201\\.codex\\plugins\\cache\\openai-primary-runtime\\presentations\\26.905.11957\\skills\\presentations";
const RUNTIME_PYTHON = "C:\\Users\\23201\\.cache\\codex-runtimes\\codex-primary-runtime\\dependencies\\python\\python.exe";
const FINAL = path.join(OUTDIR, "资源耦合卫星地面调度_DQN家族_严格模板最终版.pptx");

const helperPath = path.join(SKILL_DIR, "container_tools", "runtime_helpers.mjs");
const { importRuntimeModule } = await import(pathToFileURL(helperPath).href);
const { FileBlob, PresentationFile } = await importRuntimeModule("@oai/artifact-tool");
const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL_DIR, "container_tools", "artifact_tool_utils.mjs")).href);

await fs.mkdir(OUTDIR, { recursive: true });
const presentation = await PresentationFile.importPptx(await FileBlob.load(TEMPLATE));
if (presentation.slides.items.length !== 12) throw new Error("Template slide count changed");

const load = async (name) => new Uint8Array(await fs.readFile(path.join(ASSET, name)));
const figures = {
  system: await load("fig_system_paths.png"),
  physical: await load("fig_physical_generator.png"),
  primary: await load("fig_reviewer_primary.png"),
  main: await load("fig_main_family.png"),
  family: await load("fig_dqn_family.png"),
  sensitivity: await load("fig_sensitivity_planning.png"),
  training: await load("fig_training_diagnostics.png"),
};

function setText(id, value) {
  const shape = presentation.resolve(id);
  shape.text = value;
}

function replaceImage(id, blob, alt) {
  const image = presentation.resolve(id);
  const frame = image.frame;
  const geometry = image.geometry;
  const borderRadius = image.borderRadius;
  const rotation = image.rotation;
  const flipHorizontal = image.flipHorizontal;
  const flipVertical = image.flipVertical;
  const lockAspectRatio = image.lockAspectRatio;
  image.replace({ blob, contentType: "image/png", alt, fit: "contain" });
  image.frame = frame;
  image.crop = { left: 0, top: 0, right: 0, bottom: 0 };
  image.geometry = geometry;
  image.borderRadius = borderRadius;
  image.rotation = rotation;
  image.flipHorizontal = flipHorizontal;
  image.flipVertical = flipVertical;
  image.lockAspectRatio = lockAspectRatio;
}

function setNotes(slideIndex, value) {
  presentation.slides.getItem(slideIndex).speakerNotes.textFrame.setText(value);
}

// Slide 1: cover. Existing branding, background image and every frame remain unchanged.
setText("sh/65g3298r", "资源耦合卫星地面调度中DQN家族的统计优势");
setText("sh/sryl4zqx", "汇报人：杨博丞");
setText("sh/0bmd476t", "哈尔滨工业大学（深圳）  空天科技学院\n卫星数据智能计算技术实验室");
setText("sh/utg3698n", "卫星数据智能计算技术实验室");
setNotes(0, "论文题目：Statistical Evidence for a DQN-Family Advantage in a Resource-Coupled Satellite-Ground Scheduling Benchmark。开场说明研究对象是带持续资源状态的卫星—地面序贯调度。" );

// Slide 2: three-part agenda, matching the template's original length.
setText("sh/9072xkry", "目     录");
setText("sh/a10jqpsj", "  研究背景与问题");
setText("sh/q5wjelsz", "  基准设计与方法");
setText("sh/9wnqhczy", "  实验结果与结论");
setNotes(1, "目录保持模板原有三部分结构：研究背景与问题、基准设计与方法、实验结果与结论。" );

// Slide 3: problem setting.
setText("sh/d0jax03i", "一、研究背景与问题");
setText("sh/943mhgre", "资源耦合卫星地面调度");
setText("sh/cza94vmx", "卫星任务可在星上处理、地面处理或星地协同之间选择。三种动作会共同改变热状态、能量、任务队列、计算利用率、带宽和剩余通信窗口。");
setText("sh/x8nml0ra", "这些资源会跨任务持续演化。当前成本较低的动作可能占用后续任务所需的计算或链路资源，因此调度策略必须考虑长期累积影响。");
setText("sh/obq90bml", "单步成本不足以描述资源耦合调度中的长期代价");
replaceImage("im/o32dw321", figures.system, "三种卫星地面处理路径及六类后置资源");
replaceImage("im/n2tc3y1g", figures.physical, "合成任务生成器的物理一致性审计");
setNotes(2, "对应论文 System Model。左图说明三种动作与六种持续资源；右图说明任务属性间的相关性。contact 指归一化的剩余通信窗口，而不是通信延迟。" );

// Slide 4: question and contribution overview.
setText("sh/0ba143al", "一、研究背景与问题");
setText("sh/p0batw72", "研究问题与主要贡献");
setText("sh/1cj2d8b6", "在匹配网络结构、训练预算和评测轨迹的条件下，本文检验长期价值学习能否稳定优于一步决策与有限视野规划。研究构建了可复现的合成软约束基准，比较六种DQN目标，并在20个模型种子、共享测试轨迹和五个完全耦合场景上进行联合统计推断。");
setText("sh/doj29oba", "研究重点是DQN家族优势及其统计支持，不宣称单一目标普遍最优");
replaceImage("im/83apgj29", figures.main, "DQN家族相对MPC-4的整体证据链");
replaceImage("im/n2187e1o", figures.family, "六种DQN目标的场景表现");
setNotes(3, "对应 Introduction 现版本保留的三项贡献。本页先给出研究问题和证据框架，不把 centered 目标表述为普遍最优。" );

// Slide 5: benchmark architecture.
setText("sh/dgbulwnm", "二、基准设计与方法");
setText("sh/cf2tcr61", "资源状态与决策流程");
setText("sh/n6dcr65o", "1、状态包含15维任务描述、时间与链路相位，以及6维持续资源。\n2、动作包括星上处理、地面处理和星地协同。\n3、解析转移模型统一返回即时成本和动作后的资源状态，用于训练、MPC和部署评测。");
setText("sh/m5kbi1oj", "统一状态、转移与成本模型，保证各调度方法在相同条件下比较");
replaceImage("im/rqdw7qls", figures.system, "资源耦合卫星地面调度的动作与状态框架");
setNotes(4, "对应 Materials and Methods。强调状态包含任务、时间相位和六类持续资源，所有比较方法共享同一解析成本与转移模型。" );

// Slide 6: objective family and training.
setText("sh/yhg7epsj", "二、基准设计与方法");
setText("sh/zi98nu94", "六种DQN学习目标");
setText("sh/oryp8fah", "所有模型采用相同的24维输入、128–128–64网络，并进行38400次真实交互。比较Standard、Full-action Q、Immediate advantage、Centered、Double和Double-centered。辅助变体只在训练阶段使用全动作结果。");
setText("sh/pc76hkr2", "只改变学习目标，其余训练条件和评测轨迹保持一致");
replaceImage("im/6xcbq9cz", figures.training, "Standard DQN与Centered目标的训练诊断");
setNotes(5, "对应 DQN Objective Family 和训练设置。六个目标共享结构、优化器、探索计划和交互预算；模型化替代动作只作为训练辅助，不在部署时调用。" );

// Slide 7: statistical evaluation protocol.
setText("sh/cb2tkvap", "三、实验结果与结论");
setText("sh/dcbud0ra", "统计评测设置");
setText("sh/xcz2l03q", "实验使用20个独立模型种子，每个种子在20条共享保留轨迹上评测。主要结论覆盖5个完全耦合场景，共形成30项家族对比。统计推断采用10000次联合bootstrap和Holm校正符号检验。");
setText("sh/eh4jil4r", "模型、场景与敏感性三类检查");
setText("sh/n6x0fqlo", "支持判据：均值差为负、95%区间排除0，并通过多重比较校正");
replaceImage("im/gb25wj6t", figures.physical, "合成任务生成器审计");
replaceImage("im/hcbmpone", figures.primary, "七类评测场景的总体表现");
replaceImage("im/vat4ne5o", figures.sensitivity, "参数敏感性与规划比较");
setNotes(6, "对应 Experimental Design。主要结论来自5个fully coupled regimes，30个对比等于6个DQN目标乘5个场景。联合bootstrap为10,000次，符号检验使用Holm校正。" );

// Slide 8: overall performance. Hidden template text is also replaced, but object order is untouched.
setText("sh/18byd4zy", "三、实验结果与结论");
setText("sh/g72x4zyd", "七类场景总体表现");
setText("sh/m5gvmhwn", "Static与Reduced用于诊断耦合边界；Nominal、Burst、Link-limited、Energy-limited和Thermal-stress用于主要结论。成本越低越好。");
setText("sh/0jydkreh", "五个完全耦合场景中，DQN家族均低于所有非DQN基线");
replaceImage("im/ep47m9kn", figures.primary, "七类场景中各调度方法的平均成本");
setNotes(7, "对应论文 Fig. 3。静态和reduced场景用于诊断；主要结论只基于五个fully coupled regimes。" );

// Slide 9: family-level evidence.
setText("sh/1cfmhgne", "三、实验结果与结论");
setText("sh/0b65obm9", "DQN家族相对MPC-4的联合证据");
setText("sh/98ji147e", "30个DQN–MPC-4平均差均为负，配对95%区间全部排除0。最不利均值差为−5.92，同时95%上界为−5.03；Holm校正后最大p值为5.722×10⁻⁵。");
setText("sh/ml8j6p8n", "30/30个比较支持DQN家族优势");
replaceImage("im/aho72lwb", figures.main, "30个DQN相对MPC-4的均值差和联合区间");
setNotes(8, "核心结论页。差值定义为DQN成本减MPC-4成本，因此负值表示DQN更好。30个均值差均为负；最不利均值差−5.92，同时95%上界−5.03。" );

// Slide 10: within-family evidence.
setText("sh/xc3mho32", "三、实验结果与结论");
setText("sh/cbu58j2h", "目标内部差异");
setText("sh/xwnupgvy", "Nominal场景中，六种DQN成本为77.66–78.40，MPC-4为90.83。家族内部差异较小并随场景变化。Centered在多个场景中最低，但并非普遍最优。");
setText("sh/atwbelcn", "稳定结论属于DQN家族，目标之间没有普遍赢家");
replaceImage("im/u5obql8f", figures.family, "六种DQN目标在五个完全耦合场景中的比较");
setNotes(9, "对应论文 Fig. 5。Nominal场景六种DQN成本范围为77.66–78.40，家族内部差异小于与MPC-4的差距。" );

// Slide 11: robustness, planning and limitations.
setText("sh/xcryxg7y", "三、实验结果与结论");
setText("sh/wbih4b6d", "敏感性与规划深度");
setText("sh/tsnip0ny", "8个参数剖面均支持Centered相对Standard的改善，幅度为0.5%至1.66%。预览统一缩放±15%时，各有3/5场景满足支持判据。精确规划从H=1增至H=6，成本由99.33降至89.35，运行时间由0.13增至42.50 ms。");
setText("sh/65wzelo7", "结果支持受控合成基准中的长期价值学习，真实任务与硬约束仍需验证");
replaceImage("im/6hkrqp43", figures.sensitivity, "参数敏感性和规划深度比较");
setNotes(10, "对应敏感性、规划深度和Discussion。预览误差±15%只获得部分场景支持。规划越深成本越低，但运行时间快速增长。本文未测量匹配条件下的DQN推理延迟。" );

// Slide 12: closing. Keep the exact closing-slide composition and background.
setText("sh/q903ad4n", "感谢各位聆听！\n敬请批评指正！");
setNotes(11, "结束页。" );

const workspaceDir = "H:\\degree-dissertation";
const stagingDir = path.join(ROOT, ".codex-finalizer-strict");
await fs.mkdir(stagingDir, { recursive: true });
const candidatePath = path.join(stagingDir, "candidate-strict.pptx");
await (await PresentationFile.exportPptx(presentation)).save(candidatePath);

const result = await finalizePresentation({
  explicitTotalSlideCount: 12,
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
  ],
  requiredNativeTableOwnerSlides: [],
  requiredNativeChartOwnerSlides: [],
  verifyArtifactToolImport: true,
  receiptPath: path.join(stagingDir, "strict-template-final.validation.json"),
});

console.log(JSON.stringify({ final: FINAL, slideCount: presentation.slides.items.length, result }, null, 2));
