# Solr Observability AI — Case Study, Version 2

A submission-ready prototype for detecting and explaining SolrCloud operational incidents from synthetic Solr request logs and JVM GC telemetry. It simulates a 25-node cluster, injects seven controlled failure modes, detects anomalies with transparent rules, correlates evidence into incidents, and scores the result against labelled ground truth.

## What this prototype does

This is a small SolrCloud monitoring demo. It creates one hour of sample data for 25 nodes and injects seven problems, including high GC, slow queries, replica failures, disk pressure, ZooKeeper failures, and an out-of-memory error.

The pipeline reads the generated JSONL files, checks request, JVM, and node metrics, and groups related signals into incidents. It compares the detected incidents with the known scenarios and displays the results in a Streamlit dashboard. The optional Gemini call summarizes the incident evidence; it does not decide whether an incident exists.

The data is synthetic and the rules are intentionally simple. The prototype uses a fixed random seed, fixed thresholds, and node/time-based correlation. A production version would need real logs, adaptive thresholds, and Solr shard and replica topology.

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
