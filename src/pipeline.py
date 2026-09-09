from __future__ import annotations
import argparse, json
from pathlib import Path
from .synthetic_generator import generate
from .parsers import read_jsonl
from .detection import detect
from .correlation import correlate
from .evaluation import evaluate
from .llm import build_rca_prompt, run_rca
def run(output: str | Path) -> dict:
    out=Path(output); summary=generate(out)
    signals=detect(read_jsonl(out/"solr_requests.jsonl"),read_jsonl(out/"jvm_gc.jsonl"),read_jsonl(out/"node_system.jsonl"))
    incidents=correlate(signals); metrics=evaluate(incidents,out/"ground_truth.json")
    for i in incidents: i["rca_prompt"]=build_rca_prompt(i)
    (out/"signals.json").write_text(json.dumps(signals,indent=2)); (out/"incidents.json").write_text(json.dumps(incidents,indent=2)); (out/"evaluation.json").write_text(json.dumps(metrics,indent=2)); summary.update({"signals":len(signals),"detected_incidents":len(incidents),"f1":metrics["f1"]})
    (out/"run_summary.json").write_text(json.dumps(summary,indent=2)); return summary
if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--output",default="data/generated"); a=p.parse_args(); print(json.dumps(run(a.output),indent=2))
