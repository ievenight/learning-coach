# Learning Coach — Playbook

Detailed how-to for each technique, with templates. SKILL.md tells you *when* and
*why*; this tells you *how*. Pull the piece you need; don't dump the whole file
on the user.

## Contents
1. Retrieval practice (the core engine)
2. Desirable difficulty & deliberate practice
3. Recursive gap-filling
4. Top-down, problem-first learning
5. Spacing, gaps, and interleaving
6. The Feynman technique (teach-it-back)
7. Spaced-repetition cards — how to write them
8. Quiz / question sets — how to write them
9. Designing a learning plan
10. Focus & session design
11. AI-as-tutor: prompts to teach the user how to self-teach

---

## 1. Retrieval practice (the core engine)

The act of pulling information *out* of memory — not putting it in — is what makes
it stick. Self-testing once soon after first exposure roughly halves how much is
forgotten over the following weeks, and the benefit compounds with each retrieval.

How to run it as a coach:
- **Test before you teach.** Even on brand-new material, a guess primes encoding.
  "Before I explain — what would you predict, and why?" Wrong answers are fine and
  useful, as long as the correct answer follows.
- **Prefer generation over recognition.** Ask them to produce the answer, derive
  the step, or explain the mechanism. Multiple-choice lets recognition masquerade
  as knowledge.
- **Blank-page recall.** Periodically: "Close the notes. Reproduce the whole
  argument / proof / process from scratch." Whatever they can't reproduce is what
  they don't yet own.
- **Retrieve soon, then space.** A check the same day or next day beats a delayed
  one for first consolidation; later checks should be spaced out (§5).
- **Show the correct answer every time.** Retrieval without feedback can entrench
  errors. Always close the loop with the right answer and *why*.

The struggle-pile method (efficient self-testing): attempt each item; the ones you
nail go in the "got it" pile, the ones you fumble go in the "struggled" pile; redo
only the struggled pile; repeat. The hard pile shrinks roughly exponentially, so a
few focused hours can reach mastery.

---

## 2. Desirable difficulty & deliberate practice

Easy practice barely changes the brain — there's nothing to adapt to. Growth
happens at the edge: material that is *frustrating but achievable*, about one step
beyond comfortable (a useful rule of thumb from expert practice: push ~20% past
what already feels smooth).

- Keep the difficulty knob near that edge. Too easy → boredom, no plasticity. Too
  hard → flailing and demoralization. Re-calibrate as they improve (seek the next
  challenge rather than re-running mastered material).
- **Deliberate practice is not flow.** Flow is smooth and time-disappears; the
  practice that actually drives improvement is the opposite — effortful,
  attention-demanding, slightly uncomfortable, fully conscious of exactly what
  you're trying to do. Don't sell learning as effortless.
- **Don't rescue too fast.** When the learner is stuck, a little silence and a
  hint beats handing over the answer. The productive-struggle window is where
  encoding happens.
- **Difficulty, not misery.** If a learner is suffering, it's usually not the
  material — it's fear of failing, time pressure, or "I shouldn't be struggling."
  Name that and defuse it; struggle at the edge of ability should feel taxing but
  okay, even satisfying.

---

## 3. Recursive gap-filling

Frame any learning task as: find the gap → fill it → check whether filling it
revealed a new gap → repeat, until it bottoms out in things they already know.

- Help them **notice** gaps they'd skate past. On a key sentence: "Do you
  understand *why* that's true, or only *that* it's stated?" Often the answer
  surprises them.
- Go **one concept at a time.** Don't fill three gaps in one breath; chase one
  thread to the bottom, then surface.
- Have them **state their current understanding back** ("here's what I think is
  happening…") so you can locate the exact gap rather than re-explaining things
  they already have.
- Teach them the meta-move: most "I don't get this topic" is really a small number
  of specific unfilled prerequisites. Find those, not "the topic."

---

## 4. Top-down, problem-first learning

For a motivated learner, starting from foundations and grinding upward is slow and
demotivating. Starting from a real problem and pulling prerequisites in as needed
is faster and self-reinforcing, because each piece arrives exactly when it's
relevant (and curiosity is open — the brain encodes best when it wants the answer).

How to run it:
- Anchor on a concrete goal/project/problem the learner cares about ("build a tiny
  X", "understand why my Y is failing", "value this option").
- Get a rough end-to-end attempt going *first*, even if much is opaque. Then dive
  into the pieces: "what does this part do? why is it here? how does this step
  work?" — recursing into prerequisites only as each becomes load-bearing.
- Use a syllabus/textbook outline as a **scaffold** to know roughly what exists
  and in what order — then treat it as tentative and skip around by interest. As
  competence grows, drop the scaffold ("fading").
- Caveat: a short "intro to X" pass can still be worth it up front — not because
  you need all of it, but to get the map and vocabulary that lets you navigate.
  Judge by whether the learner can otherwise tell what they're missing.

---

## 5. Spacing, gaps, and interleaving

Three distinct, compounding effects:

- **Spacing (across sessions).** Revisiting material after a delay beats massing
  it together. A practical ladder: same day → next day → ~3 days → ~1 week → ~2–3
  weeks. Each successful recall lets you stretch the next gap.
- **Gap effects (within a session).** Brief pauses (even 5–30 seconds) of doing
  nothing right after new material let the brain replay it rapidly, strengthening
  it. Don't fire-hose; let a hard idea breathe before moving on.
- **Interleaving.** Mixing related-but-different problems/topics (rather than
  blocking one type) improves the ability to tell them apart and to apply the
  right tool — even though it feels harder in the moment. Lightly mixing in
  tangential, easier material also aids encoding by connecting new knowledge to
  existing knowledge.

---

## 6. The Feynman technique (teach-it-back)

Ask the learner to explain the concept simply, as if to a 12-year-old or a
beginner. Two things happen: they retrieve (good), and their explanation goes
fuzzy exactly where their understanding is thin (a precise gap-finder).

- Prompt: "Explain X to me like I've never heard of it. I'll stop you wherever it
  gets vague — those are the gaps."
- When their explanation stalls or hand-waves, *that spot* is the next thing to
  learn. Send them back to it, then have them re-explain.
- For self-teaching with an LLM, the same loop works: understand → explain your
  understanding back to the model → let it flag what's off or missing → repeat.

---

## 7. Spaced-repetition cards — how to write them

For material that genuinely must be memorized (vocabulary, taxonomy, formulae,
key facts), spaced-repetition cards are cheap and durable. Good cards are the
whole game.

Rules for good cards:
- **Atomic** — one fact or idea per card. Split anything compound.
- **Question on the front, single answer on the back.** Phrase the front so it
  *forces retrieval*, not recognition.
- **Avoid lists** to recall as a set; turn them into several focused cards or
  cloze deletions.
- **Make it meaningful, not rote.** Where possible, frame the card around *using*
  the fact (a small applied problem) rather than reciting it — applied retrieval
  beats parroting and is less tedious.

Template:
```
Q: <single, retrieval-forcing prompt>
A: <one clear answer>
(optional) Why/connection: <one line tying it to something known>
```
Example (applied, not rote):
```
Q: A 1 mL vial holds vaccine at 5 ng/µL of a 4,000-nucleotide RNA. Roughly how
   many RNA copies? (You'll need the mass of one nucleotide.)
A: ~order 10^14 — uses ~330 g/mol per nucleotide → mass per RNA → Avogadro.
```

---

## 8. Quiz / question sets — how to write them

- **Open-ended and short-answer first.** "Explain why…", "what breaks if…",
  "derive…", "when would you use A vs B?" These demand recall and reasoning.
- Include the **load-bearing conceptual questions**, not only recall trivia — the
  ones that reveal whether the mental model is right.
- Mix difficulty; include at least one that pushes past comfortable.
- For multiple-choice (when format requires it), write distractors that punish a
  shallow read — plausible-looking answers that only deeper understanding rules
  out.
- Provide an **answer key with explanations**, so self-testers can close the loop.
- Offer to deliver questions **one at a time** (so the user attempts before seeing
  the answer) rather than as a list with answers visible.

---

## 9. Designing a learning plan

A good plan is top-down, retrieval-heavy, and spaced — not a content checklist.

Template:
```
Goal / driving problem: <what they actually want to do or understand>
Current level & known anchors: <where they're starting; what to connect to>

Phase 1 — Get something working / a rough whole
  - Concrete first artifact or problem to attempt
  - Prerequisites to pull in *only as needed*

Phase 2..N — Recurse into the pieces
  - For each: attempt → explain mechanism → retrieve → connect

Retrieval & spacing built in
  - Self-test soon after each new piece
  - Spaced revisits: next day / ~3 days / ~1 week
  - Teach-it-back checkpoint(s)

Edge-pushing
  - Each phase ends slightly past comfortable; next challenge identified
```
Keep it adjustable — the plan is a scaffold to fade, not a contract.

---

## 10. Focus & session design

Attention is trainable and is the prerequisite for everything else.

- **Single-task, distraction-free blocks.** Phone away/out of reach, notifications
  off, one thing only. Task-switching is corrosive to deep learning.
- **Schedule it at consistent times.** A regular study time entrains focus; expect
  a few days to settle into a new rhythm.
- **Front-load the hard retrieval** when energy is highest (e.g., morning).
  Blank-page recall is taxing — don't save it for a depleted evening.
- **Sleep is part of the method, not separate from it.** Consolidation happens
  during sleep, especially the night after learning. All-nighters trade away the
  consolidation you studied for. Where sleep is short, a brief non-sleep-deep-rest
  / yoga-nidra style rest can partially help.
- **Train focus directly** between sessions: a few minutes daily of bringing
  attention back to one target (breath or a visual point) measurably improves
  concentration. "Productive meditation" — holding one problem in mind on a walk,
  repeatedly returning to it — trains working memory for hard, linear work.
- **Borrow accountability.** Studying a hard problem with one or two others at a
  shared board raises everyone's concentration (you can't drift without falling
  behind). Teaching peers is itself a top study habit.

---

## 11. AI-as-tutor: prompts to teach the user how to self-teach

If the user is (or could be) learning with an LLM, the biggest unlock is the
mindset switch from "do the work for me" to "help me learn." Coach them on it.

The recursive loop to teach them:
1. Start from a problem/project; ask the model for a runnable first attempt even
   if it's opaque.
2. Go line by line / part by part: "what does this do? why is it here?"
3. On every fuzzy answer, follow up — "*why* does that make it work? what would
   happen without it?" — until it bottoms out.
4. State your understanding back and ask the model to confirm or correct it
   (Feynman with the model as checker).
5. Ask it to generate quizzes and *new* practice problems, and to extract the
   shared principle behind a set of past problems.

High-leverage prompt patterns to hand them:
- "Explain this like I'm 12, with a real-world analogy."
- "Be direct and concrete. Show every intermediate step / the shapes at each
  stage. Don't skip."
- "Don't give me the answer yet — ask me a question that checks whether I
  understand the prerequisite."
- "Here are my last 10 practice questions. What fundamental thing do they all
  test? Now generate 10 new ones at a slightly harder level."
- "Here's my understanding: <…>. What's wrong or missing?"

The two skills to keep training (and to tell them to train): noticing when they
*don't* understand, and recognizing the "click" when they do. Chase the clicks;
make them as frequent as possible.

