# 0008 — How to drop the stored card license key

- Status: accepted
- Date: 2026-11-09
- Supersedes: none
- Superseded by: none

## Brief

**Question.** When the closed-source Dreame Vacuum Card stops shipping, how should an existing config entry that stored `dvc_key` lose that key without a new entry, a new `unique_id`, or a failed setup?

**Why now.** The HACS default review (hacs/default#13420) rejects the release because it bundles that card, its license client, and a purchase step. Installed entries already store the license in options. Leaving the key in place keeps a credential this integration will no longer use. Deleting it is a config-entry storage change, which this council has to decide before the code changes.

**Constraints.**

- Installed users. Domain stays `dreame_vacuum`. Entry id, `unique_id`, device identifiers, and service schemas stay. Config flow `VERSION` is 1 and the tree has no `async_migrate_entry`. Vacuum, sensor, select, camera, and service behavior stay. The card is not part of that behavior.
- Home Assistant floor. `hacs.json` stays `2024.2.0`. No new runtime dependency. `http` stays a manifest dependency because the map camera registers views on it. `lovelace` is an `after_dependencies` entry used only to register the card.
- HACS. The zip is the integration package. It must not contain `frontend.py` or the bundled script. hassfest and HACS validation still have to pass. The integration version becomes `v2.1.2` in the same release so a later tag can match the manifest.
- Secrets. `dvc_key` is a purchased license. It lives in options today. Diagnostics already redact that key. The migration must not log the value. No token, host, or device id is added to the tree.

**Unknowns.**

- Whether any entry stored `dvc_key` in `data` as well as options. The flow writes it to options. The migration treats both stores the same so an unexpected copy cannot survive.
- How many installed entries have a non-empty key. The count does not change the storage shape.

**Options.**

1. Bump config flow `VERSION` from 1 to 2 and add `async_migrate_entry` that deletes `dvc_key` from options and from data. Leave the entry id, `unique_id`, credentials, and every other option. New flows never write the key. Keep `dvc_key` on the diagnostics redaction list. Revert of the commit does not put a deleted key back.
2. Leave the key in storage and ignore it. Entries still load, because Home Assistant does not reject an unused option. The license stays in options. Revert is a code revert and does not touch storage.
3. Do nothing. The card, the license client, and the purchase step stay, and the HACS default review stays blocked.

## Positions

### Architect

- Option: 1
- Owns: the shell. `ConfigFlow.VERSION` in `config_flow.py`, and `async_migrate_entry` in the integration `__init__.py`. The device core does not learn the key. No new package.
- Because: The key is entry storage, which the shell already owns. A second family does not need a plugin or a shared helper to forget one option. The domain stays the existing constant, so a later rename does not gain a new hard-coded path. The migration is a deletion of one key, not a condition inside the Dreame family.
- Cost: Config flow `VERSION` moves from 1 to 2, and every existing entry is rewritten once. That rewrite is the point of the option. A later family still adds a sibling package; this change does not reserve one.
- Would change my mind if: the key were read by the device core, or two families needed a shared store for it.

### Pragmatist

- Option: 1
- User impact: none for identity. The same config entry, the same entities, and the same history stay. The embedded card goes away, which is the outcome the review requires.
- Because: Option 2 leaves a license in options after the only reader is gone. Option 3 does not unblock the catalog. The migration is the small storage edit the user-visible removal needs, not a refactor of the inherited integration. Vacuum setup does not depend on the key. The slice is one pull request: delete the card, stop writing the key, and migrate entries that already have it.
- Cost: Revert of the commit does not restore a deleted key. The key has no function once the card is gone, so that restore has no user outcome. The inherited options-version copy in the coordinator stays for the map-object migration it already performs.
- Would change my mind if: an installed entry failed setup unless `dvc_key` was still present.

### Security

- Veto: no
- Option: 1
- Because: The license client sends the key, a device-derived token, and a hash of the integration source to `api.tasshack.com`. Removing that client stops that data from leaving the house. `dvc_key` is a credential stored in options, which this integration should not keep once nothing reads it. Deleting it on migration removes the credential from the entry. Diagnostics keep redacting the key so a dump taken before migration, or a nested copy, stays masked. The migration must not log the value. TLS verification is unchanged. No endpoint is added. No dependency is added.
- Cost: A user who paid for a card key loses the stored copy in this integration. The card itself is no longer shipped, so the stored copy cannot activate it here.
- Would change my mind if: the value were not a credential, or the migration printed the entry.

### Home Assistant conventions

- Option: 1
- HA surface: flow, coordinator, manifest
- Because: A storage-format change increments `VERSION` and implements `async_migrate_entry`. Shipping the deletion without that migration fails review. Entry id, `unique_id`, and device identifiers stay. There is still one coordinator per entry. The removed step's strings leave `strings.json` and the locale catalogs. `services.yaml` has no card field. `iot_class` stays `cloud_polling`. `http` stays because the map camera registers views. `lovelace` leaves `after_dependencies` because only the card used it. The floor stays `2024.2.0`. `async_update_entry` on that floor has no `version` argument, so the migration assigns `entry.version` and then updates data and options. hassfest and the HACS zip stay valid with the package at the archive root.
- Cost: Entries created by a future downgrade to a build that still shows the card step would not understand version 2. That build is the one this change removes.
- Would change my mind if: the floor's config-entry API could not persist a version bump without a newer Home Assistant.

## Rebuttals

### Architect

no change

### Pragmatist

no change

### Security

no change

### Home Assistant conventions

no change

## Verdict

- Recommendation: option 1
- Rejected: option 2, because it leaves a license credential in options after the card is gone. Option 3, because it leaves the HACS review blocked.
- Dissent: none
- Security veto: none
- Kill criteria: an existing entry fails to set up, a `unique_id` or device identifier changes, or a new flow writes `dvc_key`.
- Next action: In one pull request, remove the card bundle, the license client, the purchase step, and the upgrade notification; migrate version 1 entries by deleting `dvc_key` from options and data; keep diagnostics redaction; bump the integration version to `v2.1.2`.
