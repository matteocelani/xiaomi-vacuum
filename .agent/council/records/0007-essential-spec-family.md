# 0007 — Where does the Essential spec-family profile live?

- Status: accepted
- Date: 2026-11-04
- Supersedes: none
- Superseded by: none

## Brief

**Question.** Where does a third MIoT spec-family profile live, so `mijia.vacuum.v1`, `v2`, and `v3` share it and a later Essential-layout model can declare only diffs, without changing the council 0004 Xiaomi base or the council 0005 sweep profile?

**Why now.** All three models have a released MIoT version 1. Property and action address overlap with the sweep profile (`b112`), ignoring nothing, is about 0.15. Overlap with the station profile (`d109gl`) is about 0.16. The shared addresses do not share a value domain: sweep status wire 1 is Idle and wire 2 is Paused, while these specs use wire 1 for Idle and wire 2 for Sweeping. Sweep mode `2/4` is sweep, sweep-and-mop, or mop. These specs use `2/4` for whole-home, spot, and edge. Action `2/3` is Start Charge here and Start Only Sweep on the sweep profile. The closest one-off layout, E5 (`c108`), shares status wires 1 through 6, but action `2/3` is Pause there and Start Charge here, and `2/5` is suction there and water level here. Copying any of those profiles would send the wrong addresses.

**Constraints.**

- Installed users. Domain stays `dreame_vacuum`. No config-entry key, entity `unique_id`, device identifier, or service schema changes. Council 0004 flag rules, the local miIO transport, and `resolve_family` returning `None` for every model that is not registered stay as they are. Council 0006 brand prefixes stay. `DEVICE_INFO` changes are additions.
- Home Assistant floor. `hacs.json` stays `2024.2.0`. No new runtime dependency. No new package and no new top-level directory.
- Secrets. Spec fixtures are public MIoT documents. No token, host, or device id.
- The 0004 base contract is the codec hook, the explicit maps, the fail-closed flags, and the Dreame catalog path when the codec is `None`. The 0005 sweep profile stays in `sweep.py`. This record does not rewrite either contract.

**Unknowns.**

- No robot is on this network. The released specs name services and addresses. They do not prove which entities a live G1 or Essential should show.
- miot-spec.org also lists version 2 for each model, status `debug`. This record uses released version 1 only. Whether version 2 ever ships is unknown.
- Mop-status values are published as empty descriptions. Remote direction on `v2` and `v3` is the same. This record does not invent those meanings.
- Fault codes 1 through 12 are not the Dreame error vocabulary. The shell error sensor still owns that vocabulary when `ERROR` is mapped.

**Options.**

1. Keep one Xiaomi package and one `XiaomiModel` codec. Leave station tables in `profile.py` and sweep tables in `sweep.py`. Add `essential.py` for the Essential-service addresses, state map, value maps, and controls. A model file composes that profile and declares only its diffs. `v2` and `v3` use `regional_variant` where the released spec differs, and `alias_model` only if a later spec is identical. `resolve_family` still returns the codec. Flags still come from `apply_capabilities`. Revert is a commit revert and does not move storage.
2. Paste the v1 addresses into each model file and refactor a shared profile when a fourth Essential-layout model arrives. Revert is a commit revert. The shared shape is already visible on three model codes, so the split would be a later rewrite of the same tables.
3. Compose the sweep profile, the station profile, or the E5 record, and patch the diffs. Revert is a commit revert. The value domains and several action addresses disagree, so the patch would be most of the profile.
4. Add a second device-family package for this layout. Revert does not move storage. It is a new package the 0004 and 0005 records refused, and both packages would still speak MIoT through the same codec.
5. Do nothing. The three released models stay unsupported.

## Positions

### Architect

- Option: 1
- Owns: `xiaomi/essential.py` owns the Essential spec family. `xiaomi/profile.py` keeps the station family. `xiaomi/sweep.py` keeps the sweep family. Model modules own diffs. None of the three profiles imports another. The shell still sees one facade.
- Because: Option 4 is a second package with one codec and one transport. Option 2 hides a third profile inside copy-paste. Option 3 installs addresses whose values mean something else, including an action that starts charging where another profile pauses. The composers already exist. Hard-coding `dreame_vacuum` is not part of this option. Flag derivation stays on the codec, so an Essential model cannot turn a flag on by naming a station address it did not map.
- Cost: A reader has to know which profile a model composes. E5 stays a one-off because its action table is not this one.
- Would change my mind if: these models used the sweep or station siid table and the same value domain, so another profile had no third caller.

### Pragmatist

- Option: 1
- User impact: none for an already-configured vacuum. Same config entry, same entities, same history. These three models are not in a release.
- Because: The user-visible hole is three models on no spec, or on the wrong one. A new package does not fix that. `v2` changes the voice-language value list and `v3` moves Start Charge from `2/3` to `3/1`, so the variant helper already in `model.py` is the diff. I am deferring token handling to Security. The slice that lands now is the profile, these three models, and tests that the station and sweep lists stay put.
- Cost: `essential.py` is a new module. A value the Dreame select cannot round-trip stays a Xiaomi control until a later row maps it.
- Would change my mind if: shipping the profile required a new config entry for a vacuum the user already added.

### Security

- Veto: no
- Option: 1
- Because: Option 1 adds no endpoint, no dependency, and no TLS change. Nothing new leaves the house. The token stays on the transport. Spec fixtures are the public released documents, with no token, host, or device id. I will veto an implementation that logs a token, a property body, or a datagram, or that sends an address the released spec does not list. Option 4 is not a secret exposure. It is not the proposal I support.
- Cost: The safer call is the same boundary as 0004. The Essential profile does not give the shell a second way to read the token.
- Would change my mind if: mapping the family required a property value in a log or a fixture captured from a robot.

### Home Assistant conventions

- Option: 1
- HA surface: new entities only for the new models, through the existing Xiaomi control descriptions and the existing vacuum entity. New English keys in `strings.json`. No service field.
- Because: Config-entry identity, `unique_id`s, device identifiers, `services.yaml`, and the platform list stay put. One coordinator per entry. `iot_class` stays `cloud_polling`. The floor stays `2024.2.0`. hassfest and the HACS zip have to accept the new `strings.json` keys. The catalog row is the same copied row the other Xiaomi models use, replaced at load by the codec. `DEVICE_INFO` gains index keys only.
- Cost: The shell error sensor names fault codes with the Dreame vocabulary. A control is used where that vocabulary would be the wrong value domain, as with charging state.
- Would change my mind if: the profile required a second config entry, a service field, or a helper that Home Assistant 2024.2.0 does not provide.

## Rebuttals

### Architect

No change. The Pragmatist is right that `regional_variant` already exists. That does not make option 2 smaller once the three model files copy the same tables.

### Pragmatist

No change. Option 1 is the smallest change that lets the next Essential-layout model be a diff. I am not asking for a new package.

### Security

No change. The veto line stands. Option 1 does not cross it.

### Home Assistant conventions

No change. A device-core profile keeps a single coordinator and does not raise the floor.

## Verdict

- Recommendation: Option 1. The Xiaomi base stays the explicit maps, the local miIO transport, and fail-closed flags on `XiaomiModel`. `resolve_family` still selects that codec or returns `None`. Station tables stay in `profile.py`. Sweep tables stay in `sweep.py`. The Essential family lives in `essential.py`. Model files compose it and declare only diffs. `v1` is the base. `v2` replaces the voice-language value list. `v3` replaces that list and moves Start Charge to the battery service. Domain stays `dreame_vacuum`. Do not add a package, a model-string branch in the shell, a map, or a change to the 0004 flag rules. Do not map the debug version 2 documents.
- Rejected: Option 2, because the shared Essential layout is already visible on three model codes. Option 3, because the shared addresses mean different commands and values. Option 4, because a second package does not change the codec and 0004 already refused it. Option 5, because the three released models stay unsupported.
- Dissent: none
- Security veto: none
- Kill criteria: A station or sweep model's property map, action map, or derived flag list changes. An Essential model sends an siid/piid or siid/aiid that its released spec does not list. `resolve_family` returns a codec for a model that is not registered. An existing `DEVICE_INFO` record or index entry changes. Domain, config-entry identity, `unique_id`s, device identifiers, or a service schema changes. Any of those reconvenes the council.
- Next action: In this pull request, add `essential.py`, register `mijia.vacuum.v1`, `v2`, and `v3` on that profile from their released version 1 specs, and test that every spec item is mapped or omitted and that station and sweep capability lists stay put.
