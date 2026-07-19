from datetime import datetime, timezone
from typing import Any


def append_version_history(
    current_history: list[Any] | None, before: dict[str, Any], actor_id: str
) -> list[Any]:
    history = list(current_history or [])
    history.append(
        {
            "changed_at": datetime.now(timezone.utc).isoformat(),
            "actor_id": actor_id,
            "before": before,
        }
    )
    return history
