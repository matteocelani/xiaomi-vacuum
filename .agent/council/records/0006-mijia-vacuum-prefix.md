# 0006 — Where does the mijia vacuum prefix live in the catalog decoder?

- Status: accepted
- Date: 2026-11-04
- Supersedes: none
- Superseded by: none

## Brief

**Question.** Where does the `mijia` model prefix live in the catalog decoder, so a device that reports `mijia.vacuum.*` is accepted without changing how brand codes 0, 1, 2, and 3 resolve?

**Why now.** `mijia.vacuum.b108za`, `b108zb`, and `b108zh` have released MIoT specs. The decoder and the catalog only know `xiaomi`, `mova`, `trouver`, and `dreame`. An unknown brand code becomes `dreame`. Putting these models on brand 1 would publish them as `xiaomi.vacuum.*`, which is not the string the device reports, so the flow would not list them.

**Constraints.**

- Installed users. Domain stays `dreame_vacuum`. No config-entry key, entity `unique_id`, device identifier, or service schema changes. Council 0004 flag rules stay. `xiaomi.vacuum.c102gl`, `c102cn`, `d103cn`, and `d110ch` stay on the Dreame base. A branch on the prefix `xiaomi.vacuum.` or on `capability.mijia` stays forbidden.
- Home Assistant floor. `hacs.json` stays `2024.2.0`. No new runtime dependency. No new package and no new top-level directory.
- Secrets. Spec fixtures are public MIoT documents. No token, host, or device id.
- `DEVICE_INFO` changes are additions. Existing records and existing model-index entries stay. Brand codes in the current blob are only 0, 1, 2, and 3. Equality, not a dict lookup, is what the decoder uses today, so `1.0` and `True` still match brand 1.

**Unknowns.**

- No robot is on this network. The released specs name services and addresses. They do not prove which entities a live 2S or 3S should show.
- Whether a later upstream catalog uses brand 4 for a different brand. It is unused in the blob this record sees.

**Options.**

1. Keep the decoder in `dreame/catalog.py`. Replace the prefix chain with a private table of `(brand code, prefix)` pairs, matched with equality, default `dreame`. Brands 1, 2, and 3 stay `xiaomi`, `mova`, and `trouver`. Brand 4, unused today, is `mijia`. Revert is a commit revert and does not move storage.
2. Add one `elif` for brand 4 and leave the `else` as `dreame`. Revert is a commit revert. The next prefix edits the chain again.
3. Store the three models under brand 1, so the catalog calls them `xiaomi.vacuum.b108za` and the same for the other two. Revert is a commit revert. The flow matches the string the device reports, so those rows would not be offered.
4. Do nothing. The three released models stay unsupported.

## Positions

### Architect

- Option: 1
- Owns: `dreame/catalog.py` owns the brand-to-prefix table and the model id it builds. The Xiaomi package still owns the codec. The shell still calls `load_model_catalog` and does not learn a second prefix parser. Neither family imports the other.
- Because: Option 2 hides the same table inside another branch. Option 3 publishes the wrong model id. A dict lookup would treat `1.0` differently from today's equality and would change resolution the blob does not use but the decoder currently accepts. The table is private data with four callers in this change, not a registry other packages register into. Hard-coding `dreame_vacuum` is not part of this option.
- Cost: Brand 4 is reserved. A later upstream brand 4 would decode as `mijia` until this record is superseded.
- Would change my mind if: the device reported `xiaomi.vacuum.b108za` and the `mijia` string was only a marketing name.

### Pragmatist

- Option: 1
- User impact: none for an already-configured vacuum. Same config entry, same entities, same history. These three models are not in a release.
- Because: The user-visible hole is that the flow cannot name `mijia.vacuum.b108za`. A new package does not fix that. One new record and three index keys are the catalog change. I am deferring token handling to Security. The slice that lands now is the table, these three models, and tests that the existing prefix counts stay put.
- Cost: The next prefix is another row, and brand 4 cannot be reused without a new record.
- Would change my mind if: accepting the models required a new config entry for a vacuum the user already added.

### Security

- Veto: no
- Option: 1
- Because: Option 1 adds no endpoint, no dependency, and no TLS change. Nothing new leaves the house. The token stays on the transport. Spec fixtures are the public released documents, with no token, host, or device id. I will veto an implementation that logs a token, a property body, or a datagram, or that sends an address the released spec does not list. Option 3 is not a secret exposure. It is not the proposal I support.
- Cost: The safer call is the same boundary as 0004. The prefix table does not give the shell a second way to read the token.
- Would change my mind if: decoding the prefix required a property value in a log or a fixture captured from a robot.

### Home Assistant conventions

- Option: 1
- HA surface: none. The flow already matches `load_model_catalog` keys. New entities, if the codec maps any, use the existing descriptions. No service field.
- Because: Config-entry identity, `unique_id`s, device identifiers, `services.yaml`, and the platform list stay put. One coordinator per entry. `iot_class` stays `cloud_polling`. The floor stays `2024.2.0`. hassfest and the HACS zip have nothing new to judge if strings and the manifest stay untouched. A catalog key is how the flow already accepts a model.
- Cost: A user who types a model by hand still uses the string the device reports. This option does not add a repair flow.
- Would change my mind if: the prefix required a second config entry, a service field, or a helper that Home Assistant 2024.2.0 does not provide.

## Rebuttals

### Architect

No change. The Pragmatist is right that the slice is the table and three models. That does not make option 2 smaller once the following prefix arrives.

### Pragmatist

No change. Option 1 is the smallest change that keeps today's equality and lets the next prefix be a row. I am not asking for a new package.

### Security

No change. The veto line stands. Option 1 does not cross it.

### Home Assistant conventions

No change. A catalog prefix keeps a single coordinator and does not raise the floor.

## Verdict

- Recommendation: Option 1. `dreame/catalog.py` owns a private `(brand code, prefix)` table matched with equality. Unlisted brands, including 0, stay `dreame`. Brand 4 is `mijia` because 0, 1, 2, and 3 are already taken and 4 is unused. Existing model ids stay. Domain stays `dreame_vacuum`. Do not add a package, a model-string branch in the shell, or a change to the 0004 flag rules.
- Rejected: Option 2, because the next prefix would edit the chain again and the table is the same size. Option 3, because the flow would look up a model id the device does not report. Option 4, because the three released models stay unsupported.
- Dissent: none
- Security veto: none
- Kill criteria: A model that decodes as `dreame`, `xiaomi`, `mova`, or `trouver` today decodes as a different prefix. Brand 4 is already used by a record in `DEVICE_INFO`. `resolve_family` returns a codec for a model that is not registered. Domain, config-entry identity, `unique_id`s, device identifiers, or a service schema changes. Any of those reconvenes the council.
- Next action: In this pull request, add the prefix table, append one catalog record and the three model-index keys, and register `mijia.vacuum.b108za`, `b108zb`, and `b108zh` from their latest released specs without changing existing prefix resolution.
