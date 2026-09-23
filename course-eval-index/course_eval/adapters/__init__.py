import importlib


def get_adapter(name, cfg):
    """Load an adapter module by name (course_eval/adapters/<name>.py) and instantiate it."""
    mod = importlib.import_module(f"course_eval.adapters.{name}")
    return mod.Adapter(cfg)
