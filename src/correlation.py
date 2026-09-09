from __future__ import annotations
from collections import defaultdict
from datetime import datetime

def classify(names: set[str]) -> str:
    if "OOM_ERROR" in names: return "NODE_OOM"
    if "ZK_FAILURE" in names: return "COORDINATION_FAILURE"
    if "REPLICA_FAILURE" in names: return "REPLICA_UNAVAILABLE"
    if "DISK_SATURATION" in names: return "DISK_IO_SATURATION"
    if "FULL_GC" in names: return "FULL_GC_STORM"
    if {"HIGH_HEAP", "LONG_GC_PAUSE"} <= names: return "JVM_MEMORY_PRESSURE"
    return "SOLR_QUERY_LATENCY"
def correlate(signals: list[dict]) -> list[dict]:
    by_node=defaultdict(list)
    for s in signals: by_node[s["node"]].append(s)
    incidents=[]
    for node, events in by_node.items():
        events.sort(key=lambda x:x["timestamp"]); groups=[]; current=[]; last=None
        for e in events:
            now=datetime.fromisoformat(e["timestamp"])
            if last and (now-last).total_seconds()>120: groups.append(current); current=[]
            current.append(e); last=now
        if current: groups.append(current)
        for g in groups:
            names={x["signal"] for x in g}
            # Require multi-source corroboration, a categorical hard failure, or
            # sustained high latency (an independently useful user-impact alert).
            sustained_latency = sum(x["signal"] == "HIGH_SOLR_LATENCY" for x in g) >= 2
            if len({x["source"] for x in g}) < 2 and not (names & {"OOM_ERROR","ZK_FAILURE","REPLICA_FAILURE"} or sustained_latency): continue
            incidents.append({"incident_id":f"INC-{len(incidents)+1:03d}","node":node,"start":g[0]["timestamp"],"end":g[-1]["timestamp"],"classification":classify(names),"severity":"critical" if names & {"OOM_ERROR","FULL_GC","ZK_FAILURE"} else "high","signals":sorted(names),"evidence":g})
    return incidents
