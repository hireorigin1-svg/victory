from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.session import Base, get_db
from app.main import create_app


@pytest.fixture()
def client() -> Generator[TestClient, None, None]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    app = create_app(seed_data=False)

    def override_get_db() -> Generator[Session, None, None]:
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client


def _register_and_login(client: TestClient, role: str = "director") -> str:
    payload = {
        "email": f"{role}@example.com",
        "name": f"{role.title()} User",
        "password": "correct-horse-battery",
        "role": role,
    }
    response = client.post("/api/v1/auth/register", json=payload)
    assert response.status_code == 201
    login = client.post(
        "/api/v1/auth/login",
        json={"email": payload["email"], "password": payload["password"]},
    )
    assert login.status_code == 200
    return login.json()["access_token"]


def test_register_login_and_character_crud(client: TestClient) -> None:
    token = _register_and_login(client)
    headers = {"Authorization": f"Bearer {token}"}

    created = client.post(
        "/api/v1/characters",
        headers=headers,
        json={
            "name": "Hanuman",
            "face": "divine simian face with serene strength",
            "hair": "dark tied hair",
            "skin": "warm golden-brown",
            "height": "towering",
            "body": "muscular and agile",
            "clothes": "orange dhoti with sacred ornaments",
            "accessories": "golden mace",
            "voice": "deep and calm",
            "walking_style": "measured heroic stride",
            "expressions": {"default": "devoted", "battle": "focused"},
            "reference_images": ["s3://cinemind/hanuman/ref-1.png"],
        },
    )

    assert created.status_code == 201
    character_id = created.json()["id"]

    updated = client.patch(
        f"/api/v1/characters/{character_id}",
        headers=headers,
        json={"clothes": "orange dhoti with red sash and sacred ornaments"},
    )

    assert updated.status_code == 200
    assert updated.json()["clothes"] == "orange dhoti with red sash and sacred ornaments"
    assert len(updated.json()["version_history"]) == 1


def test_viewer_cannot_create_environment(client: TestClient) -> None:
    token = _register_and_login(client, role="viewer")
    response = client.post(
        "/api/v1/environments",
        headers={"Authorization": f"Bearer {token}"},
        json={"location": "Forest Hermitage", "lighting": "soft dawn light"},
    )

    assert response.status_code == 403


def test_director_flow_compiles_prompt_and_checks_continuity(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    character = client.post(
        "/api/v1/characters",
        headers=headers,
        json={
            "name": "Rama",
            "face": "calm noble face",
            "hair": "dark hair tied back",
            "skin": "warm brown",
            "height": "tall",
            "body": "athletic",
            "clothes": "blue silk robes",
            "accessories": "bow and quiver",
        },
    ).json()
    environment = client.post(
        "/api/v1/environments",
        headers=headers,
        json={
            "location": "Ancient forest path",
            "architecture": "stone shrines and banyan roots",
            "lighting": "golden dawn",
            "weather": "clear",
            "time": "sunrise",
        },
    ).json()
    camera = client.post(
        "/api/v1/cameras",
        headers=headers,
        json={
            "name": "Hero tracking",
            "lens": "35mm anamorphic",
            "camera_angle": "low angle",
            "movement": "slow dolly forward",
            "aspect_ratio": "2.39:1",
            "film_look": "mythic cinematic realism",
        },
    ).json()
    scene = client.post(
        "/api/v1/scenes",
        headers=headers,
        json={
            "scene_number": 1,
            "script": "Rama waits in the forest as Hanuman arrives.",
            "environment_id": environment["id"],
            "character_ids": [character["id"]],
            "timeline": "Opening dawn sequence",
        },
    ).json()
    shot = client.post(
        "/api/v1/shots",
        headers=headers,
        json={
            "scene_id": scene["id"],
            "shot_number": 1,
            "user_instruction": "Rama looks toward the rising sun.",
            "camera_id": camera["id"],
            "environment_id": environment["id"],
            "lighting": "golden dawn",
            "emotion": "peaceful resolve",
            "pose": "standing still",
        },
    )

    assert shot.status_code == 201
    shot_body = shot.json()
    assert "Rama" in shot_body["prompt"]
    assert "golden dawn" in shot_body["prompt"]

    analyzed = client.post(
        f"/api/v1/shots/{shot_body['id']}/analyze-vision", headers=headers
    )
    assert analyzed.status_code == 200
    assert analyzed.json()["vision_analysis"]["lighting"] == "golden dawn"

    continuity = client.post(
        f"/api/v1/shots/{shot_body['id']}/continuity", headers=headers
    )
    assert continuity.status_code == 200
    assert continuity.json()["overall_continuity_score"] == 100


def test_prompt_compiler_v2_uses_film_bible_and_warns_on_conflict(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}
    bible = client.patch(
        "/api/v1/film-bible",
        headers=headers,
        json={
            "lighting_style": "warm golden temple light",
            "camera_rules": ["never switch to handheld inside temple scenes"],
            "continuity_rules": ["approved visual memory overrides new text"],
        },
    )
    assert bible.status_code == 200

    environment = client.post(
        "/api/v1/environments",
        headers=headers,
        json={"location": "Temple courtyard", "lighting": "warm golden temple light"},
    ).json()
    scene = client.post(
        "/api/v1/scenes",
        headers=headers,
        json={
            "scene_number": 2,
            "script": "The hero enters the temple courtyard.",
            "environment_id": environment["id"],
        },
    ).json()
    compiled = client.post(
        "/api/v1/shots/compile",
        headers=headers,
        json={
            "scene_id": scene["id"],
            "user_instruction": "Make the shot dark and handheld.",
        },
    )

    assert compiled.status_code == 200
    body = compiled.json()
    assert "warm golden temple light" in body["prompt"]
    assert body["warnings"]
    assert any(item["priority"] == 2 for item in body["explanation"])


def test_director_engine_approval_creates_visual_memory_and_movie_state(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    run = client.post(
        "/api/v1/director/run",
        headers=headers,
        json={
            "script": "Hanuman stands at the temple gate.",
            "user_instruction": "Hanuman raises the golden gada.",
            "max_attempts": 2,
        },
    )
    assert run.status_code == 200
    shot_id = run.json()["shot"]["id"]

    approved = client.post(f"/api/v1/director/shots/{shot_id}/approve", headers=headers)
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"

    memory = client.get("/api/v1/memory/visual", headers=headers)
    assert memory.status_code == 200
    assert memory.json()[0]["shot_id"] == shot_id

    movie_state = client.get("/api/v1/memory/movie-state", headers=headers)
    assert movie_state.status_code == 200
    assert movie_state.json()["current_shot_id"] == shot_id


def test_director_workflow_stores_gpt_claude_higgsfield_and_review_loop(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    scene = client.post(
        "/api/v1/scenes",
        headers=headers,
        json={"scene_number": 21, "script": "Hanuman enters Lanka at sunset."},
    ).json()

    started = client.post(
        "/api/v1/director-workflows/start",
        headers=headers,
        json={
            "scene_id": scene["id"],
            "shot_number": 1,
            "director_instruction": "Hanuman walks through Lanka with calm power.",
            "lighting": "sunset firelight",
            "emotion": "calm power",
            "pose": "walking forward",
        },
    )
    assert started.status_code == 201
    workflow = started.json()
    assert workflow["gpt_prompt"]
    assert workflow["claude_prompt"]
    assert workflow["higgsfield_prompt"] == workflow["gpt_prompt"]
    assert workflow["llm_context"]["scene_id"] == scene["id"]
    assert workflow["llm_context"]["project_memory"]
    assert workflow["llm_context"]["continuity_memory"]
    assert workflow["llm_context"]["learning_memory"]

    interactions = client.get(
        f"/api/v1/director-workflows/{workflow['id']}/llm-interactions",
        headers=headers,
    )
    assert interactions.status_code == 200
    interaction_body = interactions.json()
    assert {item["provider"] for item in interaction_body} == {"openai", "anthropic"}
    assert all(item["request_context"]["scene_id"] == scene["id"] for item in interaction_body)

    uploaded = client.post(
        f"/api/v1/director-workflows/{workflow['id']}/upload-result",
        headers=headers,
        json={"image_url": "mock://higgsfield/shot-1.png", "video_url": "mock://higgsfield/shot-1.mp4"},
    )
    assert uploaded.status_code == 200
    assert uploaded.json()["approval_status"] == "result_uploaded"

    rejected = client.post(
        f"/api/v1/director-workflows/{workflow['id']}/review",
        headers=headers,
        json={"approved": False, "reasons": ["Face drifted", "Costume changed"]},
    )
    assert rejected.status_code == 200
    rejected_body = rejected.json()
    assert rejected_body["approval_status"] == "rejected"
    assert rejected_body["review_reasons"] == ["Face drifted", "Costume changed"]
    assert rejected_body["improved_gpt_prompt"]
    assert rejected_body["improved_claude_prompt"]

    repaired_interactions = client.get(
        f"/api/v1/director-workflows/{workflow['id']}/llm-interactions",
        headers=headers,
    ).json()
    assert len(repaired_interactions) == 4
    assert {item["purpose"] for item in repaired_interactions} == {"initial_prompt", "rejection_repair"}

    shot = client.get(f"/api/v1/shots/{workflow['shot_id']}", headers=headers)
    assert shot.status_code == 200
    assert shot.json()["status"] == "rejected"
    assert shot.json()["rejection_reason"] == "Face drifted; Costume changed"

    approved = client.post(
        f"/api/v1/director-workflows/{workflow['id']}/review",
        headers=headers,
        json={"approved": True, "image_url": "mock://higgsfield/shot-1-fixed.png"},
    )
    assert approved.status_code == 200
    assert approved.json()["approval_status"] == "approved"

    approved_shot = client.get(f"/api/v1/shots/{workflow['shot_id']}", headers=headers)
    assert approved_shot.json()["status"] == "approved"
    assert approved_shot.json()["approved_image"] == "mock://higgsfield/shot-1-fixed.png"


def test_director_os_v2_builds_blueprint_packet_translation_and_learning_record(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    character = client.post(
        "/api/v1/characters",
        headers=headers,
        json={
            "name": "Hanuman",
            "face": "consistent heroic simian face",
            "hair": "dark tied hair",
            "clothes": "orange silk with gold ornaments",
            "accessories": "golden gada",
            "reference_images": ["mock://references/hanuman-face-01"],
        },
    ).json()
    environment = client.post(
        "/api/v1/environments",
        headers=headers,
        json={
            "location": "Temple Courtyard",
            "lighting": "golden hour",
            "reference_images": ["mock://references/temple-01"],
        },
    ).json()
    scene = client.post(
        "/api/v1/scenes",
        headers=headers,
        json={
            "scene_number": 44,
            "script": "Hanuman walks toward Rama in the temple courtyard.",
            "environment_id": environment["id"],
            "character_ids": [character["id"]],
        },
    ).json()

    run = client.post(
        "/api/v1/director-os/v2/run",
        headers=headers,
        json={
            "scene_id": scene["id"],
            "script": scene["script"],
            "user_instruction": "Hanuman walks slowly through golden hour light holding the golden gada.",
            "provider": "higgsfield",
            "claude_review_below": 100,
        },
    )
    assert run.status_code == 200
    body = run.json()
    assert body["blueprint_id"]
    assert body["knowledge_packet_id"]
    assert body["translation_id"]
    assert body["blueprint"]["characters"][0]["name"] == "Hanuman"
    assert body["knowledge_packet"]["film_bible"] is None
    assert body["translated_prompt"]
    assert body["claude_review"]
    assert body["learning_record"]["provider"] == "higgsfield"


def test_media_upload_accepts_images_and_rejects_other_files(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    uploaded = client.post(
        "/api/v1/media/uploads",
        headers=headers,
        files={"file": ("frame.png", b"fake-image-bytes", "image/png")},
    )
    assert uploaded.status_code == 201
    body = uploaded.json()
    assert body["url"].endswith(".png")
    assert body["content_type"] == "image/png"
    assert body["size"] == len(b"fake-image-bytes")

    rejected = client.post(
        "/api/v1/media/uploads",
        headers=headers,
        files={"file": ("notes.txt", b"not media", "text/plain")},
    )
    assert rejected.status_code == 400


def test_brain_feedback_loop_logs_experiment_critic_evolution_and_dna(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    run = client.post(
        "/api/v1/director/run",
        headers=headers,
        json={
            "script": "Rama watches the battlefield from a hill.",
            "user_instruction": "Rama steps forward with calm resolve.",
            "max_attempts": 1,
        },
    )
    assert run.status_code == 200
    shot_id = run.json()["shot"]["id"]

    loop = client.post(
        "/api/v1/brain/feedback-loop",
        headers=headers,
        json={"shot_id": shot_id, "provider": "mock", "max_attempts": 5},
    )
    assert loop.status_code == 200
    loop_body = loop.json()
    assert loop_body["accepted"] is True
    assert loop_body["experiment"]["accepted"] is True

    experiments = client.get("/api/v1/brain/experiments", headers=headers)
    assert experiments.status_code == 200
    assert len(experiments.json()) >= 1

    reviews = client.get(f"/api/v1/brain/shots/{shot_id}/critic-reviews", headers=headers)
    assert reviews.status_code == 200
    assert len(reviews.json()) >= 1

    evolution = client.get(f"/api/v1/brain/shots/{shot_id}/prompt-evolution", headers=headers)
    assert evolution.status_code == 200
    assert len(evolution.json()) >= 1

    dna = client.get(f"/api/v1/brain/shots/{shot_id}/dna", headers=headers)
    assert dna.status_code == 200
    assert dna.json()["dna"]["face"] is not None


def test_research_layer_records_genomes_behavior_ab_tests_and_analytics(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    run = client.post(
        "/api/v1/director/run",
        headers=headers,
        json={
            "script": "Hanuman crosses the forest path.",
            "user_instruction": "Hanuman walks through warm golden light.",
            "max_attempts": 1,
        },
    )
    assert run.status_code == 200
    shot_id = run.json()["shot"]["id"]

    loop = client.post(
        "/api/v1/brain/feedback-loop",
        headers=headers,
        json={"shot_id": shot_id, "provider": "mock", "max_attempts": 3},
    )
    assert loop.status_code == 200

    genomes = client.get(f"/api/v1/research/shots/{shot_id}/genomes", headers=headers)
    assert genomes.status_code == 200
    assert genomes.json()[0]["genes"]["lighting"]

    behavior = client.get("/api/v1/research/provider-behavior/summary?provider=mock", headers=headers)
    assert behavior.status_code == 200
    assert behavior.json()["records"] >= 1

    ab_test = client.post(
        "/api/v1/research/ab-tests",
        headers=headers,
        json={"shot_id": shot_id, "provider": "mock"},
    )
    assert ab_test.status_code == 200
    assert ab_test.json()["winning_variant"] in ["A", "B"]

    analytics = client.get("/api/v1/research/analytics", headers=headers)
    assert analytics.status_code == 200
    assert "mock" in analytics.json()["success_rate_by_provider"]


def test_scene_simulator_warns_before_generation(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}
    first_env = client.post(
        "/api/v1/environments",
        headers=headers,
        json={"location": "Temple", "lighting": "dawn"},
    ).json()
    second_env = client.post(
        "/api/v1/environments",
        headers=headers,
        json={"location": "Forest", "lighting": "dawn"},
    ).json()
    scene_one = client.post(
        "/api/v1/scenes",
        headers=headers,
        json={"scene_number": 10, "script": "Hero waits in temple.", "environment_id": first_env["id"]},
    ).json()
    scene_two = client.post(
        "/api/v1/scenes",
        headers=headers,
        json={"scene_number": 11, "script": "Hero is suddenly in forest.", "environment_id": second_env["id"]},
    ).json()
    shot = client.post(
        "/api/v1/shots",
        headers=headers,
        json={
            "scene_id": scene_one["id"],
            "shot_number": 1,
            "user_instruction": "Hero stands still.",
            "environment_id": first_env["id"],
        },
    ).json()
    client.post(f"/api/v1/director/shots/{shot['id']}/approve", headers=headers)

    simulation = client.post(f"/api/v1/research/scenes/{scene_two['id']}/simulate", headers=headers)
    assert simulation.status_code == 200
    assert simulation.json()["safe_to_generate"] is False


def test_visual_intelligence_reference_ast_plan_graph_and_diff(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    run = client.post(
        "/api/v1/director/run",
        headers=headers,
        json={
            "script": "Hanuman stands before the temple pillars.",
            "user_instruction": "Hanuman raises the golden gada in warm backlight.",
            "max_attempts": 1,
        },
    )
    assert run.status_code == 200
    shot_id = run.json()["shot"]["id"]

    reference = client.post(
        "/api/v1/visual-intelligence/references",
        headers=headers,
        json={"shot_id": shot_id, "image_url": "mock://approved/hanuman-perfect", "quality_score": 99},
    )
    assert reference.status_code == 201

    selection = client.post(
        "/api/v1/visual-intelligence/references/select",
        headers=headers,
        json={
            "shot_id": shot_id,
            "requested_continuity": {
                "face": "Hanuman canonical face",
                "costume": "golden crown orange costume",
                "background": "temple pillars",
            },
        },
    )
    assert selection.status_code == 200
    assert len(selection.json()["selected_segments"]) >= 3

    ast = client.post(f"/api/v1/visual-intelligence/shots/{shot_id}/prompt-ast", headers=headers)
    assert ast.status_code == 200
    assert ast.json()["ast"]["type"] == "ROOT"

    styles = client.post("/api/v1/visual-intelligence/cinematography/seed", headers=headers)
    assert styles.status_code == 200
    assert len(styles.json()) >= 3

    plan = client.post(
        f"/api/v1/visual-intelligence/shots/{shot_id}/visual-plan?style_name=Rajamouli",
        headers=headers,
    )
    assert plan.status_code == 200
    assert plan.json()["camera"]["lens"] == "24mm"

    graph = client.post(f"/api/v1/visual-intelligence/shots/{shot_id}/scene-graph", headers=headers)
    assert graph.status_code == 200
    assert graph.json()["entities"]

    candidate = client.post(
        "/api/v1/shots",
        headers=headers,
        json={
            "scene_id": run.json()["scene_id"],
            "shot_number": 2,
            "user_instruction": "Hanuman lowers the gada.",
            "lighting": "cool moonlight",
        },
    ).json()
    client.patch(
        f"/api/v1/shots/{candidate['id']}",
        headers=headers,
        json={"vision_analysis": {"lighting": "cool moonlight", "pose": "lowering weapon"}},
    )
    diff = client.post(
        f"/api/v1/visual-intelligence/diff?baseline_shot_id={shot_id}&candidate_shot_id={candidate['id']}",
        headers=headers,
    )
    assert diff.status_code == 200
    assert diff.json()["overall_delta_score"] <= 100


def test_failure_clustering_endpoint(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}
    run = client.post(
        "/api/v1/director/run",
        headers=headers,
        json={"script": "A test shot.", "user_instruction": "Hero looks left.", "max_attempts": 1},
    )
    shot_id = run.json()["shot"]["id"]
    client.post(
        "/api/v1/brain/feedback-loop",
        headers=headers,
        json={"shot_id": shot_id, "provider": "mock", "max_attempts": 1},
    )
    clusters = client.post("/api/v1/visual-intelligence/failures/cluster", headers=headers)
    assert clusters.status_code == 200
    assert isinstance(clusters.json(), list)


def test_evaluation_framework_seeds_runs_scores_and_calibrates_reviews(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    benchmarks = client.post("/api/v1/evaluation/benchmarks/seed", headers=headers)
    assert benchmarks.status_code == 200
    assert len(benchmarks.json()) == 5

    providers = client.post("/api/v1/evaluation/providers/seed", headers=headers)
    assert providers.status_code == 200
    assert any(item["provider"] == "higgsfield" for item in providers.json())

    run = client.post(
        "/api/v1/evaluation/benchmark-runs",
        headers=headers,
        json={
            "benchmark_id": benchmarks.json()[0]["id"],
            "provider": "mock",
            "pipeline_version": "test",
        },
    )
    assert run.status_code == 200
    assert run.json()["summary_scores"]["overall"] >= 0

    scores = client.get(f"/api/v1/evaluation/benchmark-runs/{run.json()['id']}/scores", headers=headers)
    assert scores.status_code == 200
    assert len(scores.json()) > 0

    shot_id = scores.json()[0]["shot_id"]
    review = client.post(
        "/api/v1/evaluation/human-reviews",
        headers=headers,
        json={
            "shot_id": shot_id,
            "reviewer_name": "QA",
            "face_consistency": 9,
            "costume": 9,
            "environment": 9,
            "lighting": 9,
            "cinematography": 9,
            "motion": 9,
            "overall_quality": 9,
            "notes": "Looks strong",
        },
    )
    assert review.status_code == 200
    assert review.json()["calibration_delta"] is not None

    dashboard = client.get("/api/v1/evaluation/dashboard", headers=headers)
    assert dashboard.status_code == 200
    assert dashboard.json()["benchmark_count"] == 5
    assert dashboard.json()["north_star"]["target"] == 2


def test_phase_2_research_ops_plan_batch_learn_report_and_debate(client: TestClient) -> None:
    token = _register_and_login(client, role="director")
    headers = {"Authorization": f"Bearer {token}"}

    plan = client.get("/api/v1/evaluation/research/experiment-plan", headers=headers)
    assert plan.status_code == 200
    assert plan.json()["variant_count"] > 0

    batch = client.post(
        "/api/v1/evaluation/research/autonomous-batch?provider=mock&max_benchmarks=1",
        headers=headers,
    )
    assert batch.status_code == 200
    assert batch.json()["summary"]["benchmarks_run"] == 1

    genes = client.get("/api/v1/evaluation/research/gene-learning", headers=headers)
    assert genes.status_code == 200
    assert "gene_impacts" in genes.json()

    dna = client.get("/api/v1/evaluation/research/provider-dna?provider=mock", headers=headers)
    assert dna.status_code == 200
    assert dna.json()["sample_count"] >= 1

    report = client.get("/api/v1/evaluation/research/monthly-report", headers=headers)
    assert report.status_code == 200
    assert report.json()["generation_count"] >= 1

    debate = client.post(
        "/api/v1/evaluation/research/debate",
        headers=headers,
        json={"prompt": "Hero walks through temple with 35mm lens.", "context": {}},
    )
    assert debate.status_code == 200
    assert debate.json()["decision"] in ["approve", "revise"]

    symbolic = client.post(
        "/api/v1/evaluation/research/symbolic-prompt",
        headers=headers,
        json={"components": {"user_instruction": "Hero walks", "film_bible": {"film_lighting_style": "warm"}}},
    )
    assert symbolic.status_code == 200
    assert "ACTION_" in symbolic.json()["compact_language"]
