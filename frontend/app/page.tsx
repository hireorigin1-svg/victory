"use client";

import { FormEvent, ReactNode, useEffect, useMemo, useState } from "react";
import {
  Aperture,
  Box,
  CheckCircle2,
  Clapperboard,
  Copy,
  FileText,
  LogIn,
  Map,
  Plus,
  RefreshCw,
  Upload,
  WandSparkles
} from "lucide-react";
import {
  CameraProfile,
  Character,
  DirectorWorkflow,
  DirectorWorkflowEvaluation,
  DirectorOSV2RunResponse,
  DirectorRunResponse,
  FeedbackLoopResponse,
  EnvironmentRecord,
  LLMInteraction,
  SceneRecord,
  ShotRecord,
  approveShot,
  createCamera,
  createCharacter,
  createEnvironment,
  createProp,
  createScene,
  createShot,
  evaluateDirectorWorkflow,
  getFilmBible,
  listCameras,
  listCharacters,
  listEnvironments,
  listProps,
  listScenes,
  listShots,
  listWorkflowLLMInteractions,
  login,
  reviewDirectorWorkflow,
  getBrainSummary,
  getProductionAnalytics,
  getProviderBehaviorSummary,
  runDirector,
  runDirectorOSV2,
  runABTest,
  compileVisualPlan,
  ingestReference,
  seedCinematography,
  getEvaluationDashboard,
  getExperimentPlan,
  getGeneLearning,
  getProviderDNA,
  getResearchReport,
  debatePrompt,
  runBenchmark,
  runAutonomousBatch,
  seedBenchmarks,
  seedProviderCapabilities,
  selectReferences,
  submitHumanReview,
  symbolicPrompt,
  runFeedbackLoop,
  saveFilmBible,
  startDirectorWorkflow,
  uploadMedia,
  uploadDirectorWorkflowResult
} from "@/lib/api";
import { Field } from "@/components/Field";

const emptyCharacter = { name: "", face: "", hair: "", clothes: "", accessories: "" };
const emptyEnvironment = { location: "", architecture: "", lighting: "", weather: "", time: "" };
const emptyCamera = { name: "", lens: "", camera_angle: "", movement: "", aspect_ratio: "2.39:1", film_look: "" };
const emptyProp = { name: "", category: "object", description: "", position: "", damage_state: "" };
const emptyScene = { scene_number: "1", script: "", timeline: "" };
const emptyShot = { shot_number: "1", user_instruction: "", lighting: "", emotion: "", pose: "" };
const emptyDirector = { script: "", user_instruction: "", max_attempts: "5" };
const emptyDirectorOSV2 = { script: "", user_instruction: "", provider: "higgsfield", max_attempts: "5", claude_review_below: "95" };
const emptySimpleDirector = { director_instruction: "", lighting: "", emotion: "", pose: "" };
const emptyWorkflowUpload = { image_url: "", video_url: "" };
const emptyBible = {
  project_name: "Default Project",
  lighting_style: "consistent cinematic naturalism",
  color_palette: "saffron, deep teal, warm gold",
  camera_rules: "preserve lens language unless scene changes",
  lens_package: "35mm anamorphic, 50mm portrait",
  action_rules: "only change position when script explicitly requires it",
  weather_rules: "weather remains stable inside a scene",
  continuity_rules: "previous approved visual memory is ground truth"
};
const emptyReference = { image_url: "mock://approved/reference-1", quality_score: "100" };

const fieldPresets: Record<string, string[]> = {
  face: [
    "oval heroic face",
    "round youthful face",
    "sharp angular face",
    "broad strong jaw",
    "soft expressive face",
    "aged wise face",
    "divine calm face",
    "battle-worn face",
    "canonical approved face"
  ],
  hair: [
    "long flowing black hair",
    "tied topknot",
    "shoulder-length wavy hair",
    "short neat hair",
    "braided hair",
    "silver aged hair",
    "wind-swept hair",
    "wet rain-soaked hair",
    "canonical approved hair"
  ],
  clothes: [
    "orange silk dhoti",
    "temple robes",
    "royal armor",
    "battle armor",
    "forest travel costume",
    "gold embroidered costume",
    "simple village costume",
    "ceremonial costume",
    "canonical approved costume"
  ],
  accessories: [
    "gold crown",
    "sacred thread",
    "arm bands",
    "necklace",
    "earrings",
    "waist belt",
    "weapon holster",
    "no accessories",
    "canonical approved accessories"
  ],
  location: [
    "ancient temple entrance",
    "palace corridor",
    "forest path",
    "mountain cliff",
    "battlefield",
    "royal court",
    "village street",
    "ocean shore",
    "Lanka city street",
    "interior chamber"
  ],
  architecture: [
    "South Indian temple architecture",
    "golden palace architecture",
    "stone cave architecture",
    "wooden village architecture",
    "ruined ancient architecture",
    "mythic fortress architecture",
    "dense forest environment",
    "open natural landscape",
    "canonical approved environment"
  ],
  lighting: [
    "soft golden sunrise",
    "warm sunset backlight",
    "overcast diffused daylight",
    "moonlit blue night",
    "torch-lit interior",
    "dramatic rim light",
    "high contrast battle light",
    "soft devotional glow",
    "canonical approved lighting"
  ],
  weather: [
    "clear sky",
    "cloudy",
    "light rain",
    "heavy rain",
    "mist",
    "storm",
    "dusty wind",
    "humid haze",
    "same as previous shot"
  ],
  time: [
    "dawn",
    "morning",
    "midday",
    "golden hour",
    "sunset",
    "blue hour",
    "night",
    "same time as previous shot"
  ],
  lens: [
    "24mm wide",
    "35mm cinematic",
    "50mm natural",
    "65mm portrait",
    "85mm close portrait",
    "100mm telephoto",
    "anamorphic 35mm",
    "same lens as previous shot"
  ],
  camera_angle: [
    "eye-level",
    "low angle heroic",
    "high angle vulnerable",
    "over-the-shoulder",
    "profile side angle",
    "three-quarter angle",
    "top-down",
    "same camera angle as previous shot"
  ],
  movement: [
    "locked-off static",
    "slow push in",
    "slow pull back",
    "tracking left",
    "tracking right",
    "handheld subtle",
    "crane up",
    "orbit around subject",
    "same movement as previous shot"
  ],
  aspect_ratio: ["2.39:1", "16:9", "1.85:1", "4:3", "9:16"],
  film_look: [
    "epic mythological cinema",
    "realistic historical drama",
    "Rajamouli-style scale",
    "devotional cinematic realism",
    "dark battle sequence",
    "soft romantic drama",
    "high detail premium VFX",
    "same film look as previous shot"
  ],
  category: [
    "weapon",
    "vehicle",
    "jewelry",
    "costume item",
    "ritual object",
    "set dressing",
    "food",
    "document",
    "object"
  ],
  position: [
    "held in right hand",
    "held in left hand",
    "on waist",
    "on shoulder",
    "on ground foreground",
    "background left",
    "background right",
    "center frame",
    "same position as previous shot"
  ],
  damage_state: [
    "new",
    "slightly worn",
    "dusty",
    "blood-stained",
    "burned",
    "broken",
    "wet",
    "same damage state as previous shot"
  ],
  emotion: [
    "calm",
    "devotional",
    "determined",
    "angry",
    "sad",
    "fearful",
    "surprised",
    "victorious",
    "exhausted",
    "same emotion as previous shot"
  ],
  pose: [
    "standing still",
    "walking forward",
    "looking left",
    "looking right",
    "looking up",
    "kneeling",
    "holding weapon ready",
    "hands folded",
    "mid-action",
    "same pose as previous shot"
  ],
  timeline: [
    "before battle",
    "during battle",
    "after battle",
    "morning continuation",
    "same moment as previous scene",
    "flashback",
    "time jump",
    "night continuation"
  ],
  lighting_style: [
    "consistent cinematic naturalism",
    "soft devotional glow",
    "dramatic mythological realism",
    "warm torch-lit interiors",
    "high contrast battle lighting",
    "natural daylight continuity"
  ],
  color_palette: [
    "saffron, deep teal, warm gold",
    "earth tones, muted green, temple stone",
    "crimson, gold, charcoal",
    "moon blue, silver, deep black",
    "sunset amber, dusty brown, royal red",
    "forest green, warm skin tones, soft gold"
  ],
  camera_rules: [
    "preserve lens language unless scene changes",
    "keep eye-line direction continuous",
    "avoid changing camera height within a dialogue beat",
    "use heroic low angle only for power moments",
    "match previous approved camera unless script changes it"
  ],
  lens_package: [
    "35mm anamorphic, 50mm portrait",
    "24mm wide, 35mm medium, 85mm close-up",
    "35mm natural, 65mm portrait, 100mm detail",
    "anamorphic 35mm, anamorphic 50mm, anamorphic 75mm"
  ],
  action_rules: [
    "only change position when script explicitly requires it",
    "prop hand continuity must be preserved",
    "emotion changes must follow the script beat",
    "movement should inherit from previous approved shot",
    "avoid sudden costume or body changes"
  ],
  weather_rules: [
    "weather remains stable inside a scene",
    "rain must leave visible wetness in following shots",
    "dust must remain on costume until cleaned by story",
    "daylight weather cannot change without timeline reason"
  ],
  continuity_rules: [
    "previous approved visual memory is ground truth",
    "Film Bible overrides user instruction unless director approves",
    "character identity must match canonical approved images",
    "costume and props inherit from the previous approved shot",
    "warn before changing face, hair, costume, weather, or location"
  ]
};

function presetsFor(name: string) {
  return fieldPresets[name] ?? [];
}

export default function Home() {
  const [token, setToken] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("Sign in with your Victory director account.");
  const [characters, setCharacters] = useState<Character[]>([]);
  const [environments, setEnvironments] = useState<EnvironmentRecord[]>([]);
  const [cameras, setCameras] = useState<CameraProfile[]>([]);
  const [props, setProps] = useState<{ id: string; name: string; category: string }[]>([]);
  const [scenes, setScenes] = useState<SceneRecord[]>([]);
  const [shots, setShots] = useState<ShotRecord[]>([]);
  const [characterForm, setCharacterForm] = useState(emptyCharacter);
  const [environmentForm, setEnvironmentForm] = useState(emptyEnvironment);
  const [cameraForm, setCameraForm] = useState(emptyCamera);
  const [propForm, setPropForm] = useState(emptyProp);
  const [sceneForm, setSceneForm] = useState(emptyScene);
  const [shotForm, setShotForm] = useState(emptyShot);
  const [directorForm, setDirectorForm] = useState(emptyDirector);
  const [simpleDirectorForm, setSimpleDirectorForm] = useState(emptySimpleDirector);
  const [workflowUpload, setWorkflowUpload] = useState(emptyWorkflowUpload);
  const [uploadingMedia, setUploadingMedia] = useState(false);
  const [workflowReviewReasons, setWorkflowReviewReasons] = useState("");
  const [directorWorkflow, setDirectorWorkflow] = useState<DirectorWorkflow | null>(null);
  const [workflowInteractions, setWorkflowInteractions] = useState<LLMInteraction[]>([]);
  const [workflowEvaluation, setWorkflowEvaluation] = useState<DirectorWorkflowEvaluation | null>(null);
  const [bibleForm, setBibleForm] = useState(emptyBible);
  const [directorResult, setDirectorResult] = useState<DirectorRunResponse | null>(null);
  const [directorOSV2Form, setDirectorOSV2Form] = useState(emptyDirectorOSV2);
  const [directorOSV2Result, setDirectorOSV2Result] = useState<DirectorOSV2RunResponse | null>(null);
  const [feedbackResult, setFeedbackResult] = useState<FeedbackLoopResponse | null>(null);
  const [brainSummary, setBrainSummary] = useState("No experiments yet.");
  const [researchSummary, setResearchSummary] = useState("No provider behavior learned yet.");
  const [analyticsSummary, setAnalyticsSummary] = useState("No production analytics yet.");
  const [referenceForm, setReferenceForm] = useState(emptyReference);
  const [referenceSummary, setReferenceSummary] = useState("No reference set selected.");
  const [visualPlanSummary, setVisualPlanSummary] = useState("No visual plan compiled.");
  const [benchmarkId, setBenchmarkId] = useState("");
  const [evaluationSummary, setEvaluationSummary] = useState("No benchmark data yet.");
  const [researchOpsSummary, setResearchOpsSummary] = useState("Research ops idle.");
  const [selectedSceneId, setSelectedSceneId] = useState("");
  const [selectedEnvironmentId, setSelectedEnvironmentId] = useState("");
  const [selectedCameraId, setSelectedCameraId] = useState("");

  async function refresh(authToken = token) {
    if (!authToken) return;
    const [nextCharacters, nextEnvironments, nextCameras, nextProps, nextScenes, nextShots] =
      await Promise.all([
        listCharacters(authToken),
        listEnvironments(authToken),
        listCameras(authToken),
        listProps(authToken),
        listScenes(authToken),
        listShots(authToken)
      ]);
    setCharacters(nextCharacters);
    setEnvironments(nextEnvironments);
    setCameras(nextCameras);
    setProps(nextProps);
    setScenes(nextScenes);
    setShots(nextShots);
    getFilmBible(authToken)
      .then((bible) =>
        setBibleForm({
          project_name: bible.project_name,
          lighting_style: bible.lighting_style ?? "",
          color_palette: bible.color_palette.join(", "),
          camera_rules: bible.camera_rules.join("\n"),
          lens_package: bible.lens_package.join(", "),
          action_rules: bible.action_rules.join("\n"),
          weather_rules: bible.weather_rules.join("\n"),
          continuity_rules: bible.continuity_rules.join("\n")
        })
      )
      .catch(() => undefined);
    getBrainSummary(authToken)
      .then((summary) =>
        setBrainSummary(
          `${summary.total_experiments} experiments, ${summary.acceptance_rate}% accepted`
        )
      )
      .catch(() => undefined);
    Promise.all([
      getProviderBehaviorSummary(authToken, "mock"),
      getProductionAnalytics(authToken),
      getEvaluationDashboard(authToken)
    ])
      .then(([behavior, analytics, evaluation]) => {
        setResearchSummary(`${behavior.records} behavior records, avg face ${behavior.average_face_score}%`);
        setAnalyticsSummary(
          `${analytics.average_generations_to_approval} avg retries, providers ${Object.keys(analytics.success_rate_by_provider).length}`
        );
        setEvaluationSummary(
          `${evaluation.benchmark_count} benchmarks, avg ${evaluation.average_overall_score}%, north star ${evaluation.north_star.value}`
        );
      })
      .catch(() => undefined);
    setSelectedSceneId((current) => current || nextScenes[0]?.id || "");
    setSelectedEnvironmentId((current) => current || nextEnvironments[0]?.id || "");
    setSelectedCameraId((current) => current || nextCameras[0]?.id || "");
  }

  useEffect(() => {
    const saved = window.localStorage.getItem("cinemind-token");
    if (saved) {
      setToken(saved);
      refresh(saved).catch((error) => setMessage(error.message));
    }
  }, []);

  const latestPrompt = useMemo(
    () => directorWorkflow?.higgsfield_prompt ?? directorResult?.prompt ?? shots.find((shot) => shot.prompt)?.prompt ?? "Run the Director Engine or create a shot to compile the first prompt.",
    [directorWorkflow, directorResult, shots]
  );

  async function handleLogin(event: FormEvent) {
    event.preventDefault();
    try {
      const nextToken = await login(email, password);
      window.localStorage.setItem("cinemind-token", nextToken);
      setToken(nextToken);
      setMessage("Director console connected.");
      await refresh(nextToken);
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Login failed");
    }
  }

  async function submit<T extends Record<string, string>>(
    event: FormEvent,
    action: () => Promise<unknown>,
    success: string,
    reset: (value: T) => void,
    empty: T
  ) {
    event.preventDefault();
    try {
      await action();
      reset(empty);
      setMessage(success);
      await refresh();
    } catch (error) {
      setMessage(error instanceof Error ? error.message : "Save failed");
    }
  }

  return (
    <main className="min-h-screen">
      <header className="border-b border-line bg-white">
        <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-5 py-4">
          <div className="flex items-center gap-3">
            <span className="grid size-10 place-items-center rounded bg-ink text-white">
              <Clapperboard size={21} />
            </span>
            <div>
              <h1 className="text-xl font-semibold">Victory</h1>
              <p className="text-sm text-ink/65">Continuity-first filmmaking system</p>
            </div>
          </div>
          <button
            className="inline-flex h-9 items-center gap-2 rounded border border-line bg-white px-3 text-sm"
            onClick={() => refresh().catch((error) => setMessage(error.message))}
            type="button"
          >
            <RefreshCw size={15} />
            Refresh
          </button>
        </div>
      </header>

      <div className="mx-auto grid max-w-7xl gap-5 px-5 py-5 xl:grid-cols-[300px_1fr]">
        <aside className="grid content-start gap-5">
          <Panel title="Session" icon={<LogIn size={18} />}>
            <form className="grid gap-3" onSubmit={handleLogin}>
              <Field label="Email" name="email" value={email} onChange={(_, v) => setEmail(v)} type="email" />
              <Field label="Password" name="password" value={password} onChange={(_, v) => setPassword(v)} type="password" />
              <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-signal px-3 text-sm font-semibold text-white">
                <LogIn size={16} />
                Login
              </button>
              <p className="text-sm text-ink/65">{message}</p>
            </form>
          </Panel>

          <Panel title="Compiled Prompt" icon={<WandSparkles size={18} />}>
            <pre className="max-h-[420px] overflow-auto whitespace-pre-wrap rounded border border-line bg-panel p-3 text-xs leading-5">
              {latestPrompt}
            </pre>
            {directorResult?.warnings.length ? (
              <div className="mt-3 rounded border border-caution/40 bg-caution/10 p-3 text-sm text-ink">
                {directorResult.warnings.map((warning) => (
                  <p key={warning}>{warning}</p>
                ))}
              </div>
            ) : null}
          </Panel>
          <Panel title="Director Brain" icon={<WandSparkles size={18} />}>
            <div className="grid gap-3">
              <Metric label="Memory" value={brainSummary} />
              <Metric label="Provider Research" value={researchSummary} />
              <Metric label="Production Analytics" value={analyticsSummary} />
              {feedbackResult ? (
                <>
                  <Metric label="Loop Score" value={`${feedbackResult.quality_report?.overall_continuity_score ?? 0}%`} />
                  <Metric label="Prompt Versions" value={String(feedbackResult.versions)} />
                </>
              ) : null}
            </div>
          </Panel>
        </aside>

        <section className="grid gap-5">
          <Panel title="Film Bible" icon={<FileText size={18} />}>
            <form
              className="grid gap-3 md:grid-cols-2"
              onSubmit={(event) =>
                submit(
                  event,
                  () =>
                    saveFilmBible(token, {
                      project_name: bibleForm.project_name,
                      lighting_style: bibleForm.lighting_style,
                      color_palette: splitList(bibleForm.color_palette),
                      camera_rules: splitLines(bibleForm.camera_rules),
                      lens_package: splitList(bibleForm.lens_package),
                      action_rules: splitLines(bibleForm.action_rules),
                      weather_rules: splitLines(bibleForm.weather_rules),
                      continuity_rules: splitLines(bibleForm.continuity_rules)
                    }),
                  "Film Bible saved. It now overrides lower-priority prompt inputs.",
                  setBibleForm,
                  bibleForm
                )
              }
            >
              {Object.entries(bibleForm).map(([name, value]) => (
                <Field
                  key={name}
                  label={labelize(name)}
                  name={name}
                  value={value}
                  options={presetsFor(name)}
                  textarea={name.includes("rules")}
                  onChange={(field, nextValue) =>
                    setBibleForm((current) => ({ ...current, [field]: nextValue }))
                  }
                />
              ))}
              <SubmitButton label="Save Film Bible" />
            </form>
          </Panel>

          <Panel title="Director OS v2" icon={<Clapperboard size={18} />}>
            <form
              className="grid gap-3 md:grid-cols-3"
              onSubmit={async (event) => {
                event.preventDefault();
                try {
                  const result = await runDirectorOSV2(token, {
                    script: directorOSV2Form.script,
                    user_instruction: directorOSV2Form.user_instruction,
                    scene_id: selectedSceneId || null,
                    provider: directorOSV2Form.provider,
                    max_attempts: Number(directorOSV2Form.max_attempts),
                    claude_review_below: Number(directorOSV2Form.claude_review_below)
                  });
                  setDirectorOSV2Result(result);
                  setMessage(`Director OS v2 built a ${result.provider} prompt with ${result.confidence_score}% blueprint confidence.`);
                  await refresh();
                } catch (error) {
                  setMessage(error instanceof Error ? error.message : "Director OS v2 failed");
                }
              }}
            >
              <Select label="Scene" value={selectedSceneId} onChange={setSelectedSceneId} options={scenes.map((item) => ({ value: item.id, label: `Scene ${item.scene_number}` }))} />
              <Select
                label="Provider"
                value={directorOSV2Form.provider}
                onChange={(value) => setDirectorOSV2Form((current) => ({ ...current, provider: value }))}
                options={[
                  { value: "higgsfield", label: "Higgsfield" },
                  { value: "veo", label: "Veo" },
                  { value: "kling", label: "Kling" },
                  { value: "runway", label: "Runway" }
                ]}
              />
              <Field label="Claude Below" name="claude_review_below" value={directorOSV2Form.claude_review_below} onChange={(f, v) => setDirectorOSV2Form((c) => ({ ...c, [f]: v }))} />
              <div className="md:col-span-3">
                <Field label="Script" name="script" value={directorOSV2Form.script} textarea onChange={(f, v) => setDirectorOSV2Form((c) => ({ ...c, [f]: v }))} />
              </div>
              <div className="md:col-span-3">
                <Field label="Director Instruction" name="user_instruction" value={directorOSV2Form.user_instruction} textarea onChange={(f, v) => setDirectorOSV2Form((c) => ({ ...c, [f]: v }))} />
              </div>
              <Field label="Max Attempts" name="max_attempts" value={directorOSV2Form.max_attempts} onChange={(f, v) => setDirectorOSV2Form((c) => ({ ...c, [f]: v }))} />
              <SubmitButton label="Run OS v2" />
            </form>
            {directorOSV2Result ? (
              <div className="mt-4 grid gap-4">
                <div className="grid gap-3 md:grid-cols-4">
                  <Metric label="Blueprint Confidence" value={`${directorOSV2Result.confidence_score}%`} />
                  <Metric label="Provider" value={directorOSV2Result.provider} />
                  <Metric label="Evaluation" value={`${directorOSV2Result.evaluation.overall_continuity_score}%`} />
                  <Metric label="Decision" value={directorOSV2Result.decision} />
                </div>
                <div className="grid gap-3 lg:grid-cols-2">
                  <PromptBox title="Shot Blueprint" value={JSON.stringify(directorOSV2Result.blueprint, null, 2)} />
                  <PromptBox title="Knowledge Packet" value={JSON.stringify(directorOSV2Result.knowledge_packet, null, 2)} />
                  <PromptBox title="GPT Reasoning Prompt" value={directorOSV2Result.gpt_prompt} />
                  <PromptBox title="Claude Review" value={JSON.stringify(directorOSV2Result.claude_review ?? { skipped: true }, null, 2)} />
                </div>
                <PromptBox title="Translated Provider Prompt" value={directorOSV2Result.translated_prompt} copy />
                <PromptBox title="Learning Record" value={JSON.stringify(directorOSV2Result.learning_record, null, 2)} />
              </div>
            ) : null}
          </Panel>

          <Panel title="Director Workflow" icon={<Clapperboard size={18} />}>
            <form
              className="grid gap-3 md:grid-cols-3"
              onSubmit={async (event) => {
                event.preventDefault();
                try {
                  const workflow = await startDirectorWorkflow(token, {
                    ...simpleDirectorForm,
                    scene_id: selectedSceneId || null,
                    shot_number: shots.length + 1,
                    camera_id: selectedCameraId || null,
                    environment_id: selectedEnvironmentId || null
                  });
                  setDirectorWorkflow(workflow);
                  setWorkflowInteractions(await listWorkflowLLMInteractions(token, workflow.id));
                  setWorkflowEvaluation(null);
                  setMessage("GPT and Claude generated Higgsfield prompts from the stored DB context.");
                  await refresh();
                } catch (error) {
                  setMessage(error instanceof Error ? error.message : "Director workflow failed");
                }
              }}
            >
              <div className="md:col-span-3">
                <Field
                  label="Director Instruction"
                  name="director_instruction"
                  value={simpleDirectorForm.director_instruction}
                  textarea
                  onChange={(field, value) => setSimpleDirectorForm((current) => ({ ...current, [field]: value }))}
                />
              </div>
              <Select label="Scene" value={selectedSceneId} onChange={setSelectedSceneId} options={scenes.map((item) => ({ value: item.id, label: `Scene ${item.scene_number}` }))} />
              <Select label="Camera" value={selectedCameraId} onChange={setSelectedCameraId} options={cameras.map((item) => ({ value: item.id, label: item.name }))} />
              <Select label="Environment" value={selectedEnvironmentId} onChange={setSelectedEnvironmentId} options={environments.map((item) => ({ value: item.id, label: item.location }))} />
              {["lighting", "emotion", "pose"].map((field) => (
                <Field
                  key={field}
                  label={labelize(field)}
                  name={field}
                  options={presetsFor(field)}
                  value={simpleDirectorForm[field as keyof typeof simpleDirectorForm]}
                  onChange={(name, value) => setSimpleDirectorForm((current) => ({ ...current, [name]: value }))}
                />
              ))}
              <SubmitButton label="Generate Prompt" />
            </form>

            {directorWorkflow ? (
              <div className="mt-4 grid gap-4">
                <div className="grid gap-3 lg:grid-cols-3">
                  <PromptBox title="GPT Prompt" value={directorWorkflow.gpt_prompt ?? ""} />
                  <PromptBox title="Claude Prompt" value={directorWorkflow.claude_prompt ?? ""} />
                  <PromptBox title="Higgsfield Prompt" value={directorWorkflow.higgsfield_prompt ?? ""} copy />
                </div>
                <div className="grid gap-3 md:grid-cols-2">
                  <MediaFileField
                    label="Upload Image"
                    accept="image/*"
                    disabled={uploadingMedia}
                    onChange={async (file) => {
                      if (!file) return;
                      setUploadingMedia(true);
                      try {
                        const upload = await uploadMedia(token, file);
                        setWorkflowUpload((current) => ({ ...current, image_url: upload.url }));
                        setMessage("Image uploaded and URL added to the workflow.");
                      } catch (error) {
                        setMessage(error instanceof Error ? error.message : "Image upload failed");
                      } finally {
                        setUploadingMedia(false);
                      }
                    }}
                  />
                  <MediaFileField
                    label="Upload Video"
                    accept="video/*"
                    disabled={uploadingMedia}
                    onChange={async (file) => {
                      if (!file) return;
                      setUploadingMedia(true);
                      try {
                        const upload = await uploadMedia(token, file);
                        setWorkflowUpload((current) => ({ ...current, video_url: upload.url }));
                        setMessage("Video uploaded and URL added to the workflow.");
                      } catch (error) {
                        setMessage(error instanceof Error ? error.message : "Video upload failed");
                      } finally {
                        setUploadingMedia(false);
                      }
                    }}
                  />
                  <Field
                    label="Image URL"
                    name="image_url"
                    value={workflowUpload.image_url}
                    onChange={(field, value) => setWorkflowUpload((current) => ({ ...current, [field]: value }))}
                  />
                  <Field
                    label="Video URL"
                    name="video_url"
                    value={workflowUpload.video_url}
                    onChange={(field, value) => setWorkflowUpload((current) => ({ ...current, [field]: value }))}
                  />
                  <button
                    className="inline-flex h-10 items-center justify-center gap-2 rounded bg-ink px-3 text-sm font-semibold text-white"
                    type="button"
                    onClick={async () => {
                      const workflow = await uploadDirectorWorkflowResult(token, directorWorkflow.id, workflowUpload);
                      setDirectorWorkflow(workflow);
                      setWorkflowInteractions(await listWorkflowLLMInteractions(token, workflow.id));
                      setMessage("Higgsfield result uploaded and stored against this workflow.");
                      await refresh();
                    }}
                  >
                    <Upload size={16} />
                    Upload Result
                  </button>
                  <button
                    className="inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold"
                    type="button"
                    onClick={async () => {
                      const evaluation = await evaluateDirectorWorkflow(token, directorWorkflow.id);
                      setWorkflowEvaluation(evaluation);
                      setMessage(`AI Evaluation complete: ${evaluation.overall}% overall.`);
                      await refresh();
                    }}
                  >
                    <RefreshCw size={16} />
                    AI Evaluation
                  </button>
                </div>
                {workflowEvaluation ? (
                  <div className="grid gap-3 md:grid-cols-5">
                    <Metric label="Face" value={`${workflowEvaluation.face}%`} />
                    <Metric label="Costume" value={`${workflowEvaluation.costume}%`} />
                    <Metric label="Environment" value={`${workflowEvaluation.environment}%`} />
                    <Metric label="Lighting" value={`${workflowEvaluation.lighting}%`} />
                    <Metric label="Overall" value={`${workflowEvaluation.overall}%`} />
                  </div>
                ) : null}
                <div className="grid gap-3">
                  <Field
                    label="Review Reasons"
                    name="review_reasons"
                    value={workflowReviewReasons}
                    textarea
                    onChange={(_, value) => setWorkflowReviewReasons(value)}
                  />
                  <div className="grid gap-3 md:grid-cols-2">
                    <button
                      className="inline-flex h-10 items-center justify-center gap-2 rounded bg-signal px-3 text-sm font-semibold text-white"
                      type="button"
                      onClick={async () => {
                        const workflow = await reviewDirectorWorkflow(token, directorWorkflow.id, {
                          approved: true,
                          image_url: workflowUpload.image_url || null,
                          video_url: workflowUpload.video_url || null,
                          reasons: splitLines(workflowReviewReasons)
                        });
                        setDirectorWorkflow(workflow);
                        setWorkflowInteractions(await listWorkflowLLMInteractions(token, workflow.id));
                        setMessage("Approved shot saved with image/video/prompt and visual memory.");
                        await refresh();
                      }}
                    >
                      <CheckCircle2 size={16} />
                      Approved
                    </button>
                    <button
                      className="inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold"
                      type="button"
                      onClick={async () => {
                        const workflow = await reviewDirectorWorkflow(token, directorWorkflow.id, {
                          approved: false,
                          image_url: workflowUpload.image_url || null,
                          video_url: workflowUpload.video_url || null,
                          reasons: splitLines(workflowReviewReasons)
                        });
                        setDirectorWorkflow(workflow);
                        setWorkflowInteractions(await listWorkflowLLMInteractions(token, workflow.id));
                        setMessage("Rejected shot stored. GPT and Claude generated improved prompts.");
                        await refresh();
                      }}
                    >
                      Rejected
                    </button>
                  </div>
                </div>
                {directorWorkflow.improved_gpt_prompt || directorWorkflow.improved_claude_prompt ? (
                  <div className="grid gap-3 lg:grid-cols-2">
                    <PromptBox title="Improved GPT Prompt" value={directorWorkflow.improved_gpt_prompt ?? ""} copy />
                    <PromptBox title="Improved Claude Prompt" value={directorWorkflow.improved_claude_prompt ?? ""} />
                  </div>
                ) : null}
                {workflowInteractions.length ? (
                  <div className="grid gap-3 md:grid-cols-4">
                    {workflowInteractions.map((item) => (
                      <Metric key={item.id} label={`${item.provider} ${item.purpose}`} value={item.status} />
                    ))}
                  </div>
                ) : null}
              </div>
            ) : null}
          </Panel>

          <Panel title="Director Engine" icon={<WandSparkles size={18} />}>
            <form
              className="grid gap-3"
              onSubmit={async (event) => {
                event.preventDefault();
                try {
                  const result = await runDirector(token, {
                    script: directorForm.script,
                    user_instruction: directorForm.user_instruction,
                    max_attempts: Number(directorForm.max_attempts)
                  });
                  setDirectorResult(result);
                  setMessage(`Director Engine completed with ${result.quality_report.overall_continuity_score}% continuity.`);
                  await refresh();
                } catch (error) {
                  setMessage(error instanceof Error ? error.message : "Director run failed");
                }
              }}
            >
              <Field label="Script" name="script" value={directorForm.script} textarea onChange={(f, v) => setDirectorForm((c) => ({ ...c, [f]: v }))} />
              <Field label="User Instruction" name="user_instruction" value={directorForm.user_instruction} textarea onChange={(f, v) => setDirectorForm((c) => ({ ...c, [f]: v }))} />
              <Field label="Max Attempts" name="max_attempts" value={directorForm.max_attempts} onChange={(f, v) => setDirectorForm((c) => ({ ...c, [f]: v }))} />
              <SubmitButton label="Run Director Engine" />
            </form>
            {directorResult ? (
              <div className="mt-4 grid gap-3 md:grid-cols-3">
                <Metric label="Quality" value={`${directorResult.quality_report.overall_continuity_score}%`} />
                <Metric label="Decision" value={directorResult.quality_report.decision} />
                <Metric label="Warnings" value={String(directorResult.warnings.length)} />
              </div>
            ) : null}
          </Panel>

          <Panel title="Self-Improving Feedback Loop" icon={<RefreshCw size={18} />}>
            <div className="grid gap-3 md:grid-cols-[1fr_180px]">
              <Select
                label="Shot"
                value={directorResult?.shot.id ?? shots[0]?.id ?? ""}
                onChange={() => undefined}
                options={(directorResult ? [directorResult.shot, ...shots] : shots).map((item) => ({
                  value: item.id,
                  label: `Shot ${item.shot_number}: ${item.status}`
                }))}
              />
              <button
                className="mt-6 inline-flex h-10 items-center justify-center gap-2 rounded bg-signal px-3 text-sm font-semibold text-white"
                type="button"
                onClick={async () => {
                  const shotId = directorResult?.shot.id ?? shots[0]?.id;
                  if (!shotId) {
                    setMessage("Create or run a shot first.");
                    return;
                  }
                  const result = await runFeedbackLoop(token, {
                    shot_id: shotId,
                    provider: "mock",
                    max_attempts: 5
                  });
                  setFeedbackResult(result);
                  setMessage(`Feedback loop ${result.accepted ? "accepted" : "rejected"} after ${result.versions} prompt version(s).`);
                  await refresh();
                }}
              >
                Run Brain Loop
              </button>
            </div>
            {feedbackResult?.critic_review?.suggested_corrections?.length ? (
              <div className="mt-3 rounded border border-line bg-panel p-3 text-sm">
                {feedbackResult.critic_review.suggested_corrections.map((item) => (
                  <p key={item}>{item}</p>
                ))}
              </div>
            ) : null}
          </Panel>

          <Panel title="AI Research Layer" icon={<Aperture size={18} />}>
            <div className="grid gap-3 md:grid-cols-2">
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded bg-ink px-3 text-sm font-semibold text-white"
                type="button"
                onClick={async () => {
                  const shotId = directorResult?.shot.id ?? shots[0]?.id;
                  if (!shotId) {
                    setMessage("Create or run a shot before A/B testing.");
                    return;
                  }
                  const result = await runABTest(token, {
                    shot_id: shotId,
                    provider: "mock"
                  });
                  setMessage(`A/B test winner: ${result.winning_variant ?? "none"} at ${result.winner_score ?? 0}%.`);
                  await refresh();
                }}
              >
                Run A/B Test
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold"
                type="button"
                onClick={() => refresh().catch((error) => setMessage(error.message))}
              >
                Refresh Research
              </button>
            </div>
          </Panel>

          <Panel title="Visual Intelligence" icon={<Map size={18} />}>
            <div className="grid gap-3 md:grid-cols-2">
              <Field
                label="Reference Image URL"
                name="image_url"
                value={referenceForm.image_url}
                onChange={(field, value) => setReferenceForm((current) => ({ ...current, [field]: value }))}
              />
              <Field
                label="Quality Score"
                name="quality_score"
                value={referenceForm.quality_score}
                onChange={(field, value) => setReferenceForm((current) => ({ ...current, [field]: value }))}
              />
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded bg-ink px-3 text-sm font-semibold text-white"
                type="button"
                onClick={async () => {
                  await ingestReference(token, {
                    image_url: referenceForm.image_url,
                    quality_score: Number(referenceForm.quality_score)
                  });
                  setMessage("Reference ingested and segmented.");
                }}
              >
                Ingest Reference
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold"
                type="button"
                onClick={async () => {
                  const shotId = directorResult?.shot.id ?? shots[0]?.id;
                  if (!shotId) {
                    setMessage("Create or run a shot before selecting references.");
                    return;
                  }
                  const selection = await selectReferences(token, {
                    shot_id: shotId,
                    requested_continuity: {
                      face: "canonical face",
                      costume: "approved costume",
                      background: "matching environment"
                    }
                  });
                  setReferenceSummary(`${selection.selected_segments.length} segment references selected.`);
                }}
              >
                Select References
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold"
                type="button"
                onClick={async () => {
                  await seedCinematography(token);
                  setMessage("Cinematography styles seeded.");
                }}
              >
                Seed Styles
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded bg-signal px-3 text-sm font-semibold text-white"
                type="button"
                onClick={async () => {
                  const shotId = directorResult?.shot.id ?? shots[0]?.id;
                  if (!shotId) {
                    setMessage("Create or run a shot before compiling a visual plan.");
                    return;
                  }
                  const plan = await compileVisualPlan(token, shotId);
                  setVisualPlanSummary(`Lens ${String(plan.camera.lens)}, ${String(plan.lighting.style ?? "motivated light")}`);
                }}
              >
                Compile Visual Plan
              </button>
            </div>
            <div className="mt-3 grid gap-3 md:grid-cols-2">
              <Metric label="References" value={referenceSummary} />
              <Metric label="Visual Plan" value={visualPlanSummary} />
            </div>
          </Panel>

          <Panel title="Evaluation Framework" icon={<FileText size={18} />}>
            <div className="grid gap-3 md:grid-cols-2">
              <Metric label="Evaluation" value={evaluationSummary} />
              <Metric label="Research Ops" value={researchOpsSummary} />
              <Field
                label="Benchmark ID"
                name="benchmark_id"
                value={benchmarkId}
                onChange={(_, value) => setBenchmarkId(value)}
              />
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded bg-ink px-3 text-sm font-semibold text-white"
                type="button"
                onClick={async () => {
                  const benchmarks = await seedBenchmarks(token);
                  await seedProviderCapabilities(token);
                  setBenchmarkId(benchmarks[0]?.id ?? "");
                  setMessage("Benchmarks and provider capabilities seeded.");
                  await refresh();
                }}
              >
                Seed Benchmarks
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded bg-signal px-3 text-sm font-semibold text-white"
                type="button"
                onClick={async () => {
                  if (!benchmarkId) {
                    setMessage("Seed or enter a benchmark ID first.");
                    return;
                  }
                  const run = await runBenchmark(token, {
                    benchmark_id: benchmarkId,
                    provider: "mock",
                    pipeline_version: "local"
                  });
                  setMessage(`Benchmark complete: overall ${run.summary_scores.overall ?? 0}%.`);
                  await refresh();
                }}
              >
                Run Benchmark
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold"
                type="button"
                onClick={async () => {
                  const shotId = directorResult?.shot.id ?? shots[0]?.id;
                  if (!shotId) {
                    setMessage("Create or run a shot before submitting review.");
                    return;
                  }
                  const review = await submitHumanReview(token, {
                    shot_id: shotId,
                    reviewer_name: "Director",
                    face_consistency: 9,
                    costume: 9,
                    environment: 9,
                    lighting: 9,
                    cinematography: 9,
                    motion: 9,
                    overall_quality: 9,
                    notes: "Calibration sample"
                  });
                  setMessage(`Human review saved. Calibration delta ${review.calibration_delta ?? 0}.`);
                  await refresh();
                }}
              >
                Submit 9/10 Review
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold"
                type="button"
                onClick={async () => {
                  const plan = await getExperimentPlan(token);
                  setResearchOpsSummary(`${plan.variant_count} reproducible variants planned.`);
                }}
              >
                Plan Experiments
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded bg-ink px-3 text-sm font-semibold text-white"
                type="button"
                onClick={async () => {
                  const batch = await runAutonomousBatch(token);
                  setResearchOpsSummary(`${batch.summary.benchmarks_run} benchmark batch, avg ${batch.summary.average_overall}%.`);
                  await refresh();
                }}
              >
                Run Research Batch
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold"
                type="button"
                onClick={async () => {
                  const [genes, dna, report] = await Promise.all([
                    getGeneLearning(token),
                    getProviderDNA(token, "mock"),
                    getResearchReport(token)
                  ]);
                  const geneCount = Object.keys(genes.gene_impacts).length;
                  setResearchOpsSummary(`${geneCount} genes learned, ${dna.sample_count} provider samples, ${report.generation_count} generations reported.`);
                }}
              >
                Learn + Report
              </button>
              <button
                className="inline-flex h-10 items-center justify-center gap-2 rounded border border-line bg-white px-3 text-sm font-semibold"
                type="button"
                onClick={async () => {
                  const prompt = directorResult?.prompt ?? latestPrompt;
                  const [debate, symbolic] = await Promise.all([
                    debatePrompt(token, { prompt, context: { source: "evaluation_panel" } }),
                    symbolicPrompt(token, { components: directorResult?.shot.prompt_components ?? {} })
                  ]);
                  setResearchOpsSummary(`${debate.decision}: ${symbolic.compact_language || "no symbols yet"}`);
                }}
              >
                Debate Prompt
              </button>
            </div>
          </Panel>

          <div className="grid gap-5 lg:grid-cols-2">
            <ResourceForm
              title="Characters"
              icon={<Clapperboard size={18} />}
              form={characterForm}
              textareas={["face", "hair", "clothes", "accessories"]}
              onChange={(field, value) => setCharacterForm((current) => ({ ...current, [field]: value }))}
              onSubmit={(event) =>
                submit(event, () => createCharacter(token, characterForm), "Character saved.", setCharacterForm, emptyCharacter)
              }
            />
            <ResourceForm
              title="Environments"
              icon={<Map size={18} />}
              form={environmentForm}
              textareas={["architecture", "lighting"]}
              onChange={(field, value) => setEnvironmentForm((current) => ({ ...current, [field]: value }))}
              onSubmit={(event) =>
                submit(event, () => createEnvironment(token, environmentForm), "Environment saved.", setEnvironmentForm, emptyEnvironment)
              }
            />
            <ResourceForm
              title="Camera"
              icon={<Aperture size={18} />}
              form={cameraForm}
              textareas={["film_look"]}
              onChange={(field, value) => setCameraForm((current) => ({ ...current, [field]: value }))}
              onSubmit={(event) =>
                submit(event, () => createCamera(token, cameraForm), "Camera profile saved.", setCameraForm, emptyCamera)
              }
            />
            <ResourceForm
              title="Props"
              icon={<Box size={18} />}
              form={propForm}
              textareas={["description"]}
              onChange={(field, value) => setPropForm((current) => ({ ...current, [field]: value }))}
              onSubmit={(event) =>
                submit(event, () => createProp(token, propForm), "Prop saved.", setPropForm, emptyProp)
              }
            />
          </div>

          <Panel title="Scene Planner" icon={<FileText size={18} />}>
            <form
              className="grid gap-3 md:grid-cols-2"
              onSubmit={(event) =>
                submit(
                  event,
                  () =>
                    createScene(token, {
                      scene_number: Number(sceneForm.scene_number),
                      script: sceneForm.script,
                      timeline: sceneForm.timeline,
                      environment_id: selectedEnvironmentId || null,
                      character_ids: characters.map((character) => character.id),
                      prop_ids: props.map((prop) => prop.id)
                    }),
                  "Scene saved.",
                  setSceneForm,
                  emptyScene
                )
              }
            >
              <Field label="Scene Number" name="scene_number" value={sceneForm.scene_number} onChange={(f, v) => setSceneForm((c) => ({ ...c, [f]: v }))} />
              <Select label="Environment" value={selectedEnvironmentId} onChange={setSelectedEnvironmentId} options={environments.map((item) => ({ value: item.id, label: item.location }))} />
              <div className="md:col-span-2">
                <Field label="Script" name="script" value={sceneForm.script} textarea onChange={(f, v) => setSceneForm((c) => ({ ...c, [f]: v }))} />
              </div>
              <div className="md:col-span-2">
                <Field label="Timeline" name="timeline" value={sceneForm.timeline} options={presetsFor("timeline")} onChange={(f, v) => setSceneForm((c) => ({ ...c, [f]: v }))} />
              </div>
              <SubmitButton label="Add Scene" />
            </form>
          </Panel>

          <Panel title="Shot + Prompt Compiler" icon={<WandSparkles size={18} />}>
            <form
              className="grid gap-3 md:grid-cols-3"
              onSubmit={(event) =>
                submit(
                  event,
                  () =>
                    createShot(token, {
                      ...shotForm,
                      shot_number: Number(shotForm.shot_number),
                      scene_id: selectedSceneId,
                      camera_id: selectedCameraId || null,
                      environment_id: selectedEnvironmentId || null
                    }),
                  "Shot compiled from stored continuity.",
                  setShotForm,
                  emptyShot
                )
              }
            >
              <Select label="Scene" value={selectedSceneId} onChange={setSelectedSceneId} options={scenes.map((item) => ({ value: item.id, label: `Scene ${item.scene_number}` }))} />
              <Select label="Camera" value={selectedCameraId} onChange={setSelectedCameraId} options={cameras.map((item) => ({ value: item.id, label: item.name }))} />
              <Field label="Shot Number" name="shot_number" value={shotForm.shot_number} onChange={(f, v) => setShotForm((c) => ({ ...c, [f]: v }))} />
              <div className="md:col-span-3">
                <Field label="User Instruction" name="user_instruction" value={shotForm.user_instruction} textarea onChange={(f, v) => setShotForm((c) => ({ ...c, [f]: v }))} />
              </div>
              {["lighting", "emotion", "pose"].map((field) => (
                <Field key={field} label={labelize(field)} name={field} value={shotForm[field as keyof typeof shotForm]} options={presetsFor(field)} onChange={(f, v) => setShotForm((c) => ({ ...c, [f]: v }))} />
              ))}
              <SubmitButton label="Compile Shot" />
            </form>
          </Panel>

          <div className="grid gap-5 lg:grid-cols-3">
            <RecordList title="Characters" records={characters.map((item) => item.name)} />
            <RecordList title="Scenes" records={scenes.map((item) => `Scene ${item.scene_number}: ${item.script}`)} />
            <RecordList
              title="Shots"
              records={shots.map((item) => `Shot ${item.shot_number}: ${item.status} (${item.continuity_score ?? "not checked"})`)}
              actions={shots
                .filter((item) => item.status !== "approved")
                .map((item) => ({
                  label: `Approve shot ${item.shot_number}`,
                  onClick: async () => {
                    await approveShot(token, item.id);
                    await refresh();
                  }
                }))}
            />
          </div>
        </section>
      </div>
    </main>
  );
}

function Panel({ title, icon, children }: { title: string; icon: ReactNode; children: ReactNode }) {
  return (
    <section className="rounded border border-line bg-white p-4">
      <div className="mb-4 flex items-center gap-2">
        {icon}
        <h2 className="text-base font-semibold">{title}</h2>
      </div>
      {children}
    </section>
  );
}

function ResourceForm({
  title,
  icon,
  form,
  textareas,
  onChange,
  onSubmit
}: {
  title: string;
  icon: ReactNode;
  form: Record<string, string>;
  textareas: string[];
  onChange: (field: string, value: string) => void;
  onSubmit: (event: FormEvent) => void;
}) {
  return (
    <Panel title={title} icon={icon}>
      <form className="grid gap-3" onSubmit={onSubmit}>
        {Object.entries(form).map(([name, value]) => (
          <Field
            key={name}
            label={labelize(name)}
            name={name}
            value={value}
            options={presetsFor(name)}
            textarea={textareas.includes(name)}
            onChange={onChange}
          />
        ))}
        <SubmitButton label={`Add ${title}`} />
      </form>
    </Panel>
  );
}

function SubmitButton({ label }: { label: string }) {
  return (
    <button className="inline-flex h-10 items-center justify-center gap-2 rounded bg-ink px-3 text-sm font-semibold text-white">
      <Plus size={16} />
      {label}
    </button>
  );
}

function Select({
  label,
  value,
  onChange,
  options
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
  options: { value: string; label: string }[];
}) {
  return (
    <label className="grid gap-1 text-sm font-medium text-ink">
      <span>{label}</span>
      <select
        className="h-10 rounded border border-line bg-white px-3 text-sm outline-none focus:border-signal focus:ring-2 focus:ring-signal/20"
        value={value}
        onChange={(event) => onChange(event.target.value)}
      >
        <option value="">Select</option>
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
    </label>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded border border-line bg-panel p-3">
      <p className="text-xs font-semibold uppercase text-ink/55">{label}</p>
      <p className="mt-1 text-base font-semibold">{value}</p>
    </div>
  );
}

function PromptBox({ title, value, copy = false }: { title: string; value: string; copy?: boolean }) {
  return (
    <div className="rounded border border-line bg-panel">
      <div className="flex items-center justify-between gap-2 border-b border-line px-3 py-2">
        <h3 className="text-sm font-semibold">{title}</h3>
        {copy ? (
          <button
            className="grid size-8 place-items-center rounded border border-line bg-white hover:border-signal"
            onClick={() => navigator.clipboard.writeText(value)}
            title="Copy"
            type="button"
          >
            <Copy size={15} />
          </button>
        ) : null}
      </div>
      <pre className="max-h-56 overflow-auto whitespace-pre-wrap p-3 text-xs leading-5">{value || "Not generated yet."}</pre>
    </div>
  );
}

function MediaFileField({
  label,
  accept,
  disabled,
  onChange
}: {
  label: string;
  accept: string;
  disabled: boolean;
  onChange: (file: File | null) => void;
}) {
  return (
    <label className="grid gap-1 text-sm font-medium text-ink">
      <span>{label}</span>
      <input
        accept={accept}
        className="w-full rounded border border-line bg-white px-3 py-2 text-sm outline-none transition file:mr-3 file:rounded file:border-0 file:bg-ink file:px-3 file:py-1 file:text-sm file:font-semibold file:text-white focus:border-signal focus:ring-2 focus:ring-signal/20"
        disabled={disabled}
        onChange={(event) => onChange(event.target.files?.[0] ?? null)}
        type="file"
      />
    </label>
  );
}

function RecordList({
  title,
  records,
  actions = []
}: {
  title: string;
  records: string[];
  actions?: { label: string; onClick: () => Promise<void> }[];
}) {
  return (
    <section className="rounded border border-line bg-white">
      <h2 className="border-b border-line px-4 py-3 text-base font-semibold">{title}</h2>
      <div className="divide-y divide-line">
        {records.length === 0 ? (
          <p className="px-4 py-4 text-sm text-ink/65">No records yet.</p>
        ) : (
          records.map((record, index) => (
            <p className="px-4 py-3 text-sm text-ink/75" key={`${record}-${index}`}>
              {record}
            </p>
          ))
        )}
      </div>
      {actions.length ? (
        <div className="grid gap-2 border-t border-line p-3">
          {actions.map((action) => (
            <button
              className="h-9 rounded border border-line bg-white px-3 text-sm hover:border-signal"
              key={action.label}
              onClick={() => action.onClick()}
              type="button"
            >
              {action.label}
            </button>
          ))}
        </div>
      ) : null}
    </section>
  );
}

function labelize(value: string) {
  return value
    .split("_")
    .map((part) => part.charAt(0).toUpperCase() + part.slice(1))
    .join(" ");
}

function splitList(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

function splitLines(value: string) {
  return value
    .split("\n")
    .map((item) => item.trim())
    .filter(Boolean);
}
