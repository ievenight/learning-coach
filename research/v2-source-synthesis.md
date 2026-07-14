# Learning Coach v2: fresh synthesis of the six source transcripts

Date: 2026-07-14

This note records a new pass over the six local transcripts. It is a design
synthesis, not a claim that podcast statements are equivalent to peer-reviewed
evidence. Primary retrieval and spacing research is cross-checked in
[v2-agent-patterns.md](v2-agent-patterns.md).

## Selection rule

A source idea belongs in runtime policy only when it changes the tutor's next
observable move. Mechanism details, anecdotes, fixed effect sizes, sponsors, and
unrelated clinical or productivity material stay out of runtime context.

## 1. Gabriel Petersson: AI self-learning

Source: [video](https://www.youtube.com/watch?v=vq5WhoPCWQ8), local transcript
01, especially lines 315–410 and 450–735.

Useful moves:

- Start from a real problem and recurse into prerequisites when they become
  load-bearing.
- Treat “noticing I do not understand” as a skill the tutor can externalize.
- Let the learner state a model back to the LLM, then probe the exact weak edge.
- Make intermediate states visible and change representation when a generic
  explanation does not click.
- Separate “use AI to learn” from “use AI to replace the learner's work.”

Correction for v2: asking the model repeatedly is not itself evidence of learning.
The tutor must add unaided retrieval and transfer checks.

## 2. Andy Matuschak: tools for thought and learning

Source: [video](https://www.youtube.com/watch?v=dmeRQN9z504), local transcript
02, especially lines 35–315, 500–610, 720–780, and 985–1070.

Useful moves:

- Diagnose two distinct failures: forgotten after understanding versus never
  understood and never noticed.
- Use questions as metacognitive scaffolding, then fade the scaffolding.
- Preserve the learner's actual goal; misalignment creates misery that should not
  be mislabeled as desirable difficulty.
- Treat memory as support for difficult multi-step understanding.
- Switch from information acquisition to apprenticeship for frontier judgment,
  taste, and tacit practice.

Correction for v2: the tutor should carry metacognitive load, not increase it with
a long questionnaire.

## 3. David Eagleman: plasticity and memory

Source: [video](https://www.youtube.com/watch?v=lEULFeUVYf0), local transcript
03, especially lines 535–595, 815–925, and 1090–1120.

Useful moves:

- Anchor information to an active curiosity or problem.
- Move to the next edge once a challenge is already smooth.
- Use a focus → attempt/error → correction → later consolidation loop.
- Optimize directed change, not novelty or difficulty for its own sake.

Correction for v2: neuromodulator stories are rationale, not runtime instructions.
The actionable rule is to create relevant attempts and feedback.

## 4. Huberman: studying and learning

Source: [video](https://www.youtube.com/watch?v=ddq8JIMhz7c), local transcript
04, especially lines 1235–1510, 1680–1825, and 1920–2155.

Useful moves:

- Treat tests as learning events, not merely evaluation.
- Prefer open production over recognition-only checks.
- Check early, then revisit later.
- Do not use confidence or smooth reading as a mastery signal.
- Welcome errors and close the feedback loop.

Correction for v2: remove universal percentages and fixed schedules. Record the
actual probe, delay, assistance, and outcome.

## 5. Michael Kilgard: brain and learning

Source: [video](https://www.youtube.com/watch?v=rcAyjg-oy84), local transcript
05, especially lines 200–335, 1280–1360, 1640–1835, 2370–2510, and 3190–3470.

Useful moves:

- Active interaction matters more than passive exposure.
- Reflection is a separate phase: identify the moment or connection that changed.
- Attention and reward select what should be learned; a good coach points to the
  decisive moment.
- Mental rehearsal mainly consolidates patterns already performed.

Correction for v2: “active” does not mean constant questioning. A direct
explanation can be followed by one meaningful prediction, reconstruction, or
application.

## 6. Cal Newport: active recall and deliberate practice

Source: [video](https://www.youtube.com/watch?v=p4ZfkezDTXQ), local transcript
06, especially lines 740–935 and 970–1185.

Useful moves:

- Reconstruct from scratch rather than rereading.
- Keep a struggle set containing only missed or assisted items.
- Practice at the current edge instead of repeating smooth performance.
- Distinguish learning practice from flow or performance.
- Narrow attention to one target and avoid rapid context switching.

Correction for v2: “brutal” effort is not a target. The tutor should preserve
productive strain while enforcing a round cap and structural pivot.

## Cross-source runtime synthesis

The six transcripts converge on five tutor actions:

1. Establish relevance and one capability target.
2. Elicit a real attempt when teaching is desired.
3. Locate the smallest gap from learner output.
4. Supply minimal feedback and change structure after repeated failure.
5. Verify later performance through retrieval, application, or transfer.

They do not resolve the LLM-specific problems of mode selection, context
compaction, durable state, consent, or mastery bookkeeping. Those require the
agent-engineering layer described in v2-agent-patterns.md.

## Material intentionally excluded from runtime

- exact effect sizes and universal review intervals;
- neurotransmitter names and simplified brain mechanisms;
- sponsor segments, career stories, social-media commentary, and clinical
  treatment material;
- claims that one technique is literally the only way to learn;
- any inference that a user has mastered a concept because the explanation felt
  clear.

