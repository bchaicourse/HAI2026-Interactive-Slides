"""Tab 2: Build Pipeline UI."""

import uuid

import streamlit as st


def _agent_names():
    return [a["name"] for a in st.session_state.agents]


def render(tab):
    with tab:
        st.markdown(
            "Each step runs in sequence. A step is either a **single agent** or a "
            "**team** (wrapped as `SocietyOfMindAgent`, which runs the inner team "
            "and returns a summary to the next step)."
        )

        names = _agent_names()

        for i, step in enumerate(st.session_state.pipeline):
            sid = step["id"]
            step_label = step.get("agent_name") or step.get("team_name", "Team")
            with st.expander(f"Step {i + 1}: {step_label}", expanded=False):
                stype = st.radio(
                    "Type", ["agent", "team"],
                    index=0 if step["type"] == "agent" else 1,
                    key=f"st_{sid}",
                    horizontal=True,
                )
                st.session_state.pipeline[i]["type"] = stype

                if stype == "agent":
                    cur = step.get("agent_name", "")
                    idx = names.index(cur) if cur in names else 0
                    chosen = st.selectbox("Agent", names, index=idx, key=f"sa_{sid}")
                    st.session_state.pipeline[i]["agent_name"] = chosen

                else:
                    _render_team_config(i, step, sid, names)

                if st.button("Remove Step", key=f"sr_{sid}"):
                    st.session_state.pipeline.pop(i)
                    st.rerun()

        if st.button("Add Step"):
            st.session_state.pipeline.append({
                "id": str(uuid.uuid4()),
                "type": "agent",
                "agent_name": names[0] if names else "",
                "team_name": "Team",
                "team_type": "roundrobin",
                "members": [],
                "max_turns": 6,
                "termination_keyword": "",
                "team_description": "",
                "routing_guidance": "",
                "handoffs": {},
            })
            st.rerun()


def _render_team_config(i, step, sid, names):
    """Render team-specific configuration widgets."""
    tname = st.text_input(
        "Team Name", step.get("team_name", "Team"), key=f"stn_{sid}",
    )
    tdesc = st.text_input(
        "Description", step.get("team_description", ""), key=f"std_{sid}",
    )
    tt_options = ["roundrobin", "llm_orchestration", "swarm"]
    ttype = st.selectbox(
        "Team Type", tt_options,
        index=tt_options.index(step.get("team_type", "roundrobin")),
        key=f"stt_{sid}",
    )
    members = st.multiselect(
        "Members", names,
        default=[m for m in step.get("members", []) if m in names],
        key=f"sm_{sid}",
    )
    max_t = st.number_input(
        "Max Turns", 1, 30, step.get("max_turns", 6), key=f"smt_{sid}",
    )
    st.session_state.pipeline[i].update(
        team_name=tname, team_description=tdesc,
        team_type=ttype, members=members, max_turns=max_t,
    )

    if ttype in ("roundrobin", "llm_orchestration"):
        kw = st.text_input(
            "Termination Keyword", step.get("termination_keyword", ""), key=f"sk_{sid}",
        )
        st.session_state.pipeline[i]["termination_keyword"] = kw

    if ttype == "llm_orchestration":
        guide = st.text_area(
            "Additional Routing Guidance",
            step.get("routing_guidance", ""),
            key=f"sg_{sid}",
            height=80,
            help="Appended to the default selector prompt. Leave empty for default.",
        )
        st.session_state.pipeline[i]["routing_guidance"] = guide

    if ttype == "swarm":
        st.markdown("**Handoff Configuration**")
        st.caption(
            "First agent in the list receives the initial task. "
            "At least one agent must hand off to 'user' for termination."
        )
        ho = step.get("handoffs", {})
        for m in members:
            options = [x for x in members if x != m] + ["user"]
            targets = st.multiselect(
                f"{m} hands off to:",
                options,
                default=[t for t in ho.get(m, []) if t in members or t == "user"],
                key=f"sh_{sid}_{m}",
            )
            ho[m] = targets
        st.session_state.pipeline[i]["handoffs"] = ho
