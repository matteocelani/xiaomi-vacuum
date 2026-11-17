# 0001 — How should a Xiaomi-wide rename and expansion be sequenced?

- Status: superseded
- Date: 2026-10-26
- Supersedes: none
- Superseded by: 0009

## Brief

**Question.** What sequence should this project use for a Xiaomi-wide repository name and for devices beyond the Dreame family, so installed config entries, entity `unique_id`s, and device identifiers stay put?

**Why now.** The owner wants the repository aimed at `xiaomi-vacuum` and wants devices beyond the Dreame family (Dreame, MOVA, Mijia, and TROUVER transports that share one protocol). A domain rename, a second family package, and a second HACS component are council triggers. Product behavior is not broken. Until a sequence is accepted, the next pull request cannot tell a GitHub rename from a config-entry migration.

**Constraints.**

- Installed users. `manifest.json` `domain` is `dreame_vacuum`, and `DOMAIN` in `custom_components/dreame_vacuum/const.py` is the same string. Config flow `VERSION` is 1. The tree has no `async_migrate_entry`. Entity `unique_id`s are built from the device MAC plus a stable key (room, shortcut, and map ids add their own suffixes) and do not include the domain, except the vacuum entity, whose `unique_id` is `{mac}_` plus `DOMAIN`. Device-registry identifiers are `(DOMAIN, mac)`. `services.yaml` targets `integration: dreame_vacuum`. Home Assistant stores the config entry under that domain. Changing the domain is a migration of entries, the entity registry, and device identifiers, in the same release, and it needs a council record.
- Home Assistant floor. `hacs.json` `homeassistant` is `2024.2.0`. Raising it is a breaking change and is not part of this decision.
- HACS. One custom integration, config-entry only, `zip_release` true, zip filename `dreame_vacuum.zip`. The package directory must match the domain. The HACS zip must not contain `.agent`, tests, or workflows. `iot_class` is `cloud_polling`.
- Secrets. Usernames, passwords, tokens, `auth_key`, `dvc_key`, host, MAC, and device id live in config-entry data. They must not be logged, put on attributes or events, or added to diagnostics. No new runtime dependency is proposed by the option that keeps the domain. TLS verification and the diagnostics redaction list are unchanged by a docs-only or repository-only step. The MIT license and `Copyright (c) 2022 Tasshack` stay.
- Structure already fixed by the rules. A second family is a sibling package that does not import the Dreame family. A shared package is created only in the change that has a second caller. Empty packages and capability tables for a family that does not exist are forbidden.

**Unknowns.**

- How many HACS installs track this fork, `Tasshack/dreame-vacuum`, or a default store listing. The README badges, `documentation`, and `issue_tracker` still point at the Tasshack project. Whether a GitHub rename redirect is enough for HACS to keep updating those installs is not known.
- The second device: no model, protocol, or transport was named. It is not known whether it is a vacuum, whether it works locally, or whether it needs a dependency that is not already in the manifest.
- The target domain string. Collision with another custom component on a user's system was not checked. A non-vacuum device would make a `vacuum` domain a false description.
- Whether Home Assistant 2024.2.0 can change a config entry's domain in place. This integration never does. `async_update_entry` is the public path for data, options, title, and `unique_id`. Domain is not one of those fields in this tree.
- How many automations call services whose target filter is `integration: dreame_vacuum`. No install inventory was available.

**Options.**

1. Sequence inside this integration, and do not rename the domain. The GitHub repository may be renamed toward `xiaomi-vacuum`, and repository docs may say so, in a change that does not edit `custom_components/`, `manifest.json`, or `hacs.json`. The domain stays `dreame_vacuum`. No sibling package, shared package, or capability table is added for a device that does not exist. When a concrete second device exists, it is a sibling package in the pull request that adds that device. That pull request still does not rename the domain. A domain rename is a new council, and only if that device cannot be added under `dreame_vacuum`. Reversibility of the now-step: it writes no Home Assistant storage, so a revert does not touch entries or history. A GitHub rename is not undone for HACS clients by the revert alone (unknown; listed above). The refused domain migration is the hard-to-reverse part, and this option does not do it.
2. Same now-step as option 1, but commit now that the domain rename and its migration ship in the release after the first non-Dreame device, rather than staying an open question. Reversibility of the now-step matches option 1. The later migration is hard to reverse once installs have upgraded: entries, the vacuum `unique_id` that embeds `DOMAIN`, and device identifiers `(DOMAIN, mac)` will have moved, and a revert needs a reverse migration.
3. Rename the domain and add the family layout now. Change the domain, package directory, and HACS zip name in the next release, ship the entry and registry migration in that release, and add a sibling or shared package, or a capability table, before a second device exists. Reversibility: low. After upgrades, storage has moved. Service targets that say `integration: dreame_vacuum` are not rewritten by Home Assistant. There is no migration in the tree today.
4. Separate integration. This repository and the domain stay Dreame permanently. Anything that is not the current family is a new HACS integration with its own domain and repository. Reversibility for installed users: high, because their entries are untouched. The new integration can be abandoned. This repository does not become Xiaomi-wide.
5. Do nothing. No repository rename, no docs change, no package, no migration. Reversibility: total. What stays blocked: the owner's request has no accepted sequence, so the next change can still treat a domain edit as a documentation rename.

## Positions

### Architect

- Option: 2
- Owns: No new package in this decision. The Dreame family package remains the only device core. The shell remains the only owner of the single `DOMAIN` constant, and device-core code remains forbidden to import it or Home Assistant. The pull request that adds a concrete second device owns that sibling package, must not import the Dreame family, and must not add a shared package unless a second caller is in that same change.
- Because: A second family is a sibling package, not a flag inside Dreame and not a second HACS integration. Creating that package, or a capability table, before the device exists is an abstraction with one implementation, which I reject. Renaming the domain now hard-codes a Xiaomi-wide name onto the only family we have. Leaving the domain as `dreame_vacuum` after a sibling lands keeps the integration named for one family, so the rename is the following release, not an open question. A GitHub rename does not hard-code the domain.
- Cost: The repository name and the Home Assistant domain disagree until that later release, and the migration is still unpaid. This stance does not price the installed base.
- Would change my mind if: the second device is in the same pull request as its sibling package, so the domain rename can be judged against two real families instead of scheduled ahead of them.

### Pragmatist

- Option: 1
- User impact: none. An already-configured user keeps the same config entry, the same entities, and the same history, because this step writes no storage.
- Because: No current user outcome needs a storage migration. Config flow `VERSION` is 1, there is no `async_migrate_entry`, and the vacuum `unique_id` embeds `DOMAIN`. Scheduling that rewrite is not required to rename a Git repository or to leave room for a sibling package. The slice that can land now is the repository rename and repository docs, with no file under `custom_components/` changed. The sibling package waits for a concrete device, and the domain stays unless that device cannot be added under it. The ten-family picture is deferred to the Architect, and credential handling to Security.
- Cost: The domain keeps saying Dreame after the repository says Xiaomi, and no second family is started. That delay is intentional.
- Would change my mind if: a named second device cannot be added as a sibling without a new config entry for a vacuum the user already configured, or without a storage migration.

### Security

- Veto: no
- Option: 1
- Because: Option 1 sends no new data out of the house and adds no endpoint, no dependency, and no diagnostic field. Credentials stay in config-entry data; entities must not read them, and logs must not print the entry. Options 2 and 3 would copy password, token, `auth_key`, `dvc_key`, host, MAC, and device id in a migration this council has not designed. I do not veto those options today, because I am not accepting them. I will veto a later migration that logs entry data, turns TLS verification off, expands diagnostics with map or account data, or adds an unreviewed parser. Option 4 duplicates the credential surface for a device that does not exist.
- Cost: Egress, TLS, and dependency review for a second family are deferred. The safer boundary will be awkward to scope, and that scoping waits until a device exists.
- Would change my mind if: the repository-rename change adds a dependency, a cloud endpoint, a user-supplied host, or a fixture captured from a real device.

### Home Assistant conventions

- Option: 1
- HA surface: none
- Because: Option 1 leaves config-entry identity, `unique_id`s, device identifiers, `services.yaml`, the one coordinator per entry, and `iot_class` alone. The domain continues to match the package directory, so the HACS zip and hassfest stay valid on Home Assistant 2024.2.0. A domain rename is not an `async_update_entry` in this tree: `VERSION` is 1, there is no migration, the vacuum `unique_id` embeds `DOMAIN`, device identifiers are `(DOMAIN, mac)`, and `services.yaml` targets `integration: dreame_vacuum`. Those breaks are not required to add a sibling later. A second config entry for a vacuum the user already added is rejected, and the floor is not raised.
- Cost: If the unnamed next device is not a vacuum, the domain `dreame_vacuum` stays a narrow name. That is not a reason to invent a second integration or a new `iot_class` today.
- Would change my mind if: the named device cannot be one config entry under `dreame_vacuum` without a second entry for an existing vacuum, a false `iot_class`, or a helper that 2024.2.0 does not provide.

## Rebuttals

### Architect

Home Assistant conventions is right that `services.yaml` targets `integration: dreame_vacuum`, that the vacuum `unique_id` embeds `DOMAIN`, and that device identifiers are `(DOMAIN, mac)`. I am not switching to option 1. Those facts are the price of option 2, and the Pragmatist can keep refusing to pay it now. They do not make it acceptable to leave the integration named after one family once a sibling exists. Option 2's now-step is the same as option 1, so nothing irreversible is in this decision's first change.

### Pragmatist

No switch. The Architect's "release after the first non-Dreame device" schedules a storage migration before that device exists. Reverting the commit does not restore entries once they have moved. The sibling package can land under `dreame_vacuum` without that migration, which is the sequencing I already asked for.

### Security

No change. I am not vetoing option 2 in advance, and I am not withdrawing the veto line above. Option 2 is not the proposal I support. A later migration that logs or dumps config-entry data, disables TLS, or adds a dependency to perform the rename is the condition that would make the veto `yes` when that migration is actually proposed.

### Home Assistant conventions

No change. A sibling package under the current domain keeps a single coordinator per config entry, leaves `iot_class` as `cloud_polling`, and does not raise the 2024.2.0 floor. I will not pre-approve a domain migration. This version's public entry update does not cover the domain, and service targets that name `dreame_vacuum` would still break.

## Verdict

- Recommendation: Option 1. The GitHub repository may be renamed toward `xiaomi-vacuum`, and repository docs may say so, without changing the Home Assistant domain. The domain stays `dreame_vacuum`. A second device family is a sibling package under this integration, created only in the pull request that adds a concrete device. No capability table, empty package, or shared package lands before that device. The domain is not renamed in that pull request. A domain rename requires a new council, and only if that device cannot be added under `dreame_vacuum`.
- Rejected: Option 2, because only the Architect supported scheduling a domain migration, and the other three refused a storage rewrite that no current device requires. Option 3, because it renames the domain and reserves a family layout while only one family exists, with no migration in the tree and with breaks in `unique_id`s, device identifiers, and `services.yaml`. Option 4, because a second HACS integration duplicates the shell and the credential surface for a device that was not named, and the existing rule is a sibling package inside this integration. Option 5, because it leaves the next pull request free to treat a domain edit as a docs rename. Capability-table groundwork now is rejected with option 3: it is an abstraction with no second caller.
- Dissent: The Architect did not switch. Unedited: "A second family is a sibling package, not a flag inside Dreame and not a second HACS integration. Creating that package, or a capability table, before the device exists is an abstraction with one implementation, which I reject. Renaming the domain now hard-codes a Xiaomi-wide name onto the only family we have. Leaving the domain as `dreame_vacuum` after a sibling lands keeps the integration named for one family, so the rename is the following release, not an open question. A GitHub rename does not hard-code the domain."
- Security veto: none
- Kill criteria: A named second device cannot be added as a sibling package under `dreame_vacuum` without a second config entry for a vacuum the user already has, a false `iot_class`, a helper absent from Home Assistant 2024.2.0, or a new runtime dependency. Or a repository rename strands HACS updates and there is no working retarget. Either observation reconvenes the council. Neither one authorizes a domain migration by itself.
- Next action: In one pull request, update the project paragraph in `AGENTS.md` so it matches option 1 (the repository may be renamed, the domain stays `dreame_vacuum`, and a second family package waits for a concrete device) and link this record, with no edits under `custom_components/` and no change to `manifest.json` or `hacs.json`.
