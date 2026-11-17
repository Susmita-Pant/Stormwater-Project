"""Builder regression tests, NOT independent verifier acceptance or live model evaluation."""
import unittest,json,time
from pathlib import Path
root=Path(__file__).resolve().parent
suite=unittest.defaultTestLoader.discover(str(root/'tests'));t=time.perf_counter();result=unittest.TextTestRunner(verbosity=2).run(suite)
summary={'suite':'builder regression','tests':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'runtime_seconds':time.perf_counter()-t,'live_model_tested':False,'independent_verification':False}
(root/'outputs/builder_test_results.json').write_text(json.dumps(summary,indent=2));raise SystemExit(not result.wasSuccessful())
