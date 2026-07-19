from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class GenerationResult:
    provider: str
    provider_model: str
    generated_image: str | None
    generated_video: str | None
    metadata: dict


class GenerationProvider(ABC):
    name: str
    capabilities: dict = {
        "image_generation": True,
        "image_to_video": False,
        "reference_handling": False,
        "seed_support": False,
        "available_resolutions": [],
        "model_versions": [],
    }

    @abstractmethod
    def generate(self, prompt: str, metadata: dict | None = None) -> GenerationResult:
        raise NotImplementedError


class MockProvider(GenerationProvider):
    name = "mock"
    capabilities = {
        "image_generation": True,
        "image_to_video": False,
        "reference_handling": True,
        "seed_support": True,
        "available_resolutions": ["1024x576"],
        "model_versions": ["mock-continuity-v1"],
    }

    def generate(self, prompt: str, metadata: dict | None = None) -> GenerationResult:
        return GenerationResult(
            provider=self.name,
            provider_model="mock-continuity-v1",
            generated_image=f"mock://generated/{abs(hash(prompt))}",
            generated_video=None,
            metadata={"prompt_length": len(prompt), **(metadata or {})},
        )


class HiggsfieldProvider(MockProvider):
    name = "higgsfield"
    capabilities = {
        "image_generation": True,
        "image_to_video": True,
        "reference_handling": True,
        "seed_support": False,
        "available_resolutions": ["720p", "1080p"],
        "model_versions": ["unknown"],
    }


class RunwayProvider(MockProvider):
    name = "runway"


class KlingProvider(MockProvider):
    name = "kling"


class VeoProvider(MockProvider):
    name = "veo"


class GenerationProviderRegistry:
    providers: dict[str, type[GenerationProvider]] = {
        "mock": MockProvider,
        "higgsfield": HiggsfieldProvider,
        "runway": RunwayProvider,
        "kling": KlingProvider,
        "veo": VeoProvider,
    }

    def get(self, name: str = "mock") -> GenerationProvider:
        provider_cls = self.providers.get(name, MockProvider)
        return provider_cls()
