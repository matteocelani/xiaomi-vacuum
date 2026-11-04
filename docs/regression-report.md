# Dreame regression report

The Xiaomi work on this fork does not change behavior for any Dreame, MOVA, TROUVER, or Mijia model that was already in the catalog inherited from Tasshack/dreame-vacuum. No Dreame regression was found, and no product code was changed.

## Method

The baseline is the tree this fork inherited: the second parent of `0e763e6` (`Merge pull request #1 from Tasshack/master`), commit `f5b8472b8e2e4bb3dff7bc2a81a5fd594eca9585`. That is also `last_synced_sha` in `.agent/upstream-sync.json`. `git archive` of `custom_components/dreame_vacuum` at that commit is the upstream checkout. Tests do not clone the network and do not call a device.

Current Tasshack `master` is `fec086caf064f2681e8bcc7be20a0d0ef54f444d` (`v2.0.3`), 25 commits ahead of that baseline. Those commits are unsynced upstream work (map rendering, TLS, diagnostics redaction, and similar). They are not Xiaomi regressions, and this comparison does not treat them as failures to fix.

`tests/regression/snapshot_dreame.py` imports one checkout and records, for every catalog model:

- The catalog record, the capability list that record points at, and a SHA-256 of the per-model key. The key itself is not written into the snapshot.
- The model id from the pre-catalog brand rule (`1` xiaomi, `2` mova, `3` trouver, anything else dreame, with `1.0` and `True` still matching `1`) and, on this fork, the id from `load_model_catalog`.
- Capability flags and public attributes after `DreameVacuumDeviceCapability.load`, twice: no properties reported, and every Dreame property reported. Each case is repeated with and without a cloud map manager.
- The static entity set. Platform description lists (`binary_sensor`, `button`, `camera`, `number`, `select`, `sensor`, `switch`, `time`) are filtered with each description's `exists_fn`. Cameras are included only when `capability.map` is true. Segment, shortcut, and room entities depend on a live map and are not synthesized. `vacuum.py` was not modified and still registers one vacuum entity unconditionally.
- Whether `_apply_reported_family` installs a codec. The resolver is called with the catalog model id. Host and token are empty, so no local miIO socket is opened.
- Whether `family_fault_name` returns a name, and whether `controls_of` adds Xiaomi controls.

A second section of the snapshot is shared by every model: property and action maps, `DID` resolution, the Dreame error-name table, `error_name` for every `DreameVacuumErrorCode` with no codec, `split_group_value` / `combine_group_value`, `cleaning_paused`, positive-flag conversion, schedule / DnD / stream / off-peak parsers, map action addresses when `action_mapping` is unset, and the miIO timeout.

`tests/regression/test_inherited_models.py` builds one case per inherited model from the upstream catalog. Nothing in that list is hardcoded.

The inherited commit has no `tests/` directory. There is no upstream test suite to run.

## Counts

| Set | Count |
| --- | --- |
| Inherited models | 763 |
| `dreame.vacuum` | 620 |
| `mova.vacuum` | 121 |
| `trouver.vacuum` | 18 |
| `xiaomi.vacuum` already on the Dreame base | 4 (`c102cn`, `c102gl`, `d103cn`, `d110ch`) |
| Fork catalog | 811 |
| Added by this fork | 48 |

The 48 additions are 42 `xiaomi.vacuum` models and 6 `mijia.vacuum` models (`b108za`, `b108zb`, `b108zh`, `v1`, `v2`, `v3`). Brand code 4 did not occur in the inherited catalog. The old config-flow `else` branch would have called a brand-4 row `dreame.vacuum`. That prefix is used only by these new rows.

## Shared files

Product files that differ from `f5b8472`, outside `custom_components/dreame_vacuum/xiaomi/`:

| File | Dreame path |
| --- | --- |
| `dreame/catalog.py` | New decoder. Config flow model ids go through it. |
| `dreame/const.py` | `DEVICE_INFO` only. The gzip blob was recompressed. Inherited records were not edited. |
| `dreame/device.py` | Codec hook on connect and on property read/write, `DID` uses the instance map, string guards, `cleaning_paused`, positive flags, paused `start` may call `RESUME` when that action is mapped, `error_name` asks the codec first. |
| `dreame/family_codec.py` | Installs maps and a local transport only when a codec is passed in. |
| `dreame/map.py` | Map actions use `DreameVacuumActionMapping` when `action_mapping` is unset. |
| `dreame/protocol.py` | `property_transport` stays `None` unless a codec sets it. Cloud `prop` must be a string before `json.loads`. |
| `dreame/types.py` | `RESUME` action enum, optional `DID` map, codec hook at the end of `capability.load`. |
| `dreame/__init__.py` | Re-exports `load_model_catalog`. |
| `config_flow.py` | `load_devices` calls `load_model_catalog`. |
| `coordinator.py` | Passes `resolve_family` into the device. |
| `entity.py` | `description_exists` requires a mapped action. `control_keys` retains Xiaomi entities only. |
| `binary_sensor.py`, `button.py`, `switch.py`, `time.py` | Extra `exists_fn` checks that the Dreame property or action is on the device map. |
| `number.py`, `select.py`, `sensor.py` | `add_xiaomi_controls` after the Dreame descriptions. |
| `strings.json` | Keys added. No inherited key removed. |
| `xiaomi_controls.py` | New. Adds nothing when the device has no codec. |

## Result

For all 763 inherited models the fork matches the inherited tree:

- Catalog record JSON, capability-list JSON, and key hash.
- `load_model_catalog` id equals the historical brand prefix.
- `resolve_family` does not install a codec, and the Dreame property and action maps are not replaced.
- `family_fault_name` returns `None`. Fault names stay the Dreame table. `error_name` for every error code matches.
- Capability flags and attributes match with no properties reported and with every Dreame property reported.
- Static entity sets match in all four states (empty or fully reported, with or without a map manager).
- Class-level property and action maps match. `DID(siid, piid)` matches. Map `REQUEST_MAP` and `WIFI_MAP` addresses match. miIO timeout stays 2 seconds. `property_transport` stays `None`.

The four inherited `xiaomi.vacuum` models stay on the Dreame base. A codec is not applied to them.

## Discrepancies

No inherited model disagreed on catalog data, flags, maps, entities, or Dreame fault names.

These fork changes are intentional and do not affect Dreame integers, Dreame JSON strings, or the Dreame maps:

| Input | Fork | Inherited tree | Cause |
| --- | --- | --- | --- |
| `cleaning_paused` for `0`, `1`, `2`, bools, and `None` | same | same | Unchanged for Dreame numbers. |
| `cleaning_paused` for `"0"`, `"2"`, `"no"` | `False` | `True` (`bool` of a non-empty string) | Only the string `"1"` is treated as paused. MIoT sends numeric strings. |
| Positive flags for ints, bools, and floats | same as `bool(value > 0)` | same | The attribute builder does not call this when the value is missing. |
| Positive flags for `None` and numeric strings | bool | `TypeError` | `_is_positive_value` accepts MIoT strings. `None` never reaches the old comparison. |
| Schedule, DnD, stream, and off-peak JSON strings | same parsed value | same | Dreame still sends strings. |
| Those properties as a number | ignored | `AttributeError` or `TypeError` | `isinstance(..., str)` before `split` or `json.loads`. |
| `DreameVacuumAction.RESUME` | enum member, not in `DreameVacuumActionMapping` | absent | Paused `start` keeps calling `START` on a Dreame map. |

`description_exists` and the charging, DnD, mapping, and backup `exists_fn` checks are stricter about map membership. Every inherited model still uses the class-level Dreame maps, which contain those properties and actions, so the entity sets stay the same.

## Regressions

Found: 0. Fixed: 0. No product file was edited.
