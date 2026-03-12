"""Builds AutoGen agents and teams from UI configuration."""

import os
import re

from autogen_agentchat.agents import AssistantAgent, SocietyOfMindAgent
from autogen_agentchat.base import Handoff
from autogen_agentchat.conditions import HandoffTermination, TextMentionTermination
from autogen_agentchat.teams import RoundRobinGroupChat, SelectorGroupChat, Swarm
from autogen_core.tools import FunctionTool
from autogen_ext.models.openai import OpenAIChatCompletionClient

from wiki_tool import search_wikipedia

WIKI_TOOL = FunctionTool(
    search_wikipedia,
    description="Search Wikipedia for factual information about any topic.",
)


def _make_client(parallel_tool_calls=True):
    kwargs = {
        "model": "gpt-4o-mini",
        "api_key": os.getenv("OPENAI_API_KEY"),
    }
    if not parallel_tool_calls:
        kwargs["parallel_tool_calls"] = False
    return OpenAIChatCompletionClient(**kwargs)


def _find_agent_cfg(agents_config, name):
    for cfg in agents_config:
        if cfg["name"] == name:
            return cfg
    raise ValueError(f"Agent '{name}' not found in config")


def _safe_name(name):
    """Sanitize a name to be a valid Python identifier."""
    safe = re.sub(r'\W+', '_', name).strip('_')
    return safe or "Agent"


def _build_agent(cfg, client, handoffs=None):
    """Create an AssistantAgent from a config dict."""
    kwargs = {}
    if cfg.get("has_wiki_tool"):
        kwargs["tools"] = [WIKI_TOOL]
        if not handoffs:
            kwargs["reflect_on_tool_use"] = True
    if cfg.get("description"):
        kwargs["description"] = cfg["description"]
    if handoffs:
        kwargs["handoffs"] = handoffs

    return AssistantAgent(
        _safe_name(cfg["name"]),
        model_client=client,
        system_message=cfg.get("system_message", ""),
        **kwargs,
    )


def build_pipeline(agents_config, pipeline_steps):
    """Build the outer team from agent configs and pipeline steps.

    Returns:
        (team_or_agent, is_team) tuple.
    """
    client = _make_client()
    swarm_client = _make_client(parallel_tool_calls=False)

    outer_members = []

    for step in pipeline_steps:
        if step["type"] == "agent":
            cfg = _find_agent_cfg(agents_config, step["agent_name"])
            outer_members.append(_build_agent(cfg, client))

        elif step["type"] == "team":
            team_type = step["team_type"]
            member_cfgs = [
                _find_agent_cfg(agents_config, n)
                for n in step.get("members", [])
            ]
            if not member_cfgs:
                raise ValueError(f"Team '{step.get('team_name')}' has no members")

            inner = _build_inner_team(
                team_type, member_cfgs, step, client, swarm_client,
            )

            som = SocietyOfMindAgent(
                _safe_name(step.get("team_name", "Team")),
                team=inner,
                model_client=client,
                description=step.get("team_description", ""),
            )
            outer_members.append(som)

    if not outer_members:
        raise ValueError("Pipeline has no steps")

    outer = RoundRobinGroupChat(outer_members, max_turns=len(outer_members))
    return outer, True


def _build_inner_team(team_type, member_cfgs, step, client, swarm_client):
    """Build the inner team for a SocietyOfMind step."""
    term_kw = step.get("termination_keyword", "").strip()

    if team_type == "roundrobin":
        members = [_build_agent(cfg, client) for cfg in member_cfgs]
        term = TextMentionTermination(term_kw) if term_kw else None
        return RoundRobinGroupChat(
            members,
            termination_condition=term,
            max_turns=step.get("max_turns", 6),
        )

    elif team_type == "llm_orchestration":
        members = [_build_agent(cfg, client) for cfg in member_cfgs]
        kwargs = {}
        if term_kw:
            kwargs["termination_condition"] = TextMentionTermination(term_kw)
        guidance = step.get("routing_guidance", "").strip()
        if guidance:
            kwargs["selector_prompt"] = (
                "{history}\n\n"
                "Read the above conversation. Then select the next role from "
                "{participants} to play. Only return the role.\n\n"
                "Available roles:\n{roles}\n\n"
                f"Additional routing guidance:\n{guidance}"
            )
        return SelectorGroupChat(
            members,
            model_client=client,
            max_turns=step.get("max_turns", 10),
            **kwargs,
        )

    elif team_type == "swarm":
        handoff_map = step.get("handoffs", {})
        members = []
        for cfg in member_cfgs:
            targets = handoff_map.get(cfg["name"], [])
            handoffs = [
                Handoff(
                    target=t if t == "user" else _safe_name(t),
                    description="Return to user" if t == "user" else f"Hand off to {t}",
                )
                for t in targets
            ] or None
            members.append(_build_agent(cfg, swarm_client, handoffs=handoffs))

        return Swarm(
            members,
            termination_condition=HandoffTermination(target="user"),
            max_turns=step.get("max_turns", 15),
        )

    else:
        raise ValueError(f"Unknown team type: {team_type}")
