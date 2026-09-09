"""Controlled 25-node SolrCloud log generator; no production data is used."""
from __future__ import annotations
import argparse, json, random
from datetime import datetime, timedelta, timezone
from pathlib import Path

SCENARIOS = [
    ("JVM_MEMORY_PRESSURE", "solr-node-03", 10, 18, "Heap pressure causes long GC pauses and slow requests."),
    ("FULL_GC_STORM", "solr-node-07", 20, 28, "Repeated full GC pauses cause request latency spikes."),
    ("SOLR_QUERY_LATENCY", "solr-node-11", 30, 38, "Expensive queries cause high request latency without JVM pressure."),
    ("REPLICA_UNAVAILABLE", "solr-node-15", 12, 22, "A shard replica becomes unavailable, producing 503 responses."),
    ("DISK_IO_SATURATION", "solr-node-19", 40, 48, "Slow disk I/O extends GC and indexing request latency."),
    ("COORDINATION_FAILURE", "solr-node-21", 25, 33, "ZooKeeper session instability causes leader-election errors."),
    ("NODE_OOM", "solr-node-24", 48, 55, "Heap exhaustion leads to OutOfMemoryError and node request failures."),
]

def write_jsonl(path: Path, items: list[dict]) -> None:
    with path.open("w") as f:
        for item in items: f.write(json.dumps(item) + "\n")

def generate(output: str | Path, seed: int = 42) -> dict:
    rng = random.Random(seed); out = Path(output); out.mkdir(parents=True, exist_ok=True)
    base = datetime(2026, 1, 15, 9, 0, tzinfo=timezone.utc)
    nodes = [f"solr-node-{i:02d}" for i in range(1, 26)]
    solr, gc, system = [], [], []
    scenario_by_node = {node: (kind, start, end) for kind, node, start, end, _ in SCENARIOS}
    for minute in range(60):
        ts = (base + timedelta(minutes=minute)).isoformat()
        for node in nodes:
            active = scenario_by_node.get(node)
            kind = active[0] if active and active[1] <= minute <= active[2] else None
            latency = max(15, int(rng.gauss(95, 25))); status = 200; message = "request completed"
            heap = max(35, min(72, round(rng.gauss(54, 7), 1))); pause = max(5, round(rng.gauss(28, 9), 1)); full_gc = False
            disk = max(15, round(rng.gauss(32, 8), 1))
            if kind == "JVM_MEMORY_PRESSURE": heap, pause, latency = 91 + rng.random()*5, 850 + rng.random()*500, 1100 + rng.randrange(900)
            elif kind == "FULL_GC_STORM": heap, pause, latency, full_gc = 89 + rng.random()*7, 1500 + rng.random()*1300, 1700 + rng.randrange(1000), True
            elif kind == "SOLR_QUERY_LATENCY": latency, message = 1900 + rng.randrange(1800), "slow distributed query"
            elif kind == "REPLICA_UNAVAILABLE": status, latency, message = 503, 1100 + rng.randrange(700), "replica unavailable for shard2"
            elif kind == "DISK_IO_SATURATION": disk, pause, latency, message = 96 + rng.random()*3, 650 + rng.random()*500, 1050 + rng.randrange(850), "slow fsync during index commit"
            elif kind == "COORDINATION_FAILURE": status, latency, message = 500, 850 + rng.randrange(600), "ZooKeeper session expired; leader election failed"
            elif kind == "NODE_OOM": heap, pause, status, latency, message = 99.5, 2800 + rng.random()*900, 500, 3000 + rng.randrange(1000), "java.lang.OutOfMemoryError: Java heap space"
            solr.append({"timestamp": ts, "node": node, "collection": "products", "request_path": "/select" if minute % 3 else "/update", "status": status, "latency_ms": latency, "message": message})
            gc.append({"timestamp": ts, "node": node, "gc_type": "Full GC" if full_gc or kind == "NODE_OOM" else "G1 Young Generation", "pause_ms": pause, "heap_used_pct": heap})
            system.append({"timestamp": ts, "node": node, "disk_util_pct": disk})
    truth = [{"scenario": k, "node": n, "start_minute": s, "end_minute": e, "expected_rca": d} for k,n,s,e,d in SCENARIOS]
    write_jsonl(out / "solr_requests.jsonl", solr); write_jsonl(out / "jvm_gc.jsonl", gc); write_jsonl(out / "node_system.jsonl", system)
    (out / "ground_truth.json").write_text(json.dumps({"simulation_start": base.isoformat(), "nodes": nodes, "incidents": truth}, indent=2))
    return {"nodes": len(nodes), "solr_events": len(solr), "gc_events": len(gc), "incidents": len(truth)}

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--output", default="data/generated"); p.add_argument("--seed", type=int, default=42); a=p.parse_args(); print(generate(a.output, a.seed))
