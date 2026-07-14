# Learner State Protocol

Use this protocol only for an approved multi-session learning track.

## Contents

1. Storage rules
2. Durable layers
3. Mastery evidence
4. Read and write lifecycle
5. Compaction recovery
6. Offline portability

## 1. Storage rules

Choose storage in this order:

1. an inspectable persistent-memory system already provided by the host;
2. a user-approved workspace directory such as .learning-coach/;
3. another user-selected local directory.

Do not store mutable learner state inside the installed skill. Do not assume a
specific vendor path. Ask once when a track is created; subsequent updates inside
that track inherit the approval.

## 2. Durable layers

The bundled script creates:

~~~text
learner-state/
  index.json
  topics/
    topic-id/
      contract.json
      evidence.jsonl
      interventions.jsonl
      review-queue.json
      snapshot.json
~~~

- contract.json stores the goal, desired depth, constraints, and roadmap.
- evidence.jsonl is the append-only source of mastery evidence.
- interventions.jsonl prevents repeating an ineffective explanation after compact.
- review-queue.json stores only high-value due checks.
- snapshot.json is a compact, rebuildable view for session startup.

Correct mistakes by appending superseding evidence. Do not silently rewrite the
history. Keep summaries short and never store verbatim chat by default.

## 3. Mastery evidence

Use exposed, assisted, independent, delayed, and transfer.

Evidence records:

- concept identifier;
- challenge type: recall, explain, discriminate, apply, or transfer;
- immediate or delayed timing;
- outcome: success, partial, failure, or not_attempted;
- assistance: none, prompt, hint, or worked_example;
- a minimal non-sensitive observation.

Only evidence moves mastery. Confidence and conversational fluency do not.

## 4. Read and write lifecycle

At session start:

1. inspect the index;
2. load only the relevant contract, snapshot, and due reviews;
3. recover the saved next move;
4. correct stale state using current evidence.

During the session, append only meaningful events: a diagnostic attempt, verified
retrieval, application, material misconception, or structural intervention. Do
not write every turn.

At session end, rebuild the snapshot, save a concise checkpoint, and keep the due
queue small.

## 5. Compaction recovery

After compact, handoff, a fresh session, or suspected context loss:

1. reload the topic contract and snapshot;
2. inspect due reviews and the last interventions;
3. resume with one due probe or the saved next move;
4. do not reconstruct personal context intentionally excluded from state;
5. treat chat summaries as secondary evidence.

## 6. Offline portability

The store uses UTF-8 JSON and JSONL with relative topic paths. It can be copied,
backed up, encrypted, or versioned independently of any model vendor.

Examples:

~~~bash
python scripts/learner_state.py init --root .learning-coach \
  --topic options-greeks --title "Options Greeks" \
  --goal "Reason from mechanisms"

python scripts/learner_state.py record --root .learning-coach \
  --topic options-greeks --concept gamma-vs-delta \
  --challenge explain --outcome success --assistance none \
  --delay delayed --observation "Explained unaided after a delay"

python scripts/learner_state.py checkpoint --root .learning-coach \
  --topic options-greeks --summary "Can derive first-order exposure" \
  --next-move "Test curvature on a new payoff"

python scripts/learner_state.py due --root .learning-coach
python scripts/learner_state.py validate --root .learning-coach
~~~

Use an absolute script path when invoking it outside the installed skill.

