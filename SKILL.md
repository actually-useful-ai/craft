---
name: craft
description: "Portable workflow that starts from the goal, selects useful capabilities, preserves clear ownership, and carries work through planning, implementation, verification, and delivery. Use for structured task execution across discuss, compose, distill, reconsider, and present phases — plus board tracking, context management, skill creation, and multi-model consultation."
---

# Craft

A portable workflow engine with 16 skills across five core phases:

```
discuss → compose → distill → reconsider → present
 think      build    refine    challenge     ship
```

## Skills

| Skill | Phase | Purpose |
|-------|-------|---------|
| activate | Entry | Route from goal to the right phase |
| discuss | Think | Deliberate, debate, plan, or research |
| compose | Build | Execution — viz, frontend, docs, flow, game, skill, surgical |
| distill | Refine | Audit quality, capture patterns, manage snippets |
| reconsider | Challenge | First-principles rebuild, correctness, blast radius |
| present | Ship | Save, publish, PR, or wrap a session |
| board | Track | Lightweight Kanban for cross-session work |
| context | Support | Deep CLAUDE.md hierarchy refresh |
| enhance | Support | Prior art, reusable code, package selection |
| impress | Quality | Elevate work beyond adequacy with domain expertise |
| horizon | Strategy | Ranked opportunities and blind spots |
| chefs-choice | Entry | Hand over the approach for ambitious tasks |
| ask | Consult | Bounded outside-model consultation |
| swarm | Consult | Many small scouts synthesized into one answer |
| skill-creator | Meta | Create or revise agent skills |
| skill-auditor | Meta | Audit skill catalogs for structural errors |

## Usage

Invoke any skill as `/craft:{skill-name}`. Start with `/craft:activate` when the correct workflow is unclear.

## Scripts

Bundled scripts in `scripts/` provide session state, fleet parity checks, outside-model routing, data fetching, and board generation.

## Agents

Bundled agent profiles in `agents/` provide specialized capabilities: accessibility review, canary testing, design, diagnostics, fetching, janitor, performance, planning, repo analysis, scouting, search, security, and validation.
