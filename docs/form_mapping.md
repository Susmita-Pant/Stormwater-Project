# Form interface and gaps

Target: EPA 2022 CGP Site Inspection Report Template, as a proposed local Word-form workflow. Template source: https://www.epa.gov/npdes/construction-general-permit-resources-tools-and-templates

| Form content | Agent output | Who completes or verifies it |
|---|---|---|
| Site identification | site_id, site_name | Compliance manager confirms legal permit identity |
| Inspector identity and qualifications | inspector_of_record | Inspector confirms qualification; credential not verified here |
| Inspection date, start/end and weather | null until observed | Inspector enters actual site observations |
| Reason/frequency and triggering rainfall | due_list and rain_evidence | Domain lead/inspector confirms schedule and representative gauge |
| Areas and controls inspected | cited checklist | Inspector records actual condition; list is not exhaustive Part 4.5 coverage |
| Routine maintenance/corrective findings | corrective_actions | Inspector supplies observations, classifications and immediate response |
| Corrective action timing | computed deadline and clause | Inspector confirms work completion and extension documentation |
| Certification and signature | null; no action available | Authorized external signatory only |

Missing final-report items must not be filled with generated observations. Full Part 4.5/4.6/4.7 template coverage is a domain-led integration task before deployment. Signed records stay in the external system; our code only consumes an export.
