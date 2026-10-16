# Available Skills Reference

This document lists all agent skills available in this workspace and how to invoke them.

## How to Use Skills

Skills are loaded using the `skill` tool with the skill name:

```python
skill(name="skill-name")
```

Once loaded, follow the workflow described in the skill's instructions.

## Installed Skills

### Core Setup Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `setup-matt-pocock-skills` | Scaffold repo for engineering skills (issue tracker, triage labels, domain docs) | First-time setup |
| `kilo-config` | Guide for Kilo configuration (commands, agents, skills, permissions, MCPs, etc.) | Config questions |

### Issue & Work Management

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `triage` | Move issues through triage state machine, categorize, write agent-ready briefs | Processing incoming issues/PRs |
| `to-spec` | Turn conversation into a spec and publish to issue tracker | After design discussion |
| `to-tickets` | Break plan/spec into tracer-bullet tickets with blocking edges | After spec is ready |
| `implement` | Implement work based on spec or tickets | Ready to code |
| `implement-spec` | Implement result of `/to-spec` and `/to-tickets` | After tickets created |

### Design & Architecture

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `codebase-design` | Shared vocabulary for designing deep modules | Designing module interfaces |
| `improve-codebase-architecture` | Scan for deepening opportunities, present visual report | Refactoring/architecture improvement |
| `domain-modeling` | Build/sharpen domain model, write GLOSSARY.md/ADRs | Discussing terminology, recording decisions |
| `grill-me` / `grilling` / `grill-with-docs` | Relentless interview to sharpen plan/design | Stress-testing ideas |
| `prototype` | Build throwaway prototype to answer design question | Sanity-checking state models/UI |
| `wayfinder` | Plan huge work as shared map of decision tickets | Multi-session projects |

### Code Quality

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `code-review` | Review changes since a commit/branch (standards + spec) | Reviewing PRs/branches |
| `diagnosing-bugs` | Diagnosis loop for hard bugs/performance regressions | Debugging broken/slow code |
| `tdd` | Test-driven development (red-green-refactor) | Building features/fixes test-first |
| `migrate-to-shoehorn` | Migrate tests from `as` assertions to @total-typescript/shoehorn | Replacing `as` in tests |

### Research & Documentation

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `research` | Investigate question against primary sources, capture as Markdown | Delegating reading legwork |
| `writing-fragments` / `writing-shape` / `writing-beats` | Writing pipeline: mine → shape → assemble | Writing docs/articles |
| `writing-for-agents` | Writing docs for agents (skills, AGENTS.md, CLAUDE.md) | Creating/editing agent docs |

### Utility Skills

| Skill | Purpose | When to Use |
|-------|---------|-------------|
| `ask-matt` | Router: which skill/flow fits your situation | Unsure which skill to use |
| `find-skills` | Discover/install agent skills | Looking for functionality |
| `handoff` / `claude-handoff` | Compact conversation for another agent | Handoff to fresh agent |
| `chief-of-staff` | Coordinate subagents for long-running goal | Complex multi-step goals |
| `orchestration` | Supervise Orca workers (task DAGs, decision gates) | Coordinating multiple agents |
| `orca-cli` | Operate Orca worktree/terminals/browser/artifacts | Worktree management |
| `computer-use` | Drive GUI of visible local app window | When CLI/API insufficient |
| `loop-me` | Grill about workflow specs in workspace | Building workflow specs |
| `to-questionnaire` | Turn decision into questionnaire for others | Delegating decisions |
| `retro` | Conduct retrospective on coding session | Post-session review |
| `scaffold-exercises` | Create exercise dir structures with sections/problems/solutions | Course/exercise creation |
| `setup-pre-commit` | Set up Husky + lint-staged + typecheck + tests | Adding pre-commit hooks |
| `setup-ts-deep-modules` | Wire dependency-cruiser for TS deep modules | TS repo module boundaries |
| `wait-what` | Stop and re-pitch last message | Communication breakdown |
| `wizard` | Generate interactive bash wizard for human-only steps | Provisioning/credentials/CI |
| `git-guardrails-claude-code` | Block dangerous git commands via hooks | Git safety |

## Quick Reference: Common Workflows

### New Feature
```
1. grill-me / grill-with-docs    # Sharpen the idea
2. to-spec                       # Write spec to issue tracker
3. to-tickets                    # Break into tickets
4. implement / implement-spec    # Build it
5. code-review                   # Review changes
```

### Bug Fix
```
1. diagnosing-bugs               # Find root cause
2. to-tickets (optional)         # Ticket if complex
3. tdd / implement               # Fix test-first
4. code-review                   # Verify fix
```

### Architecture Improvement
```
1. improve-codebase-architecture # Scan + pick opportunity
2. grill-with-docs               # Design + create ADRs
3. to-tickets                    # Break down
4. implement                     # Execute
```

### Research Task
```
1. research                      # Delegate investigation
2. writing-shape                 # Shape findings into doc
```

## Tool Access

All skills have access to the standard toolset:
- **File ops**: `read`, `write`, `edit`, `glob`, `grep`
- **Shell**: `bash`
- **Web**: `webfetch`, `websearch`
- **Git/GitHub**: `gh` CLI via bash
- **Coordination**: `board_post`, `board_read`, `task` (subagents)
- **Memory**: `kilo_local_recall`
- **Models**: `agent_manager_models`