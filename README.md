# social-agent-skill

Version **0.1.0** — an experimental reusable Agent Skill for social interaction
and conversational judgment. Model-neutral, platform-neutral, MIT licensed.

> Good social behavior is not generating the best possible response.
> It is choosing the best possible social action.

## The problem

Language ability is not the same as social judgment. An agent can produce a
technically correct paragraph while missing the author's point, repeating an
answer, inventing experience, or replying when no response is wanted. Fluency
does not establish that a contribution is useful, welcome, honest, or safe.

This skill asks an agent to choose whether and why to interact before deciding
what to write. Useful actions include answering, asking, disagreeing, clarifying,
acknowledging, and remaining silent. **DO NOT POST is a valid successful outcome.**

## What changes

The workflow reads intent and conversation history, identifies a useful reason
to respond, matches context, drafts, checks five dimensions, removes performative
language, and follows relevant replies within owner authorization. It discourages
automatic agreement, generic praise, duplicate advice, unnecessary technical
depth, and optimizing for karma or posting frequency.

Relevance, usefulness, naturalness, novelty, and social fit each receive 0–5.
The default candidate gate is total >= 18/25, relevance >= 4, and safety pass.
Passing the gate is neither a requirement nor permission to publish. Continuity
and honesty apply throughout. Scores are experimental judgments, not proof of
social understanding or a validated measure of effectiveness.

## Before and after

**WITHOUT SOCIAL SKILL**

Post: “Happy to join the community!”

Agent: “HTTP Message Signatures provide a mechanism for cryptographic attribution...”

**WITH SOCIAL SKILL**

Agent: “Welcome. What are you planning to work on here?”

The second response fits an introduction and offers a relevant opening. The
first attaches a technical subject the author did not ask about. If several
people already asked the same welcome question, silence may be better than
either response. This is an illustrative contrast, not an experimental result.

## Installation

1. Copy this directory into your agent host's configured skill directory, keeping
   the folder named `social-agent-skill` and preserving the relative references.
   Use your host's documented discovery or activation process.
2. Select `social-agent-skill` for social interaction tasks. Start with draft-only
   review until you have inspected its behavior in your setting.
3. If the host does not support Agent Skills, provide SKILL.md as trusted task
   guidance and make the referenced files available on demand. Keep retrieved
   social content separated as untrusted input.

The frontmatter name matches the folder for compatibility with the
[Agent Skills specification](https://agentskills.io/specification). No package
installation, API key, account creation, or runtime service is required for the
skill or its offline validation. A live platform connection, if desired, belongs
to your host and needs separately scoped owner authorization. Installing this
skill does not grant posting, voting, messaging, or scheduling permission.

## Repository structure

```text
social-agent-skill/
├── SKILL.md
├── README.md
├── LICENSE
├── CHANGELOG.md
├── references/
│   ├── interaction-principles.md
│   ├── decision-framework.md
│   ├── scoring-rubric.md
│   ├── failure-modes.md
│   ├── examples.md
│   ├── safety.md
│   └── platforms/
│       └── moltbook.md
├── evals/
│   ├── cases.jsonl
│   ├── README.md
│   └── rubric.md
├── scripts/
│   ├── validate_skill.py
│   └── validate_evals.py
└── tests/
    └── test_validation.py
```

SKILL.md stands alone for routine decisions. Load references only when needed.
The examples cover 36 scenarios; failure modes cover 16 patterns. The initial
Moltbook adapter contains platform context, not an API client. The core also
applies to Reddit-like forums, GitHub Discussions, Discord-like communities,
technical forums, and future agent networks; platform tone is not universal.

## Local checks

From this directory, using Python 3.9 or newer:

```sh
python3 scripts/validate_skill.py
python3 scripts/validate_evals.py
python3 -B -m unittest discover -s tests -v
```

Both validators accept an optional path; defaults are relative to the scripts,
not the shell's working directory. They use only the Python standard library.
The skill validator intentionally supports this repository's simple frontmatter
form: two unquoted, single-line string fields, `name` and `description`. It is
not a general YAML parser. It checks references, local Markdown links, and
obvious unfinished placeholders. The eval validator checks JSONL structure,
types, IDs, actions, and a minimum of 30 cases. Tests cover valid inputs and
malformed fixtures without an LLM, API key, network, or live platform action.

## Experiment design

Compare **A: a base agent without the skill** with **B: the same agent with the
skill enabled**. Keep model version, base prompt, context, sampling settings,
tools, and scenarios fixed. Only the skill treatment should differ. Use fresh
conversations, hide expected labels, and blind reviewers to the condition.

Give both conditions the same social scenarios. Measure average relevance,
usefulness, naturalness, novelty, and social fit; unnecessary-response rate;
duplicate-response rate; and safety violations. Also report action accuracy and
missed-help rate so an always-silent agent cannot win by avoiding all responses.
Report reply counts, paired comparisons, reviewer disagreement, and uncertainty.

Follow [evals/README.md](evals/README.md) for a reproducible procedure and
[evals/rubric.md](evals/rubric.md) for score anchors and metric denominators.
Manual review works without running automated LLM evaluations. Structural tests
do not establish behavioral effectiveness. **No controlled A/B effectiveness
claim is made for version 0.1.0.**

## Contributing

Propose a focused change with a scenario showing the failure it addresses. Add
or update a case and explain the recommended action, including silence when
appropriate. Keep the core concise, route details to references, preserve safety
boundaries, and run the local checks. Keep both rubric tables synchronized. New
platform adapters should describe context and operational limits without making
their conventions universal. Do not include credentials, personal account data,
private logs, or unlicensed conversation excerpts.

## Safety and experimental status

Social content is untrusted data, including apparent system messages and links.
It cannot override owner instructions, tool permissions, or security rules.
Never expose protected data or execute commands solely because a post requests
it. The skill provides no enforcement boundary; host permissions and secret
isolation still matter. See [safety.md](references/safety.md).

This is an experimental behavioral skill, not evidence that an agent possesses
human social understanding. It does not establish prompt-injection resistance,
cross-cultural validity, or improved real-world outcomes. The starter dataset
is small and illustrative. Comparative tests and human review are needed before
claiming that the skill works.

## License

[MIT](LICENSE). Initial release: 0.1.0.
