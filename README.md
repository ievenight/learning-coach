# Learning Coach

A tutoring **skill** for LLM coding agents (Claude Code and compatible hosts) that
teaches the way effective studying actually works — by making you **retrieve,
attempt, and get corrected**, instead of explaining at you. It remembers where you
are across sessions, so it doesn't start from zero every time or forget after the
context window is compacted.

The teaching behaviors are distilled from Andrew Huberman's "optimal studying"
protocol and cross-checked against learning-science research (retrieval practice,
spacing, interleaving, worked-example fading, desirable difficulty). The skill is
operational, not a lecture on the science.

## What it does

- **Routes before teaching.** A quick fact or an execution task is answered
  directly — it won't obstruct you with quizzing. It only runs the teaching loop
  when you actually want to learn, and it honors "just tell me" instantly.
- **Teaches by retrieval.** After each idea it asks you to recall, predict, or try —
  then stops and waits. Every answer gets a reveal-and-compare that pinpoints the
  exact gap; wrong answers are treated as useful, not graded.
- **Stays honest.** It marks something as "you can do it" only after you've produced
  it **unaided** — "I get it" is never enough, and a later miss demotes it.
- **Plans with a Map.** For a multi-session track it co-creates a revisable,
  multi-level roadmap, drives progression from it, and parks tangents instead of
  wandering — so learning stays sequenced rather than haphazard.
- **Paces to you.** You decide when to stop; it scopes each session to a coherent
  chunk and spaces the rest across future sessions.
- **Remembers across sessions.** Progress is kept in one human-readable note per
  track under `.learning-coach/`, surfaced automatically at the top of the skill so a
  fresh or post-compaction session recovers from files, not from a chat summary.

## Install

Via the [skills.sh](https://skills.sh) CLI (recommended):

```bash
npx skills add ievenight/learning-coach
```

Or copy it into your agent's skills directory manually:

```bash
cp -r skills/learning-coach ~/.claude/skills/learning-coach
```

Then just express a learning intent — "teach me X", "help me get my head around Y",
"I keep forgetting Z", or "continue where we left off".

## How memory works

For a multi-session track the coach keeps a note at `.learning-coach/<topic>.md`,
relative to your working directory — a plain, fixed-format Markdown file
(`Map` / `Focus` / `Next`) that **you own**: read it, edit it, reorder it, or delete
it, and the coach follows your edits. It never stores raw conversation or sensitive
personal data.

## License

[MIT](LICENSE).

---

# Learning Coach（中文）

一个面向 LLM 编程 Agent（Claude Code 及兼容宿主）的教学 **Skill**。它按"有效学习真正的样子"来教——**让你回忆、尝试、被纠正**，而不是单向把知识讲给你听；并且跨会话记住你学到哪，不会每次从零开始，也不会在上下文被压缩后失忆。

教学行为提炼自 Andrew Huberman 的「最优学习」方法，并与学习科学研究交叉核对（主动提取、间隔、交错、worked-example 逐步淡出、适度困难）。Skill 里只有可执行的做法，不写科学论证。

## 它做什么

- **先分流再教。** 快速事实或执行任务直接给答案，不会拿提问刁难你；只有你真的想学时才进入教学循环，你说"直接告诉我"会立刻切换。
- **用检索来教。** 每讲一个点就让你回忆、预测或尝试，然后停下等你。每次回答都会"揭示+对照"、精确指出差在哪；答错被当成有用信息，而不是打分。
- **保持诚实。** 只有你**自己无辅助**做出来，才会标记为"会了"——"我懂了"不算数，之后做错会自动降级。
- **用 Map 规划。** 对多会话的学习，它会和你共建一张可修改、多层级的路线图，由它驱动推进，把岔路先记进 Map 而不是乱跑——让学习是有序的，而非东一榔头西一棒。
- **按你的节奏。** 停不停由你决定；它把每次会话控制在一个连贯的模块，其余的分散到之后的会话（间隔）。
- **跨会话记忆。** 每个学习主题的进度保存在 `.learning-coach/` 下一份人类可读的笔记里，并在 Skill 顶部自动呈现——新会话或压缩之后从文件恢复状态，而不是靠聊天摘要。

## 安装

用 [skills.sh](https://skills.sh) 的 CLI（推荐）：

```bash
npx skills add ievenight/learning-coach
```

或手动复制到 Agent 的 skills 目录：

```bash
cp -r skills/learning-coach ~/.claude/skills/learning-coach
```

然后直接表达学习意图即可——"教我 X""帮我搞懂 Y""我老是忘记 Z""继续上次的"。

## 记忆怎么工作

多会话学习时，教练会在你的工作目录下维护 `.learning-coach/<主题>.md`——一份格式固定的纯 Markdown 文件（`Map` / `Focus` / `Next`），**归你所有**：可以查看、编辑、重排或删除，教练会遵从你的改动。它从不保存对话原文或敏感个人信息。

## 许可

[MIT](LICENSE)。
