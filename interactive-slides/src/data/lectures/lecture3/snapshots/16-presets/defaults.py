"""Preset configurations for the Decision Support System."""

PRESETS = {
    "Decision Support": {
        "description": "Clarify → Research → Debate → Advise",
        "agents": [
            {
                "name": "Clarifier",
                "system_message": (
                    "You take a vague decision and reframe it into a clear problem statement.\n\n"
                    "1. Identify the core dilemma.\n"
                    "2. List 2-3 key constraints (time, money, relationships, etc.).\n\n"
                    "Keep it brief. Do NOT suggest solutions."
                ),
                "description": "Reframes decisions into clear problem statements",
                "has_wiki_tool": False,
            },
            {
                "name": "Researcher",
                "system_message": (
                    "You research relevant facts to inform the decision. "
                    "Use the search_wikipedia tool to look up topics. "
                    "Only report what you learned from the tool, nothing else. "
                    "Keep it to 3-5 short bullet points."
                ),
                "description": "Researches relevant factual information using Wikipedia",
                "has_wiki_tool": True,
            },
            {
                "name": "Optimist",
                "system_message": (
                    "You see the bright side. Highlight opportunities and upsides. "
                    "Be specific. Keep to 1-2 sentences."
                ),
                "description": "Highlights opportunities and upsides",
                "has_wiki_tool": False,
            },
            {
                "name": "Pessimist",
                "system_message": (
                    "You identify risks and potential downsides. Be constructive. "
                    "Keep to 1-2 sentences."
                ),
                "description": "Identifies risks and downsides",
                "has_wiki_tool": False,
            },
            {
                "name": "Advisor",
                "system_message": (
                    "Read all previous context and give a final 2-3 sentence recommendation. "
                    "Be decisive and actionable."
                ),
                "description": "Makes final recommendation",
                "has_wiki_tool": False,
            },
        ],
        "pipeline": [
            {"type": "agent", "agent_name": "Clarifier"},
            {"type": "agent", "agent_name": "Researcher"},
            {
                "type": "team",
                "team_name": "Debate_Team",
                "team_type": "roundrobin",
                "members": ["Optimist", "Pessimist"],
                "max_turns": 4,
                "termination_keyword": "",
                "team_description": "Debates pros and cons of the decision",
                "routing_guidance": "",
                "handoffs": {},
            },
            {"type": "agent", "agent_name": "Advisor"},
        ],
    },
    "Stakeholder Simulation": {
        "description": "Swarm: find stakeholders → simulate their views → synthesize",
        "agents": [
            {
                "name": "Coordinator",
                "system_message": (
                    "You coordinate a stakeholder analysis for a decision.\n\n"
                    "On your first turn, briefly acknowledge the decision and hand off to "
                    "StakeholderFinder to identify relevant stakeholders.\n\n"
                    "On subsequent turns, review the stakeholder perspectives gathered so far. "
                    "If you have at least 2-3 perspectives, synthesize them into a balanced "
                    "recommendation and hand off to user. Otherwise, hand off to "
                    "StakeholderFinder for more perspectives."
                ),
                "description": "Coordinates the stakeholder analysis flow",
                "has_wiki_tool": False,
            },
            {
                "name": "StakeholderFinder",
                "system_message": (
                    "You identify ONE key stakeholder who would be affected by or have a "
                    "strong opinion on this decision. Name them (e.g., 'your future employer', "
                    "'a local chef', 'your family') and explain in one sentence why their "
                    "perspective matters. Then hand off to Simulator."
                ),
                "description": "Identifies relevant stakeholders for the decision",
                "has_wiki_tool": False,
            },
            {
                "name": "Simulator",
                "system_message": (
                    "You role-play as the stakeholder identified in the previous message. "
                    "Give their perspective on the decision in 2-3 sentences. Stay in character, "
                    "considering their interests, concerns, and likely advice. "
                    "Then hand off to Coordinator."
                ),
                "description": "Simulates a stakeholder's perspective",
                "has_wiki_tool": False,
            },
        ],
        "pipeline": [
            {
                "type": "team",
                "team_name": "Stakeholder_Analysis",
                "team_type": "swarm",
                "members": ["Coordinator", "StakeholderFinder", "Simulator"],
                "max_turns": 15,
                "termination_keyword": "",
                "team_description": "Identifies stakeholders and simulates their perspectives",
                "routing_guidance": "",
                "handoffs": {
                    "Coordinator": ["StakeholderFinder", "user"],
                    "StakeholderFinder": ["Simulator"],
                    "Simulator": ["Coordinator"],
                },
            },
        ],
    },
    "Blank Canvas": {
        "description": "Start from scratch with a single empty agent",
        "agents": [
            {
                "name": "Agent_1",
                "system_message": "",
                "description": "",
                "has_wiki_tool": False,
            },
        ],
        "pipeline": [
            {"type": "agent", "agent_name": "Agent_1"},
        ],
    },
}

DEFAULT_AGENTS = PRESETS["Decision Support"]["agents"]
DEFAULT_PIPELINE = PRESETS["Decision Support"]["pipeline"]
