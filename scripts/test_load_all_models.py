import sys
from pathlib import Path
import pickle

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from arena.contestants import ContestantRegistry
from arena.contestants.adapters import create_adapter

registry = ContestantRegistry()
contestants = registry.list_contestants()

print(f"Total contestants: {len(contestants)}")
for c in contestants:
    print(f"\n--- Testing {c.contestant_id} ({c.display_name}) ---")
    adapter = create_adapter(c, mock=False)
    print(f"Adapter class: {type(adapter).__name__}")
    try:
        adapter.load_models()
        print(f"  Successfully loaded models! is_loaded={adapter.is_loaded}")
    except Exception as e:
        print(f"  Failed to load models: {e}")
