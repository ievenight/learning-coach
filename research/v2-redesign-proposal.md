# Learning Coach v2 — Redesign Proposal & Review Handoff

Generated: 2026-07-14 (Asia/Taipei)
Author: analysis pass (Claude). Status: **design proposal + confirmed defects**, not implemented.

## 0. How to use this document

This is a handoff for a **second agent to co-review**. It captures both the
*reasoning method* and the *conclusions*, so you can challenge the thinking, not
just the output.

Three kinds of claim are kept strictly separate — please preserve that separation
in your review:

- **[DEFECT]** — a defect in the current v2 code, **empirically confirmed** by
  running the CLI (repro commands in Appendix A). Treat as fact; verify the repro.
- **[PROPOSAL]** — a design recommendation. Argue with it.
- **[OPEN]** — an unresolved decision that needs a human or a judgment call.

What I want from the reviewer:
1. Try to *refute* each [DEFECT] by reproducing it. Report any that don't hold.
2. Attack the [PROPOSAL]s — especially the scheduler numbers and the
   dual-strength model. Where is this over-engineered? Where is it too naive?
3. Answer or sharpen the [OPEN] questions in §8.
4. Flag any place where a runtime rule overstates a podcast source (see §2 guardrails).

Do **not** implement anything yet. This is a review, then a decision, then code.

## 1. Scope & method

Goal (from the user, paraphrased): make the learning-coach skill behave like a
*real teacher* — cooperate with users without drifting, know what the learner
learned and their current mastery, re-test them sensibly over time, and not
"forget" after the LLM context window is compacted; design the offline/reusable
state properly.

Method:
- Read all six source transcripts in full (~167k words) via parallel agents, each
  instructed to extract only claims that *change a tutor's observable action* and
  to flag overstatement. Sources: Gabriel Petersson (AI self-learning), Andy
  Matuschak (memory systems), David Eagleman (memory/plasticity), Andrew Huberman
  (optimal studying), Michael Kilgard (brain plasticity), Cal Newport (focus).
- Read the full v2 candidate: `SKILL.md`, `tutoring-protocol.md`,
  `state-protocol.md`, `toolkit.md`, `scripts/learner_state.py`, `evals/`,
  `tests/`, and the two prior research notes.
- Deep-read the Deli AutoResearch framework
  (https://victorchen96.github.io/auto_research/framework.html#fullmd),
  focusing on its **quantitative control mechanisms** (counters, thresholds,
  liveness), not its topology.
- **Empirically probed** the state machine (`learner_state.py`) to confirm
  suspected defects rather than inferring from code (Appendix A).

## 2. Source synthesis — what the six transcripts actually converge on

Only claims that would change a tutor's next observable move. High agreement
across sources unless noted.

1. **Testing/retrieval is the strongest tool, and it is itself a learning event,
   not just assessment.** All six. Huberman headline; Kilgard "most of learning is
   intervening in the forgetting process"; Newport active recall "the only way";
   Matuschak adjunct questions; Eagleman predict-then-reveal; Petersson explain-back.
2. **Learning = offsetting forgetting.** Huberman's frame; Kilgard endorses.
   *Implication: a "mastered" mark is meaningless unless re-tested over time.* This
   is the load-bearing principle for the whole redesign.
3. **Fluency/confidence ≠ mastery (illusion of competence).** Huberman (4×-reread
   group most confident, worst performing); Petersson ("click" feeling is
   unreliable); Matuschak (engagement ≠ understanding). **v2's policy layer gets
   this right.**
4. **Elicit before reveal; productive struggle is the signal.** Eagleman
   (prediction-error releases ACh locally where the model breaks); Kilgard
   (attention gates plasticity; passive exposure fails); Newport (deliberate
   practice = opposite of flow); Matuschak (active reading = Q&A).
5. **Difficulty at the individual edge; escalate on mastery, don't grind the easy.**
   Eagleman "frustrating but achievable"; Kilgard "reward the top 10% of *current*
   ability, meet them where they are," inverted-U; Newport "+20%"; Matuschak
   scaffold-and-fade. *This requires per-learner state at the edge — it is itself
   the justification for persistence.*
6. **Feedback must be immediate, specific, contingent.** Kilgard (eligibility trace
   ~2s; "reward everything = reward nothing").
7. **Spaced repetition is a biological requirement, not optional.** Kilgard
   ("required to change the brain"); Huberman (test soon, then space); Matuschak
   (out-of-band review only for what life won't reinforce).
8. **Reflection/consolidation is a distinct phase; don't cram-then-quit.** Kilgard
   (reflection rewires; phones occlude it); Newport (shutdown ritual); Eagleman (sleep).
9. **Serve the learner's real goal / problem-first.** Matuschak (misalignment =
   misery mislabeled as desirable difficulty); Petersson (top-down from a real problem).
10. **Don't assume motivation; reduce friction + use accountability.** Matuschak
    (uses Beeminder on himself); Petersson (a year to build the ask-habit). A
    cross-session coach is itself a mild accountability mechanism.
11. **Interleave and vary context for transfer.** Matuschak, Huberman, Newport, Eagleman.
12. **Don't be completionist.** Matuschak "skip > quit"; Petersson recurse only into
    load-bearing prerequisites.

Two Matuschak specifics worth calling out (strongest source on memory systems):
- **Two-tier mastery (ACT-R compilation):** "can retrieve the fact" ≠ "can deploy
  it in combination/application." Reading alone won't compile the second.
- **Queue-inclusion rule:** only schedule material daily life/work won't naturally
  reinforce — "too early to have consistent practice" or "not firmly tethered in
  your life." Things you use daily should not occupy the review queue.

### Overstatement guardrails (things to keep OUT of runtime)

The agents independently flagged these; v2's research layer already excludes most.
Reviewer should check nothing crept back in:
- Huberman's specific numbers (50% forgetting reduction; 20–30× hippocampal replay)
  are loosely sourced — keep the *behavior*, drop the *number*.
- All neurotransmitter / brain-region mechanism = decoration, no action delta.
- Petersson is n=1 survivorship; his "click feeling = mastery" directly contradicts
  the illusion-of-competence literature — v2 correctly reframes to unaided delayed
  retrieval.
- Newport/Petersson productivity figures (4–4.5 hr ceiling, "3 days vs 6 years") are
  personal philosophy, not evidence.

**Verdict on v2's research layer:** faithful and well-scoped. The problem is the
implementation, below.

## 3. v2 as-built — what it gets right, and the confirmed defects

### What v2 gets right
- Teach/Answer/Do mode routing (both forward tests pass; matches source finding #3,
  #9 and the "don't obstruct" imperative).
- Evidence-driven (not confidence-driven) mastery *policy*.
- Storage substrate: append-only `evidence.jsonl`, atomic snapshot writes
  (temp+replace), path-safe topic regex, compaction-recovery protocol.
- Correctly borrows from AutoResearch the idea that *conversation is disposable and
  the external store is the system of record.*

### Confirmed defects (see Appendix A for repro)

- **[DEFECT-1] Mastery status is a monotonic high-water-mark; it never demotes.**
  `learner_state.py:128` only promotes. A learner who hit `transfer` once and then
  fails repeatedly still reads `transfer`. This is the exact "overstates mastery"
  risk the original handoff flagged as a hypothesis — now confirmed in code.
  `v2-agent-patterns.md` §5 rule 3 says contradictory later evidence should lower
  the active state while preserving history; the code does not do this.

- **[DEFECT-2] `needs_review` reflects only the LAST event and can hide a miss.**
  `learner_state.py:130` overwrites the flag every iteration. After a failure, a
  single trivial success clears `needs_review`. Result: `status=transfer` +
  `needs_review=false` can coexist with a recent failure. The snapshot doesn't just
  overstate — it actively conceals the miss.

- **[DEFECT-3] `supersedes` is recorded but ignored by `rebuild()`.** The field is
  written (`command_record`) but `rebuild()` never reads it, so a "superseding"
  correction does not correct anything. `state-protocol.md` promises correction via
  superseding evidence; the engine ignores it.

- **[DEFECT-4] Review queue has no completion/removal.** Passing a due review by
  recording a successful evidence event leaves the queue item in place; `due` shows
  it forever. There is no `complete` command. The queue only grows.

Secondary gaps (design, not strictly bugs):
- **No scheduling logic at all.** `review --due` is a hand-typed date; nothing
  computes the next interval from outcomes. "How to re-test later" is entirely manual.
- **Roadmap/`current_position` never updated by any command** — so "progress" isn't
  tracked.
- Minor: `now()` is UTC but `due` uses local `date.today()` (midnight-boundary
  skew); no concurrency guard; `SCHEMA_VERSION` present but no migration; and
  `git diff --check` is NOT clean (EOF blank lines + trailing whitespace at
  `research/v2-agent-patterns.md:3`), contradicting the original handoff's claim
  that it passed.

## 4. Root-cause diagnosis

The sources are about **troughs** (forgetting); the v2 code records **peaks**
(best-ever achievement). One sentence:

> v2 stores only *storage strength* (monotonic, never drops) but uses it as if it
> were *retrieval strength* (what you can produce right now, which decays).

Every defect above is a symptom of this one mismatch. The fix is to model both, and
to make the scheduler watch the decaying one.

## 5. Proposed redesign

### 5.1 [PROPOSAL] Principled model: dual-strength memory

Adopt Bjork's two-component framing (the rigorous version of Huberman's "offset
forgetting"):
- **Storage strength** — monotonic, ~never lost. Keep as `peak_challenge` for
  history/audit.
- **Retrieval strength** — decays with time, jumps up on each *effortful* retrieval.
  This is what a teacher actually decides on, and what v2 lacks entirely.

Design consequence: a failure lowers the *current* state while `peak` preserves
history — no lying, no history erasure. Simultaneously fixes DEFECT-1 and -2.

Key operating insight (the scheduler's pivot): Huberman's "even 40–50% accuracy
beats rereading" + "challenging study is most effective" = **retrieval should be
tested when it's effortful-but-still-possible**, i.e. deliberately let retrieval
strength sag into a target band before re-testing. Testing too soon = no desirable
difficulty; too late = relearning. *Catching that window is the teacher's craft the
scheduler automates.*

### 5.2 [PROPOSAL] Data structure: a per-concept, per-challenge grid — integer-driven

A concept is not one enum. It is a grid (challenge type × its own strength/schedule).
Control variables are **discrete integers/enums** (auditable, in the AutoResearch
spirit); any float is a display-only *estimate*, clearly labeled, never read by the
algorithm. (Rationale: floats imply manufactured precision from sparse data —
Matuschak and Huberman both warn against this.)

```jsonc
// concept record
{
  "concept_id": "gamma-vs-delta",
  "label": "Gamma vs. Delta",
  "prereqs": ["delta-basics"],
  "peak_challenge": "transfer",       // storage strength: monotonic, audit only
  "current_frontier": "apply",        // the challenge the teacher should probe next
  "open_gap": "confuses gamma sign near expiry",
  "reinforced_by_life": false,        // Matuschak inclusion filter (§5.8)
  "confidence": { "learner_self_report": 0.9, "coach_estimate": 0.4 }, // isolated; never drives state
  "cells": {
    "recall":   { "reps_unaided": 3, "consecutive_inadequate": 0, "interval_idx": 4, "last_outcome": "success", "last_ts": "2026-07-14", "next_due": "2026-07-30", "recognition_only_cap": false, "strength_estimate": 0.72 },
    "explain":  { "reps_unaided": 2, "consecutive_inadequate": 1, "interval_idx": 3, "last_outcome": "partial", "last_ts": "2026-07-14", "next_due": "2026-07-21", "recognition_only_cap": false, "strength_estimate": 0.55 },
    "apply":    { "reps_unaided": 0, "consecutive_inadequate": 2, "interval_idx": 1, "last_outcome": "failure", "last_ts": "2026-07-14", "next_due": "2026-07-15", "recognition_only_cap": false, "strength_estimate": 0.20 },
    "transfer": { "reps_unaided": 0, "consecutive_inadequate": 0, "interval_idx": 0, "last_outcome": null, "last_ts": null, "next_due": null, "recognition_only_cap": false, "strength_estimate": null }
  }
}
```

Challenge ladder: `exposure → recall → explain → apply → transfer` (maps
exposed→...→transfer and Huberman's familiarity→recall→mastery→virtuosity, and
Matuschak's fact-vs-compilation two tiers).

`evidence.jsonl` stays append-only; add `recognition_only` (bool) and make
`supersedes` actually honored.

### 5.3 [PROPOSAL] The scheduler — with numbers

The engine for "how to re-test later." No universal constant (sources warn against
it); three adaptive signals instead.

**Signal 1 — target success band, not 100%.** Huberman: 40–50% errors still beat
rereading; challenging study is best. Target retrieval success band **0.6–0.85**:
- above band → too easy → lengthen interval OR raise challenge type
- in band → expand normally
- below band → shorten interval, drop challenge, and trigger a structural pivot (§5.4)

This one signal drives both *when* to test and *how hard* — matching Kilgard's
"reward the top 10% of current ability" and Eagleman's "frustrating but achievable."

**Signal 2 — interval ladder that stretches/contracts by outcome.** Seed ladder
(days): `L = [0, 1, 3, 7, 16, 35, 75]`. `L[0]=0` ⇒ **first test same/next day**
(Huberman's "hallmark" immediate-then-delayed finding).

```python
def schedule_next(cell, outcome, assistance, horizon_scale):
    if outcome == "success" and assistance == "none":
        cell.reps_unaided += 1
        cell.consecutive_inadequate = 0
        cell.interval_idx = min(cell.interval_idx + 1, len(L) - 1)   # success → stretch
    elif outcome in ("partial",) or (outcome == "success" and assistance != "none"):
        cell.consecutive_inadequate += 1                            # held, not rewarded
    else:  # failure — productive, not punished
        cell.consecutive_inadequate += 1
        cell.interval_idx = 1                                       # back to "tomorrow"
    cell.interval_idx = clamp(cell.interval_idx, 0, len(L) - 1)
    cell.next_due = today() + round(L[cell.interval_idx] * horizon_scale)
    return cell
```

**Signal 3 — retention horizon scales the whole ladder.** Cepeda 2006 (cited in
`v2-agent-patterns.md`): optimal spacing depends on the desired retention interval.
Add `retention_horizon` to the contract (exam in 3 weeks vs. lifelong skill) →
`horizon_scale`. Short horizon compresses the ladder; long horizon stretches it.

**Challenge escalation (the most teacher-like step).** When a cell is stable
(`reps_unaided >= 2` and `consecutive_inadequate == 0` and success in band), the
next probe **raises `current_frontier` one rung and resets `interval_idx` to a low
value** (a harder challenge is "new material" — low storage strength again), rather
than stretching the same question forever. `recall`→`explain`→`apply`→`transfer`→
long maintenance. **v2 has no escalation; once it records a transfer success it
sits at transfer permanently — the opposite of teaching.**

### 5.4 [PROPOSAL] Plateau detector + escalation ladder (AutoResearch `stale_count`)

The biggest transplant. Replace v2's prose "after two failures, pivot" with a real
counter (`consecutive_inadequate`, per cell) and a structured escalation ladder.
Note the 1:1 correspondence with AutoResearch's "≥2 change a *structural*
constraint, not tactical parameters":

```
consecutive_inadequate == 1  → tactical: one directional hint, same representation
consecutive_inadequate == 2  → STRUCTURAL pivot: switch to a representation NOT
                               previously tried (check interventions.jsonl, avoid
                               every result=no_progress), or expose a prerequisite,
                               or a concrete case / near-miss contrast.  (NOT synonyms)
consecutive_inadequate == 3  → reveal directly + worked example, then ask a small transfer
consecutive_inadequate == 4  → ESCALATE / GRACEFUL DEFER (AutoResearch "≥4 flag" +
                               "never abandon silently"): stop grinding; tell the
                               learner explicitly; record open_gap; hypothesize a
                               missing prerequisite or wrong-time/energy; defer to a
                               future session or back up to a prerequisite concept.
```

The 4th rung is the point: the round cap ends in a *graceful deferral*, not "keep
trying." This protects both against Socratic obstruction and against silent
give-up — directly serving "cooperate, don't drift."

**Per-session hard cap** (AutoResearch "15 rounds / 30 min"): a single concept gets
`≤ 3` elicitation rounds per session, then defer regardless of the plateau count
(Newport/Kilgard: fatigue kills plasticity; Matuschak: grinding causes quit-out).

These counters MUST be persisted in the cell so a post-compaction agent keeps
counting instead of re-grinding from zero.

### 5.5 [PROPOSAL] Execution/evaluation separation — the adversarial grader

AutoResearch: "the agent doing the work does not judge its own progress; stall
determination is made by the orchestration layer on quantitative metrics." Applied
to the LLM tutor's specific failure mode (sycophancy / over-crediting):

- **Tutor role** (in conversation): teaches, elicits, gives feedback, and **only
  records raw evidence events** (concept, challenge, outcome, assistance,
  recognition_only, observation). May be warm/encouraging. **Has no authority to set
  status/strength.**
- **Grader role** (separate pass; reads ONLY `evidence.jsonl` + honesty invariants;
  never sees the warm conversation): computes state, promotes/demotes, updates
  schedule. Because it can't see "you're doing great," it can't be sycophantic.

This reconceives `rebuild()` from a passive aggregator into an *adversarial grader*.
Add AutoResearch Pattern D (independent audit of the evidence chain) as a runnable
QA: **every `mastered` must be backed by a real unaided + delayed + different-context
event; if not, demote.** This is directly unit-testable.

Companion (AutoResearch "verify every 20, never batch"): honesty invariants run **on
every state write**, not at session end — never accumulate unverified mastery claims.

### 5.6 [PROPOSAL] Session state machine + compaction recovery

"What to do next" must be a pure function of files (contract + snapshot + due queue +
interventions), never of chat history.

```
on_session_start(topic):
    contract, snapshot, due = load(topic)         # only these; not old chat
    # AutoResearch "report-alive first": trust timestamps, not labels
    for cell in snapshot.cells:
        if now - cell.last_ts > retention_horizon(cell):
            cell.status = "needs_reverification"  # expired label is untrusted
    if due has overdue items:
        action = highest-priority due probe (most overdue; tie → most foundational)
    elif snapshot.checkpoint.next_move:
        action = execute saved next_move
    else:
        action = advance roadmap to next current_frontier
    state the reconstructed position in one line, invite correction, then act
```

Anti-repeat-explanation (teacher "I've tried that on you, it didn't land"): when a
cell needs a pivot, choose a representation NOT already marked `no_progress` in
`interventions.jsonl`; if all tried, fall back to a prerequisite (structural pivot).

### 5.7 [PROPOSAL] Honesty invariants (encode "a teacher who doesn't self-deceive")

Enforced on every state write (host hook if available, else in the close routine):
1. **Recognition cap:** evidence with `recognition_only=true` can never push a cell
   past `assisted` (Huberman: MC tests familiarity, not recall).
2. **Confidence isolation:** self-report only enters `confidence`, never strength.
3. **Expiry demotion:** any "mastered" evidence older than its retention horizon →
   `needs_reverification`; never reported as current ability.
4. **`mastered` definition:** requires unaided + delayed + materially-different
   context (transfer) — all three.
5. **`supersedes` honored** in rebuild (fixes DEFECT-3).

### 5.8 [PROPOSAL] Queue inclusion filter (Matuschak)

Don't schedule what life reinforces. Gate on enqueue (also fixes DEFECT-4's
"queue only grows" by making enqueue selective and letting a passed review clear/
reschedule its cell):

```python
def should_schedule(concept):
    if concept.reinforced_by_life:            return False   # life is the SRS
    if concept.current_frontier == "exposure": return False  # only seen, not attempted
    return True
```

### 5.9 [PROPOSAL] Offline / reuse: three scopes (from `v2-agent-patterns.md` §8)

Only two of three scopes are implemented. The missing middle is the reusable asset:
- **Skill policy** (public, versioned): decision flow, state protocol, privacy. *Exists.*
- **Topic kit** (portable, optional, NO learner data): roadmap, concept graph, item
  templates, transfer tasks. **Missing** — this is what another learner reuses.
- **Learner state** (private, exportable): contract, evidence, snapshot, queue. *Exists.*

## 6. AutoResearch transplant — summary + explicit rejections

**Adopt (the quantitative control discipline):**

| AutoResearch mechanism | Its number | Our mapping | Our number |
|---|---|---|---|
| `stale_count` + escalation | 0-new→+1; ≥2 structural pivot; ≥4 flag; 3 nudges→stop | per-cell `consecutive_inadequate` + ladder | §5.4 (1/2/3/4) |
| execution/evaluation separation | worker never self-judges | tutor records; separate grader promotes | §5.5 |
| `last_seen` / report-alive after compaction | heartbeat>2h; interval×3 | decay clock; recompute status from timestamps | §5.6 |
| round cap | 15 rounds / 30 min | per concept per session | ≤3 rounds |
| validate between iterations; verify every 20, never batch | — | retrieval check between moves; invariants on every write | §5.5/5.7 |
| integer counters over opaque scores | discrete metrics | control = integers; float = display only | §5.2 |

**Reject (do NOT import — a learner is a participant, not a stalled headless worker):**
- Zero-interaction / never-end-on-a-question / no-confirmation. The tutor loop *is*
  ask-then-wait. Invert it.
- L0/L1/L2 watchdog + hourly cron + unattended patrol / nudging the user. The decay
  clock is for *state*, not for pinging the user.
- Firing N parallel agents to refute a single learner answer — over-engineered; a
  single grader pass suffices.
- Its self-rated scores (8.0/10 etc.) — it self-flags these as non-external. Use
  real multi-turn forward tests instead.

## 7. Traceability — every proposed rule maps to a source

| Design rule | Primary source(s) |
|---|---|
| Dual-strength; test in effortful band | Huberman (offset forgetting; 40–50% ok); Bjork frame |
| First test same/next day (`L[0]=0`) | Huberman (immediate-then-delayed hallmark) |
| Success → stretch interval | Huberman (perf ∝ #tests) |
| Failure → reset, not punish | Huberman (errors productive) |
| Horizon scales ladder | Cepeda 2006 (in v2-agent-patterns) |
| Challenge escalation recall→transfer | Huberman ladder; Matuschak ACT-R; Eagleman remix |
| Target-band difficulty | Kilgard (top-10% current ability); Eagleman (frustrating-but-achievable); Newport (+20%) |
| Structural pivot at plateau, not synonyms | v2 SKILL + AutoResearch (structural not tactical); Matuschak (endless rephrasing fails) |
| Graceful defer at rung 4 | AutoResearch (≥4 flag; never abandon silently); Matuschak (skip>quit) |
| Grader ≠ tutor | AutoResearch (exec/eval separation); Huberman/Matuschak (fluency≠mastery) |
| Recognition cap | Huberman (MC = familiarity) |
| Recompute status from timestamps post-compaction | AutoResearch (report-alive); Huberman (offset forgetting) |
| Queue inclusion filter | Matuschak (schedule only what life won't reinforce) |
| Per-session round cap | Newport/Kilgard (fatigue); Matuschak (quit-out) |
| Preferred-representation persistence | Petersson (default style ≠ personal learning style) |

## 8. [OPEN] Questions for the reviewer / decisions to make

1. **Interval ladder values.** Is `[0,1,3,7,16,35,75]` a sane seed? Should it be
   per-challenge (transfer probably needs a different curve than recall)?
2. **Success band 0.6–0.85.** Defensible? Over sparse data (2–3 attempts) a "success
   rate" is noisy — do we need a minimum-N before the band drives decisions, or a
   Bayesian prior? Or drop the band and drive purely off `consecutive_inadequate`?
3. **Float vs. integer.** I argue control should be integer-only and `strength` is
   display-only. Counter-argument: a decaying float is the natural way to express
   "how due is this." Which wins?
4. **`retention_horizon` function.** How does horizon → `horizon_scale`? Linear?
   Capped? What's the default when the learner never states a horizon?
5. **Grader as separate agent vs. deterministic function.** Is a full separate LLM
   pass worth it, or is a deterministic `rebuild()` with honesty invariants enough
   to prevent over-crediting? (Cheaper, more auditable, but less able to judge
   nuance in an observation string.)
6. **Per-challenge vs. per-concept scheduling.** The grid multiplies state ~5×. Is
   that worth it, or should we schedule at concept granularity and just record the
   challenge type on evidence?
7. **Concurrency & migration.** Still unaddressed. Single-user assumption OK for v1
   of this redesign? Do we ship a v1→v2 schema migration now or later?
8. **Where does difficulty calibration live** — in the scheduler (band), in the
   tutor's prompt, or both? Risk of the two disagreeing.

## 9. Concrete next step (proposed)

Prototype branch of `learner_state.py`:
1. Rewrite `rebuild()` as an integer-driven **grader**: per-cell state, honor
   `supersedes`, separate `peak`/`current`, run honesty invariants, mastered audit.
2. Add `schedule_next` (§5.3) + queue completion (fixes DEFECT-4).
3. Add `consecutive_inadequate` + the escalation ladder; enforce "avoid tried
   representations."
4. Add a `next` command: pure function over files → one concrete action (§5.6).
5. Contract gains `retention_horizon`, `reinforced_by_life`; bump `SCHEMA_VERSION`
   to 2 with a migration.
6. Multi-turn unit tests: first-test-same-day; plateau→2 structural pivot; plateau→4
   graceful defer; `reps_unaided≥2`→escalate challenge; expiry demotion; mastered
   audit; compaction recovery from files only.

Do not start coding until the [OPEN] questions in §8 are resolved.

## 10. Post-review convergence (Codex + Claude) — the agreed v1 scope

A second agent (Codex) independently reviewed this proposal. Both reviews **converged
on the diagnosis** (all four defects confirmed; "peak ≠ current capability" is the
root idea). The disagreements were about *how much machinery* to build. Recorded
decisions below supersede the heavier parts of §5 for the first implementation.

**Corrections to this proposal (accepted):**
- §4 over-attributes: only DEFECT-1/2 stem from peak/current confusion. DEFECT-3
  (correction semantics) and DEFECT-4 (queue lifecycle) are ordinary state-machine
  incompleteness — no memory theory required.
- §5.3 Signal-1 (success band 0.6–0.85) is **dropped** — logically unsound: "40–50%
  errors beat rereading" does not imply an optimal target error rate, and 1–3
  evidence points per cell are not a rate. Drive scheduling off discrete outcomes.
- §5.2 `strength_estimate` float is **dropped** (even as display — invites fake
  "82% mastery"). Control is integers/enums only.
- §5.5 runtime LLM grader is **dropped**: the raw event fields (outcome, assistance,
  challenge_type, observation) are still judged by the tutor, so a separate grader
  computes on already-polluted data. Replaced by **criteria-based evidence** (below)
  + a **deterministic reducer** + auditable invariants. LLM audit is offline QA only.
- §5.2 full 5-cell grid → **sparse `capabilities`** (materialize only tested
  challenges). A failure demotes only the affected dimension, not all of them.
- §5.3 ladder `[0,1,3,7,16,35,75]` → simpler `1→3→7→14→30`, explicitly a
  **heuristic**, user/topic-kit overridable; store a `due_window` (earliest/latest),
  not an exact date. Same-session immediate retrieval does not enter the durable queue.
- §5.4 collapse to 3 rungs (hint → structural pivot → reveal/defer); do not
  mechanically force a 4th; honor an explicit "keep going."
- §2 synthesis prose tightened: "all six," "biological requirement," "strongest tool"
  are too tidy. "Learning = offsetting forgetting" is Huberman/Kilgard framing, not a
  six-source consensus. Keep behaviors; do not turn podcast phrasing into hard params.

**What survives (both agents agree):** peak/current separation via
`peak_challenge + current_frontier + sparse capabilities`; deterministic reducer;
honesty invariants (§5.7); plateau counter persisted (§5.4); pure-file `next`
command (§5.6); queue inclusion filter (§5.8).

**New must-haves Codex surfaced (accepted, higher priority than scheduler polish):**
1. **User operation loop + NL interface** — create/resume/record/checkpoint/archive/
   export/delete, each with stable natural-language triggers. Internals are useless if
   the LLM doesn't know which topic to read or when to create/end one.
2. **No proactive reminders.** A passive Skill cannot wake the user. Runtime must
   distinguish passive re-test (check due on next open), active reminder (needs host
   automation + consent), offline plan (dates only). Never promise "I'll test you in 3 days."
3. **Concept identity** — stable `id` + `label` + `aliases` + `prerequisites` +
   `merge` command; forbid creating a new id without checking existing ones. Prevents
   evidence fragmenting across `gamma-vs-delta` / `delta-gamma-difference` / etc.
4. **Criteria-based evidence** — event carries `challenge_type` + `criteria` (list) +
   `met_criteria` (bools) + short non-sensitive summary. This, not a separate grader,
   is the real antidote to tutor over-crediting.
5. **Real black-box recovery test** — Agent A writes state; delete A's conversation;
   Agent B gets only Skill + learner state; assert B knows the goal + current frontier,
   doesn't repeat a failed explanation, picks the right due review, invents no unsaved context.
6. **Progress = capability roadmap**, not chapter position (`{capability, state}` list).
7. **`supersedes` strict semantics** — same concept only; no cycles; no dangling
   target; superseded events excluded from snapshot but retained; keep
   `superseded_event_ids` for audit.
8. **Don't show a mastery score.** Show peak evidence / latest evidence / reliable-now
   / next step / review status in words.

**Agreed implementation order (do NOT keep writing design docs):**
1. Fix the four confirmed defects.
2. `status` → `peak_challenge + sparse capabilities + current_frontier`;
   `needs_reverification` cleared only by same-or-higher-level new evidence.
3. Concept identity + review completion (`review_id`, consume+reschedule) + evidence criteria.
4. `consecutive_inadequate` + representation history.
5. Deterministic pure-file `next` command.
6. Black-box file-only recovery test.
7. Then the simple heuristic scheduler.
8. Use it across several days of a real learning track; check the state actually helps the next session.

**Deferred (revisit only after the above ships with real usage):** success-rate band,
strength float, runtime LLM grader, full 5-cell matrix, topic kit, background reminders,
concurrency control, complex migration (no production learner data yet → bump straight
to schema v2). Also still-open: `now()` UTC vs local-date skew in `due` (Appendix A note).

**Draft→stable exit criteria (both agents):** never reports peak as current ability;
review queue can complete/reschedule/clear; post-compaction it doesn't repeat a failed
teaching move; every mastery conclusion traces to evidence; quick Q&A and execution are
not blocked by the teaching machinery. Until then, **Draft PR #1 stays Draft.**

## Appendix A — Reproducible defect probes

Run against `skill/learning-coach/scripts/learner_state.py`:

```bash
S=skill/learning-coach/scripts/learner_state.py
python3 $S init --root /tmp/lc --topic t --title T --goal G
# DEFECT-1: transfer success then later recall FAILURE — status should demote, doesn't
python3 $S record --root /tmp/lc --topic t --concept c --challenge transfer --outcome success --assistance none --delay delayed --observation x
python3 $S record --root /tmp/lc --topic t --concept c --challenge recall  --outcome failure --assistance none --observation y
# → snapshot: status=transfer, needs_review=true
# DEFECT-2: a trivial recall success now CLEARS needs_review despite the failure in history
python3 $S record --root /tmp/lc --topic t --concept c --challenge recall  --outcome success --assistance none --observation z
# → snapshot: status=transfer, needs_review=false   (miss concealed)
# DEFECT-3: supersedes recorded but rebuild ignores it → status unchanged
# DEFECT-4: add a review, then "pass" it by recording success → review-queue still has the item
```

Observed results (2026-07-14): all four confirmed. Code anchors: promotion-only at
`learner_state.py:128`; `needs_review` last-event overwrite at `:130`; `rebuild()`
never reads `supersedes` (`:102-149`); no completion path in `command_review`
(`:215-233`).

## Appendix B — Source pointers

Transcripts: `01-sources/0{1..6}-*.txt` (design-source material, not peer-reviewed).
Prior research notes (still valid, this doc extends them):
`research/v2-source-synthesis.md`, `research/v2-agent-patterns.md`.
AutoResearch framework: https://victorchen96.github.io/auto_research/framework.html#fullmd
(first-party protocol; its own validation is self-rated and in-framework).
