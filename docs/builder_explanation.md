# Explain your builder contribution

Your job is code, tools, orchestration and the runbook. You should be able to trace one row all the way through the system.

**A short explanation:** “I built a local workflow that reads site records and hourly rainfall, computes the inspection due list in Python, retrieves that site's SWPPP clauses, and prepares a cited checklist and corrective-action draft. The language model cannot compute deadlines or complete an inspection. Every tool call is logged, and a separate replay checks the deterministic results.”

**Why is this agentic?** In Ollama mode a model chooses among allowed next tools, sees the task context and prepares structured output. Dependency gates require all stages. It has bounded autonomy; it is deliberately not a fully autonomous inspector. Fixture mode is a deterministic simulation of the workflow, not live AI.

**Why not let the model choose rain thresholds?** The threshold and calendar logic are governed rules. `engine.py` uses Decimal rainfall sums and timezone-aware Python dates. Source values, units and time coverage are validated first.

**What is retrieval here?** Filter the document corpus by site, version and required control. Pass only those clauses to the model. Validate the returned citation, quote and approved task against the actual retrieved source. This is small-corpus retrieval, not semantic embedding search.

**How do you prove it cannot close an inspection?** The dispatcher rejects tools absent from policy. A completion callback is deliberately supplied in the adversarial test; it still cannot be invoked. Output contracts reject injected completion fields. The report status is set by code to DRAFT or ESCALATE; inspection_status stays NOT_COMPLETED. Only imported human records can show completed work.

**What happens on Sunday?** Python evaluates the site's work calendar. A continuous 24-hour clock normally applies. If the entire window is outside normal working hours, footnote 67 permits the next business-day close. The code uses the beginning of the hourly threshold-crossing interval as a conservative bound. Ask the domain lead to verify work calendars and any exceptions.

**What breaks first at a real contractor?** Export mismatch, unrepresentative gauges, missing hourly data and unapproved permit assumptions. Explain that station proximity is only a screen. Our public raw rainfall cache is not silently treated as site measurements.

**What do the tests establish?** Deterministic calculations and software boundaries for the seeded cases. They do not establish live-model accuracy, complete permit coverage, usability, energy use or financial return.

**What should you do before presenting?** Run the fixture demo yourself, inspect one audit, run Ollama, change one synthetic input and predict the change, then ask the verifier to challenge it. Commit the changes you understand, with your own name. Do not claim an A+ or a production-ready system from these checks alone.
