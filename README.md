# Construction stormwater inspection agent

Option 4, CIVE 580C8, Fall 2026. Builder: Susmita Pant. Domain lead, verifier and adoption lead: **team must assign names**. This is a working, scoped builder implementation, not a completed team submission or a production compliance system.

Start with **RUNBOOK.md**. The package runs a three-site rainy-week replay without a cloud account. Open the generated `report.html` for the inspector preparation report. Local Ollama mode is implemented but must be run and evaluated on your laptop; fixture mode does not test AI quality.

## Builder ownership

- `engine.py`: deterministic rainfall, distance, due-list, corrective-action and output-contract tools.
- `agent.py`: bounded tool routing, local model adapter, guarded checklist drafting, report exports, audit.
- `data/policy.json`: allowlist. There is no inspection-completion, signing, submission or source-writing tool.
- `replay.py`: checks input/output hashes and reruns deterministic tools.
- `watch.py`: periodic event checks of local exports, including time-based overdue reevaluation.
- `make_data.py`: reproducible project-specific synthetic generator following the labs' generator pattern. This is newly written project data, not an instructor-supplied stormwater generator.
- `tests/` and `run_checks.py`: builder regression checks; independent verifier evaluation remains required.

## Lab connections

| Lab | Applied pattern | Implementation |
|---|---|---|
| 1–2 | Local model; structured data | Local Ollama JSON calls and versioned JSON/CSV inputs |
| 3–4 | Complete scripts; no framework | Python tools and bounded loop |
| 5 | Output contracts and escalation | Exact fields, source validation, numeric tools; fail closed |
| 6 | Retrieve then validate evidence | Site/control/version-filtered retrieval and exact quotes |
| 7 | Multi-tool routing and reason log | Tool allowlist, prerequisites, bounded calls, route reasons |
| 8 | Known-answer evaluation | Builder regression tests; separate repeated LLM eval still needed |
| 9 | Adversarial inputs | Wrong units, NaN, forged tools, extra completion fields, fabricated quotes |
| 10–13 | Brief-required audit/governance/cost | Audit and policy implemented from brief; lab files not supplied |

Retrieval intentionally uses exact control metadata for the small synthetic corpus, not embeddings. Live model output is constrained to source-backed checklist actions. This limits creativity and keeps numbers out of model-authored deliverables. Expand to embeddings only after measuring a retrieval need; retain site/version filters and quote checks.

## Scope and boundaries

Synthetic New Mexico-like construction sites, EPA CGP baseline Part 4.2 schedules. Do not apply these rules to a Colorado state permit or another jurisdiction without domain review. Public permit PDF is cached; domain lead must confirm the downloaded version and any applicable modifications before accepting rules. Station distance is a project screening rule, not proof of representativeness or an EPA distance threshold.

The code does not inspect, observe, certify, sign, send, submit or mark an inspection complete. Completed records are read from a human-maintained external export. No credentials or write connection to that system exist in this project. A user who edits source files or Python code is outside this process boundary; hashes detect changed inputs, not malicious administrators.

Snowmelt, special/reduced inspection frequencies, dewatering, prolonged storms, extensions and permit applicability remain domain-review cases. Consecutive wet local dates escalate rather than silently treating a prolonged storm as an isolated event. Hourly threshold timing uses the earliest bound of the crossing hour, so an alert can be up to an hour early. A displayed OVERDUE state is an operational flag, not a legal violation finding.

## What is finished and what is pending

Implemented and exercised: fixture path, three sites, rain triggers, standard deadline calculations, cited checklist, policy denial, audit and replay, HTML/CSV/JSON outputs, builder regression tests.

Pending team acceptance: domain-approved jurisdiction and holiday/work calendar; real contractor form/export selection and mapping; live Ollama evaluation and latency on a 16 GB laptop; independent verifier cases and failure register; human time study, measured energy, cost model; cold start test and final panel rehearsal. Public ASOS observations are cached as reference evidence, but the default replay uses synthetic hourly increments. Do not present fixture pass rates as model accuracy.

## Academic contribution

Understand, run and explain this AI-assisted code. Disclose assistance under course policy. Commit your own reviewed changes under your own Git identity. No commits or teammate contributions have been invented. Your verifier should write independent expected answers rather than copy these tests. Your domain lead must own permit interpretation; your adoption lead owns measured business results.
