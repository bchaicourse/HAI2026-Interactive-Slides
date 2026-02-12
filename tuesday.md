Agentic Interaction
===

# From Prompting to Agents

The most common way to interact with a large language model today is through **prompting**: you write a text input, the model generates a response, and the interaction is complete. This works well for self-contained questions like "Explain quantum computing" or "Write a Python function to sort a list." But consider a more realistic request:

> *"Plan me a weekend trip to Tokyo. Find flights under $800, check the weather forecast, and avoid areas I've already visited."*
> 

Try this with any standard LLM, and you will quickly run into three walls.

**No hands.** The model cannot actually look up flight prices or check a live weather forecast. It has no way to reach out to external systems: no access to airline APIs, weather services, or booking platforms. It can only generate text based on what it learned during training, which means any prices or forecasts it produces are fabricated. The model has no ability to **act on the world**.

**No memory.** The phrase "areas I've already visited" assumes the model knows something about you, perhaps that you visited Shibuya and Asakusa on a previous trip. But a standard LLM starts every conversation from scratch. It has no record of past interactions, no user profile, no accumulated context. Each prompt is an isolated event. The model has no ability to **retain context** across sessions.

**No autonomy.** Even if the model could search for flights and recall your travel history, who decides what to do first? The user would have to spell out every step in advance: "First check my budget, then search flights in that range, then look up the weather, then filter out places I've been, then combine it all into an itinerary." But real tasks rarely unfold so predictably. Maybe the cheapest flights land at midnight, so you need to rethink the first day's schedule, or maybe rain is forecast on Saturday, so you should swap indoor and outdoor activities. The user cannot anticipate all of this upfront. The model has no ability to **figure out the next step on its own**.

## Agents

![image.png](attachment:11c1a244-4b49-4975-b4ab-c6bbcf3817db:image.png)

[Source: https://arxiv.org/abs/2308.11432]

To address these limitations, research on **AI agents** is being actively pursued. An AI agent is a system designed to act on its environment, observe the results, and decide what to do next, repeating this loop until a goal is achieved.

LLMs already bring strong language understanding, broad knowledge, and the ability to reason through complex instructions. If we can give them the hands, memory, and autonomy they currently lack, they become powerful agents. Let's explore how.

---

# Tools: Giving LLMs Hands

## Why LLMs need Tools

By itself, an LLM is a standalone model. It has no access point to the outside world: it cannot check today's weather, look up a flight price, or read a file on your computer. Everything it produces comes from patterns learned during training. To give an LLM hands, we need a mechanism that lets it reach out and interact with external systems.

![image.png](attachment:714ba643-c2e6-47ee-80d4-6d306abe2255:image.png)

## How We Can Give Tools: Function Calling

**Function calling** is the mechanism that makes this possible. The idea is straightforward. Instead of generating free-form text, the model outputs a structured request: "call this function with these arguments." A surrounding system receives that request, executes it, and feeds the result back to the model. The model never runs the function directly. It asks; the system acts.

Consider a concrete example. You ask an agent, "What is the weather in Paris this weekend?" The model cannot answer this from memory, so it generates a function call: `get_weather(location="Paris", date="2026-02-07")`. The system takes this request, hits a weather API, and returns the forecast data. The model then reads that data and composes a natural language response. From the user's perspective, the agent just "knew" the weather. Behind the scenes, it made a structured request and got an answer.

![image.png](attachment:7a9d86cd-4692-4caa-ac83-ec8a7b33f07f:image.png)

[Source: https://platform.openai.com/docs/guides/function-calling]

## Common Tools for LLMs

The most common tools cover the operations agents need most often. **Web search** retrieves up-to-date information. **Code interpreters** run Python or other languages in a sandbox. **File system managers** access and modify local documents. These are general-purpose building blocks that appear in almost every agent system.

**Example:** Claude Code using the **Web Search** tool to get weather information

![image.png](attachment:5cb8eb06-b0c6-4a5a-b946-edf5762a16d3:image.png)

**Example:** Claude Code interacting with a **file system**

![image.png](attachment:43997908-686f-4b68-8d3f-79c4bd91eeaa:image.png)

## Expanding Capabilities Through API Integration

Beyond common capabilities such as web search and file access, agents become significantly more powerful when they connect to the APIs behind the software people already use. Give an agent access to the Figma API, and it can create and modify design files directly. Connect the Slack API, and it can read channels and send messages on your behalf. Plug in the GitHub API, and it can open pull requests, leave code reviews, and merge branches. Each API connection turns a previously human-only workflow into something an agent can participate in. The set of tools an agent has is, in practice, the set of APIs it can reach, and every new connection widens what it is capable of.

**Example:** Claude Agent for Slack + Github

![mcp-demo-slack-github.gif](attachment:a3181167-64c0-4488-b428-5eda04f8bd95:mcp-demo-slack-github.gif)

[Source: https://www.youtube.com/watch?v=XpXImenrSPI]

**Example:** Figma UI Design

![mcp-demo-figma.gif](attachment:33095948-5079-46ba-8d34-cefe407fa8bf:mcp-demo-figma.gif)

[Source: https://www.youtube.com/watch?v=lzbbPBLPtdY]

**Example:** Blender 3D Modeling

![mcp-demo-3d-blender.gif](attachment:7c7906a5-9817-4183-a74e-d5b13e466595:mcp-demo-3d-blender.gif)

[Source: https://www.youtube.com/watch?v=FDRb03XPiRo]

**Example:** Controlling a Robot with LLM

![mcp-demo-robot.gif](attachment:c192ddf1-d5b8-458e-b3dd-ff4eff92f53f:mcp-demo-robot.gif)

[Source: https://www.youtube.com/watch?v=EmpQQd7jRqs]

## Model Context Protocol (MCP)

**Model Context Protocol (MCP)** is a proposed standard that provides a unified way for agents to integrate with external APIs and data sources. Instead of building custom bridges for each API, developers define a standard interface that any MCP-compatible agent can discover and invoke, much like how USB standardized hardware connectivity regardless of the device.

![image.png](attachment:61b336a1-f12e-4cc3-87f3-563171b97945:image.png)

[Source: https://modelcontextprotocol.io/docs/getting-started/intro]

**Example:** Figma MCP

![image.png](attachment:921236e8-fccf-4360-b7bc-618f7c609f5c:image.png)

[Source: https://help.figma.com/hc/en-us/articles/32132100833559-Guide-to-the-Figma-MCP-server]

## Keep the Toolbox Focused

While tools expand what an agent can do, adding more of them is not without cost. Every tool comes with a definition: a name, a description, and a parameter schema. All of these get injected into the system message and count against the model's context window. As the list grows, the model has to sift through more descriptions before deciding which tool to use, and its accuracy in making that choice drops. [OpenAI recommends keeping the count under twenty.](https://platform.openai.com/docs/guides/function-calling) The real design challenge is not to give the agent as many tools as possible, but to choose the right ones and describe each one clearly enough that the model can pick and use them reliably.

---

# Memory: Giving Agents Context

## Why LLMs need Contexts

An LLM is, at its core, a massive collection of numbers—billions of floating-point weights shaped during training. There is no database inside, no filing cabinet of facts. And yet, knowledge does exist within those weights. Ask the model for the capital of France, and it will answer "Paris." The patterns in the training data left an imprint, and that imprint encodes a remarkable amount of world knowledge. This is sometimes called **parametric memory**: knowledge baked into the model itself.

![LLMs are just a massive grid of numbers.](attachment:24dd69d7-ff97-49a7-b84a-126770a49c8e:image.png)

LLMs are just a massive grid of numbers.

![LLM inference is nothing more than simple arithmetic repeated billions of times, yet real-world knowledge emerges from it. [Source: https://www.youtube.com/watch?v=eMlx5fFNoYc]](attachment:eb848570-2b56-4a2e-b6e9-1a65aa0b2e2c:matrix.gif)

LLM inference is nothing more than simple arithmetic repeated billions of times, yet real-world knowledge emerges from it. [Source: https://www.youtube.com/watch?v=eMlx5fFNoYc]

But parametric memory is fundamentally different from what we practically call memory. **It is frozen** at the time of training, so the model cannot know what happened yesterday. **It is approximate**, a blurry statistical reconstruction rather than a precise record. And most importantly, **it is generic**. The model has no parametric memory of *you*: your preferences, your past conversations, the documents on your desk. Every session starts from zero, and every user is a stranger.

So while parametric memory gives LLMs an impressive baseline of general knowledge, it is not the kind of memory an agent needs. An agent that plans your trip or manages your calendar needs to know things about *your* world, and it needs that knowledge to accumulate over time. That requires a different mechanism.

## How We Can Give Contexts

Every time the model is called, it sees whatever text has been placed in its input. This is the only channel through which the model receives information. That input might include a **system prompt** defining the agent's role and instructions, **previous messages** from the conversation so the model can reference what was said earlier, or **dynamically retrieved content** such as a relevant document, a database record, or the result of a search query selected on the fly to match the current situation.

The key constraint is that **this input space—the context window—is finite**. A long conversation eventually exceeds the limit. A knowledge base might contain thousands of pages. The agent cannot include everything, so it has to select. The central design question is not whether to give the model context, but *what* to put in that limited window. Usually, three criteria guide that selection: recency, relevance, and importance [Source: https://arxiv.org/pdf/2304.03442].

## Memory Criterion 1: Recency

Recency favors what happened recently. A condition the user mentioned two minutes ago is more likely to matter right now than something from three days back. This is the simplest criterion, and the most intuitive.

### Conversation History

Conversation history is recency-based memory in its purest form. The most recent messages are always included in the context window, while older ones get pushed out as the window fills up. The simplest approach is to cut off everything beyond a certain point: keep the most recent messages and discard the rest.

![image.png](attachment:cb6a49bd-8341-476c-86dd-c1ab2e77c8c2:image.png)

[Source: https://platform.openai.com/docs/guides/conversation-state]

### Summarizing the History

If losing older context entirely feels too costly, an alternative is summarization: ask the LLM to condense the older portion of the conversation into a compact summary, which takes up far less space in the context window while preserving the key points.

**Example:** Claude Code compacting the previous conversation

![image.png](attachment:136d9b64-ca37-4e0b-90e4-c4cbdfa03b19:image.png)

## Memory Criterion 2: Relevance

Relevance favors what is semantically related to the current question, regardless of when it was recorded. A user asking "What are the visa requirements for Japan?" benefits from retrieving a document about Japanese immigration policy, even if that document was stored months ago. The timing does not matter; the content does.

This is the principle behind **RAG (Retrieval-Augmented Generation)**. RAG retrieves the most relevant documents at query time and inserts them into the context window, allowing the agent to draw on a large knowledge base without exceeding token limits. 

![image.png](attachment:0d454f18-5b72-431e-b73c-a3c6e5fab19b:image.png)

[Source: https://shiftasia.com/community/retrieval-augmented-generation-rag-a-comprehensive-guide-to-smarter-more-accurate-ai/]

### RAG Step 1: Chunking

![image.png](attachment:f9be56d5-f6b7-4513-976a-e742100d2349:image.png)

In practice, documents are rarely embedded whole. A single document may be too long to fit in a context window or too broad in scope to produce a useful embedding, so it is first split into smaller segments called **chunks**. A chunk might be a paragraph, a section, or a fixed number of tokens, depending on the application. The goal is to create units small enough to be precise but large enough to be self-contained.

### RAG Step 2: Embedding

With the data chunked, the system needs a way to search across potentially millions of chunks quickly. Reading every chunk and comparing it to the user's question in natural language would be far too slow. **Embeddings** solve this by converting each chunk into a numerical vector, a list of numbers that captures its semantic meaning. Texts that mean similar things end up as vectors that are geometrically close together, even if they share few words. For example, "Population of Seoul" and "number of residents in the capital of South Korea" have almost no surface overlap, but their embeddings land near each other in vector space.

**Example:** Tensorflow Embedding Projector

![embeddingspace.gif](attachment:f7a6817c-3a7d-4158-a4bc-7f737599316d:embeddingspace.gif)

[Source: https://projector.tensorflow.org/]

All chunk embeddings are stored in a specialized database called a **vector store**, which is optimized for finding the nearest neighbors of a given vector. When a user's question arrives, the system converts it into an embedding of its own and queries the vector store for the closest matches, retrieving the chunks most likely to contain a relevant answer.

### RAG Step 3: Reranking

Embedding search is fast, but it is also lossy. Compressing an entire passage into a single vector inevitably discards nuance: subtle distinctions, negations, and conditional statements can all get flattened. The retrieved chunks are *probably* relevant, but their ranking may not reflect what the user actually needs most.

To sharpen the results, many RAG pipelines add a **reranking** step. A specialized model called a **cross-encoder** takes each candidate chunk alongside the original query and scores how well they actually match, reading both texts together rather than comparing pre-computed vectors. This is slower than vector search, which is why it is only applied to the small set of candidates rather than the entire corpus, but it produces a much more accurate final ranking. The top-ranked chunks after reranking are what ultimately gets inserted into the model's context window.

![Cross-encoder models calculate similarity between two texts more accurately than embeddings](attachment:20e50315-9c7f-4d26-9cc5-d5e69b8e8011:image.png)

Cross-encoder models calculate similarity between two texts more accurately than embeddings

## Memory Criterion 3: Importance

Importance favors information that is inherently significant, independent of recency or relevance to the current query. "The user has a severe nut allergy" matters more than "the weather was sunny yesterday," and it matters regardless of when it was mentioned or what the current question is about. 

Importance is harder to operationalize than the other two criteria. One approach is to use the LLM itself as a judge, asking it to rate how significant a piece of information is on a scale.

**Example:** LLM abstracting a user profile through reflection

![image.png](attachment:7ce07719-dfd3-41fe-b022-cc431da92f62:image.png)

[Source: https://arxiv.org/pdf/2304.03442]

## Designing Balanced Memory Systems

In practice, real systems combine all three criteria, weighting recency, relevance, and importance together to decide what makes it into the context window at any given moment. Designing to include only the most important information for the purpose within the given limited LLM context window is an important challenge for agent designers.

![Just as an operating system partitions a process's finite memory into distinct regions, a language model's context window is divided among competing elements such as system prompts, tool definitions, user profiles, dynamic examples, and conversation history.](attachment:9684c62f-f229-4b1a-ba61-0458145891fb:image.png)

Just as an operating system partitions a process's finite memory into distinct regions, a language model's context window is divided among competing elements such as system prompts, tool definitions, user profiles, dynamic examples, and conversation history.

**🔎 Thinking Point:** Consider a scenario you want to use an agent for. What tools and what kind of memory would be most important for that agent? What would you be willing to compromise on instead?

---

# Autonomy: Letting Agents Think for Themselves

An agent with tools and memory can access external systems and draw on past context. But if it can only do one thing per request and then stop, it is not much more than a fancy function call. What makes it autonomous is **the ability to repeat a cycle**: think about the current situation, act by calling a tool or producing output, observe the result, and then think again. This pattern is widely known as **ReAct**, which is short for **Reasoning + Acting**, after an influential paper that showed how combining reasoning and action in an explicit loop outperforms either one alone.

![image.png](attachment:61ee761d-00ab-4c1e-a22c-ed8ef280ef7f:image.png)

[Source: https://react-lm.github.io/]

**Example:** Reasoning Only vs. Acting Only vs. Reasoning + Acting

![image.png](attachment:b01bf9d1-4cf1-481b-9f66-9e9d63c5733f:image.png)

 [Source: https://arxiv.org/abs/2210.03629]

Adding this loop alone unlocks a wide range of capabilities. The most common is **self-correction**. A coding agent writes a function, runs it, and gets a traceback. Instead of handing the error back to the user, it reads the message, spots the bug, fixes the code, and runs it again. If the second attempt fails too, it tries a third time with a different approach. The user asked for working code and gets working code; the failures in between were just intermediate observations that the agent handled on its own. 

The loop also enables **adaptation**. An agent searching for direct flights to Tokyo finds they are all over budget. Rather than stopping there, it pivots: tries flights with layovers, checks nearby airports, shifts the travel dates. Nobody told it to explore these alternatives. It observed that its initial plan was not working and changed strategy mid-task, the way a human travel agent would.

---

# When Agents Go Wrong

Tools, memory, and autonomy make agents genuinely useful. They also make agents genuinely dangerous. 

## Unintended Actions

Chatbots that only generate text have a limited blast radius: the worst case is a wrong or offensive answer. Agents are different, because they *act*. A prompt injection on a chatbot produces a bad response. A prompt injection on an agent with file access, email access, and shell access produces real-world consequences.

**Example:** Replit coding agent deletes the production database

![image.png](attachment:280bc3a1-83e1-4831-b70a-da68d3b5b6b0:image.png)

[Source: https://x.com/jasonlk/status/1946239068691665187]

**Example:** OpenClaw

![image.png](attachment:1f8cec06-d87e-4fc7-a09c-9598edfb6f24:image.png)

In January 2026, an open-source AI agent called OpenClaw (originally named Clawdbot) went viral, gaining over 145,000 GitHub stars in under two weeks. OpenClaw runs locally on a user's machine and connects to messaging platforms like iMessage, Slack, and WhatsApp. It can read and write files, execute shell commands, send messages, manage calendars, and control smart home devices. It remembers conversations across sessions and learns user preferences over time.

The appeal is obvious: a personal assistant that is always on, always available, and always learning. But the risks became equally obvious almost immediately. In [one reported incident](https://news.bloomberglaw.com/artificial-intelligence/ai-agent-goes-rogue-spamming-openclaw-user-with-500-messages), a software engineer gave OpenClaw access to his iMessage. The agent proceeded to send over **500 unsolicited messages** to the user, his wife, and random contacts in his address book. 

## Memory, User Profiling, and Privacy

The more an agent remembers about you, the more useful it becomes. An agent that knows your dietary restrictions, your past travel history, or your project deadlines can help in ways a stateless chatbot never could.

But how much do you actually want your agent to know about you? Imagine an AI that periodically reflects on your conversations and builds up a profile of high-level findings: your communication style, your political leanings, your anxieties, your relationship dynamics. It raises a question most users have never been explicitly asked: **did you consent to this?** When you chatted casually with an AI about your weekend, did you agree to have that conversation analyzed and distilled into a lasting record of your personality?

![image.png](attachment:a97cfa6a-b8a9-4fc6-8c82-a967526853f4:image.png)

**Example:** Microsoft Windows Recall

Microsoft launched a service called "Windows Recall" as an AI-powered feature of Windows 11. It was a kind of "photographic memory for your PC," designed to remember everything you do on your computer and let you find it again later. Every few seconds, it automatically captured screenshots of the user's screen, analyzed and indexed the content of those images, and allowed users to search for and revisit things they had previously seen. Despite its potential convenience, public reception was largely negative. Some users felt that what Windows Recall did amounted to an invasion of privacy, while others raised serious concerns about the security of storing such sensitive data locally on their devices.

![windowsrecall.gif](attachment:191a0fed-7842-489b-9a82-fb5f4aafe352:windowsrecall.gif)

![image.png](attachment:9a4f4de8-025d-4ef8-83f6-e5a5fac440f8:image.png)

[Source: https://www.youtube.com/watch?v=uhuYCNM1bEI]

# Designing the Right Level of Autonomy

We want AI agents to have just the right amount of power, and this is a design problem. How can we design human-AI interaction that doesn't require us to specify every detail, but still prevents the agent from making consequential mistakes?

The most basic approach is to **show users what the agent is doing** as transparently as possible and **provide ways for them to intervene** when needed. The simplest method is asking the user before taking consequential actions. But the design challenge is calibration—ask too often, and the agent becomes tedious; ask too rarely, and dangerous actions slip through. Where exactly an agent should sit on this spectrum depends on context, user preferences, and risk tolerance.

**Example:** Claude Code asking permissions for bash command

![image.png](attachment:6113b263-7353-4ae0-b9bb-8a7ce6508f5d:image.png)

**Example:** VS Code + Github Copilot showing the code change and asking for user approval

![image.png](attachment:ceebd108-bfca-4720-b6b4-fa1b20217ebc:da4df105-44f2-42f4-ad50-1d562449b6fd.png)

**🔎 Thinking Point:** Current interfaces often provide a binary choice: allow or deny. Is there a better way to design this?