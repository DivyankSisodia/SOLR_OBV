# Solr Observability AI — Case Study, Version 2

A submission-ready prototype for detecting and explaining SolrCloud operational incidents from synthetic Solr request logs and JVM GC telemetry. It simulates a 25-node cluster, injects seven controlled failure modes, detects anomalies with transparent rules, correlates evidence into incidents, and scores the result against labelled ground truth.

## What is included

* 25-node, 60-minute SolrCloud synthetic telemetry simulation
* Seven labelled failure scenarios and realistic baseline noise
* Raw Solr-style request events and JVM GC events (JSONL)
* Parsers, deterministic rules, correlation, health scoring, and evidence-grounded RCA prompt creation
* Ground-truth precision / recall / F1 evaluation
* Streamlit dashboard for cluster overview, incidents, evidence, and evaluation

## Quick start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 -m src.pipeline --output data/generated
streamlit run app/streamlit_app.py
```

The pipeline has a fixed random seed, so results are reproducible. To run the automated smoke test:

```bash
python3 -m unittest discover -s tests -v
```

## Key design decision

An LLM is used only after deterministic rules and cross-source correlation have produced bounded evidence. It may summarize the likely root cause and remediation, but cannot invent signals or mark an incident as detected. See `docs/CASE_STUDY_SOLUTION.md` for the architecture, rules, prompt, trade-offs, and production roadmap.
