export type Character = {
  id: string;
  name: string;
  face?: string | null;
  hair?: string | null;
  clothes?: string | null;
  accessories?: string | null;
  version_history: unknown[];
};

export type EnvironmentRecord = {
  id: string;
  location: string;
  architecture?: string | null;
  lighting?: string | null;
  weather?: string | null;
  time?: string | null;
  version_history: unknown[];
};

export type CameraProfile = {
  id: string;
  name: string;
  lens?: string | null;
  camera_angle?: string | null;
  movement?: string | null;
  aspect_ratio?: string | null;
  film_look?: string | null;
};

export type SceneRecord = {
  id: string;
  scene_number: number;
  script: string;
  environment_id?: string | null;
  character_ids: string[];
  prop_ids: string[];
  timeline?: string | null;
};

export type ShotRecord = {
  id: string;
  scene_id: string;
  shot_number: number;
  user_instruction: string;
  prompt?: string | null;
  generated_image?: string | null;
  generated_video?: string | null;
  approved_image?: string | null;
  approved_video?: string | null;
  status: string;
  continuity_score?: number | null;
  director_explanation?: unknown[];
  continuity_warnings?: string[];
  generation_attempts?: number;
  prompt_components?: Record<string, unknown>;
};

export type DirectorWorkflow = {
  id: string;
  shot_id: string;
  director_instruction: string;
  gpt_prompt?: string | null;
  claude_prompt?: string | null;
  higgsfield_prompt?: string | null;
  uploaded_image_url?: string | null;
  uploaded_video_url?: string | null;
  approval_status: string;
  review_reasons: unknown[];
  improved_gpt_prompt?: string | null;
  improved_claude_prompt?: string | null;
  llm_context: Record<string, unknown>;
  workflow_events: unknown[];
};

export type LLMInteraction = {
  id: string;
  workflow_id?: string | null;
  shot_id?: string | null;
  provider: string;
  model?: string | null;
  purpose: string;
  status: string;
  error_message?: string | null;
  response_text: string;
};

export type DirectorWorkflowEvaluation = {
  face: number;
  costume: number;
  environment: number;
  lighting: number;
  camera: number;
  overall: number;
  decision: string;
  notes: string[];
};

export type MediaUpload = {
  url: string;
  filename: string;
  content_type: string;
  size: number;
};

export type FilmBible = {
  id: string;
  project_name: string;
  lighting_style?: string | null;
  color_palette: string[];
  camera_rules: string[];
  lens_package: string[];
  action_rules: string[];
  weather_rules: string[];
  continuity_rules: string[];
};

export type DirectorRunResponse = {
  scene_id: string;
  shot: ShotRecord;
  prompt: string;
  explanation: unknown[];
  warnings: string[];
  quality_report: {
    overall_continuity_score: number;
    decision: string;
    notes: string[];
  };
  movie_state: Record<string, unknown>;
};

export type DirectorOSV2RunResponse = {
  scene_id: string;
  shot: ShotRecord;
  blueprint_id: string;
  knowledge_packet_id: string;
  translation_id: string;
  blueprint: Record<string, unknown>;
  knowledge_packet: Record<string, unknown>;
  gpt_prompt: string;
  claude_review?: Record<string, unknown> | null;
  translated_prompt: string;
  confidence_score: number;
  provider: string;
  evaluation: {
    overall_continuity_score: number;
    decision: string;
    notes: string[];
  };
  decision: string;
  learning_record: Record<string, unknown>;
};

export type FeedbackLoopResponse = {
  shot: ShotRecord;
  experiment: {
    id: string;
    provider: string;
    overall_score?: number | null;
    accepted: boolean;
  } | null;
  critic_review: {
    id: string;
    suggested_corrections: string[];
    corrected_prompt?: string | null;
  } | null;
  quality_report: {
    overall_continuity_score: number;
    decision: string;
  } | null;
  accepted: boolean;
  versions: number;
};

export type BrainSummary = {
  total_experiments: number;
  accepted: number;
  rejected: number;
  acceptance_rate: number;
  provider_average_scores: Record<string, number>;
};

export type ProductionAnalytics = {
  average_generations_to_approval: number;
  success_rate_by_provider: Record<string, number>;
  average_score_by_provider: Record<string, number>;
  continuity_failures_by_category: Record<string, number>;
  cost_per_accepted_shot: number;
};

export type ProviderBehaviorSummary = {
  provider: string;
  records: number;
  average_face_score: number;
  learned_rules: string[];
};

export type ReferenceAsset = {
  id: string;
  image_url: string;
  quality_score?: number | null;
};

export type ReferenceSelection = {
  id: string;
  selected_segments: { segment_type: string; score: number }[];
  rationale: string[];
};

export type VisualPlan = {
  id: string;
  camera: Record<string, unknown>;
  lighting: Record<string, unknown>;
  composition: Record<string, unknown>;
  constraints: string[];
};

export type BenchmarkProject = {
  id: string;
  name: string;
  shot_count: number;
  scenario: string;
};

export type EvaluationDashboard = {
  benchmark_count: number;
  average_overall_score: number;
  human_ai_calibration_delta: number;
  north_star: { metric: string; value: number; target: number };
};

export type ResearchReport = {
  title: string;
  generation_count: number;
  acceptance_rate: number;
  average_face_score: number;
  average_overall_score: number;
  discoveries: string[];
};

export type ProviderDNA = {
  provider: string;
  sample_count: number;
  likes: string[];
  dislikes: string[];
  average_scores: Record<string, number>;
};

const API_BASE =
  process.env.NEXT_PUBLIC_API_BASE_URL ??
  "https://victory-backend-production.up.railway.app";

async function request<T>(
  path: string,
  token: string,
  options: RequestInit = {}
): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
      ...options.headers
    }
  });

  if (!response.ok) {
    const body = await response.json().catch(() => ({}));
    throw new Error(body.detail ?? `Request failed with ${response.status}`);
  }

  return response.json();
}

export async function login(email: string, password: string): Promise<string> {
  const response = await fetch(`${API_BASE}/api/v1/auth/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password })
  });
  if (!response.ok) {
    throw new Error("Invalid email or password");
  }
  const data = (await response.json()) as { access_token: string };
  return data.access_token;
}

export function listCharacters(token: string) {
  return request<Character[]>("/api/v1/characters", token);
}

export function createCharacter(token: string, payload: Record<string, string>) {
  return request<Character>("/api/v1/characters", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listEnvironments(token: string) {
  return request<EnvironmentRecord[]>("/api/v1/environments", token);
}

export function createEnvironment(token: string, payload: Record<string, string>) {
  return request<EnvironmentRecord>("/api/v1/environments", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listCameras(token: string) {
  return request<CameraProfile[]>("/api/v1/cameras", token);
}

export function createCamera(token: string, payload: Record<string, string>) {
  return request<CameraProfile>("/api/v1/cameras", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listProps(token: string) {
  return request<{ id: string; name: string; category: string }[]>("/api/v1/props", token);
}

export function createProp(token: string, payload: Record<string, string>) {
  return request<{ id: string; name: string; category: string }>("/api/v1/props", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listScenes(token: string) {
  return request<SceneRecord[]>("/api/v1/scenes", token);
}

export function createScene(token: string, payload: Record<string, unknown>) {
  return request<SceneRecord>("/api/v1/scenes", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listShots(token: string) {
  return request<ShotRecord[]>("/api/v1/shots", token);
}

export function createShot(token: string, payload: Record<string, unknown>) {
  return request<ShotRecord>("/api/v1/shots", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export async function uploadMedia(token: string, file: File) {
  const body = new FormData();
  body.append("file", file);
  const response = await fetch(`${API_BASE}/api/v1/media/uploads`, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${token}`
    },
    body
  });
  if (!response.ok) {
    const payload = await response.json().catch(() => ({}));
    throw new Error(payload.detail ?? `Upload failed with ${response.status}`);
  }
  return response.json() as Promise<MediaUpload>;
}

export function listDirectorWorkflows(token: string) {
  return request<DirectorWorkflow[]>("/api/v1/director-workflows", token);
}

export function startDirectorWorkflow(token: string, payload: Record<string, unknown>) {
  return request<DirectorWorkflow>("/api/v1/director-workflows/start", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function listWorkflowLLMInteractions(token: string, workflowId: string) {
  return request<LLMInteraction[]>(`/api/v1/director-workflows/${workflowId}/llm-interactions`, token);
}

export function uploadDirectorWorkflowResult(
  token: string,
  workflowId: string,
  payload: Record<string, unknown>
) {
  return request<DirectorWorkflow>(`/api/v1/director-workflows/${workflowId}/upload-result`, token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function evaluateDirectorWorkflow(token: string, workflowId: string) {
  return request<DirectorWorkflowEvaluation>(`/api/v1/director-workflows/${workflowId}/evaluate`, token, {
    method: "POST"
  });
}

export function reviewDirectorWorkflow(
  token: string,
  workflowId: string,
  payload: Record<string, unknown>
) {
  return request<DirectorWorkflow>(`/api/v1/director-workflows/${workflowId}/review`, token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getFilmBible(token: string) {
  return request<FilmBible>("/api/v1/film-bible", token);
}

export function saveFilmBible(token: string, payload: Record<string, unknown>) {
  return request<FilmBible>("/api/v1/film-bible", token, {
    method: "PATCH",
    body: JSON.stringify(payload)
  });
}

export function runDirector(token: string, payload: Record<string, unknown>) {
  return request<DirectorRunResponse>("/api/v1/director/run", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function runDirectorOSV2(token: string, payload: Record<string, unknown>) {
  return request<DirectorOSV2RunResponse>("/api/v1/director-os/v2/run", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function approveShot(token: string, shotId: string) {
  return request<ShotRecord>(`/api/v1/director/shots/${shotId}/approve`, token, {
    method: "POST"
  });
}

export function runFeedbackLoop(token: string, payload: Record<string, unknown>) {
  return request<FeedbackLoopResponse>("/api/v1/brain/feedback-loop", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getBrainSummary(token: string) {
  return request<BrainSummary>("/api/v1/brain/experiments/summary", token);
}

export function getProductionAnalytics(token: string) {
  return request<ProductionAnalytics>("/api/v1/research/analytics", token);
}

export function getProviderBehaviorSummary(token: string, provider = "higgsfield") {
  return request<ProviderBehaviorSummary>(
    `/api/v1/research/provider-behavior/summary?provider=${encodeURIComponent(provider)}`,
    token
  );
}

export function runABTest(token: string, payload: Record<string, unknown>) {
  return request<{ winning_variant?: string | null; winner_score?: number | null }>(
    "/api/v1/research/ab-tests",
    token,
    {
      method: "POST",
      body: JSON.stringify(payload)
    }
  );
}

export function ingestReference(token: string, payload: Record<string, unknown>) {
  return request<ReferenceAsset>("/api/v1/visual-intelligence/references", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function selectReferences(token: string, payload: Record<string, unknown>) {
  return request<ReferenceSelection>("/api/v1/visual-intelligence/references/select", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function seedCinematography(token: string) {
  return request<unknown[]>("/api/v1/visual-intelligence/cinematography/seed", token, {
    method: "POST"
  });
}

export function compileVisualPlan(token: string, shotId: string, style = "Rajamouli") {
  return request<VisualPlan>(
    `/api/v1/visual-intelligence/shots/${shotId}/visual-plan?style_name=${encodeURIComponent(style)}`,
    token,
    { method: "POST" }
  );
}

export function seedBenchmarks(token: string) {
  return request<BenchmarkProject[]>("/api/v1/evaluation/benchmarks/seed", token, {
    method: "POST"
  });
}

export function runBenchmark(token: string, payload: Record<string, unknown>) {
  return request<{ id: string; summary_scores: Record<string, number> }>(
    "/api/v1/evaluation/benchmark-runs",
    token,
    {
      method: "POST",
      body: JSON.stringify(payload)
    }
  );
}

export function getEvaluationDashboard(token: string) {
  return request<EvaluationDashboard>("/api/v1/evaluation/dashboard", token);
}

export function seedProviderCapabilities(token: string) {
  return request<unknown[]>("/api/v1/evaluation/providers/seed", token, {
    method: "POST"
  });
}

export function submitHumanReview(token: string, payload: Record<string, unknown>) {
  return request<{ calibration_delta?: number | null }>("/api/v1/evaluation/human-reviews", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}

export function getExperimentPlan(token: string) {
  return request<{ variant_count: number; variants: unknown[] }>(
    "/api/v1/evaluation/research/experiment-plan",
    token
  );
}

export function runAutonomousBatch(token: string) {
  return request<{ summary: { benchmarks_run: number; average_overall: number } }>(
    "/api/v1/evaluation/research/autonomous-batch?provider=mock&max_benchmarks=1",
    token,
    { method: "POST" }
  );
}

export function getGeneLearning(token: string) {
  return request<{ gene_impacts: Record<string, Record<string, number>> }>(
    "/api/v1/evaluation/research/gene-learning",
    token
  );
}

export function getProviderDNA(token: string, provider = "mock") {
  return request<ProviderDNA>(
    `/api/v1/evaluation/research/provider-dna?provider=${encodeURIComponent(provider)}`,
    token
  );
}

export function getResearchReport(token: string) {
  return request<ResearchReport>("/api/v1/evaluation/research/monthly-report", token);
}

export function debatePrompt(token: string, payload: Record<string, unknown>) {
  return request<{ decision: string; final_recommendation: string }>(
    "/api/v1/evaluation/research/debate",
    token,
    {
      method: "POST",
      body: JSON.stringify(payload)
    }
  );
}

export function symbolicPrompt(token: string, payload: Record<string, unknown>) {
  return request<{ compact_language: string }>("/api/v1/evaluation/research/symbolic-prompt", token, {
    method: "POST",
    body: JSON.stringify(payload)
  });
}
