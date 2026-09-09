"""Explainable signal-level rules. Thresholds are deliberately configuration-friendly."""
from __future__ import annotations
RULES = {"HIGH_LATENCY_MS": 1000, "HIGH_HEAP_PCT": 85, "LONG_GC_PAUSE_MS": 500, "HIGH_DISK_PCT": 90}
def detect(solr: list[dict], gc: list[dict], system: list[dict]) -> list[dict]:
    signals=[]
    def emit(e, typ, detail): signals.append({"timestamp":e["timestamp"], "node":e["node"], "signal":typ, "detail":detail, "source": "solr" if "latency_ms" in e else ("jvm_gc" if "pause_ms" in e else "system")})
    for e in solr:
        if e["latency_ms"] >= RULES["HIGH_LATENCY_MS"]: emit(e,"HIGH_SOLR_LATENCY",f'{e["latency_ms"]} ms')
        if e["status"] >= 500: emit(e,"SOLR_ERROR",f'{e["status"]}: {e["message"]}')
        if "OutOfMemoryError" in e["message"]: emit(e,"OOM_ERROR",e["message"])
        if "ZooKeeper" in e["message"]: emit(e,"ZK_FAILURE",e["message"])
        if "replica unavailable" in e["message"]: emit(e,"REPLICA_FAILURE",e["message"])
    for e in gc:
        if e["heap_used_pct"] >= RULES["HIGH_HEAP_PCT"]: emit(e,"HIGH_HEAP",f'{e["heap_used_pct"]}%')
        if e["pause_ms"] >= RULES["LONG_GC_PAUSE_MS"]: emit(e,"LONG_GC_PAUSE",f'{e["pause_ms"]} ms')
        if e["gc_type"] == "Full GC": emit(e,"FULL_GC",e["gc_type"])
    for e in system:
        if e["disk_util_pct"] >= RULES["HIGH_DISK_PCT"]: emit(e,"DISK_SATURATION",f'{e["disk_util_pct"]}%')
    return signals
