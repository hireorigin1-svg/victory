from __future__ import annotations

import re
from collections import Counter, defaultdict

from app.schemas.script_intelligence import (
    ScriptAnalysisResponse,
    ScriptCharacterBreakdown,
    ScriptSceneBreakdown,
    StoryboardPanel,
    StoryboardResponse,
)


SCENE_RE = re.compile(r"^(INT\.|EXT\.|INT/EXT\.|I/E\.|EST\.)\s+.+", re.IGNORECASE)
TRANSITION_RE = re.compile(r"^(CUT TO:|SMASH CUT TO:|DISSOLVE TO:|FADE IN:|FADE OUT\.|END\.)$", re.IGNORECASE)
CHARACTER_RE = re.compile(r"^[A-Z][A-Z0-9 .'/-]{1,30}$")
PROP_KEYWORDS = [
    "copper thread",
    "brass lamp",
    "tablet",
    "waveform",
    "palm-leaf manuscript",
    "manuscript",
    "oil lamps",
    "coin",
    "camera",
    "bracelet",
    "conch",
    "disc",
    "star map",
    "satellites",
    "lotus",
]


class ScriptIntelligenceService:
    def analyze(self, title: str, script_text: str) -> ScriptAnalysisResponse:
        text = self._normalize(script_text)
        warnings = self._warnings(text)
        scene_chunks = self._split_scenes(text)
        scenes = [self._scene_breakdown(index + 1, heading, body) for index, (heading, body) in enumerate(scene_chunks)]
        characters = self._characters(text, scenes)
        props = self._props(text)
        locations = self._locations(scenes)
        genre = self._genre(text)
        themes = self._themes(text)
        summary = self._summary(scenes)
        return ScriptAnalysisResponse(
            title=title.strip() or "Untitled Script",
            genre=genre,
            logline=self._logline(genre, scenes, characters),
            summary=summary,
            scene_count=len(scenes),
            character_count=len(characters),
            characters=characters,
            locations=locations,
            props=props,
            themes=themes,
            continuity_rules=self._continuity_rules(characters, props, locations),
            scenes=scenes,
            warnings=warnings,
        )

    def storyboards(
        self,
        title: str,
        script_text: str,
        style: str,
        max_panels: int,
    ) -> StoryboardResponse:
        analysis = self.analyze(title, script_text)
        panels: list[StoryboardPanel] = []
        for scene in analysis.scenes[:max_panels]:
            panels.append(self._panel(scene, len(panels) + 1, style))
        if not panels and script_text.strip():
            pseudo_scene = ScriptSceneBreakdown(
                scene_number=1,
                heading="SCENE 1",
                location="Unknown location",
                summary=script_text.strip()[:400],
                characters=[],
                props=self._props(script_text),
                emotional_beat="neutral",
                visual_style=style,
            )
            panels.append(self._panel(pseudo_scene, 1, style))
        warnings = list(analysis.warnings)
        if len(analysis.scenes) > max_panels:
            warnings.append(f"Storyboard limited to {max_panels} panel(s) from {len(analysis.scenes)} parsed scenes.")
        return StoryboardResponse(
            title=analysis.title,
            panel_count=len(panels),
            panels=panels,
            warnings=warnings,
        )

    def _normalize(self, script_text: str) -> str:
        text = script_text.replace("\r\n", "\n").replace("\r", "\n")
        text = re.sub(r"[ \t]+", " ", text)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()

    def _warnings(self, text: str) -> list[str]:
        warnings: list[str] = []
        if "429" in text or "credits remaining" in text.lower():
            warnings.append("Input appears to contain an API credit error message. Remove report/error text and upload only the screenplay.")
        if "fallback mode" in text.lower():
            warnings.append("Input appears to contain fallback report text. This analyzer only trusts screenplay content.")
        if not SCENE_RE.search(text):
            warnings.append("No standard INT./EXT. scene headings found. Scene detection may be limited.")
        return warnings

    def _split_scenes(self, text: str) -> list[tuple[str, str]]:
        lines = [line.strip() for line in text.splitlines()]
        chunks: list[tuple[str, list[str]]] = []
        current_heading: str | None = None
        current_body: list[str] = []
        for line in lines:
            if SCENE_RE.match(line):
                if current_heading:
                    chunks.append((current_heading, current_body))
                current_heading = line.upper()
                current_body = []
            elif current_heading:
                current_body.append(line)
        if current_heading:
            chunks.append((current_heading, current_body))
        if chunks:
            return [(heading, "\n".join(body).strip()) for heading, body in chunks]
        return [("SCENE 1", text)]

    def _scene_breakdown(self, scene_number: int, heading: str, body: str) -> ScriptSceneBreakdown:
        action_lines = [
            line
            for line in body.splitlines()
            if line and not CHARACTER_RE.match(line) and not TRANSITION_RE.match(line)
        ]
        action = " ".join(action_lines)
        return ScriptSceneBreakdown(
            scene_number=scene_number,
            heading=heading,
            location=self._location_from_heading(heading),
            time_of_day=self._time_from_heading(heading),
            summary=self._clip(action, 360),
            characters=self._scene_characters(body),
            props=self._props(body),
            emotional_beat=self._emotion(action),
            visual_style=self._visual_style(heading, action),
        )

    def _characters(self, text: str, scenes: list[ScriptSceneBreakdown]) -> list[ScriptCharacterBreakdown]:
        lines = [line.strip() for line in text.splitlines()]
        counts: Counter[str] = Counter()
        descriptions: dict[str, str] = {}
        body_language: dict[str, str] = {}
        for index, line in enumerate(lines[:-1]):
            if self._is_character_cue(line, lines[index + 1]):
                name = self._clean_character(line)
                counts[name] += 1
        for scene in scenes:
            for character in scene.characters:
                descriptions.setdefault(character, self._character_description(character, text))
                body_language.setdefault(character, self._character_body_language(character, text))
        first_scene: dict[str, int] = {}
        for scene in scenes:
            for character in scene.characters:
                first_scene.setdefault(character, scene.scene_number)
        names = set(counts) | {name for scene in scenes for name in scene.characters}
        return [
            ScriptCharacterBreakdown(
                name=name,
                dialogue_lines=counts.get(name, 0),
                first_scene=first_scene.get(name),
                description=descriptions.get(name) or self._character_description(name, text),
                body_language=body_language.get(name) or self._character_body_language(name, text),
            )
            for name in sorted(names, key=lambda item: (first_scene.get(item, 999), item))
            if name not in {"FADE IN", "FADE OUT", "CUT TO", "SMASH CUT TO", "DISSOLVE TO", "END"}
        ]

    def _scene_characters(self, body: str) -> list[str]:
        lines = [line.strip() for line in body.splitlines()]
        names: list[str] = []
        for index, line in enumerate(lines[:-1]):
            if self._is_character_cue(line, lines[index + 1]):
                names.append(self._clean_character(line))
        for match in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*,\s*\d{2}\b", body):
            names.append(match.group(1).upper())
        return sorted(set(names))

    def _is_character_cue(self, line: str, next_line: str) -> bool:
        if not line or TRANSITION_RE.match(line) or SCENE_RE.match(line):
            return False
        if not CHARACTER_RE.match(line):
            return False
        if len(line.split()) > 4:
            return False
        return bool(next_line and not SCENE_RE.match(next_line) and not TRANSITION_RE.match(next_line))

    def _clean_character(self, line: str) -> str:
        return line.replace("(V.O.)", "").replace("(O.S.)", "").strip(" .").upper()

    def _character_description(self, name: str, text: str) -> str:
        pattern = re.compile(rf"([^.\n]*\\b{re.escape(name.title())}\\b[^.\n]*\\.)")
        match = pattern.search(text)
        if match:
            return self._clip(match.group(1).strip(), 220)
        upper_pattern = re.compile(rf"([^.\n]*\\b{re.escape(name)}\\b[^.\n]*\\.)")
        match = upper_pattern.search(text)
        return self._clip(match.group(1).strip(), 220) if match else "Description should be reviewed from screenplay context."

    def _character_body_language(self, name: str, text: str) -> str:
        lowered = text.lower()
        if "body language" in lowered or "posture" in lowered:
            sentences = re.findall(r"[^.\n]*(?:body language|posture|walk|gesture|breath|shoulders|eyes)[^.\n]*\.", text, flags=re.IGNORECASE)
            if sentences:
                return self._clip(" ".join(sentences[:2]), 220)
        return "Infer from action lines and dialogue delivery."

    def _props(self, text: str) -> list[str]:
        lowered = text.lower()
        found = [item for item in PROP_KEYWORDS if item in lowered]
        repeated_caps = [
            item.lower()
            for item, count in Counter(re.findall(r"\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?\b", text)).items()
            if count >= 2 and item.lower() not in {"arjun", "meera", "ananya", "raghav", "guardian"}
        ]
        return sorted(set(found + repeated_caps))[:20]

    def _locations(self, scenes: list[ScriptSceneBreakdown]) -> list[str]:
        return sorted({scene.location for scene in scenes if scene.location})

    def _location_from_heading(self, heading: str) -> str:
        clean = re.sub(r"^(INT\.|EXT\.|INT/EXT\.|I/E\.|EST\.)\s+", "", heading, flags=re.IGNORECASE)
        return clean.split(" - ")[0].strip().title() or "Unknown location"

    def _time_from_heading(self, heading: str) -> str | None:
        parts = heading.split(" - ")
        return parts[-1].strip().title() if len(parts) > 1 else None

    def _genre(self, text: str) -> str:
        lowered = text.lower()
        myth = any(word in lowered for word in ["vaikuntham", "tirumala", "temple", "deity", "devotional", "sanctum"])
        scifi = any(word in lowered for word in ["signal", "satellite", "waveform", "tablet", "frequency", "equations"])
        drama = any(word in lowered for word in ["mother", "memory", "faith", "humility", "promise"])
        if myth and scifi:
            return "mythological sci-fi drama" if drama else "mythological sci-fi"
        if myth:
            return "mythological devotional drama"
        if scifi:
            return "science fiction drama"
        return "drama"

    def _themes(self, text: str) -> list[str]:
        candidates = {
            "faith and science": ["faith", "science", "equations", "devotion"],
            "memory": ["memory", "remember", "promise", "grandfather"],
            "listening": ["listen", "listening", "signal", "song"],
            "devotion": ["temple", "sanctum", "lamp", "deity"],
            "technology as bridge": ["tablet", "camera", "satellite", "broadcast"],
            "humility": ["skeptical", "humility", "doubt"],
        }
        lowered = text.lower()
        themes = [theme for theme, words in candidates.items() if any(word in lowered for word in words)]
        return themes or ["human transformation"]

    def _summary(self, scenes: list[ScriptSceneBreakdown]) -> str:
        if not scenes:
            return "No screenplay scenes were detected."
        first = scenes[0].summary
        last = scenes[-1].summary
        return self._clip(f"{first} The story progresses through {len(scenes)} parsed scene(s) and resolves with: {last}", 700)

    def _logline(
        self,
        genre: str,
        scenes: list[ScriptSceneBreakdown],
        characters: list[ScriptCharacterBreakdown],
    ) -> str:
        lead = characters[0].name.title() if characters else "A protagonist"
        location = scenes[0].location if scenes else "an unknown world"
        return f"In a {genre}, {lead} follows an impossible signal from {location} into a test of faith, memory, and cinematic continuity."

    def _continuity_rules(
        self,
        characters: list[ScriptCharacterBreakdown],
        props: list[str],
        locations: list[str],
    ) -> list[str]:
        rules = [
            "Scene headings must drive location and time-of-day changes.",
            "Characters should keep costume, prop ownership, and body-language continuity across adjacent scenes.",
        ]
        if props:
            rules.append(f"Track recurring props exactly: {', '.join(props[:8])}.")
        if characters:
            rules.append(f"Track primary character identities: {', '.join(character.name for character in characters[:8])}.")
        if locations:
            rules.append(f"Do not switch locations outside parsed headings: {', '.join(locations[:8])}.")
        return rules

    def _panel(self, scene: ScriptSceneBreakdown, panel_number: int, style: str) -> StoryboardPanel:
        action = scene.summary or scene.heading
        lighting = self._lighting(scene.heading, action)
        camera = self._camera(scene.heading, action, panel_number)
        shot_type = self._shot_type(panel_number, action)
        image_prompt = (
            f"{shot_type}, {style}, {scene.heading}, {action} "
            f"Characters: {', '.join(scene.characters) or 'none specified'}. "
            f"Props: {', '.join(scene.props) or 'none specified'}. "
            f"Camera: {camera}. Lighting: {lighting}. "
            "Maintain screenplay continuity, grounded production design, no unrelated people, no market-report elements."
        )
        return StoryboardPanel(
            panel_number=panel_number,
            scene_number=scene.scene_number,
            heading=scene.heading,
            shot_type=shot_type,
            camera=camera,
            lighting=lighting,
            characters=scene.characters,
            props=scene.props,
            action=action,
            image_prompt=image_prompt,
            continuity_notes=[
                f"Location must remain {scene.location}.",
                f"Emotional beat: {scene.emotional_beat}.",
                "Use only characters and props parsed from this screenplay scene.",
            ],
        )

    def _shot_type(self, panel_number: int, action: str) -> str:
        lowered = action.lower()
        if panel_number == 1:
            return "wide establishing frame"
        if any(word in lowered for word in ["face", "eyes", "breath", "watches"]):
            return "medium close-up"
        if any(word in lowered for word in ["gate", "hall", "courtyard", "hills"]):
            return "wide cinematic frame"
        return "medium cinematic frame"

    def _camera(self, heading: str, action: str, panel_number: int) -> str:
        lowered = f"{heading} {action}".lower()
        if "vaikuntham" in lowered or "deity" in lowered or "guardian" in lowered:
            return "low angle heroic 35mm, slow push in"
        if "tablet" in lowered or "manuscript" in lowered or "coin" in lowered:
            return "50mm detail insert, controlled focus"
        if panel_number == 1:
            return "24mm establishing lens, gentle crane movement"
        return "35mm natural perspective, stable cinematic framing"

    def _lighting(self, heading: str, action: str) -> str:
        lowered = f"{heading} {action}".lower()
        if "pre-dawn" in lowered:
            return "silver-blue pre-dawn mist with oil-lamp warmth"
        if "sunset" in lowered:
            return "warm saffron sunset backlight"
        if "sanctum" in lowered:
            return "dim gold camphor glow with devotional highlights"
        if "vaikuntham" in lowered or "celestial" in lowered:
            return "pearl-white celestial glow with golden rim light"
        return "soft devotional cinematic light"

    def _emotion(self, action: str) -> str:
        lowered = action.lower()
        if any(word in lowered for word in ["skeptical", "doubt"]):
            return "skeptical wonder"
        if any(word in lowered for word in ["devotional", "lamp", "sanctum", "deity"]):
            return "devotional awe"
        if any(word in lowered for word in ["fail", "losing", "freeze"]):
            return "urgent discovery"
        if any(word in lowered for word in ["return", "stabilize", "bows"]):
            return "resolution and grace"
        return "mystery and discovery"

    def _visual_style(self, heading: str, action: str) -> str:
        lowered = f"{heading} {action}".lower()
        if "vaikuntham" in lowered:
            return "celestial devotional realism"
        if "temple" in lowered or "sanctum" in lowered:
            return "temple devotional cinematic realism"
        if "control room" in lowered or "tablet" in lowered:
            return "spiritual technology contrast"
        return "grounded cinematic drama"

    def _clip(self, text: str, limit: int) -> str:
        compact = " ".join(text.split())
        if len(compact) <= limit:
            return compact
        return compact[: limit - 3].rstrip() + "..."
