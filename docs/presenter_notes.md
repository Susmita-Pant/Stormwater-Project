# Presenter notes for Susmita

Use these to rehearse; adapt the wording to what you have personally run and understood.


## Slide 1

Opening, 40 seconds. I am Susmita Pant, the builder for our four-person Option 4 team. This is our current implementation and team handoff. The system prepares the inspector and tracks clocks; the accountable person still inspects and signs. Distinguish the tested fixture replay from the unvalidated local-model path.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 2

About 50 seconds. Describe a site inspector who must review rainfall, find due sites, locate applicable SWPPP controls and prepare records while also doing field work. The question on screen is illustrative wording, not a quote from an interview. We have not measured a time saving yet. The compliance manager is the second user and owns the incoming records.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 3

About 50 seconds. I own the implementation, tools, orchestration and runbook. Domain review and independent verification are separate responsibilities. The other names have not been supplied, so assign them in the README before submission. The adoption lead must measure costs and user time rather than make up a return on investment.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 4

About 70 seconds. Start from local exports. The agent executes five required tools: check_rain, list_due, retrieve_swppp, compute_actions and draft_report. In local Ollama mode the model selects among tools whose prerequisites are satisfied. All mandatory gates still run. Model failure is logged and escalated. Fixture mode is an explicit deterministic substitute for testing the plumbing.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 5

About 65 seconds. These are synthetic sites and synthetic rainfall, replayed September 26 through October 2, 2026. S01 has the biweekly-plus-rain schedule. S02 is weekly, so baseline Part 4.2 does not add a separate rain trigger. S03 contains a missing rain interval and a possible discharge. OVERDUE means a conservative operational flag, not a final permit-violation determination. In the live demo open the HTML to inspect exact dates.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 6

About 60 seconds. Open data/swppp.json and locate the S01 clause. The corpus is synthetic and site/version-filtered. The output validator requires exact source quotations, correct section IDs and all required controls. A model cannot insert a new section or a computed deadline into this text. This intentionally uses metadata retrieval for a small corpus; semantic embeddings are not necessary for the current scope.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 7

About 65 seconds. The policy allowlist has five tools and no close, sign or submit operation. The dispatcher checks policy before invoking a tool. Show test_prompt_injection_completion: even when a completion callback is supplied, the dispatcher denies it. The contract rejects an added inspection_status field. Only the external inspector form can record completion; imported signed records affect future scheduling. This protects the agent boundary, not a malicious administrator with filesystem access.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 8

About 65 seconds. These are actual builder regression results from the delivered code, not an independent acceptance study. Tests cover exact rainfall threshold, gaps, units, duplicates, weekend and holiday clocks, corrective actions, citations, denied tools and end-to-end replay. Twelve deterministic tool calls across three sites reproduce. Live Ollama quality, repeated runs and laptop performance remain to be measured by the team. Do not describe 35 out of 35 as model accuracy.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 9

About 70 seconds. Rain at a nearby station is not necessarily rain at the site. The distance threshold is a project screen, not an EPA rule. The permit scope is baseline Part 4.2 only. Consecutive wet dates are flagged for multi-day storm review. Snowmelt, dewatering and special inspection schedules require domain review. The HTML is a preparation sheet; it does not cover every field in the official inspection report. We must confirm the real contractor export and form.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 10

About 60 seconds. This is a plan, not a claimed financial result. Compare manual and assisted drafting on matched cases, including review time and error correction. Measure laptop energy, runtime and setup/support effort. Local inference has no per-call cloud bill but is not costless. The adoption lead should compute cost per report, total ownership cost and a sensitivity band from measurements.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 11

About 60 seconds. Champion: compliance manager. Accountable user: qualified inspector. Likely concerns are false alerts, added export work and legal accountability. Begin in shadow mode, comparing outputs to current practice. Expand only after independent acceptance and a cold-start run. The brief requires another team to install from the runbook in 15 minutes. This slide is a proposed path that the adoption lead should refine with a real user.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.


## Slide 12

About 65 seconds. I would start by collecting a real-shaped export and agreeing the permit rule matrix before expanding the AI features. I would bring the verifier in before building so expected results are independent. Next, run the local model on the team laptop, resolve domain questions, measure user time and execute the cold-start rehearsal. Transition to the eight-minute demonstration using the RUNBOOK. Be ready to show a failure, not just the happy path.

Sources: CIVE 580C8 Final Project Brief, Option 4 and rubric; supplied Labs 5–9. EPA 2022 CGP Parts 4–5: https://www.epa.gov/system/files/documents/2022-01/2022-cgp-final-permit.pdf . Implementation: stormwater_builder/engine.py, agent.py and docs/.