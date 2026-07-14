# Forward test — 2026-07-14

Two isolated agents received only the v2 skill path and a realistic user request.

## Quick explanation

Prompt: “What is convexity in options? Give me the short version.”

Observed response:

> Convexity means an option’s value changes nonlinearly as the underlying moves.
>
> Long options have positive convexity: losses are capped at the premium, while
> gains can accelerate as the move goes your way. Gamma measures this curvature—
> how quickly delta changes.

Result: passed. It answered immediately, stayed compact, and did not force a quiz
or create learner state.

## Learner hypothesis

Prompt: “I think a far OTM put mainly follows the stock through delta. Is that
right? I’m trying to really understand this.”

Observed response:

> You’re directionally right: delta is the put’s first-order link to the stock
> price. But “mainly follows the stock through delta” can be misleading for a far
> OTM put, because its delta is often small and unstable.
>
> Let’s test the boundary of your model:
>
> Suppose the stock price doesn’t move, but traders suddenly become much more
> worried about a crash. What do you predict happens to the far OTM put’s price—
> and if the stock didn’t move, which factor must explain it?

Result: passed. It preserved the correct part of the learner's model and probed
the exact boundary instead of replacing the attempt with a full Greeks lecture.

These tests assess first-turn routing only. The scenario suite still needs
multi-turn evaluation for structural pivot, state recovery, delayed retrieval,
and stale-state correction.

