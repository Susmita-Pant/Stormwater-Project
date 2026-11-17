# Runbook for Susmita and the cold start team

## First run on Windows

1. Extract the ZIP. Open the `stormwater_builder` folder. In File Explorer's address bar type `powershell` and press Enter.
2. Check Python: `py --version` (Python 3.11 or newer recommended).
3. On Windows install timezone data once: `py -m pip install tzdata`. The core code otherwise uses only Python's standard library. On Linux/macOS, use `python3` instead of `py`; timezone data is usually installed by the OS.
4. Run `py run_checks.py`. Read the final PASS/FAIL output. The saved summary is `outputs/builder_test_results.json`.
5. Run `py agent.py --mode fixture`. Copy the printed output-folder path. Open its `report.html`; inspect `due_list.csv` and `reports.json` too.
6. Run `py replay.py "outputs\<printed-run-id>"`. It should verify the audit chain, hashes and deterministic outputs.

The fixture replay is intentionally dated September 26–October 2, 2026. These dates are sample inputs, not the current clock. The supplied `outputs/final_demo` is a saved example. Fresh runs create new folders; never overwrite audit evidence. A run interrupted before the finish record is incomplete and replay rejects it.

## Enable the actual local AI

Before going offline, use the same Ollama installation as Lab 1:

```
ollama pull llama3.2:3b
ollama list
py agent.py --mode ollama --model llama3.2:3b
```

Open Ollama or run `ollama serve` in a separate terminal if it is not running. This code only calls `127.0.0.1:11434`, not a cloud API. Once the model is downloaded, inference can run without internet. Timeout is 120 seconds per model call. A malformed or unavailable model produces escalation, not invented completion. Check `audit.jsonl` for model routing recovery; do not count a fallback run as successful live model performance.

The model chooses among currently allowed tools and drafts a strictly source-backed checklist. Python still executes all mandatory stages. The allowlist is **not** a permission the model can change. AI-generated free-form report narratives are intentionally excluded from this initial scope.

## Demonstration sequence

1. Run fixture mode and open HTML. Identify S01, the storm due dates, and the source station distance.
2. Show S02: weekly schedule has no extra baseline Part 4.2 rain inspection.
3. Show S03: missing rain hour and possible discharge both require a person.
4. Show a checklist citation in `reports.json`, then its matching section in `data/swppp.json`.
5. Run `py -m unittest discover -s tests -p test_builder.py -v`; point to the completion-denial and fabricated-quote tests.
6. Run `replay.py` on the exact run folder. Explain that hash chaining is tamper evidence, not external immutable storage.
7. If locally evaluated, rerun with `--mode ollama`. Say explicitly which mode is on screen.

## Repeat the clock over a week

Run these separately; each creates a new audit folder:

```
py agent.py --as-of 2026-09-27T19:00:00+00:00
py agent.py --as-of 2026-09-29T00:00:00+00:00
py agent.py --as-of 2026-10-02T00:00:00+00:00
```

For an operator pilot, `py watch.py --once --mode ollama` checks the present clock against current local exports. The supplied historical fixtures will correctly flag missing/stale observations. `watch.py` without `--once` polls hourly; Ctrl+C stops it. It drafts files only; no alerts are sent automatically. A production service needs supervision, retention, access control and a tested export process.

## Input contracts

- `sites.json`: stable site ID, lat/lon, IANA timezone, baseline inspection, weekly or biweekly_rain schedule, SWPPP version, controls, inspector, station and representativeness approval, working weekdays, opening/closing times and holiday dates.
- `rain.csv`: station_id, start_utc, end_utc, rain_in, units, quality. Exactly one non-overlapping one-hour increment per station and hour. Include 24 hours of warm-up before the replay start. UTC hour alignment required. Missing is not zero. Only `units=in`, `quality=ok`, finite nonnegative values are accepted.
- `inspections.json`: human-exported completed records with site_id, COMPLETED status, completed_at and named inspector. File trust is a pilot assumption; production needs authenticated export provenance.
- `deficiencies.json`: operator observation, discovery time, human-confirmed classification and explicit possible_discharge flag. Unconfirmed or unsupported classification escalates.
- `swppp.json`: one matching clause per control/site/version; source text and approved checklist action. Missing or duplicate/conflicting clauses escalate.

Replace exports atomically. Keep date-time offsets. Invalid file syntax stops processing; fix the input, retain the failed-run evidence and rerun. Do not repair data by guessing.

## Operational integration

Proposed initial system: the contractor's locally stored EPA 2022 CGP Site Inspection Report Template (Word form), with a separately maintained inspection export. The compliance manager exports records before the morning run and after a signed inspection; rainfall exporter supplies hourly increments. This is a concrete file-based pilot interface, **not an implemented proprietary app API**. The actual contractor's form and export must be confirmed with the team.

Agent outputs: `due_list.csv` for scheduling, `reports.json` for structured transfer, `report.html` for human review. Inspector manually transfers checked information into the official form, supplies actual observations/times, signs in that external system, and exports the completed record. Agent never writes back. `docs/form_mapping.md` names the remaining fields; HTML is a preparation sheet, not a permit-complete signed report.

## Troubleshooting

- `ZoneInfoNotFoundError`: run `py -m pip install tzdata` while online.
- Cannot reach model: start Ollama; check `ollama list`; verify model name. Fixture mode tests plumbing only.
- ESCALATE: inspect reason and source; do not delete the flag to get a green demo.
- Output directory already exists: omit `--out` for a fresh unique directory.
- Replay says input changed: recover the exact committed inputs/code for that run; do not alter hashes.
- Public CSV is raw METAR: do not feed it directly to the hourly engine; precipitation reset intervals differ from fixed hour bins.

## Team release checks

Domain lead signs off permit applicability, working calendars, classifications and unsupported conditions. Verifier runs independent truth cases, repeated model tests at two temperatures, category pass rates and adversarial tests. Adoption lead measures minutes per report, energy and support costs. Another team completes installation within the brief's 15-minute cold-start window without spoken help. Claim these only after they occur.
