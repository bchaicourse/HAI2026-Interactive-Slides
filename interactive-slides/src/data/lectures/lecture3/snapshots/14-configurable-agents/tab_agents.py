"""Tab 1: Define Agents UI."""

import uuid

import streamlit as st


def render(tab):
    with tab:
        for i, agent in enumerate(st.session_state.agents):
            aid = agent["id"]
            label = agent["name"] + (" [wiki]" if agent.get("has_wiki_tool") else "")
            with st.expander(label, expanded=False):
                c1, c2 = st.columns([3, 1])
                with c1:
                    name = st.text_input("Name", agent["name"], key=f"an_{aid}")
                with c2:
                    wiki = st.checkbox(
                        "Wikipedia tool",
                        agent.get("has_wiki_tool", False),
                        key=f"aw_{aid}",
                    )
                desc = st.text_input(
                    "Description",
                    agent.get("description", ""),
                    key=f"ad_{aid}",
                    help="Visible to LLM orchestrators when routing.",
                )
                msg = st.text_area(
                    "System Message",
                    agent.get("system_message", ""),
                    key=f"am_{aid}",
                    height=120,
                )
                st.session_state.agents[i].update(
                    name=name, description=desc, system_message=msg, has_wiki_tool=wiki,
                )
                if st.button("Remove", key=f"ar_{aid}"):
                    st.session_state.agents.pop(i)
                    st.rerun()

        if st.button("Add Agent"):
            st.session_state.agents.append({
                "id": str(uuid.uuid4()),
                "name": f"Agent_{len(st.session_state.agents) + 1}",
                "system_message": "",
                "description": "",
                "has_wiki_tool": False,
            })
            st.rerun()
