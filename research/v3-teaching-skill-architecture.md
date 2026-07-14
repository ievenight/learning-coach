# Learning Coach v3 — Teaching-Skill Architecture & Review Handoff

Generated: 2026-07-14 (Asia/Taipei)
Status: **integrated design** from a 5-analyst + adversarial-critic workflow, cross-verified
against the shipped `learner_state.py` and `SKILL.md`. Supersedes the design portions of
`v2-redesign-proposal.md`; keeps its §10 convergence. Not implemented beyond the v2 prototype.

## 0. How this was produced & how to read it

Five parallel analysts (turn-level pedagogy; Claude/Codex skill mechanics; LLM agent
capabilities/limits; exhaustive execution failure modes; prior art) plus an adversarial
completeness critic. Two analysts and the critic independently re-verified the code.

Claim types, kept separate on purpose:
- **[FACT]** — verified against docs or the live CLI (line refs are confirmed).
- **[DECISION]** — a design choice this doc makes, with its rationale/prior-art anchor.
- **[DEFER]** — named, not silently omitted.
- **[DON'T]** — an overstatement or dead-end to avoid.

Reviewer asks: attack the [DECISION]s (especially the scheduler and the grading mechanism);
confirm the [FACT] defects by reproducing them; challenge the deferrals.

## 1. The one architectural spine

> **The prompt teaches; the code and hooks enforce.**

[FACT] Skill/memory docs are explicit: injected text (SKILL.md, references, CLAUDE.md) is
*context, not enforced configuration* — "if a skill seems to stop influencing behavior… the
model is choosing other tools… use hooks to enforce behavior deterministically"
(code.claude.com/docs/en/skills, /memory). Only three things reliably happen: (a) `!`cmd``
dynamic injection at skill load, (b) hooks at lifecycle events, (c) logic inside
`learner_state.py`. **Every load-bearing guarantee that lives only in prose will be skipped
some fraction of the time** — and worst exactly late in a long session (context rot), which is
where the honesty-critical steps (verify-before-promote, log evidence, reload-after-compaction)
fire.

Consequence that drives the whole layout: **pedagogy → prose (fragile, tune it); state math +
honesty invariants → `learner_state.py` (reliable); recovery → a settings-level `SessionStart`
hook + a top-of-body `!`next`` injection (reliable).** Anything honesty-critical currently in a
droppable reference or in the reducer-as-intended-but-not-implemented is a latent failure.

## 2. The honesty problem, restated correctly (the core of the whole effort)

[FACT] The design's premise is "the tutor only appends evidence; a deterministic reducer
derives mastery." True at the transition layer. **But every evidence field the reducer consumes
— `outcome`, `assistance`, `recognition_only`, `challenge_type`, `delay_class`, `met_criteria`
— is judged by the same sycophantic model.** Determinism does not remove sycophancy; it
*relocates* it from the state-transition layer (genuinely fixed) to the evidence-logging layer
(not fixed). A deterministic reducer over a flattering label **launders a bad judgment into a
clean audit trail** — and because `peak` is monotonic, one over-credit is permanent and a false
`peak=transfer` suppresses the very re-test that would catch it.

[FACT] Sycophancy is empirically the dominant LLM-tutor failure: Sharma et al. (Anthropic, ICLR
2024) — agreement-with-user across all families, worse with scale/RLHF; and Bastani et al.
(2024, Turkish HS math RCT) — unguarded GPT-4 access left students **17% worse** once removed
(the crutch effect), mitigated by two guardrails: **hints-not-answers** (we have it) and
**feeding the tutor the correct solution** (we lack it entirely).

[DECISION] Three defenses, in order of leverage:
1. **Make the evidence fields hard to fudge** (criteria gate `outcome`; recognition default
   flips to the honest side; require the *harder* condition to be positively asserted) — §5.
2. **A scoped, live, adversarial re-grade at promotion only.** The v2 review dropped the runtime
   grader, but that conflated two different levers: a grader reading the *tutor's labels* (useless
   — polluted input) vs. one reading the *learner's raw answer* (valuable). For **promotion events
   only** (writing peak→independent or →transfer), capture the learner's production verbatim and
   run **one** cold-context adversarial pass ("find the gap in this answer"; input = raw answer +
   criteria, none of the warm conversation) before the write. Cheap (one call, at rare events),
   reads raw text not labels. This is the single highest-leverage unaddressed mitigation.
3. **Offline "mastered audit"** (subagent/CI): every `peak=mastered` must trace to a real
   unaided+delayed+different-context event, else demote. Not on the live path.

[DON'T] Do not claim the honesty machinery *eliminates* over-crediting. Realistic target: a state
file honest at the transition layer and **at most ~one notch optimistic** at the evidence layer —
narrower and auditable, not perfect.

## 3. Corrections to the current prototype (the workflow re-audited my own v2 code)

Honest record: the v2 rewrite fixed the four original defects but **introduced/left new ones**,
confirmed against `learner_state.py` today:

- **[FACT] Spaced repetition is effectively dead below the `transfer` rung.** `_reschedule_frontier`
  schedules the *advanced frontier* — a fresh cell with `interval_idx=0` → always ~1 day out.
  Interval growth (3→7→14→30) only ever applies at `transfer`. A concept mastered at `recall` is
  re-probed daily forever. (F1; `:298-303`, `:154-163`) **This defeats "re-test sensibly over time"
  for the entire climb.**
- **[FACT] The review queue re-teaches surpassed material.** Advancing recall→…→transfer orphans an
  overdue review at every passed rung (reschedule only replaces the *same* `(concept,frontier)`);
  `next` then hands back `explain` the learner already passed. DEFECT-4 reintroduced across
  escalation. (F2)
- **[FACT] `criteria`/`met_criteria` are stored and length-validated but never read by `rebuild`.**
  `outcome=success` with all criteria false still credits peak. The "criteria = antidote to
  over-crediting" claim is currently decorative. (C1; `:450-451`, `:669-671`)
- **[FACT] A single *immediate* one-shot success reaches peak.** `unaided` ignores `delay_class`
  and rep count (`:214`, `:236`); `delay_class` is recorded but never gates peak. The stated
  invariant "mastered = unaided+delayed+different-context" (§5.7) is prose-only. (C4)
- **[FACT] `consecutive_inadequate` is per-concept, not per-cell**, and reset by *any* unaided
  success (`:243-244`): an easy `recall` win wipes the plateau count for a failing `apply`, so the
  structural-pivot trigger never fires on a genuinely stuck sub-skill. (C7 — proposal said per-cell;
  code is per-concept.)
- **[FACT] `recognition_only` correctly blocks peak but leaves the cell `latest_outcome=success`
  and does not set `needs_reverification`** — a recognition pass "satisfies" the challenge. (C2/PROBE-J)
- **[FACT] SKILL.md promises "inspect, correct, export, or delete" but no delete/export/archive
  command exists** (`:701-810`). A false capability promise on data deletion is a privacy/trust
  liability. (O-9)
- **[FACT] One malformed JSONL line hard-fails every read** (`read_jsonl`, `:97-98`): a crashed
  append bricks the whole topic. No partial-line tolerance.
- **[FACT] `SKILL.md`'s 1-D ladder (`unseen→exposed→assisted→independent→delayed→transfer`)
  ≠ the code's 3 orthogonal axes** (`challenge_type` × `assistance` × `delay/recognition`).
  "assisted/independent/delayed" in the prose are not rungs — they are the assistance/delay
  dimensions collapsed onto the challenge ladder. A tutor reasoning from the prose can't map
  "independent" onto the CLI flags it must pass → **mislabeled evidence at the source**, upstream
  of every invariant. (C-5)

Root causes: (a) the scheduler repeats the same peak-vs-current confusion one level up —
conflating "what to teach next" (frontier, advancing) with "what to re-test for forgetting" (the
mastered cell, decaying); (b) the reducer is a faithful *aggregator* of tutor judgments, not the
*constraining grader* it was described as — every field that should limit over-crediting is
recorded-but-ignored or absent.

## 4. Skill file architecture (enforcement layer A)

[DECISION] **Triggering — bias to recall, gate precision in the body.** The dominant real-world
failure is UNDER-triggering: teaching requests ("explain X", "why does Y") look like things the
model can just do in one turn, so the skill never loads — and implicit study intent (bare
questions inside a study session) is where it's most valuable and least likely to fire. The
description carries the entire load decision (body loads only on invocation). So:
- Split `description` (what it is) + `when_to_use` (pushy trigger incl. implicit intent: "even if
  they only say 'explain', 'walk me through', 'why', or ask a bare question about a topic they're
  studying or already have a track for"), combined **< 1,024 chars** (spec cap).
- Over-triggering is the acceptable direction **only because** the body has a hard route gate that
  bails to Answer/Do. You cannot ship the pushy description without that gate (§5 router).
- Ship a **trigger-eval** (~20 labeled queries: implicit-intent positives + near-miss negatives
  like "just answer this", "fix this bug"), 3 runs each, pass ≥0.5, 60/40 split. This is the
  deliverable that catches the #1 practical failure.

[DECISION] **Progressive disclosure — put honesty rules in the body, not references.** [FACT]
Auto-compaction re-attaches only the most-recent invocation of each skill, first ~5,000 tokens,
shared 25k budget; `references/*.md` are separate messages that can be dropped. Today the honesty
invariants and mastery definitions live in droppable `state-protocol.md`/`tutoring-protocol.md` —
**a post-compaction agent may keep the friendly loop but lose "recognition can't raise peak."**
Re-sort by "does compaction-survival matter," not "is this about state": compact honesty rules +
"the store is the system of record; write evidence through, don't batch; after compaction reload
from files not the summary" go in the **SKILL.md body**; verbose recipes/pedagogy stay in
references. Keep the body < 500 lines / ~5k tokens (it's ~1.2k now — room to spare).

[DECISION] **Recovery — deterministic, not hoped-for.**
- A **settings-/plugin-level `SessionStart` hook** (matcher `startup|resume|compact`) runs
  `learner_state.py next` and injects frontier + due probe + tried-interventions, labeled
  authoritative. [FACT] It must NOT be a skill-frontmatter hook — those only fire while the skill
  is active, and the skill isn't active at cold start.
- Portable fallback needing no install: a **top-of-body `!`list-tracks``/`!`next`` injection**
  (fires every invocation) + the body rule "re-invoke `/learning-coach` after a compaction."
- [DECISION][DEFER-resolve] **Root-discovery convention:** `.learning-coach/` in cwd + `LC_ROOT`
  override + a one-line pointer in `MEMORY.md`/`CLAUDE.md`. A wrong `root` next session silently
  yields an empty store — the exact persistence failure the design exists to prevent — so this
  must be decided, not flagged. (G-6)

[DECISION] **No proactive reminders — grounded.** [FACT] `/loop`/session-cron fire only while the
app is open and idle; Cloud Routines run from a fresh clone with no local-file access, ≥1h; Desktop
tasks need the machine on + per-task setup. A passive skill cannot wake the user. Three honest
tiers: **passive re-test** (surface due on next open), **offline plan** (emit dates the user acts
on), **active reminder** only via user-consented host automation over committed state. A hard
**"never promise a reminder"** rule goes in the body (currently absent).

[DECISION] **Portability is asymmetric.** The portable, tool-neutral asset is the
`learner_state.py` store + JSON schema (Claude and Codex shell out identically). Triggering/
disclosure does not port — Codex has no description-triggering, concatenates `AGENTS.md` always-on.
Don't design as if one SKILL.md serves both.

## 5. Runtime teaching protocol (prose layer B)

**Mode router first, hard-gated** (cooperate-not-obstruct is the cheapest and largest UX win):
- Single-fact / lookup / "just answer this" / imperative execution verb → **Answer/Do** unless an
  explicit teach cue. Honor "just tell me" and reference questions directly.
- Elicit-first is **scoped to Teach + attemptable only**. Misapplying it outside Teach is the #1
  way the skill becomes worse than a plain assistant. Both failure directions are empirically
  attested (Bastani crutch when it just answers; Khanmigo over-obstruction when it won't).

**Turn engine** (distilled from 25 WHEN/THEN rules; full list in Appendix A):
1. **Novice floor:** gate elicitation on "can they attempt?" At true zero-foothold, expose the
   core idea / one worked example first, then elicit on a variant. (Problem-first needs a foothold.)
2. **Elicit → STOP and yield the turn.** The interaction boundary is the *only* reliable forcing
   function for a real retrieval attempt; the model's verbosity default otherwise answers its own
   question ("What do you predict? Well…"), manufacturing false `independent` evidence. Rule:
   **"you may not log evidence you did not elicit."**
3. **Diagnose the smallest gap**, one hypothesis per turn; never from confidence/fluency.
4. **Intervene on a *type*-escalating ladder:** miss → tactical hint (same representation); miss
   again → **structural** change (prerequisite / concrete case / near-miss contrast / worked
   example) — never a synonym; miss again → reveal + worked example, then a small transfer.
5. **Verify with the answer hidden**, probe matched to the claimed rung.
6. **Escalate on smooth, pivot/demote on fail.** [FACT] This is the single behavior the v2 code
   most lacks — it sits at `transfer` permanently once reached and never escalates or demotes.
   On a clean first-try success, do not dwell — raise one rung (recall→explain→apply→transfer).
7. **Round cap ≤3 per concept per session → graceful deferral** (name a prerequisite hypothesis;
   never grind). Explicit "keep going" overrides the cap; disengagement (one-word replies, "forget
   it") drops a rung. **Move verify+log to concept boundaries, not session end** — [FACT] the close
   routine currently fires at maximum context rot, exactly where the model is least able to do it.

**Anti-patterns → counter-moves** (each testable) in Appendix A. The five highest-leverage
behaviors: (1) scoped elicit-then-probe-the-edge; (2) fluency is never mastery; (3) always move to
the current edge; (4) cooperate don't obstruct; (5) test soon then re-test from durable state with
a file-executable next move.

## 6. State & scheduling layer (code layer C)

**Keep** (sound): peak/current/sparse-capabilities split; append-only ledger; deterministic
reducer; pure-file `next`; integer/enum control variables (float display-only). [FACT] Prior art
triple-validates the split — Bjork storage/retrieval, Khan's demotable levels, FSRS
stability/retrievability — so anchor it to those, don't present it as novel.

**Fix (the §3 defects):**
- [DECISION] **Schedule the cell actually mastered, not the advanced frontier.** Separate two
  schedules: "teach the next rung" (forward cadence) vs. "re-test a consolidated rung for
  forgetting" (real spacing). Keep per-cell schedules; `next` picks soonest-due across them. (F1)
- [DECISION] **One active review per concept with cancel-on-advance**, consume-on-pass via
  `review_id`. (F2)
- [DECISION] **Per-cell `consecutive_inadequate`.** (C7)
- [DECISION] **Recognition/assisted success sets `needs_reverification`** on that cell. (C2)

**Mastery gate & demotion (resolves the open questions with prior art):**
- [DECISION] **Peak reaches a rung only on ≥2 unaided successes including ≥1 `delayed`.** This is
  the integer-native, sparse-data-safe version of BKT's P(mastery)≥0.95 (a lone correct answer is
  never mastery because of p(guess)) and finally enforces the §5.7 invariant in code. (C-2/C4)
- [DECISION] **Adopt Khan Academy's explicit demotion table** as the default `current_frontier`
  reducer (mastered→proficient→familiar on miss). It's the simplest proven fix for DEFECT-1; don't
  over-build past it.
- [DECISION] **ALEKS "assess only at the fringe."** `current_frontier` = outer fringe (ready to
  learn), `peak` ≈ inner fringe; never test what's deep-known or far-out-of-reach. This is the
  principled form of the queue-inclusion filter. The hand-authored `prereqs` graph is the correct
  poor-man's substitute for ALEKS's population-mined knowledge space.

**Scheduler:**
- [DECISION] Keep the `[1,3,7,14,30]` ladder as a **labeled heuristic** (we can't fit FSRS on one
  learner), but adopt FSRS *conceptually*: multiplicative stability growth (no SM-2 "ease hell"),
  and a **desired-retention knob** (0.85–0.90 sweet spot; workload is nonlinear — 90→95% ~doubles
  burden). Map `retention_horizon` → desired-retention **qualitatively** (shorter horizon = tighter
  intervals). [DON'T] Do NOT attach a 0.85–0.90 number as a control target — it's a *predicted*
  probability from a model fitted on 500M reviews, which we cannot compute; using it as an
  *observed* success target re-imports the killed 0.6–0.85 band.
- [DECISION] First test same/next-day is a **learning event that does not enter the durable queue**
  (already reconciled; keep).

**Data-layer fixes:** delete/export/archive commands (O-9, privacy); JSONL partial-line tolerance
(skip a trailing corrupt line, `:97`); a topic-resolver for "let's continue" (most-recent /
fuzzy); fuzzy-duplicate warning at `concept add` (E1 — `resolve` is a soft pre-step today).

## 7. Honesty / grading mechanism (code layer D)

- [DECISION] **Make criteria load-bearing:** the reducer *reads* `met_criteria`; `outcome` cannot
  exceed `partial` unless load-bearing criteria are met. (Fixes C1.)
- [DECISION] **`recognition_only` must be positively asserted to promote; its default must not
  credit peak.** (Fixes the failure-safe-default-points-the-wrong-way bug.)
- [DECISION] **Scoped live adversarial re-grade at promotion** (§2 lever 2): capture the learner's
  raw production verbatim only for promotion-to-independent/transfer; one cold-context re-grade
  before the write.
- [DECISION] **Content grounding (Bastani guardrail b):** checkable topics → ground the tutor in a
  reference solution before it grades; uncheckable topics → mark evidence provenance
  "tutor-judged, ungrounded" and **never promote to transfer on it alone** (else the tutor can
  teach a wrong model and certify the learner "mastered" a falsehood — G-3, currently unmitigated).
- [DECISION] **SuperMemo Minimum Information Principle as prompt-authoring rules** for the tutor:
  atomic, unambiguous, "don't test what isn't understood." Since the LLM authors the retrieval
  prompts, a compound/ambiguous question produces a **false failure → wrong demotion → wasted
  pivot**; MIP keeps outcomes clean upstream of the reducer.
- [DECISION] **Report "reliable now," never peak** (words, not a %): highest rung with a recent
  unaided non-recognition success within horizon; peak is audit-only. (Fixes D5.)

## 8. Failure-mode mitigations (layer E)

- **Gaming/crutch detector (Baker) — the biggest ITS lesson we're ignoring.** Record repeated
  answer-extraction / hint-abuse / paste as a **first-class signal**, not just an `assistance`
  value, and reflect it back to the learner (visualization interventions measurably reduce future
  gaming). Also globally **down-weight text-channel `independent` evidence** — [FACT] a text chat
  fundamentally cannot verify the human produced the answer (G-4), so favor novel-transfer items,
  reasoning-not-answer, and delayed re-probes. This is a systematic ceiling on evidence quality,
  not an edge case.
- **Leech policy + hard queue cap — do NOT defer.** [FACT] Review debt ("card mountain") is the #1
  SRS abandonment cause. Our rung-4 graceful-defer is a leech policy (keep it), and the inclusion
  filter helps, but a **hard active-queue cap + explicit leech→suspend/reformulate** should ship,
  not defer.
- **Privacy:** minimal-non-sensitive check on `observation`; allow opaque topic ids (the shared
  `index.json` aggregates titles like "managing my depression"); store consent+scope+date in the
  contract; implement delete/export.
- **Recovery reliability ≠ file completeness.** [FACT] After compaction the flattering summary sits
  in context reading as authoritative; consulting files is a deliberate call against a strong prior.
  Mitigate with the SessionStart hook + `next` self-labeling its output authoritative + custom
  compaction instructions that preserve open gaps / failed representations / due reviews verbatim.

## 9. Evaluation (layer F — the meta-gap nobody owned)

[DECISION] Three harnesses:
1. **Trigger eval** (§4) — under/over-fire on implicit intent.
2. **Black-box file-only recovery test** — Agent A writes; delete A's conversation; Agent B with
   only skill+store recovers goal/frontier, avoids a failed representation, invents nothing. (Have
   a first version; keep/extend.)
3. **[DECISION] Calibration test — the one test that checks *teaching*, not mechanism.** Simulate a
   learner with a *known ground-truth knowledge state*, run the tutor, and measure whether recorded
   `peak/current` matches ground truth (a Brier-style calibration on the tutor's own grading).
   Without this we are optimizing an unvalidated proxy — every other test checks the machine, not
   whether the machine tracks reality. [DECISION] Also adopt **LearnLM's five principles**
   (cognitive load / active learning / metacognition / curiosity / adaptivity) as a review rubric.

## 10. Prior-art ledger (adopt / avoid)

ADOPT: Khan demotion table (fixes DEFECT-1, proven); BKT "N consecutive unaided successes" as the
mastery gate (not a success-rate band); ALEKS fringe rule; FSRS DSR framing + desired-retention
knob (conceptually); SuperMemo MIP as prompt rules; Bastani answer-grounding; Baker gaming
detector + reflect-back; leech policy + queue cap; LearnLM rubric; MemGPT/Letta Human-vs-Persona
split (validates learner-state vs skill-policy separation) — but keep the **evidence ledger out of
LLM self-editing** (machine-reduced only; reserve free editing for the human-readable contract);
Generative-Agents **importance×recency** weighting on what the snapshot surfaces post-compaction.

[DON'T]:
- Sell or design to **Bloom's 2σ** — it doesn't replicate (~0.5σ; the gap was partly a 90%-vs-80%
  mastery-threshold artifact). Import the mechanisms (mastery gate + immediate specific feedback),
  never the number.
- Any **opaque continuous "mastery %"** or ML tracer at runtime — DKT fluctuates wildly and is
  uninterpretable; simple models beat it. Our integer-control stance is correct prior art; don't
  backslide.
- **Fitted statistical models on one learner** (BKT params, DKT nets, KST spaces need population
  data) — use the prereq graph + rule heuristics.
- Trusting a **warm tutor's self-reported outcome** — sycophancy is high and specifically harms
  novices; a reducer downstream of a polluted `met_criteria` can't save you (→ §2 lever 2).
- **Unverifiable citations:** two prior-art arXiv IDs (`2603.*`, `2606.*`) postdate the Jan-2026
  knowledge cutoff and could not be verified — do not lean the design on them. The load-bearing
  stances (KT-interpretability, sycophancy, crutch effect) stand on verifiable pre-cutoff work
  (Corbett & Anderson 1995; Piech 2015; Sharma et al. ICLR 2024; Bastani et al. 2024; Baker et al.).

## 11. Explicitly deferred-but-known

- **[DEFER] Curriculum decomposition / sequencing (G-1) — the biggest gap.** The system is
  *reactive*: it tracks concepts after they're taught but has no method to decompose "teach me
  statistics" into a concept sequence (`roadmap` is manual; `next` has no "introduce first"
  branch). A teaching skill with no syllabus-building method teaches whatever the learner asks in
  whatever order — the exact failure a coach should fix. Not solved here; must not be pretended
  solved. Candidate: LLM-proposes-roadmap → user-approves → stored as the prereq graph.
- **[DEFER] Longitudinal motivation / returning-after-absence (G-5).** The system tracks knowledge,
  not the learner's evolving goals/motivation; a learner returning to a pile of overdue reviews +
  guilt is where real learners quit. Larger than the queue-cap.
- **[DEFER]** FSRS fitting / any per-user statistical model (no data); multi-device sync + file
  locking (single-user local default); schema migration (no production data → bump straight to
  v-next); per-answer grader fan-out (replaced by the scoped promotion-only re-grade);
  population-mined knowledge spaces (use hand-authored prereqs); interleaving *review* across
  concepts even while the teaching frontier stays single (G-7) — do in the scheduler, cheap.

## 12. Revised implementation order

Layered by the spine (enforce first, teach second, evaluate throughout):

1. **Code enforcement fixes** (closes the confirmed over-crediting + scheduler holes): reducer
   reads `met_criteria` and gates `outcome`; peak requires ≥2 unaided incl ≥1 delayed; Khan
   demotion table; per-cell plateau + per-cell schedule; schedule the mastered cell not the
   frontier; one-active-review + cancel-on-advance; recognition sets needs_reverification; JSONL
   partial-line tolerance; delete/export/archive.
2. **SKILL.md re-architecture:** split description/when_to_use + trigger-eval; move honesty
   invariants + system-of-record rule into the body; add the hard route gate; add escalation
   (R14) + explicit-signal override (R10) + novice floor (R3) + reflection-as-distinct-phase (R21)
   + "never promise a reminder"; fix the 1-D-ladder vs 3-axis mismatch (C-5).
3. **Recovery:** settings/plugin `SessionStart` hook + top-of-body `!`next`` injection + root
   convention; custom compaction instructions preserving gaps/failed-reps/due verbatim.
4. **Honesty extras:** scoped adversarial re-grade at promotion; content-grounding for checkable
   topics; MIP prompt rules; gaming detector.
5. **Evaluation:** trigger-eval, black-box recovery, **calibration test** with a simulated learner.
6. Then: leech/queue-cap; importance×recency snapshot weighting; interleaved review queue.

## 13. Draft → stable exit criteria (updated)

Never reports peak as current ability; peak requires unaided+delayed evidence; review queue
completes/reschedules/clears and re-tests the *mastered* rung with growing spacing; post-compaction
never repeats a failed move and reloads from files not summary; every mastery conclusion traces to
evidence and survives the offline audit; criteria actually gate outcome; the router never obstructs
a quick ask; the trigger-eval passes on implicit intent; and the calibration test shows recorded
mastery correlates with ground truth. Until then, **Draft PR #1 stays Draft.**

## Appendix A — the 25 turn-level WHEN/THEN rules & anti-patterns

Full rule set (R1–R25) and the anti-pattern→counter-move table live in the workflow output at
`scratchpad/analysis/pedagogy-as-behavior.md`; port them verbatim into SKILL.md/tutoring-protocol
during step 2. Highest-leverage five are named in §5. Genuine tensions and their arbitration
(productive-struggle vs quit-out; problem-first vs novice-overload; elicit-first vs answer-now;
demote vs preserve-history; warmth vs honest-grading; space-it vs test-soon) are resolved there and
folded into §5–7 above.

## Appendix B — grounding

Verified against `skill/learning-coach/scripts/learner_state.py` and `SKILL.md` (line refs inline).
Full analyst outputs: `scratchpad/analysis/{pedagogy-as-behavior,skill-mechanics,
agent-capabilities-limits,execution-failure-modes,prior-art,critique}.md`. Prior design:
`research/v2-redesign-proposal.md` (§10 convergence still holds). Skill/hook/subagent/scheduled-task
mechanics: code.claude.com/docs; skill-authoring: agentskills.io.
