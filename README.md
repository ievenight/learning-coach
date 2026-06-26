# Learning Coach

[中文](README.zh-CN.md) | English

`learning-coach` is an LLM tutoring skill designed to help users build durable, retrievable, and usable understanding instead of passively consuming explanations.

## Version 1

Version 1 applies retrieval practice, desirable difficulty, recursive gap-filling, top-down learning, spacing, and the Feynman technique. The distributable skill lives in [`skill/learning-coach/`](skill/learning-coach/).

## Repository layout

- `skill/learning-coach/` — installable skill source.
- `research/` — source analysis and design work for future versions.
- `evals/` — behavioral evaluation cases added during the v2 redesign.

## Status

The `main` branch preserves the v1 baseline. The next iteration will redesign the skill around real LLM tutoring behavior, explicit learn-vs-do mode selection, progress and mastery tracking, retrieval scheduling, and state that survives context compaction.

## Installation

Copy `skill/learning-coach/` into your Codex skills directory, then restart or reload Codex:

```text
~/.codex/skills/learning-coach/
```

The skill itself contains only runtime instructions and references; repository documentation and research stay outside the installable folder.

## License and sources

No license has been selected yet. Source attribution and research notes will be maintained under `research/` as the v2 work progresses.
