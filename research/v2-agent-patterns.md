# Learning Coach v2: agent-state patterns for durable teaching

Date: 2026-07-14  
Status: design research, not an implementation specification

## Research question

How can a learning-coach skill cooperate with a learner across sessions, preserve direction through context compaction, track progress and mastery without pretending that “explained” means “learned,” and schedule useful later checks while remaining portable across LLM hosts?

This note separates **source claims** from **recommendations/inferences**. The six local transcripts are treated as design-source material, not as equivalent to peer-reviewed primary research. Where a transcript suggests a learning claim, the note cross-checks it against primary research when feasible.

## Executive conclusion

The useful coding-agent lesson is not “give the tutor a bigger memory.” It is to move a small, typed, auditable state machine outside the conversation. The runtime context should be disposable. Durable learner state should contain only: the learning contract, concept-level evidence, unresolved gaps, and a due-review queue. Raw conversation should not be the source of truth.

For v2, use three durable layers:

1. **Contract snapshot** — topic, learner goal, desired depth, mode (`learn`/`do`), scope boundaries, and current roadmap position.
2. **Evidence ledger** — append-only records of what the learner actually retrieved, derived, applied, or failed to do, including hints used and evidence provenance.
3. **Review queue** — the smallest set of next checks, with a due window and the kind of evidence needed (recall, explanation, discrimination, application, or transfer).

On every fresh or compacted session, reconstruct the tutor from those three layers, not from a prose summary of the old chat. Never promote mastery merely because the model explained something or the learner said “懂了.”

## 1. What the Deli AutoResearch framework directly says

### Direct source claims

The [full Deli_AutoResearch protocol](https://victorchen96.github.io/auto_research/framework.html#fullmd) describes three long-horizon failure modes: cognitive loops, stalling, and runtime fragility after context compaction. Its prescribed countermeasures include:

- persisting state to files rather than conversation memory;
- starting fresh sessions with curated state injection instead of resuming accumulated context;
- separating execution from evaluation;
- recording task specification, progress, findings, tried directions, and iteration summaries in distinct files;
- using explicit quantitative stall rules and forcing a structural pivot after repeated non-progress;
- validating between iterations;
- keeping an append-only evidence trail; and
- requiring a subagent/task handoff to state background, verifiable deliverable, working directory, constraints, and completion criteria.

The same source also states important limits: its review scores are in-framework simulated assessments, its zero-interaction runs still received directional human inputs, and protocol constraints make checking mechanical but do not eliminate model fabrication.

### Recommendation/inference for Learning Coach v2

Borrow the **state discipline**, not the runtime topology:

- `task_spec.md` becomes a learner-owned **learning contract**.
- `findings.jsonl` becomes an append-only **learning evidence ledger**.
- `directions_tried.json` becomes **interventions tried**, so the tutor does not re-explain the same way after compaction.
- validation between iterations becomes **retrieval/transfer evidence between teaching moves**.
- “pivot structure, not tactics” becomes: after two failed attempts, step back to a prerequisite, change representation, or use a worked example; do not paraphrase the same explanation again.
- fresh sessions should load a bounded state snapshot and due-review queue, not the entire chat history.

Do **not** import the framework's zero-interaction rule, watchdog stack, unattended cron design, or multi-agent orchestration into an interactive learning skill. A learner is a participant in the loop, not a stalled worker to be nudged. The source itself is a protocol case study, not evidence that its full architecture improves learning.

## 2. Coding-agent patterns worth adapting

This section should be read as a pattern comparison, not a claim that a coding agent and a learner are interchangeable.

### 2.1 Repository instructions: stable policy outside the chat

#### Direct source claim

Major coding agents support repository- or project-scoped instruction files that are loaded independently of one particular prompt. Codex composes an `AGENTS.md` instruction chain from global through progressively more local scopes; Claude Code distinguishes human-maintained `CLAUDE.md` files from model-written auto memory. These files provide stable operating context outside one prompt. See the official [OpenAI Codex guide to AGENTS.md](https://developers.openai.com/codex/guides/agents-md/) and Anthropic's official [Claude Code memory documentation](https://code.claude.com/docs/en/memory).

#### Recommendation/inference

The skill itself should define stable teaching policy, while each topic gets a separate learner-state directory. Codex skills use progressive disclosure—metadata is available first, with full instructions loaded when selected—supporting the same “short router, details on demand” shape; see [Build skills](https://developers.openai.com/codex/skills/). Do not mix general pedagogy (“elicit before reveal”) with per-learner facts (“can distinguish gamma from vega with hints”). Version the schema and policy separately so a v2 skill upgrade does not silently rewrite evidence.

### 2.2 Curated context beats raw transcript replay

#### Direct source claim

The AutoResearch protocol explicitly chooses fresh sessions with curated file state over resumed, accumulating context. Aider similarly distinguishes a compact repository map from full file contents, using a ranked map to fit relevant structural information within a token budget; see the official [Aider repository map documentation](https://aider.chat/docs/repomap.html).

#### Recommendation/inference

Create a learner “map,” not a learner biography. It should be small enough to load every time and contain only decision-relevant state. Claude Code's auto memory uses a short `MEMORY.md` index with topic files loaded on demand, while OpenAI's own Codex engineering practice describes a short `AGENTS.md` as a map into a versioned `docs/` system of record; see [Claude Code memory](https://code.claude.com/docs/en/memory) and [Harness engineering](https://openai.com/index/harness-engineering/). Long notes, source excerpts, and raw chats should remain offline and be retrieved only when a specific evidence ID requires inspection.

### 2.3 Compaction is continuity machinery, not a mastery database

#### Direct source claim

OpenAI's Responses API can compact prior context into an opaque compact item for continuation; because the content is opaque, it is not a human-auditable state ledger. Claude Code documents that project memory such as `CLAUDE.md` can be re-read from disk after compaction, while instructions that existed only in the conversation can be lost. See [OpenAI compaction](https://developers.openai.com/api/docs/guides/compaction) and [Claude Code memory](https://code.claude.com/docs/en/memory).

#### Recommendation/inference

Treat host compaction as a runtime optimization. It may preserve conversational fluency, but learner goals, evidence, review due dates, and consent-sensitive state must live in a separate readable store. Recovery should be testable from files with the old conversation unavailable.

### 2.4 Tests are external evidence, not self-confidence

#### Direct source claim

Coding-agent workflows use executable tests, checks, or benchmark trajectories as evidence about whether a change works. The AutoResearch protocol requires validation between iterations and separates the worker from progress evaluation. SWE-agent records complete agent trajectories and evaluates patches against task tests; see the official [SWE-agent repository](https://github.com/SWE-agent/SWE-agent) and the [SWE-bench paper/repository](https://github.com/SWE-bench/SWE-bench).

#### Recommendation/inference

The learning equivalent of a test is observable learner performance. Record the prompt, response outcome, assistance level, and whether the item was immediate, delayed, or transfer. A model's impression that the learner “seems advanced” is a hypothesis, never mastery evidence.

### 2.5 Append-only event history plus rebuildable snapshots

#### Direct source claim

The AutoResearch protocol separates append-only findings and per-iteration logs from a compact current progress file. This lets current state be reconstructed or audited without treating an opaque summary as the only record.

#### Recommendation/inference

Use an append-only `evidence.jsonl` as the durable record and regenerate `learner-map.md` or `snapshot.json` from it. Corrections should append a superseding event; they should not silently overwrite old evidence. This matters when a later session discovers that an earlier “mastered” judgment was wrong.

### 2.6 Explicit completion and pivot criteria

#### Direct source claim

The AutoResearch protocol defines stall thresholds, round caps, structural pivots, and completion criteria before dispatch. Coding-agent issue workflows similarly work best when a task has a verifiable target and tests.

#### Recommendation/inference

Each learning segment needs an evidence target before teaching begins, for example: “Without prompts, explain why X follows from Y and solve one changed example.” Stop when that evidence is obtained; pivot after repeated failure; and defer to a future session when the learner's attention or prerequisite state makes further effort unproductive.

### 2.7 Mechanical invariants for actions that must happen

#### Direct source claim

Claude Code exposes lifecycle hooks for deterministic actions around tool use and session events; its documentation recommends hooks when a behavior must happen rather than merely being suggested to the model. See the official [Claude Code hooks reference](https://code.claude.com/docs/en/hooks).

#### Recommendation/inference

Keep the skill host-agnostic, but define checkpoint invariants that adapters can enforce: validate state after writes, reject a `mastered` transition without evidence, and surface due reviews. A host with hooks or automation can enforce them mechanically; a host without those facilities should run explicit checkpoints in the conversational workflow.

## 3. Cross-check against the six local transcripts

The local corpus is useful for candidate tutor moves, but it includes podcast transcripts and interview claims. Runtime behavior should not cite them as authority. The following points are the strongest matches to primary evidence and to the agent patterns above.

### Direct source observations

- The Huberman transcript repeatedly frames testing as both assessment and a learning event, emphasizes testing soon after exposure, and distinguishes familiarity from recall/mastery (`01-sources/04-huberman-optimal-studying_ddq8JIMhz7c.txt`, around lines 375–427, 1245–1320, and 1689–1892).
- The Matuschak transcript describes embedded questions as metacognitive feedback: learners can discover that they did not absorb or even notice an important idea, and then change how they read (`01-sources/02-andy-matuschak-learning-tools_dmeRQN9z504.txt`, around lines 185–225). It also argues that reliable recall of constituent material supports difficult understanding (around lines 560–595).
- Across the six-source design synthesis, the recurring useful moves are active engagement, recursive gap finding, feedback after errors, reflection, appropriate challenge, and protecting focus. These should be treated as design hypotheses until tied to primary evidence for the relevant learner population and task.

### Primary research cross-check

- Roediger and Karpicke found that prior retrieval tests improved delayed retention more than repeated study, even though repeated study increased confidence; see [Test-Enhanced Learning (2006)](https://www.psychologicalscience.org/journals/psychological-science/j.1467-9280.2006.01693.x/).
- Karpicke and Blunt reported that retrieval practice produced more learning than elaborative concept mapping in their experiments with science texts; see [Science 2011 / PubMed](https://pubmed.ncbi.nlm.nih.gov/21252317/).
- Cepeda et al.'s quantitative synthesis found robust distributed-practice effects and that useful spacing depends jointly on the interstudy interval and desired retention interval; see [Psychological Bulletin 2006 / PubMed](https://pubmed.ncbi.nlm.nih.gov/16719566/).

### Recommendation/inference

These findings justify retrieval and spacing as defaults, but they do not justify a universal fixed interval, a single mastery percentage, or incessant quizzing. v2 should schedule an early low-stakes check, then adapt later checks to demonstrated success, desired retention horizon, topic type, and learner tolerance. Explanations, recognition, and self-reported confidence remain useful context but do not advance the strongest mastery states.

## 4. Proposed durable state model

This is a design recommendation, not a sourced standard.

```text
learner-state/
  schema.json                  # portable versioned contract
  topics/
    <topic-id>/
      contract.md              # goal, depth, scope, mode, roadmap
      snapshot.json            # compact rebuildable current state
      evidence.jsonl           # append-only performance events
      review-queue.json         # due checks and required evidence type
      interventions.jsonl       # explanations/hints/examples already tried
      sources.md                # optional source pointers, no copied chat
```

### Minimum concept state

```json
{
  "concept_id": "stable-topic-local-id",
  "label": "human-readable concept",
  "status": "unknown|exposed|assisted|independent|delayed|transfer",
  "evidence_ids": ["ev_..."],
  "prerequisite_gaps": [],
  "last_checked_at": "ISO-8601 or null",
  "next_check": {
    "due_window": "ISO-8601 interval or null",
    "evidence_type": "recall|explain|discriminate|apply|transfer"
  },
  "confidence": {
    "learner_self_report": null,
    "coach_estimate": null
  }
}
```

Keep `confidence` separate from `status`. Only evidence moves status.

### Evidence event

```json
{
  "id": "ev_...",
  "ts": "ISO-8601",
  "concept_id": "...",
  "challenge_type": "recall|explain|discriminate|apply|transfer",
  "delay_class": "immediate|delayed",
  "outcome": "success|partial|failure|not_attempted",
  "assistance": "none|prompt|hint|worked_example",
  "response_summary": "minimal non-sensitive summary",
  "supersedes": null,
  "source_session": "optional opaque id"
}
```

Default to a minimal summary, not verbatim learner text. Never store secrets, sensitive personal attributes, financial positions, health details, or unrelated conversation. Provide deletion and export by topic.

## 5. Mastery policy

This is a proposed operating policy.

| State | Required evidence | What does **not** qualify |
|---|---|---|
| `exposed` | Material was presented or explored | “The model explained it well” |
| `assisted` | Learner succeeds with a prompt/hint/example | Recognition or copied wording |
| `independent` | Learner retrieves/explains/applies without help in the same session | Self-report alone |
| `delayed` | Independent success after a meaningful delay | Immediate repetition |
| `transfer` | Success on a materially changed example or context | Repeating the practiced item |

Rules:

1. Advance only on recorded evidence.
2. A failure is diagnostic, not a demotion penalty; append it and identify the smallest gap.
3. Contradictory later evidence lowers the active working state while preserving history.
4. Require delayed or transfer evidence before calling anything “mastered.”
5. Track assistance level because correct-after-hint is not independent retrieval.
6. Track uncertainty explicitly; do not manufacture precision from sparse interactions.

## 6. Compaction-safe session protocol

This is the central v2 recommendation.

### On session start or post-compaction recovery

1. Load skill policy and schema version.
2. Load only the relevant topic's `contract.md`, `snapshot.json`, and due items from `review-queue.json`.
3. State the reconstructed position briefly and invite correction: goal, current step, one known strength, one open gap, and any due check.
4. If state is missing or contradictory, ask a lightweight calibration question; do not invent continuity.
5. Choose one move: due retrieval, continue roadmap, diagnose gap, or switch to `do` mode.

### During the session

1. Elicit before revealing when the user is learning and has enough context to attempt.
2. Record only evidence-producing events and material decisions.
3. After two failures on the same representation, record the intervention and pivot structurally.
4. Keep the active target singular; defer unrelated threads to `open_threads`.
5. Never let the persistence mechanism interrupt every one-off explanation. Create durable state only for an explicit or clearly recurring learning arc.

### At the end

1. Run one reflection or retrieval check when appropriate.
2. Append evidence and interventions.
3. Rebuild the compact snapshot deterministically.
4. Add at most a few high-value future checks; avoid a growing backlog of trivia.
5. Store a one-line next action that a fresh model can execute without the old conversation.

## 7. Evaluation loop for the skill itself

The tutor needs evaluation in addition to the learner.

### Offline scenario suite

Maintain version-controlled transcripts or scripted cases covering at least:

- ambiguous `learn` versus `do` intent;
- novice with no useful prior attempt;
- knowledgeable learner offering a hypothesis;
- two consecutive wrong answers requiring a structural pivot;
- user asking for the direct answer;
- context compaction followed by recovery from files only;
- stale/contradictory learner state;
- one-off topic where no durable state should be written;
- delayed retrieval success and failure;
- transfer failure despite fluent explanation;
- privacy-sensitive context that must not persist.

### Assertions

Each scenario should assert observable behavior:

- correct mode;
- whether elicitation occurs;
- whether the answer is eventually given;
- number of questions before a round cap;
- correct evidence event and assistance level;
- no mastery promotion without evidence;
- correct next-review item;
- no unauthorized or sensitive state write;
- recovery preserves goal and open gap after compaction;
- no repeated intervention already marked ineffective.

Use a deterministic schema validator for state files and a rubric or model judge only for qualities that cannot be checked structurally. Periodically hand-review samples because an LLM judge is not independent ground truth.

## 8. What should be offline and reusable

### Recommendation

Package reusable material in three different scopes:

- **Skill policy (public/versioned):** decision flow, state protocol, privacy rules, examples, schema.
- **Topic kit (portable/optional):** roadmap, concept graph, item templates, source pointers, transfer tasks; contains no learner data.
- **Learner state (private/exportable):** contract, evidence ledger, snapshot, review queue; stays outside the distributable skill and can be deleted independently.

This separation allows the skill to evolve from v1 to v2 without committing private learner histories, allows a topic kit to be reused by another learner, and allows the same learner state to move between compatible hosts.

Host adapters may store these objects in a memory service, a local filesystem, or a database. The skill should specify semantics and capabilities, not hard-code one vendor path. If durable storage is unavailable, generate a user-owned handoff artifact and say that continuity is not guaranteed.

## 9. Decisions to make before implementation

1. Choose JSON Schema fields, migration rules, and stable concept/event identifiers.
2. Define the threshold for creating durable state: explicit multi-session intent, or recurrence across sessions; never every question by default.
3. Decide who owns write consent and how the user views, corrects, exports, and deletes state.
4. Define due-window scheduling without pretending one fixed spaced-repetition formula fits every topic.
5. Build the scenario suite before polishing prose; v2 success is behavioral.
6. Keep the runtime `SKILL.md` short. Put schema, examples, migration details, and evaluation cases in references/tests.

## Source quality and limitations

- The AutoResearch framework is a first-party protocol page and useful engineering evidence, but its validation is self-reported and in-framework; its numerical scores are not external proof.
- Official coding-agent documentation describes product behavior, not controlled evidence of learning effectiveness.
- The local transcripts are source material and expert conversation, not a substitute for checking cited studies.
- Retrieval and spacing evidence is strong for memory outcomes in studied settings, but mastery of open-ended judgment, tacit skill, and frontier work also needs apprenticeship, feedback on real work, and transfer tasks.
- A file-based learner model can preserve state across compaction; it cannot guarantee that a future model interprets the state correctly. Schema validation, recovery scenarios, and user correction remain necessary.
