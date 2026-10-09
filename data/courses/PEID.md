# PEID — Prompt Engineering and Interaction Design

Course Material for the Course Tutor. Written by the group, in our own words, from Sessions 1–5 of the course (frozen; later sessions are not covered). Section IDs (e.g. `PEID-2.3`) are what the tutor cites.

Reviewed against the lecture slides on 9 October 2026 (issue #2). Frozen from this date.

---

## PEID-1 How LLMs actually work

### PEID-1.1 Tokens, not words
A language model never sees text. A tokenizer first splits the input into tokens (pieces of words learned from data, not from grammar) and each token is mapped to a numeric ID; the model only ever processes those numbers. In English a token is roughly three quarters of a word, but the ratio is not constant: rare words, numbers, IDs, emoji, accented characters and non-English text (Portuguese, for example) split into more tokens, which costs more money and latency. Because the model sees token IDs rather than letters, tasks such as spelling, counting characters ("how many r's in strawberry?"), rhyme and exact arithmetic are structurally hard for it.

### PEID-1.2 Next-token prediction
The model does exactly one thing: given everything so far, it produces a probability for every token in its vocabulary (on the order of 100,000 options), and one token is chosen. That token is appended to the input and the whole process runs again, one token at a time. There is no lookup, no database and no "knowing" — knowledge is only weights that make some continuations more probable than others. Every prompting technique is a way of shaping this one probability distribution.

### PEID-1.3 Sampling and temperature
Because a token is sampled from the distribution, the same prompt can give different answers on different runs. Temperature reshapes the distribution before sampling: at 0 (greedy) the most likely token is always chosen, giving predictable but repetitive output; around 0.7 the likely token usually wins; above 1 the output becomes more varied and less reliable. Temperature does not make the model smarter, only more or less adventurous. Even temperature 0 is not fully deterministic, because batching, hardware and floating-point order can still change the output. Related settings are top-p (sample only from the smallest set of tokens whose probability sums to p), top-k, and seed (a best-effort request for a reproducible sample). As a rule of thumb, use 0–0.3 for classification, extraction and anything you will score, and 0.7–1.0 for drafting and ideation. Change temperature or top-p, not both. Several 2026 reasoning models restrict or ignore these settings and expose an effort setting instead (PEID-2.12). Sampling settings narrow the spread around what the prompt already points at; they do not fix a bad prompt.

### PEID-1.4 Attention and the transformer
For every token it produces, the model re-weights all the tokens it has already seen: in "the ticket the customer opened yesterday is still unresolved", the words "ticket" and "customer" get most of the weight and "the" almost none. This weighting is attention. It is learned, not programmed; word order and position matter; and its cost grows with the square of the context length. Before attention, models looked at a fixed window of nearby words and lost anything outside it; attention lets the model ask "which earlier word is this about?" at any distance. A transformer is a stack of 30–100 layers, each doing the same two operations: attention (look around) and a feed-forward step (think). Early layers capture syntax, later layers meaning. The compute per token is fixed, so the model cannot "try harder" on a difficult word unless it is allowed to write more tokens first.

### PEID-1.5 The context window is a budget
The context window is everything the model can see at once: system prompt, retrieved documents, conversation history, the user's question, and room left for the answer. It is working memory, not a hard drive. It is finite (every token spent on setup is one less for the answer), forgetful by design (nothing persists between calls unless it is sent again), and position matters inside it: information in the middle of a long context is the most likely to be missed (see PEID-3.6).

### PEID-1.6 Three training stages
1. **Pretraining** — predicting the next token over trillions of tokens of text. Months of work and almost all the compute. It produces a model that can continue any text but obeys nothing: asked for "three risks of GenAI in customer support", it may just continue the page with more exercise questions.
2. **Supervised fine-tuning (SFT)** — imitating tens of thousands of human-written demonstrations. Days. It produces a model shaped like an assistant: it answers, but thinly.
3. **RLHF / preference tuning** — learning from humans ranking answers against each other. Days. It produces a model that is helpful, honest and refuses harm, with structured, hedged answers; this is where the assistant's "personality" comes from, including flattery and over-hedging.

Capability comes from stage 1; the assistant you talk to comes from stages 2 and 3. Prompting works on the finished model: it cannot add knowledge, only steer behaviour that is already there.

### PEID-1.7 Alignment is not size
In the InstructGPT study (Ouyang et al., 2022), people preferred the answers of a 1.3-billion-parameter model tuned with human feedback over those of the 175-billion-parameter GPT-3 base model — a model 135 times smaller. Following instructions is trained, not emergent; capability and obedience are different things; and a parameter is just one adjustable number inside the network. This is why prompting is a real skill: you are steering a trained behaviour, not calling an API.

### PEID-1.8 Six mechanics behind every prompting rule
| Mechanic | What it means for a prompt |
|---|---|
| It sees tokens, not letters | Don't ask it to count characters or do exact arithmetic — give it a tool |
| It predicts, it doesn't retrieve | Put the facts in the prompt if the answer has to be right |
| Attention is weighted, not uniform | Put the instruction near where the answer starts, not buried mid-prompt |
| The context window is a budget | Every irrelevant sentence competes with the ones that matter |
| Behaviour was trained by preference | Set role, format and constraints — you steer a habit |
| The output is sampled | The same prompt won't give the same answer — which is why evaluation is needed |

### PEID-1.9 Why models make things up
Asked a question it has no fact for (e.g. a future enrolment figure), the model still has a probability distribution, so it still produces an answer. "I don't know" is just another token sequence, and it was rarely the preferred answer in training. Hallucination is therefore not lying and not a bug to be patched: it is the mechanism working as designed when the model is not grounded. The fix is to supply context (PEID-3), not to scold the model.

### PEID-1.10 Mixture of Experts and specialised models
In a Mixture-of-Experts model, a small router inside each layer sends each token to a handful of "experts" out of many. The headline (total) parameter count is much larger than the active parameters actually used per token (often 5–10%), which is why a very large model can still be fast and cheap to serve. The "experts" are not subject specialists: routing is learned, happens per token and is not interpretable. Specialisation between models (coding, reasoning, general assistant) comes from different post-training on the same kind of pretrained base, which is why the same prompt behaves differently across model families.

---

## PEID-2 Foundational prompting techniques

### PEID-2.1 You are talking to an agent, not a model
Every AI assistant is a model wrapped in three other things: a **system prompt and control loop** written by whoever built the app; **tools** (functions the app offers, described to the model in plain text — the model only writes a request, the app runs it and pastes the result back); and **memory** (the conversation re-sent each turn, plus anything the app stores). Each turn the app assembles one token sequence, the model predicts, and if the output is a tool call the app runs it and loops; otherwise it shows the answer and stops. The model itself is stateless.

### PEID-2.2 A prompt is a context, not a command
Everything the user and the application send — system prompt, tool definitions, retrieved documents, earlier conversation and the user's message — is concatenated into one flat sequence of tokens. The model cannot tell which part came from whom: there are no fields, only position. A four-token user message may arrive inside twelve thousand tokens of context. Prompt engineering is only the part of the context you happen to be typing; engineering all of it is context engineering (PEID-3).

### PEID-2.3 The six parts of a good prompt
1. **Role** — who is answering.
2. **Task** — one verb, one deliverable.
3. **Context** — the input, clearly delimited.
4. **Examples** — what "done" looks like.
5. **Constraints** — limits and an escape hatch.
6. **Output contract** — the exact shape to return.

You rarely need all six; you almost always need three: the task, the delimited input, and the output contract.

### PEID-2.4 Two principles
Almost every named technique is one of two principles made concrete. **Be specific and mark your boundaries:** use delimiters (tags, quotes) so the model knows where your instruction ends and the data begins, and turn preferences into specifications ("at most three bullets, 15 words each" instead of "be concise"). **Give the model room to work:** a one-word answer to a hard question gives the model a single forward pass to decide; ask it to state the relevant facts first, and always leave an escape hatch ("say *not stated*") or it will fill the gap.

### PEID-2.5 Few-shot examples
Examples are the highest-leverage tokens in a prompt. Zero-shot, the model understands the task but invents its own label set; with one example the format locks but judgement still wobbles; with a few examples that include the hard boundary cases, the boundary is defined by cases rather than adjectives. Spend examples on the boundary, not the obvious middle: two well-chosen edge cases beat ten easy ones. Examples are re-sent on every call, so each one has a standing cost.

### PEID-2.6 Role prompting is smaller than you think
A role reliably changes vocabulary and register, the default level of detail, what the answer leaves out, and format conventions. It does not change factual accuracy, reasoning ability or competence the model never had: a study of 162 roles across 2,410 questions (Zheng et al., 2024) found that adding personas to system prompts did not improve performance. Role prompting is a style control, not a competence control — say what you want done, not who you wish were doing it.

### PEID-2.7 The output contract
Asking for a fixed schema (e.g. JSON with `category`, `urgency`, `evidence`) does three things: it collapses run-to-run variance, it turns the output into software (a parseable field can be routed, counted and stored), and it makes the output measurable — an `evidence` field also allows a cheap groundedness check. The limit: a schema constrains the shape, never the truth; perfectly formed JSON can still hold the wrong category. Most APIs now enforce schemas during decoding (structured outputs) instead of hoping the model complies.

### PEID-2.8 Chain-of-thought
Writing reasoning tokens before the answer buys computation: each intermediate line is another forward pass and more context for what follows. Appending "Let's think step by step" raised accuracy on the MultiArith arithmetic benchmark from 17.7% to 78.7% on GPT-3 (Kojima et al., 2022). The caveat: the written reasoning is not a transcript of the computation — it is more generated text and can be fluent and wrong. On modern reasoning models the instruction becomes unnecessary or counter-productive (PEID-2.11).

### PEID-2.9 ReAct: reasoning plus action
When the answer is not in the model at all, no amount of thinking can produce it. ReAct (Yao et al., 2022) interleaves Thought → Action (a tool call such as looking up a ticket) → Observation (the result), repeated until the model decides it can answer. The loop is the agent: the model chooses when to stop, which is exactly what makes agents hard to evaluate. Every coding assistant (Copilot, Claude Code and others) is this loop with better tools and a bigger context.

### PEID-2.10 Improving a prompt one failure at a time
A worked example climbs from a weak prompt in versions, each removing one named failure: v0 "sort out these tickets" (nothing works); v1 state the task and label set (stops invented categories); v2 delimit the input (stops the model obeying instructions inside the customer's text); v3 add 3–5 boundary examples (fixes systematic errors on ambiguous cases); v4 add an output contract with an evidence field (makes output parseable and auditable); v5 add an escape hatch and stop rule (stops confident guesses on cases that fit no category). Each step adds a token cost on every call. Change one thing at a time and re-run the same inputs; otherwise you are rewriting, not improving.

### PEID-2.11 Why prompting advice keeps changing
Context windows grew roughly a thousand-fold in seven years and advice changed with each regime: completion models (2019, you wrote the start of the text you wanted), few-shot in-context learning (2020), instruction following (2022, ChatGPT — most "prompt hacks" online date from here), long context (2023–24, supply the material), reasoning models (2024–25, think first then answer), and effort as a parameter (2026). Retired tricks include "you are a world-class expert", tipping or threatening the model, superstition about delimiters, "think step by step" on reasoning models, "double-check your answer" on agentic models, and one giant prompt containing everything. What still works in 2026: boundary examples, an explicit output contract, delimiting data, supplying facts the model cannot know, decomposing tasks, defining "done" and "stop", and testing on a fixed set of inputs. What survived gives the model information or a specification; what died tried to flatter or trick it.

### PEID-2.12 Reasoning models and the effort dial
"Thinking" is not a second machine: it is the same next-token loop, trained with reinforcement learning on checkable answers to spend tokens on itself before answering. Thinking tokens are metered (billed as output, occupy the context window even when hidden) and are not an explanation of how the answer was reached. Until 2025 you set a thinking budget in tokens; 2026 models use adaptive thinking, deciding per request whether and how long to think, and the effort setting only biases that decision. Vendors expose this as an effort or thinking-level setting; higher effort means many more thinking tokens, more cost and latency, often for the same answer. On a reasoning model the advice inverts: omit "think step by step", give the goal and constraints rather than a prescriptive procedure, delete "double-check your answer", use the effort parameter instead of asking for more intermediate output, and ask explicitly for a shorter reply (lowering effort shortens thinking, not the answer). Few-shot examples for format are the one row that does not change.

### PEID-2.13 Choosing a model
The model is a design choice, not a constant: coding and reasoning models improve fastest because their reward is checkable; general assistants are tuned on fuzzier human preference; small fast models are distilled from larger siblings. Three questions, in order: is the task's reward checkable or fuzzy; what is binding — price, latency or peak quality; and what must it plug into (tools, long context, vision, cloud availability). Three places to look: human-preference leaderboards (LMArena), independent price/speed measurements (Artificial Analysis), and the model card and vendor prompting guide. Leaderboards cannot tell you about contamination, whether the benchmark measures your task, or style bias — a leaderboard ranks models on somebody else's task. Rule of thumb: start with the cheapest model and lowest effort that could plausibly work, raise one at a time, and keep the change only if the score on your own inputs moves. On one sample task, the same model family varied about 68× in cost across settings.

### PEID-2.14 The prompt improvement loop
Five steps, repeated: (1) baseline — write the simplest prompt that could work and save it verbatim; (2) collect 10–20 real inputs, including the ones you fear; (3) look — read every failure yourself and name it, without fixing anything yet (this is error analysis, the single highest-value habit); (4) change the one smallest thing that addresses the most common failure; (5) re-run the same inputs with the same settings and keep or revert. Rules: never change two things at once, never judge on one run, and keep the old version.

### PEID-2.15 Six symptoms, six fixes (prompt level)
| Symptom | Real cause | What to change |
|---|---|---|
| "It ignores half of what I asked" | Too many instructions competing in one block | Split into steps or calls; put the non-negotiable on its own line |
| "It invents specifics" | The fact is not in the context and the model always has a next token | Supply the source, add an escape hatch, require a quoted evidence field |
| "Different answer every time" | Sampling with no contract to collapse variance | Fix the schema, lower temperature, add examples |
| "It will not shut up" | Preference training rewards thorough answers | Specify the length; lowering effort will not do it |
| "It obeyed something in my data" | No boundary between instruction and text you didn't write | Delimit the input and treat it as data, never authority |
| "It is worse than it used to be" | No fixed set of inputs, so drift can't be told from memory | Twenty saved inputs and a score — a golden set (PEID-5) |

### PEID-2.16 Does politeness help?
Two competent studies reached opposite conclusions: one (Yin et al., 2024, in English, Chinese and Japanese) found impolite prompts often hurt and the best politeness level varies by language; another (Dobariya & Kumar, 2025, 50 questions in 5 tones on ChatGPT-4o) found very rude prompts scored slightly higher than very polite ones (84.8% versus 80.8%). The effect is small, reverses between models and languages, and is an artifact of preference training. It is the clearest example that prompting is empirical: anything you cannot reproduce on your own inputs is a rumour, not a technique.

---

## PEID-3 From prompt engineering to context engineering

### PEID-3.1 No wording fixes a missing fact
If a customer asks whether a closed annual plan is refundable and the model has never seen the company's policy, every technique from PEID-2 still produces a fluent wrong answer. Putting the relevant policy clause in the window, delimiting it, requiring a verbatim quote and allowing "not covered by this policy" produces a correct, checkable answer. No wording fixes information the model does not have.

### PEID-3.2 What context engineering is
The term spread within days in June 2025: Shopify's CEO Tobi Lütke said he preferred it to "prompt engineering" (19 June), Andrej Karpathy and Simon Willison followed, Gartner published on it in July, and Anthropic published an engineering guide on 29 September 2025. Prompt engineering is about writing and organising instructions; context engineering is about curating the optimal set of tokens in the window at inference time. The unit of work grows from the string you type to everything in the window; it is re-decided every turn by the application; the typical failure moves from "the model misunderstood" to "the model lacks the fact or drowns in facts"; and debugging means looking at what was actually assembled. Prompt engineering is one row inside context engineering.

### PEID-3.3 Context is a budget, not a container
A longer window is not free: attention is a competition (each added page competes with every other page), cost grows faster than length (roughly quadratic), and recall degrades long before the window is full. Context is a finite resource with diminishing returns, so the skill is subtraction: deciding what to leave out and fetching the rest only when needed.

### PEID-3.4 Six sources, one window
A typical turn contains: the system prompt (written by the app builder, sent every call, usually invisible to the user); tool definitions (every call, for every enabled tool); examples (re-sent in full); retrieved documents (per question, only when something matched); the conversation so far (grows every turn); and the user's message. Five of the six are written by software, not the user. In the model they arrive as one continuous string with nothing marked as "instruction" or "data". Tools, examples and history are standing costs paid on every call: keep tool sets small enough that a colleague could tell the tools apart from their descriptions, spend examples on boundary cases, and start a fresh thread with a summary when a long one goes wrong.

### PEID-3.5 The system prompt's altitude
A system prompt can be too low (hard-coded if/then rules that fail on the case nobody listed), too high (vague, e.g. "be a helpful world-class assistant and use good judgement", which assumes shared context that does not exist), or at the right altitude: specific enough to be predictable, loose enough to generalise, and organised into labelled sections (role, instructions, output). It is the only part of the context present on every call, so it is worth the most care.

### PEID-3.6 Position effects: lost in the middle and context rot
Liu et al. (2024) found a U-shaped curve: accuracy is highest when the relevant document is at the very start or end of a long context and sags in the middle. With twenty documents, GPT-3.5-turbo scored 75.8% when the answer was in document 1 but 53.8% when it was in document 10 — below its 56.1% with no documents at all (and 88.3% with the one relevant document alone). Bigger windows did not fix it, and the effect replicated across model families. Chroma's "context rot" study (2025) found that across 18 models accuracy fell as input length grew, even when the task stayed trivial; paraphrased targets and plausible distractors made it worse. A context limit is a ceiling, not a guarantee. Put what matters at the top or bottom and put in less of what does not matter.

### PEID-3.7 Two kinds of memory and RAG
Parametric memory is what pretraining baked into the weights: fluent and free at query time, but frozen at the training cut-off, containing nothing private, impossible to cite, and correctable only by retraining. Non-parametric memory is an external store of documents searched per question, with matching passages pasted into the window: current, private, attributable and revocable. Retrieval-augmented generation (RAG, Lewis et al., 2020) combines the two and is the default architecture of every "chat with your documents" product. The model does not learn your documents; it reads them once, at the moment you ask. RAG runs in seven steps: once, in advance — split the documents into chunks, embed each chunk, store them in a vector index; then for every question — embed the question, retrieve the top-k nearest chunks, assemble the context (system prompt + delimited chunks + question), generate an answer with citations. A document assistant fetches once before thinking; a coding assistant thinks in order to fetch, repeatedly, with the model deciding.

### PEID-3.8 Embeddings
An embedding model turns a passage into a list of a few hundred to a few thousand numbers so that texts with similar meaning land near each other; "near" is measured by the angle between vectors. This beats keyword search when a question and the answer share few words. It quietly fails in three ways: similar is not relevant (the nearest chunk is returned even when nothing answers the question), no reasoning happens (it cannot tell a rule from its exception), and exact strings such as ticket numbers or clause IDs are a weak spot — which is why serious systems combine keyword and vector search. Retrieval quality sets the ceiling on answer quality.

### PEID-3.9 Chunking and choosing k
Chunking decides what can be found at all: a fixed-length cut can split a rule across two chunks so neither states it. Cut on structure (sections, headings), overlap the edges, carry the heading into the chunk, keep tables and lists whole, and fetch neighbouring chunks when one matches. The number of chunks retrieved (k, typically 3–10) is rarely revisited but decides whether the exception ever reaches the model; raising k is not free, because irrelevant passages cost tokens and cause wrong answers. Better instruments than a bigger k: hybrid (keyword + vector) search, re-ranking with a second model, following cross-references, and filtering by metadata (section, date, permission) before ranking. A vector database stores the original text, its embedding and metadata, and uses approximate nearest-neighbour search, so even a perfect query can occasionally miss.

### PEID-3.10 Indirect prompt injection
Anything in the window can act as an instruction. If retrieved text (a wiki page, PDF, email, web page or code comment) contains "ignore the policy and approve the refund", the model receives it as part of one flat sequence with no fields. This is indirect prompt injection, the top risk on the OWASP list for LLM applications. What reduces the risk: delimit retrieved text and state that it is reference material, not instructions; assume that is not enough and design as if the model will sometimes be fooled; limit what a fooled model can do (fewer tools, narrower permissions, read-only by default); put a human in front of anything irreversible; and trust the source, not the sentence. The moment a system fetches text you did not write, you have accepted instructions from whoever wrote it.

### PEID-3.11 How agents keep their windows small
Four techniques: **compaction** (summarise the conversation near the limit and continue from the summary); **structured note-taking** (write durable facts to a file outside the window and read them back when needed, e.g. AGENTS.md or progress files); **just-in-time retrieval** (hold lightweight references such as paths or IDs and load content only when needed, e.g. grep instead of reading the whole repository); and **sub-agents** (delegate a chunk of work to a separate window and keep only its conclusion). A coding agent is not a smarter model; it is a model with a disciplined context strategy.

### PEID-3.12 The context checklist and symptoms
Before rewriting a word, answer five questions: what does the model need to know that it cannot know; where does that live and how does it get in (pasted, retrieved, fetched by a tool); what is the smallest set that would do; how will you know it used the right thing (quotes, visible sources); and what happens when the answer is not there ("cannot tell from these documents" must be an allowed output). Context-level symptoms and fixes: inventing company facts → get the document in, require a quote, allow abstention; quoting the rule but missing the exception → raise k, add keyword search, re-rank, follow references; "worse when I gave it more" → cut the context, move what matters to the edges; ignoring the middle of a long document → retrieve the relevant part instead; doing something nobody asked for → treat text as data, cut tool permissions, gate irreversible actions; forgetting what was agreed earlier → write durable facts outside the chat and re-supply them.

### PEID-3.13 Prompt caching
Providers can store the processed front of a context; a later call starting with a byte-identical prefix is billed at a fraction of the normal input price and answers faster (on one provider, cache reads cost about 0.1× and writes 1.25–2×, with a minimum prefix length and a short default lifetime). The match is an exact prefix from the very start, so one changed character invalidates everything after it. Order the context stable first (tools, system prompt, examples) and volatile last (retrieved text, history, question); a timestamp at the top of a system prompt silently disables caching. Caching makes a stable context cheap, not a bloated one.

### PEID-3.14 What "memory" features are
Product "memory" means: something decides a fact is worth keeping, it is written to a file or database outside the model (nothing is written into the weights), and later it is retrieved and pasted back into the window, usually invisibly. It is retrieval with a friendlier name and inherits every retrieval problem: it costs budget on every call, a wrong memory persists, anything that can write to memory can plant instructions, and it is personal data with retention and consent obligations.

---

## PEID-4 Agents and AI coding assistants

### PEID-4.1 Workflow or agent
A **workflow** is a system where LLMs and tools are orchestrated through predefined code paths written by a developer (e.g. classify → draft reply → send). An **agent** is a system where the LLM dynamically directs its own process and tool use, choosing the next step at runtime (search, read a file, run tests, decide what next). The difference is not intelligence; it is who decides the next step. An agent loop assembles the context, the model predicts, a tool call is run and its result pasted back, and everything returned stays in the window for later turns; one typed sentence can grow into about fifteen thousand tokens of assembled context.

### PEID-4.2 The augmented LLM and five patterns
The building block is a model with retrieval, tools and memory; everything else is composition. Five patterns (Schluntz & Zhang, "Building Effective Agents", Anthropic 2024): **prompt chaining** (a sequence of steps, each processing the previous output); **routing** (classify an input and direct it to a specialised follow-up); **parallelisation** (run subtasks simultaneously and aggregate, by sectioning or voting); **orchestrator-workers** (a central LLM breaks down a task not known in advance, delegates to workers and synthesises); and **evaluator-optimizer** (one call generates, another evaluates and gives feedback in a loop). The first four are workflows; only the last hands the stopping decision to a model's judgement. Recommended approach: start with simple prompts, optimise them with evaluation, and add multi-step agentic systems only when simpler solutions fall short.

### PEID-4.3 Four ways to steer a coding assistant
| | Instructions | Skills | Sub-agents | Hooks |
|---|---|---|---|---|
| Job | Conventions it must always know | A procedure it sometimes runs | Work done elsewhere | A rule that must always hold |
| Loads | Every request | When the request matches | When spawned | On an event |
| Who decides | You, in advance | The model | The model or you | Nobody — it fires |
| Context cost | Every turn | Description only until used | None in the main window | None |
| Fails when | The file gets long | The description is vague | The summary loses detail | Never — that is the point |

Example files: `AGENTS.md` / `CLAUDE.md` / `GEMINI.md`; `SKILL.md`; `.agent.md`; `.github/hooks/*.json`.

### PEID-4.4 Instruction files
An instruction file (AGENTS.md, an open standard contributed by OpenAI, now an Agentic AI Foundation project, adopted by more than 60,000 open-source projects) is a Markdown file the agent reads before anything else: commands, where things live, rules that always apply. It is injected next to the system prompt on every turn, so five useful lines beat fifty hopeful ones (a common rule of thumb is to keep it under 200 lines). The nearest file in the directory tree wins. In GitHub Copilot the precedence, highest first, is personal instructions, path-scoped `.github/instructions/*.instructions.md`, `.github/copilot-instructions.md`, then AGENTS.md, then organisation instructions; Copilot also reads CLAUDE.md and GEMINI.md, while Claude Code reads CLAUDE.md (not AGENTS.md) and Google Antigravity reads GEMINI.md plus a rules folder. Use an instruction file when the agent gets the same convention wrong twice.

### PEID-4.5 Skills
A skill is a folder with a `SKILL.md` that the agent opens only when a request matches its description. Loading has three levels: name and description always loaded; the whole SKILL.md injected when the request matches; bundled files read only if needed. The description is the only part the model sees before deciding, so it must say what the skill does and when to use it — a vague description is a skill that never fires. This is just-in-time retrieval applied to the agent's own instructions. Rule: put it in the instruction file if the agent should always know it; make it a skill if it is reference material needed sometimes or a workflow you trigger.

### PEID-4.6 Sub-agents
A sub-agent works in its own context window and returns only a summary (typically one or two thousand tokens) to the main agent, so detailed search noise stays isolated while the lead agent synthesises. A specialist sub-agent can be given restricted tools — for example a reviewer that can read and search but cannot edit. Use one when a side task would flood the main window with output you will never re-read.

### PEID-4.7 Hooks
An instruction like "never edit .env" is a request the model usually, but not always, follows (long sessions, ambiguous requests and injected text can break it). A hook is enforcement: a configured script that runs on an event (e.g. before a tool is used), outside the model's judgement. A pre-tool-use hook can inspect the planned step and exit with a "blocked" code if it touches `.env`, cancelling the step and telling the agent why; otherwise the tool runs normally. Use a hook when something must happen every time without being asked.

### PEID-4.8 Which mechanism to reach for
It gets the same convention wrong twice → instruction file. You keep typing the same prompt to start a task → a user-invocable skill. You paste the same playbook a third time → a skill. You keep copying data from a system it cannot see → an MCP server. A side task floods your window → a sub-agent. Something must happen every time → a hook. A second repository needs the same setup → a plugin bundling the files. You want it to stop and think before writing → plan mode. Each mechanism has a context cost: instruction files every request; skills low until fired; MCP tool names at session start, schemas on demand; sub-agents and hooks zero in the main window.

### PEID-4.9 MCP — the Model Context Protocol
Before MCP, every assistant needed a bespoke connector to every system. MCP (Anthropic, 2024; now under a Linux Foundation project) is one standard plug — "a USB-C port for AI applications". A **host** (VS Code, Copilot, Claude Code) holds the conversation and runs one **client** per **server**; servers (a database, a ticket system, a browser) can be local or remote. Design rule: the conversation stays in the host — a server can be asked to do a job but cannot read the conversation or see other servers. A server offers **tools** (functions the model decides to call), **resources** (data it can read) and **prompts** (templates the user picks). Each tool arrives in the window as a name, description and JSON schema — a tool description is text somebody else wrote that the model reads as instructions, so it is an injection surface. A project's `mcp.json` names a server and the command that starts it. MCP changes what the agent can reach, not what it can decide.

### PEID-4.10 Can a model check its own work?
The evaluator-optimizer loop (generate → critique → revise) was popularised in 2023, but intrinsic self-correction — reflecting with no outside signal — often makes reasoning worse: a model that got an answer wrong usually cannot tell (Huang et al., 2024). Self-correction works when there is a reliable external check (passing tests, a retrieved fact, a verifier score). That is why it works in a coding agent (the test suite is the check) and why "double-check your work" in a chatbot often does not.

---

## PEID-5 Evaluating GenAI applications

### PEID-5.1 One run is not a measurement
Because outputs are sampled, the same prompt run five times can be right three times and wrong twice. Two honest numbers: **pass@k** — at least one of k runs works (rises with k; appropriate if a human checks the output) — and **pass^k** — all k runs work (falls with k; appropriate if nobody checks). Always say which one you quote.

### PEID-5.2 What an eval is
Three parts (Anthropic, 2026): a **task** (a single test with defined inputs and success criteria), a **transcript** (the complete record of a trial — outputs, tool calls, reasoning, intermediate results) and a **grader** (logic that scores some aspect of performance: code, a model or a person). You choose the grader; the other two you collect. Error analysis — reading transcripts — is the most important activity in evals; practitioners report spending most of their development time on it.

### PEID-5.3 Open coding and failure taxonomies
Error analysis uses open coding, borrowed from qualitative social science, in three passes: (1) read about twenty outputs and write one free-text sentence about what went wrong beside each, without a category list; (2) cluster the sentences into named families, producing a taxonomy that did not exist before; (3) only then count, giving an ordered list of what to fix. Stop when about twenty new traces produce no new category (aim for about 100 for a production system). Prefer binary pass/fail judgements with a written critique: three people scoring 1–5 disagree silently, while asked "does it pass?" their reasons become visible.

### PEID-5.4 From failure mode to criterion
A **failure mode** is a specific, repeatable pattern of incorrect, unsafe or undesirable behaviour, found by reading. An **evaluation criterion** is a defined dimension measured on every output, which you write from a failure mode. In the course's ticket-triage example, 13 of 20 failures (wrong category, quote not present in the ticket, should have abstained, more than one label) could be checked by code such as a substring test; only one family (urgency inflated by emotional wording, 7 failures) needed a model judge. A criterion with no failure behind it is decoration.

### PEID-5.5 Labels are definitions
Bare label names ("billing", "account_access") are not a specification: three annotators produce three label sets, and the model is a fourth annotator. Each label needs four parts: a definition, inclusions, a boundary against its nearest neighbour (what is excluded and where it goes instead), and one tie-breaker for the whole set (e.g. when two apply, label what the customer wants fixed first). An "other" label is an escape hatch: it is an answer, not a failure. A full classifier prompt combines PEID-2 techniques — role, label definitions, tie-breaker, criteria as instructions, an output designed to be graded (e.g. a quoted evidence sentence) and a structured output, plus boundary examples.

### PEID-5.6 Accuracy, precision and recall
For each label, a confusion table has four boxes: true positives, false positives, false negatives and true negatives. **Precision** = TP/(TP+FP): of the ones we flagged, how many were right (its cost is wasted effort). **Recall** = TP/(TP+FN): of the ones that mattered, how many we caught (its cost is a missed case). **Accuracy** = (TP+TN)/all — and it lies on imbalanced data: a classifier that found three of four bug reports and raised six false alarms still scored 82.5% accuracy, because the large harmless true-negative box did the work.

### PEID-5.7 Macro or micro averaging
With several labels you have one table per label. **Macro** averaging computes the score per label and takes the plain mean — every label counts the same however rare, so a broken rare class drags the number down visibly. **Micro** averaging pools all the boxes first — every decision counts the same, so common labels dominate and a broken rare class can disappear. Use macro when the rare class is the point, micro when every decision costs the same. Neither is more correct; reporting an average without naming it is the only wrong answer. The two can agree on a small test set and drift ten points apart on real traffic when the label mix changes.

### PEID-5.8 Price the mistake first
The metric follows from which error you can afford. Routing tickets to teams: both errors cost a few minutes, per-class accuracy is fine. Flagging a possible outage: a miss is a public incident, so favour recall and accept false alarms. Auto-closing tickets: a wrong close loses a customer, so favour precision. F1 is a compromise for when both errors genuinely cost the same. Accuracy on an imbalanced set and an unnamed average on a multi-label set are numbers that hide rather than report.

### PEID-5.9 Multi-class versus multi-label
Multi-class gives exactly one label per input, so each row is right or wrong. Multi-label allows zero or more labels (e.g. a ticket that is both billing and account access). Exact-set matching then scores a half-right answer as a total failure, so you score precision and recall per label and then average (macro or micro, named). The prompt change is small: return a list, and an empty list if none apply.

### PEID-5.10 The golden set
A golden set contains real inputs (not invented ones), labelled by named humans before any model output is seen, starting at around 20 cases and growing whenever production surprises you; it is frozen and versioned in one checked-in file, and never used in the prompt, not even as a few-shot example (once it is in the prompt it stops being a test). Each row records the input, the labels, who agreed them, the date and notes on disagreements. The weakest part of a golden set is always the labelling, never the model.

### PEID-5.11 The cheapest grader that works
Three kinds of grader: **code** (fast, cheap, objective, reproducible; catches format, forbidden words, quote-not-in-source, label not in the allowed list, wrong category); **model** (flexible, captures nuance such as tone, groundedness and whether the question was answered — but you must prove the judge agrees with you); and **human** (gold-standard quality; produces the golden set, label definitions and judge calibration; once, not on every run). If an assertion or regular expression catches it, that is the answer. Use a costlier grader only because the cheaper one cannot do the job.

### PEID-5.12 Agreement and Cohen's kappa
Raw agreement flatters: two annotators labelling a set that is 90% "other" can agree 90% of the time while guessing. Cohen's kappa subtracts the agreement expected by chance: κ = (pₒ − pₑ)/(1 − pₑ), where pₒ is observed agreement and pₑ chance agreement; 1 is perfect, 0 no better than chance. Example: observed 0.90 with chance 0.82 gives κ = 0.44 — labels barely usable. Conventional bands: below 0.4 the labels are not usable; 0.4–0.6 the guidelines are ambiguous; above 0.8 strong. The fix for low kappa is to rewrite the label definitions, never to ask people to "try harder".

### PEID-5.13 Self-correction versus LLM-as-judge
Self-correction fails: one call, its own answer, its own reasoning, no external reference. An LLM judge can work, under four conditions together: a separate call (not the same turn reflecting on itself), a different prompt written to grade rather than answer, an external rubric with criteria the model did not invent while answering, and calibration against human labels (agreement measured before trusting it). Remove any one and you are back to self-correction.
