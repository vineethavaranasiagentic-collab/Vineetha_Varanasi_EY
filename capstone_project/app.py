"""Streamlit interface for the Commercial Banking RM Copilot."""

import json

import streamlit as st

from agents import CLIENTS, create_plan, execute_plan

NO_INFORMATION = "The information is not available in the supplied client records."

st.set_page_config(page_title="RM Copilot", page_icon="🏦", layout="wide")
st.title("Commercial Banking Relationship Manager Copilot")
st.caption("Evidence-grounded planning assistant — human approval is required before client communication.")

client_id = st.selectbox("Client", options=list(CLIENTS), format_func=lambda key: CLIENTS[key].name)
request = st.text_area("Relationship-manager request", value="Review the client's March account activity and identify follow-up questions.", height=100)

if st.button("Create plan and execute", type="primary"):
    try:
        plan = create_plan(request, client_id)
        report = execute_plan(plan)
        st.subheader("Planner output")
        st.json(plan.model_dump(mode="json"))
        st.subheader("Observations")
        for observation in report.observations:
            st.info(observation)
        st.subheader("Suggested follow-ups")
        for item in report.recommended_follow_ups:
            st.write(f"- {item}")
        st.subheader("Evidence")
        st.dataframe([item.model_dump() for item in report.evidence], use_container_width=True)
        st.subheader("Draft message")
        st.text_area("Human-review draft", report.draft_message, height=180)
        st.warning("Human approval required. This application does not send messages or make lending/investment decisions.")
        with st.expander("Audit trail"):
            st.code(json.dumps(report.audit, indent=2))
    except ValueError as exc:
        st.error(str(exc))
