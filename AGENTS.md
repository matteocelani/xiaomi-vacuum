# AGENTS.md

Single source of truth for any AI coding agent working in this repository. [`CLAUDE.md`](./CLAUDE.md) is a shim that points here. Enforceable rules live in [`.agent/rules/`](./.agent/rules/), one concern per file. Repeatable procedures live in [`.agent/commands/`](./.agent/commands/). Structural decisions go through [`.agent/council/`](./.agent/council/).

When this file and a rule file disagree, the rule file wins on its concern. When two rule files disagree, stop and convene the council. Do not pick one silently.

## Project

Community Home Assistant integration for Dreame, MOVA, Mijia, and TROUVER robot vacuums, forked from Tasshack/dreame-vacuum so it can be maintained as a long-lived project. It is not an official Dreame or Xiaomi product.

The repository name is `xiaomi-vacuum`. The Home Assistant domain is `xiaomi_robot_vacuum`. Council [0009](.agent/council/records/0009-hacs-domain-rename.md) superseded the domain-stay clause of [0001](.agent/council/records/0001-xiaomi-wide-rename-and-expansion.md): this integration does not share a folder with Tasshack/dreame-vacuum, and it does not migrate existing `dreame_vacuum` config entries. A second device family is added as a sibling package under this integration only in the pull request that adds a concrete device. A further domain rename requires a new council.

The MIT license and its `Copyright (c) 2022 Tasshack` notice stay. Do not replace them, and do not add a copyright line, in passing.

## Reading order

Working memory does not survive the next task. At the start of every task:

1. Read this file.
2. Read every file in `.agent/rules/` the task can violate. A Python change reads all of them.
3. Read the matching file in `.agent/commands/` when the task is one of those procedures.
4. Read the module you will edit, and the modules that call it.

If a rule is silent or contradictory on the exact question, convene the council or ask the maintainer. Do not guess, and do not copy a legacy pattern because it is already in the tree.

## Stack

Locked unless a council record says otherwise:

- Python 3.12. The floor is the `homeassistant` version in `hacs.json` (currently 2024.2.0), which requires 3.12. Syntax newer than that floor is forbidden.
- One Home Assistant custom integration: config-entry only, installed through HACS. Continuous integration is the hassfest workflow and the HACS validation workflow already in `.github/workflows/`.
- Runtime libraries are exactly the `requirements` list in the integration manifest. Adding one is a council decision.
- Quality tools, once installed: Ruff for lint and for Black-compatible formatting, pytest for tests. Their configuration contract is in `.agent/rules/formatting.md` and `.agent/rules/tests.md`. There is no second formatter and no second linter.

## Non-negotiables

1. **Installed users keep their identity.** Config entries, entity `unique_id`s, device identifiers, and service schemas are stable. Changing any of them requires a migration in the same release and a council record.
2. **Home Assistant stays in the shell.** Protocol, capability tables, map decoding, and cloud or local transport do not import `homeassistant`. The shell adapts the device core to entities, flows, and services.
3. **No secrets in the tree.** Tokens, passwords, account ids, session cookies, real device ids, and real map dumps never appear in source, tests, fixtures, logs, diagnostics, commits, or pull requests.
4. **New code meets the rules in full.** The inherited integration predates them. Leave untouched legacy code alone. A line you add follows the rules even when the surrounding function does not.
5. **One concern, one branch, one pull request, into `master`.** `master` is the only integration branch. Do not invent a second trunk.

## How the code is organized

The repository holds one HACS integration, not a library monorepo. The integration package lives at `custom_components/<domain>/`, where `<domain>` is the value in the manifest. Tests, agent docs, workflows, and repository metadata stay outside that package, because a HACS release zips the package and must not ship them.

Inside the package the dependency arrow points one way, from a Home Assistant shell down into a pure-Python device core.

The shell owns setup and unload, the config flow and the options flow, the data-update coordinator, platform modules, the entity base, service registration, diagnostics, translations, and the manifest. It is the only code allowed to import `homeassistant`. A platform module is a registry: it declares entities and forwards lifecycle calls. It does not speak the wire protocol and it does not decode maps.

The device core owns wire protocols, authentication exchanges, capability and property tables, device state, and map decoding. It raises its own exception types and returns plain values. It is unit-tested without Home Assistant installed. A second device family, when one is added, is a sibling package with those same responsibilities, not a pile of conditionals inside the first family. Families do not import each other. The moment two families need the same helper, that helper moves into a small shared package that still does not import Home Assistant. The shell depends on a narrow facade, not on concrete enums copied into every platform module.

A new vacuum model is a row on its family base: which properties, actions, and features that model exposes. Dreame, MOVA, Mijia, and TROUVER, including Mijia models reported as `xiaomi.vacuum.*`, use the Dreame catalog base. A Xiaomi model uses the sibling base: explicit maps, local miIO, and flags derived from mapped names. Council 0004 records that split. Entities ask whether a capability is present. A branch on a model string inside an entity or a platform module is a structure error.

Placement follows use, not prediction. Code used by one family stays in that family. Code used by two families is promoted in the same change that creates the second caller. Code used by one module stays in that module. Do not add packages, protocol classes, or abstraction layers for a family that does not exist yet. Empty directories and stub modules reserved "for the rename" are dead code.

Every Python module follows the layout in `.agent/rules/modules.md`. The domain string is read from one constant. Hard-coding today's domain inside the package, including in absolute imports, will break the rename and is forbidden.

## Rules

| Concern | File |
| --- | --- |
| Layers, placement, what may import what | `.agent/rules/architecture.md` |
| Dead code, surgical edits, complexity | `.agent/rules/python-quality.md` |
| Types, enums, public signatures | `.agent/rules/typing.md` |
| Imports, including the parent-import ban | `.agent/rules/imports.md` |
| Names | `.agent/rules/naming.md` |
| Module layout | `.agent/rules/modules.md` |
| Ruff lint and Black-compatible format | `.agent/rules/formatting.md` |
| Async, executors, the event loop | `.agent/rules/async-ha.md` |
| Exceptions, logging, user-facing text | `.agent/rules/errors.md` |
| Manifest, flows, coordinators, entities, services | `.agent/rules/ha-integration.md` |
| Secrets, diagnostics, TLS, dependencies | `.agent/rules/security.md` |
| Pytest layout and coverage | `.agent/rules/tests.md` |

## Commands

| Command | Procedure |
| --- | --- |
| `/add-device` | `.agent/commands/add-device.md` |
| `/add-entity` | `.agent/commands/add-entity.md` |
| `/gate` | `.agent/commands/gate.md` |
| `/review` | `.agent/commands/code-review.md` |
| `/commit` | `.agent/commands/commit.md` |
| `/pr` | `.agent/commands/pr.md` |
| `/council` | `.agent/commands/council.md` |
| `/upstream-sync` | `.agent/commands/upstream-sync.md` |

Each procedure has preconditions, ordered steps, a done definition, and a NEVER list. Follow it. Do not improvise a shorter version.

## Council

Convene the council before a structural or hard-to-reverse decision. The trigger list, the four roles (Architect, Pragmatist, Security, Home Assistant conventions), the rounds, and the decision-record format are in [`.agent/council/README.md`](./.agent/council/README.md). Do not convene it for a model row, an entity that follows `/add-entity`, a bug fix, or a docs change. Security has a veto on credential handling, TLS, and secrets. A 2–2 split stays a split: the record says so and the maintainer decides. Do not invent a compromise the roles did not accept.

## Workflow

Branch from `master`. Prefixes are `feat/`, `fix/`, `refactor/`, `test/`, `docs/`, and `chore/`. Names are kebab-case, with no ticket numbers. The pull request body carries `Fixes #N` when an issue exists.

Commits are Conventional Commits in English, imperative mood, one concern each. The title is `type(scope): subject`, 72 characters or fewer. Scopes are `vacuum`, `map`, `flow`, `entity`, `coordinator`, `protocol`, `cloud`, `tests`, `ci`, `docs`, and `agents`. The procedure is `.agent/commands/commit.md`.

A pull request targets `master`, contains one logical change, and links the council record when one was required. The author does not merge it.

English is required in code, comments, commit messages, pull request text, and decision records. A translation catalog is the exception: a locale file is written in that locale, and `strings.json` is the English source.

## Stop and ask

Stop, and do not implement, when the task needs any of the following:

- A new runtime dependency, or a raised minimum Home Assistant version.
- A new device-family package, or a new shared package under the integration.
- A change to config-entry storage, entity `unique_id`s, device identifiers, or a service schema.
- A change to authentication, cloud endpoints, TLS, or diagnostics redaction.
- An edit to `LICENSE`.
- A rule disable, a coverage waiver, or a `type: ignore` with no removal condition.
- A behavior change in code the task did not need to touch.
- A council result of `split`, or an unresolved Security veto.

## Inherited code

The integration under `custom_components/` was imported from the upstream project and does not yet satisfy these rules. That is expected. Do not reformat it, retype it, or restructure it as a side effect of another task. When a task edits a function, bring that function into compliance only where the edit is mechanical and local: annotations on lines already being changed, import order in a file already being rewritten. If compliance requires a restructuring, that restructuring is its own change. It does not ride along.

## Docs versus code

The rules are the contract for new work. If a rule is wrong, change the rule in its own pull request first, then change the code. Do not "fix" a rule by imitating the inherited tree, and do not let the inherited tree veto a rule.

## Gate

`/gate` is defined in `.agent/commands/gate.md`. It runs Ruff check, Ruff format check, and pytest from the configuration contract in the rule files. The gate is not installed yet: `pyproject.toml` and `tests/` are absent. A docs-only change records that waiver in the pull request. The first pull request that adds or modifies Python either installs the gate in that same change or depends on a pull request that already did. Never report the gate as passed when it did not run.
