# 0009 — Which domain lets this fork sit beside Tasshack/dreame-vacuum in HACS?

- Status: accepted
- Date: 2026-11-17
- Supersedes: 0001
- Superseded by: none

## Brief

**Question.** HACS will not list this fork while it uses domain `dreame_vacuum`. Should the integration move to domain `xiaomi_robot_vacuum`, with no migration of existing `dreame_vacuum` config entries?

**Why now.** Frenck's review on hacs/default#13420 (2026-11-17) blocks the default catalog until this fork has its own domain and folder. Council 0001 kept the domain and required a new council before any rename. The maintainer accepted that existing `dreame_vacuum` entries will not carry over.

**Constraints.**

- Installed users. Config entries, the vacuum `unique_id` (`{mac}_` plus `DOMAIN`), and device identifiers `(DOMAIN, mac)` are stored under `dreame_vacuum`. Home Assistant 2024.2.0 cannot change an entry's domain through `async_update_entry`. `async_migrate_entry` runs only for entries of the domain that is loading. A migration inside `xiaomi_robot_vacuum` cannot see `dreame_vacuum` entries, and a migration that reads the other domain's storage would also see entries that belong to Tasshack/dreame-vacuum when both are installed.
- Home Assistant floor. `hacs.json` `homeassistant` stays `2024.2.0`.
- HACS. The package directory, `manifest.json` `domain`, and the zip filename must match. `Tasshack/dreame-vacuum` is already in the default catalog on `dreame_vacuum`. `roquerodrigo/ha-xiaomi-vacuum` is already in that catalog on `xiaomi_vacuum` (`custom_components/xiaomi_vacuum`, manifest version 2.14.0).
- Secrets. Passwords, tokens, `auth_key`, host, MAC, and device id stay in config-entry data. This option does not copy them. The MIT license and `Copyright (c) 2022 Tasshack` stay.
- Name check on 2026-11-17. `home-assistant/core` has no `homeassistant/components/xiaomi_vacuum` or `xiaomi_robot_vacuum` directory (contents API 404). GitHub code search for `"domain": "xiaomi_vacuum"` in `manifest.json` hits the catalog repo above and `Wessie1991/vacuum-mop-pro-2-plus`. The same search for `"domain": "xiaomi_robot_vacuum"` returns no integration manifest. Catalog folders checked beside those: `xiaomi_x20pro`, `xiaomi_vac`, `xiaomi_home`, `xiaomi_cloud_map_extractor`, `dreame_vacuum`.

**Unknowns.**

- How many installs of this fork, rather than of Tasshack/dreame-vacuum, already have a `dreame_vacuum` config entry. No install inventory was available.

**Options.**

1. Rename the domain, package directory, and HACS zip to `xiaomi_robot_vacuum`. Do not migrate `dreame_vacuum` entries, entity registry rows, or device identifiers. Document that an existing `dreame_vacuum` install is not replaced and the user adds the device again. Reversibility: low after a release, because new entries live under the new domain. Before anyone upgrades, reverting the commit restores the old folder.
2. Same rename, plus a storage migration that copies `dreame_vacuum` entries onto `xiaomi_robot_vacuum` and rewrites `unique_id`s and device identifiers. Reversibility: low. The copy cannot tell this fork's entries from a co-installed Tasshack entry, which is the situation the catalog creates.
3. Keep `dreame_vacuum` and stay off the default catalog. Reversibility: high. The HACS listing stays blocked.
4. Do nothing. Reversibility: total. The listing stays blocked, and the next change can still treat a domain edit as a documentation tweak.

## Positions

### Architect

- Option: 1
- Owns: The shell constant `DOMAIN` and the package directory `custom_components/xiaomi_robot_vacuum`. The device core does not import the domain or Home Assistant. No new package. A later family remains a sibling under this shell.
- Because: The collision is the directory, and that directory has to equal the domain. `xiaomi_vacuum` is already another catalog integration's folder, so the free name is `xiaomi_robot_vacuum`. One constant and relative imports are enough. Option 2 teaches the shell to edit another integration's storage. That boundary is the thing I reject. Option 3 leaves the hard-coded `dreame_vacuum` identity that cannot coexist in one catalog.
- Cost: The vacuum `unique_id` embeds `DOMAIN`, and device identifiers are `(DOMAIN, mac)`, so history does not follow. I am not pricing that.
- Would change my mind if: `xiaomi_robot_vacuum` were already a core component or a catalog domain.

### Pragmatist

- Option: 1
- User impact: breaking. A user who already configured this fork deletes the old config entry and adds the device again. History tied to the old `unique_id` stays behind. A user who only runs Tasshack/dreame-vacuum is unaffected until they install this integration.
- Because: The catalog collision is the problem in front of us. The smallest fix is the domain string, the folder, the zip name, services, and translations. The maintainer accepted a re-add. Option 2 is a storage rewrite this outcome does not need, and it cannot tell this fork's entries from Tasshack's once both can be installed. Option 3 does not get the integration listed.
- Cost: Users of v2.1.2 of this fork reconfigure. Service calls aimed at `dreame_vacuum` keep their old target. The ten-family layout is unchanged and stays with the Architect.
- Would change my mind if: Home Assistant 2024.2.0 had a tested way to retarget only this fork's entries, and the maintainer required history to survive.

### Security

- Veto: no
- Option: 1
- Because: Option 1 does not copy password, token, `auth_key`, host, MAC, or device id, and it does not log them. The user types credentials into the new entry. Option 2 would read another domain's config entry. I veto that option unless the migration never logs entry data, never writes secrets into diagnostics, and refuses to run while a `dreame_vacuum` integration is still installed. That design is not proposed here. TLS verification and the diagnostics redaction list stay as they are.
- Cost: Users re-enter cloud passwords. That is more awkward than a silent copy, and it avoids a second copy of the secret.
- Would change my mind if: the rename logged config-entry data or disabled TLS.

### Home Assistant conventions

- Option: 1
- HA surface: manifest, package directory, services, translations, config-flow domain, the vacuum entity `unique_id`, and device identifiers.
- Because: hassfest requires the folder to match the domain. There is no public way on 2024.2.0 to change an entry's domain, and `async_migrate_entry` runs inside the domain that is loading. The old entries are abandoned, not rewritten. The new domain starts with the current config-flow `VERSION` and the same data shape. `iot_class` stays `cloud_polling`. The floor stays `2024.2.0`. Services stay domain-level under the new domain. One coordinator per new entry.
- Cost: Old entities and device-registry rows remain until the user deletes the old entry. Automations that call `dreame_vacuum` services do not retarget.
- Would change my mind if: the minimum Home Assistant version grew a supported domain rename that could distinguish this fork's entries from Tasshack's.

## Rebuttals

### Architect

No change. The Pragmatist's re-add is the cost I left unpriced, and it does not require a second package or a cross-domain storage editor.

### Pragmatist

No change. Home Assistant conventions confirms there is no 2024.2.0 helper that would make option 2 a small, safe slice. I am not switching to it.

### Security

No change. I am not vetoing option 1. The veto line on option 2 stands. Signed map URLs in logs are a separate defect the logging rule already forbids. This decision does not accept leaving them in place, and it does not design that edit.

### Home Assistant conventions

No change. Abandoning `dreame_vacuum` entries is a breaking change and has to be said in the README. It is not a silent migration, and I will not call it one.

## Verdict

- Recommendation: Option 1. The domain, package directory, and HACS zip become `xiaomi_robot_vacuum`. Existing `dreame_vacuum` config entries, vacuum `unique_id`s, and device identifiers are not migrated.
- Rejected: Option 2, because a cross-domain copy cannot tell this fork from Tasshack/dreame-vacuum and no role accepted that risk. Option 3, because it leaves the catalog listing blocked. Option 4, because it leaves the next edit free to treat the rename as a documentation change.
- Dissent: none
- Security veto: none
- Kill criteria: `xiaomi_robot_vacuum` shows up as a core component or as another HACS default integration's domain, or a released build migrates `dreame_vacuum` entries and rewrites a co-installed Tasshack entry. Either observation reconvenes the council.
- Next action: In one pull request, rename the domain to `xiaomi_robot_vacuum` across the manifest, package directory, `hacs.json` filename, release zip, services, translations, `DOMAIN`, tests, and docs; do not add a migration; state in the README that an existing `dreame_vacuum` install is not replaced and the user adds the device again. This record lifts, for this rename only, the requirement to migrate config entries, vacuum `unique_id`s, and device identifiers in the same release. Those identities stay on `dreame_vacuum`. A later change to `xiaomi_robot_vacuum` identities still needs a migration. The same pull request may redact signed map URLs, which the logging rule already requires and which this decision does not redesign.
