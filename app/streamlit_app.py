from __future__ import annotations
import json, sys
from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st
ROOT=Path(__file__).resolve().parents[1]; sys.path.insert(0,str(ROOT))
from src.pipeline import run
from src.llm import run_rca
DATA=ROOT/"data"/"generated"
st.set_page_config(page_title="Solr Observability AI",page_icon="🛰️",layout="wide")
st.title("Solr Observability AI")
st.caption("25-node synthetic SolrCloud • explainable detection • evidence-first RCA")
if st.sidebar.button("Regenerate simulation",type="primary") or not (DATA/"evaluation.json").exists(): run(DATA)
incidents=json.loads((DATA/"incidents.json").read_text()); metrics=json.loads((DATA/"evaluation.json").read_text()); truth=json.loads((DATA/"ground_truth.json").read_text())
c1,c2,c3,c4=st.columns(4); c1.metric("Cluster nodes",len(truth["nodes"])); c2.metric("Injected scenarios",len(truth["incidents"])); c3.metric("Detected incidents",len(incidents)); c4.metric("Detection F1",f'{metrics["f1"]:.0%}')
st.divider(); left,right=st.columns([1.45,1])
with left:
    st.subheader("Incident timeline")
    frame=pd.DataFrame([{"node":i["node"],"classification":i["classification"],"start":i["start"],"end":i["end"],"severity":i["severity"]} for i in incidents])
    if not frame.empty:
        frame["start"]=pd.to_datetime(frame["start"]); frame["end"]=pd.to_datetime(frame["end"])
        st.plotly_chart(px.timeline(frame,x_start="start",x_end="end",y="node",color="classification",hover_data=["severity"],template="plotly_dark"),use_container_width=True)
with right:
    st.subheader("Evaluation")
    st.metric("Precision",f'{metrics["precision"]:.0%}'); st.metric("Recall",f'{metrics["recall"]:.0%}')
    st.dataframe(pd.DataFrame(metrics["scenario_results"]),hide_index=True,use_container_width=True)
st.subheader("Evidence-led incident detail")
choice=st.selectbox("Select incident",[f'{i["incident_id"]} · {i["node"]} · {i["classification"]}' for i in incidents])
selected=incidents[[i["incident_id"] for i in incidents].index(choice.split(" · ")[0])]
st.error(f'{selected["severity"].upper()} — {selected["classification"]} on {selected["node"]}')
a,b=st.columns([1,1.5]); a.write("**Correlated signals**"); a.write(", ".join(selected["signals"]))
b.write("**LLM handoff prompt**"); b.code(selected["rca_prompt"],language=None)

# --- Gemini-powered RCA ---
st.subheader("🤖 AI Root-Cause Analysis (Gemini)")
if st.button("Run AI Root-Cause Analysis", type="primary", key="rca_btn"):
    with st.spinner("Querying Gemini 3.7 Flash…"):
        try:
            rca_response = run_rca(selected)
            st.success("Analysis complete")
            st.markdown(rca_response)
        except Exception as e:
            st.error(f"LLM call failed: {e}")

st.dataframe(pd.DataFrame(selected["evidence"])[["timestamp","source","signal","detail"]],hide_index=True,use_container_width=True)

