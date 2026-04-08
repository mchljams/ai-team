# AI Team

A portable, generalist AI team built to assist across software projects.

## What This Is

This repository is the source of truth for the AI team — its personas, living state,
and history. Personas are designed to be generalist and reusable across projects.
Project-specific context lives in repo-level docs (e.g. `AGENTS.md`), not here.

## Structure

```
ai-team/
├── personas/       # One file per role — defines purpose, behaviors, outputs
├── TEAM.md         # Living state — roster, planned roles, decisions log
├── CHANGELOG.md    # Role evolution and team milestones
└── README.md       # This file
```

## Current Team

| Role | Name | Status |
|---|---|---|
| Program Director | TBD | ✅ Active |

## Naming Convention

Each persona carries an Irish/Gaeilge name proposed by the persona in its inaugural
session and chosen by the human lead.

## How to Activate

Personas are activated via `mchljams/.github/copilot-instructions.md`, which applies
them globally across all repositories in your personal GitHub space.

## Proving Ground

Initial application: [Hptuners/hptuners_Phoenix](https://github.com/HPTuners/hptuners_phoenix)