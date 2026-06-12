import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

passed = 0
failed = 0

test_modules = [
    "tests.test_config",
    "tests.test_image_processor",
    "tests.test_db_manager",
    "tests.test_severity_analyzer",
    "tests.test_disease_knowledge_base",
]

for module_name in test_modules:
    print(f"\n{'='*60}")
    print(f"Running: {module_name}")
    print(f"{'='*60}")
    try:
        __import__(module_name, fromlist=["test_*"])
        mod = sys.modules[module_name]
        test_funcs = [f for f in dir(mod) if f.startswith("test_")]
        for func_name in test_funcs:
            try:
                getattr(mod, func_name)()
                print(f"  PASS: {func_name}")
                passed += 1
            except AssertionError as e:
                print(f"  FAIL: {func_name} - {e}")
                failed += 1
            except Exception as e:
                print(f"  ERROR: {func_name} - {e}")
                failed += 1
    except Exception as e:
        print(f"  FAIL: Could not load module {module_name}: {e}")
        failed += 1

print(f"\n{'='*60}")
print(f"Results: {passed} passed, {failed} failed")
print(f"{'='*60}")
sys.exit(1 if failed > 0 else 0)
