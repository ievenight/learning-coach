# Learning Coach

中文 | [English](README.md)

`learning-coach` 是一个面向 LLM 的教学 Skill，目标不是让用户被动阅读一段“讲得很清楚”的解释，而是帮助用户形成持久、可提取、可实际使用的理解。

## v1

第一版主要使用主动提取、适度困难、递归补缺、问题驱动学习、间隔复习和费曼技巧。可安装的 Skill 位于 [`skill/learning-coach/`](skill/learning-coach/)。

## 仓库结构

- `skill/learning-coach/` — 可安装的 Skill 源文件。
- `research/` — 原始材料分析及后续版本设计。
- `evals/` — v2 改版过程中建立的行为评测案例。

## 当前状态

`main` 分支保存 v1 基线；`v2-redesign` 分支已经包含当前的 v2 候选版：

- 明确区分 Teach / Answer / Do；
- 用可观察证据判断掌握度；
- 使用追加式、可离线复制的 learner-state；
- 在 context compact 或新会话后恢复教学位置；
- 配套行为场景和确定性的状态层测试。

设计研究位于 [`research/`](research/)。v2 目前仍是候选版，尚未标记稳定。

## 安装

把 `skill/learning-coach/` 复制到 Codex 的 skills 目录，然后重启或重新加载 Codex：

```text
~/.codex/skills/learning-coach/
```

可安装目录只保留运行时真正需要的说明与 references；仓库 README 和研究材料放在 Skill 目录之外，避免占用运行时 context。

## 开发检查

```bash
python3 -m unittest discover -s tests -v
python3 /path/to/skill-creator/scripts/quick_validate.py skill/learning-coach
```

## 许可证与来源

目前尚未选择许可证。v2 开发过程中会在 `research/` 中维护来源归属和研究记录。
