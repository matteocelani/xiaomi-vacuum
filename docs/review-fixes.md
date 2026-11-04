# Review fixes for 54d8b26

The blocking review is fixed on `cursor/review-fail-closed-3510`.
Behavior is in `08a4d5b`. Regression tests are in `fdbbf2c`.
The re-review at `36cfa56` is fixed in the follow-up commit on the same branch.

| ID | Result | Commit | Test |
| --- | --- | --- | --- |
| C-01 | Fixed. `start_custom` raises `InvalidActionException` when `STATUS` or `CLEANING_PROPERTIES` has no piid. `START_CUSTOM` is removed from every Xiaomi family. Zone, segment, and spot services raise `NotSupportedException` unless the model maps the action and both properties. | `08a4d5b` | `tests/dreame/test_fail_closed.py` (`test_start_custom_raises_when_status_is_not_mapped`, `test_no_xiaomi_family_exposes_start_custom_or_a_null_piid`, `test_dreame_start_custom_still_sends_mapped_piids`) |
| H-01 | Fixed. The coordinator passes `CONF_MODEL`. A resolved family is installed before any poll. `xiaomi.*` and `mijia.*` with no family get empty maps and `DeviceException`. A different reported model is logged and ignored. | `08a4d5b` | `test_unresolved_xiaomi_model_fails_closed`, `test_configured_family_is_kept_when_the_robot_reports_another_model` |
| H-02 | Fixed. `set_properties` runs `convert_outgoing` on every value and raises `InvalidValueException` before any write if one property is unmapped. Dreame devices have no codec, so their values are unchanged. | `08a4d5b` | `test_set_properties_rejects_the_whole_write_when_one_property_is_unmapped`, `test_set_properties_converts_every_value_for_a_xiaomi_codec`, `test_dreame_set_properties_still_sends_the_callers_values` |
| M-01 | Fixed, then corrected by N-02 and N-08. The handshake checks host, magic, and length. Encrypted replies still require a checksum, and a checksum or decrypt failure from the right host counts toward the auth lockout. | `08a4d5b` | `tests/xiaomi/test_transport.py` |
| M-02 | Fixed. `send_async` uses `property_transport` for `get_properties` and `set_properties`, and a failed local write raises `device_unavailable` instead of falling through to the cloud. | `08a4d5b` | `test_send_async_uses_the_xiaomi_transport_and_does_not_fall_through` |
| M-03 | Fixed for wire-domain properties. Each model has spec value-lists and ranges in `xiaomi/value_limits.py`. The `+1` shift is per family and only where the spec list starts at 1. Outgoing `STATE` and `TASK_STATUS` now raise; see N-05. | `08a4d5b` | `test_outgoing_suction_uses_the_family_offset_and_rejects_unknown_wires`, `test_wire_limits_allow_published_ranges_and_reject_the_rest`, `test_write_control_rejects_a_value_outside_the_declared_range` |
| M-04 | Fixed. Unknown `STATE` and `TASK_STATUS` wires become `-1` and are logged once at debug. `task_status_code` returns `-1` for a code that is not a stored state. Known docked states still report completed. | `08a4d5b` | `tests/xiaomi/test_mapping.py`, `tests/xiaomi/test_pv11cn.py`, `test_outgoing_suction_uses_the_family_offset_and_rejects_unknown_wires` |
| M-05 | Fixed. A failed control batch no longer raises out of `refresh_controls` or the property poll. A property the robot rejects is dropped from the control store. A transport failure leaves the last good value in place. | `08a4d5b` | `test_refresh_controls_keeps_going_when_one_read_fails`, `tests/xiaomi/spec_helpers.py` (`exercise_rejected_control_traffic`) |
| M-06 | Fixed. Family install from the constructor and from the MQTT callback does not probe. `connect_device` probes on the executor. | `08a4d5b` | `tests/dreame/test_family_codec.py` still expects `apply_family` to probe; the device path passes `probe=False` |
| M-07 | Fixed. The map manager is not created for a family without map properties. A missing action map raises instead of using the Dreame map. `get_aes_key` sends only when `GET_PUBLIC_KEY` is mapped, using that property's siid and piid. | `08a4d5b` | `tests/xiaomi/test_commands.py`, `tests/dreame/test_family_codec.py` |
| M-08 | Fixed. Stream and shortcut actions resolve piids through the device map and raise when the piid is missing. `call_action` rejects a parameter whose piid is `None`. | `08a4d5b` | `test_start_custom_raises_when_status_is_not_mapped` |
| M-09 | Fixed for Xiaomi, then tightened by N-03. `send_command` accepts only `get_properties`, `set_properties`, and `action`. Property calls must be non-empty lists of mapped addresses, and action `in` values are checked. Dreame devices are unchanged. | `08a4d5b` | `test_send_command_rejects_an_unmapped_xiaomi_action`, `test_send_command_rejects_parameters_that_skip_the_allowlist` |
| M-10 | Covered. Every Dreame button `action_key` is in `DreameVacuumActionMapping`, and action-only descriptions still exist on that map. | `fdbbf2c` | `tests/xiaomi/test_dreame_entities.py` |
| M-11 | Fixed. Station addresses live in `xiaomi/station_tables.py` and controls in `xiaomi/station_controls.py`. `profile.py` re-exports them. | `08a4d5b` | `tests/xiaomi/test_mapping.py` (`test_station_address_literals_are_declared_once`) |
| L-01 | Fixed. `XiaomiButton.async_press` also catches `DeviceException`. | `08a4d5b` | Covered with the button entity path; the shell translates `DeviceException` the same way `_commit` does |
| L-02 | Fixed. A number control without a minimum or maximum raises instead of substituting 0. | `08a4d5b` | `test_write_control_rejects_a_value_outside_the_declared_range` |
| L-03 | Fixed. A bool written to a uint8 address is sent as 0 or 1. Bool-format properties stay booleans, which is what the spec exercises assert. | `08a4d5b` | `is_uint8_address` in `test_wire_limits_allow_published_ranges_and_reject_the_rest` |
| L-04 | Fixed. An unknown property or action name in a family map raises `DeviceException`. | `08a4d5b` | Exercised by `apply_family` in the existing family tests |
| L-05 | Fixed. Catalog decode errors become `DeviceException`. | `08a4d5b` | `test_catalog_decode_errors_and_brand_collisions_fail_closed` |
| L-06 | Fixed. `catalog_supports_model` and `DreameVacuumDeviceCapability.load` both require the record's brand prefix to match the full model id. | `08a4d5b` | `test_catalog_decode_errors_and_brand_collisions_fail_closed`, `test_capability_load_rejects_a_brand_that_does_not_own_the_suffix` |
| L-07 | Deferred. A real retry would open more sockets after a timeout, which `test_send_does_not_multiply_the_timeout_when_the_host_is_down` forbids. Random request ids would break the scripted response ids. The backoff from M-01 is the retry policy. | — | — |
| L-08 | Fixed without calling `set_property`. Direct `property_mapping[...]` writes go through `_property_address`, which raises `DeviceException` on a missing key. `set_property` would also schedule updates and dirty state, which would change Dreame behavior. | `08a4d5b` | The missing-key path is the same exception `set_property` already raises |
| L-09 | Fixed. The bare `except` around stop-while-restoring logs the exception and still continues. | `08a4d5b` | No new assertion; the restore path still swallows the failure after logging |
| L-10 | Fixed. The batch-size heuristic and the capability flag treat `mijia.` the same as `xiaomi.`. | `08a4d5b` | `test_unresolved_xiaomi_model_fails_closed` covers a `mijia.` model id |
| L-11 | Fixed. The voice-pack payload is built with `json.dumps`. | `08a4d5b` | No dedicated test; the payload shape for plain strings matches the previous JSON |
| L-12 | Partially fixed. The Xiaomi workflow sets `permissions: contents: read`. Pinning actions and pip packages to SHAs is deferred: a wrong pin fails CI, and the current tags are the workflow's contract. | `08a4d5b` | — |

`xiaomi/value_limits.py` is at 100% line coverage under `pytest --cov=custom_components.dreame_vacuum.xiaomi.value_limits`.

## Re-review at 36cfa56

C-01, H-01, and H-02 stayed closed. The fail-closed follow-up had rejected supported robots and unsigned handshakes.

| ID | Result | Test |
| --- | --- | --- |
| N-01 | Fixed, then narrowed by R3-L01. The four Dreame-protocol models stay on the Dreame maps. Any other `xiaomi.*` or `mijia.*` without a family is closed, even when the catalog contains it. | `test_dreame_protocol_xiaomi_models_keep_the_dreame_catalog`, `test_catalog_model_outside_the_dreame_protocol_allowlist_fails_closed` |
| N-02 | Fixed. The handshake checks the source host, magic `0x2131`, and length 32. Fixtures send the unsigned `0xff` hello that robots send. | `test_unsigned_handshake_is_accepted` |
| N-03 | Fixed. `get_properties` and `set_properties` accept only a non-empty list. `set_properties` runs `convert_outgoing`. Action `in` piids must be mapped and their values must convert. Extra keys are rejected. | `test_send_command_rejects_parameters_that_skip_the_allowlist` |
| N-04 | Fixed. `_remember_reported_model` writes `CONF_MODEL` only when `resolve_family` returns a family, so Dreame and the four Dreame-protocol Xiaomi models are not pinned or reloaded. | `tests/xiaomi/test_reported_model.py` |
| N-05 | Fixed. An integer with no value-list and no range is rejected. The seven bool names may still be written as 0 or 1. | `test_wire_limits_allow_published_ranges_and_reject_the_rest` |
| N-06 | Fixed. `set_properties` turns a codec `XiaomiValueException` into `InvalidValueException` before any write. | `test_set_properties_turns_a_codec_error_into_invalid_value` |
| N-07 | Fixed. `set_carpet_cleaning` adds `CARPET_RECOGNITION`, `CARPET_BOOST`, and `AUTO_MOUNT_MOP` only when that model maps them. Dreame still writes recognition. | `test_set_carpet_cleaning_skips_properties_the_model_does_not_map` |
| N-08 | Fixed. After a packet from the right host is decrypted, a checksum mismatch is an auth failure. Three of them set `local_auth_failed`. One does not. A wrong host stays a protocol failure. | `test_three_checksum_failures_latch_auth` |
| L-06 | Fixed at runtime. Capability loading raises `Unsupported Device!` when the catalog brand does not own the full model id. | `test_capability_load_rejects_a_brand_that_does_not_own_the_suffix` |
| STATE / TASK_STATUS | Fixed. `convert_outgoing` raises `XiaomiValueException` for both names. Incoming conversion is unchanged. | `test_outgoing_suction_uses_the_family_offset_and_rejects_unknown_wires` |
| L-07 | Still deferred. Retries and random request ids stay as recorded above. | — |
| L-12 | Still deferred. Action and pip SHA pins stay as recorded above. | — |

## Re-review at b42f68f

R3 approved with reservations: no Critical or High findings. These rows close the two Medium findings and the Lows that were safe to change.

| ID | Result | Test |
| --- | --- | --- |
| R3-M01 | Fixed. `convert_outgoing` accepts only the spec format: bool (and 0 or 1), integer types, float, or a non-numeric string. `None`, lists, bools where an int is expected, and numeric strings raise on every outgoing path, including `send_command`. | `tests/xiaomi/test_outgoing_types.py` |
| R3-M02 | Fixed. An action input piid must be in that action's spec `in` list and must resolve with `_property_for_address(siid, piid)`. A piid from another service is not accepted. | `test_action_inputs_follow_the_spec_for_every_family`, `test_action_input_uses_the_action_service_not_another_piid` |
| R3-L01 | Fixed. The Dreame-protocol fallback is the allowlist `c102cn`, `c102gl`, `d103cn`, `d110ch`, not catalog presence. | `test_catalog_model_outside_the_dreame_protocol_allowlist_fails_closed` |
| R3-L02 | Fixed. During local auth lockout, `get_properties` uses the cloud when cloud credentials exist. `set_properties` still stops locally. | `test_locked_local_reads_use_cloud_when_credentials_exist` |
| R3-L03 | Fixed. The decoded catalog is cached, so repeated model checks do not decompress the blob again. | `test_decoded_catalog_is_reused` |
