from __future__ import annotations
import json
from pathlib import Path
def evaluate(incidents: list[dict], truth_path: str | Path) -> dict:
    truth=json.loads(Path(truth_path).read_text())["incidents"]; matched=[]
    for t in truth:
        found=next((i for i in incidents if i["node"]==t["node"] and i["classification"]==t["scenario"]),None)
        matched.append({"scenario":t["scenario"],"node":t["node"],"detected":bool(found),"incident_id":found["incident_id"] if found else None})
    tp=sum(x["detected"] for x in matched); fp=max(0,len(incidents)-tp); fn=len(truth)-tp
    precision=tp/(tp+fp) if tp+fp else 0; recall=tp/(tp+fn) if tp+fn else 0
    return {"true_positives":tp,"false_positives":fp,"false_negatives":fn,"precision":round(precision,3),"recall":round(recall,3),"f1":round(2*precision*recall/(precision+recall),3) if precision+recall else 0,"scenario_results":matched}
