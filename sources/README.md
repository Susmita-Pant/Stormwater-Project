# Source provenance

The public raw ASOS snapshot is ABQ, October 1–7, 2025, UTC observation times, precipitation in inches. It is retained for source assessment and adapter development; it is **not** the rainfall used for the seeded replay. Do not silently round METAR times or sum overlapping precipitation accumulations. A reviewed station-specific normalization adapter is still needed for operational public-data ingestion.

The default synthetic fixtures in data/rain.csv are already non-overlapping hourly increments. The tests use only those fixtures.

The cached EPA PDF is the original 2022 permit returned by the URL in manifest.json. Current EPA hub: https://www.epa.gov/npdes/2022-construction-general-permit-cgp . The domain lead must check modifications and site-specific coverage. Relevant rules are Parts 4.2.1–4.2.3, footnotes 66–68, 2.1.4b, 5.2.1 and 5.4.1.

IEM source documentation: https://mesonet.agron.iastate.edu/request/download.phtml and https://mesonet.agron.iastate.edu/request/hourlyprecip.phtml . p01i is tied to the previous precipitation reset, not arbitrary reporting frequency.

The synthetic SWPPP contains only three control clauses per site. It is not a complete SWPPP or complete official inspection form. Every generated checklist item cites these synthetic clauses explicitly.

A second cached file, iem_hourly.csv, provides IEM processed hourly precipitation for the same week. It is not mixed into the synthetic replay. Confirm hour-label convention, quality and representativeness with the domain lead before adding it as operational rainfall input.
