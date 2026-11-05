# Xiaomi deep-test report

Fetched 2026-11-04 from `https://miot-spec.org/miot-spec-v2/instance?type=<urn>`.
Suites live in `tests/xiaomi/deep/test_deep_<code>.py` and read `tests/xiaomi/specs/`.
The run after the approved surface landed is `19108 passed, 0 xfailed, 0 failed` (`pytest tests/xiaomi/deep`).

## Summary

48 models. The 85 approved entities and the `xiaomi_add_schedule` service are covered by spec-generated writes in `tests/xiaomi/deep/test_deep_surface.py`. The five properties left out of the plan stay unmapped, and each omission names `docs/unmapped-props-plan.md`. `pv32gl` stays on spec version 2, and `ota-info` (siid 20, aiid 16) is not mapped.

The seven fail-closed bugs from PR #37 are on `master` and the old xfails are gone. `start_custom` uses `STATE` when `STATUS` is unmapped and still raises, without sending, when the custom action itself is unmapped. A control refresh that gets a non-list batch reads the controls one by one. An unpublished status wire is stored as `-1`, not as a completed task.

| Id | Severity | Cases | Status | What the suite shows |
| --- | --- | --- | --- | --- |
| E5 faults | medium | 16 codes | fixed in `15d0c30` | c108 value-list was shown with Dreame error names |
| C-01 | high | 33 | passing on the fail-closed master | `start_custom` does not send a missing piid |
| H-01 | high | 48 | passing on the fail-closed master | the configured model installs its family before miIO info |
| H-02 | high | 34 | passing on the fail-closed master | `set_properties` uses `convert_outgoing` |
| M-02 | medium | 48 | passing on the fail-closed master | `send_async` uses the Xiaomi transport |
| M-03 | medium | 48 | passing on the fail-closed master | outgoing values outside the spec list or range are refused |
| M-04 | medium | 48 | passing on the fail-closed master | an unknown status wire does not complete the task |
| M-05 | medium | 43 | passing on the fail-closed master | one failed control read does not fail the refresh |

Mapped addresses, control options, control ranges, status value-lists, task value-lists, and fault labels that the spec names all match the fetched documents. Alias and regional records do not point at an siid/piid the sub-model's spec lacks. Missing or invalid miIO credentials keep the cloud path.

Four latest documents differ from the live fetch by a doubled space in the "Frequency Mop Wash No Tank" descriptions (`ov31gl`, `pv32gl`, `qv41gl`, `qv42gl`, and the same text on their v1 files). Values, access, and ranges are unchanged. That is spec text, not a codec bug.

## Open questions

The 180 writable properties are no longer open xfails. 85 are entities, 90 are the `xiaomi_add_schedule` service, and 5 stay omitted with a reason in this file's plan. What is still unanswered, and does not fail the suite:

- The weekday bitmask in `day` (0..255) does not say which bit is Monday.
- Twice-clean is published on all 10 sweep models and is not an `in` parameter of add-ii, so the service rejects it instead of sending it.
- Write-only sweep settings assume state after a write. The robot does not publish a read.
- The two custom bools are unnamed. They are diagnostic. Write-only settings are not polled; the entity shows the last accepted write.
- `b108zh` fan mode in the committed spec is Full Speed (4), the same list as `b108za` and `b108zb`, not Strong (3).
- The `pv32gl` catalog still lists only version 1 as released. The integration stays on version 2 and does not expose `ota-info`.

The table below is the original inventory. The implementation is in `docs/unmapped-props-plan.md`.

| Count | Token | Description |
| --- | --- | --- |
| 10 | `enable` | (empty) |
| 10 | `day` | (empty) |
| 10 | `hour` | (empty) |
| 10 | `minute` | (empty) |
| 10 | `repeat` | (empty) |
| 10 | `clean-way` | (empty) |
| 10 | `suction` | (empty) |
| 10 | `water` | (empty) |
| 10 | `twice-clean` | (empty) |
| 10 | `remember-state` | (empty) |
| 7 | `carpet-avoid` | (empty) |
| 7 | `precise-diagnosis` | (empty) |
| 7 | `water-level-remind` | (empty) |
| 5 | `clean-times` | Clean Times |
| 5 | `alarm` | Alarm |
| 4 | `mode` | Mode |
| 4 | `sweep-avoid` | (empty) |
| 4 | `mop-avoid` | (empty) |
| 3 | `carpet-avoidance` | carpet-avoidance |
| 2 | `carpet-discriminate` | Carpet Discriminate |
| 2 | `back-wash-area` | (empty) |
| 2 | `detergent-self-delivery` | Detergent Self Delivery |
| 1 | `edge-swing-tail-sweep` | Edge Swing Tail Sweep |
| 1 | `edge-sweep-frequency` | Edge Sweep Frequency |
| 1 | `dry-time` | dry-time |
| 1 | `dry-time` | (empty) |
| 1 | `carpet-avoidance` | Carpet Avoidance |
| 1 | `enable-mop-wash` | Enable Mop Wash |
| 1 | `frequency-mop-wash` | Frequency Mop Wash |
| 1 | `water-output-for-washing-mop` | Water Output For Washing Mop |
| 1 | `drying-time` | Drying Time |
| 1 | `auto-mop-dry` | Auto Mop Dry |
| 1 | `auto-water-change` | Auto Water Change |
| 1 | `use-detergent` | Use Detergent |
| 1 | `mop-water-output-level-no-tank` | Mop Water Output Level No Tank |
| 1 | `frequency-mop-wash-no-tank` | Frequency Mop Wash No Tank |
| 1 | `detergent-depletion-reminder` | Detergent Depletion Reminder |
| 1 | `sweep-route` | Sweep Route |
| 1 | `obstacle-avoidance-strategy` | Obstacle Avoidance Strategy |
| 1 | `carpet-deep-cleaning` | Carpet Deep Cleaning |
| 1 | `sweep-carpet-first` | Sweep Carpet First |
| 1 | `mop-outer-swing` | Mop Outer Swing |
| 1 | `mop-outer-swing-frequency` | Mop Outer Swing Frequency |
| 1 | `frequency-mop-wash-by-time` | Frequency Mop Wash By Time |
| 1 | `auto-dust-arrest-power-level` | Auto Dust Arrest Power Level |
| 1 | `worry-free-clean-mode` | Worry Free Clean Mode |
| 1 | `wash-mop-water-temperature` | Wash Mop Water Temperature |
| 1 | `detergent-self-delivery-level` | Detergent Self Delivery Level |
| 1 | `sewage-self-cleaning` | (empty) |
| 1 | `self-cleaning-time` | (empty) |

`xiaomi.vacuum.pv32gl` maps spec version 2. The instance catalog lists only version 1 as released. Version 2 still downloads. Field robots may be on version 1.

## What only a real robot can show

The owner has an S20+ (`xiaomi.vacuum.b108gl`). These checks need that device:

- Local miIO handshake and the cloud fallback after a failed probe.
- Edge Swing Tail Sweep (`2/17`) and Edge Sweep Frequency (`2/18`). The spec publishes them; this record does not map them. The open-question test names both.
- Cleaning-mode wire 4, Sweep Before Mopping. The global +1 offset can send it. M-03 covers the refusal. Whether the robot accepts it is hardware.
- Station models whose fault property is a `uint32` range. The spec names no code, so Dreame labels stay. Only the robot can confirm them.
- Map, schedule, voice, and remote actions. The suites omit them with a spec rule. They are not exercised on a device.
- Self-check and summon wires. The codec stores some of them as an unknown shell state or as sweeping. The spec description is ambiguous.

## Per model

### mijia.vacuum.b108za

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:mijia-b108za:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/b108za.json`. Suite: `tests/xiaomi/deep/test_deep_b108za.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 57, mapped 27, omitted 26, open 4.
- Spec actions 42, mapped 11, omitted 31.
- Controls 0. Value-list samples 29. Named fault codes 0.
- Generated cases include 38 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 2/7 clean-times, 2/16 mode, 4/1 alarm, 6/7 carpet-avoidance.
- Known defects left xfailed: H-01, M-02, M-03, M-04, C-01, H-02.

### mijia.vacuum.b108zb

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:mijia-b108zb:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/b108zb.json`. Suite: `tests/xiaomi/deep/test_deep_b108zb.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 57, mapped 27, omitted 26, open 4.
- Spec actions 42, mapped 11, omitted 31.
- Controls 0. Value-list samples 29. Named fault codes 0.
- Generated cases include 38 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 2/7 clean-times, 2/16 mode, 4/1 alarm, 6/7 carpet-avoidance.
- Known defects left xfailed: H-01, M-02, M-03, M-04, C-01, H-02.

### mijia.vacuum.b108zh

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:mijia-b108zh:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/b108zh.json`. Suite: `tests/xiaomi/deep/test_deep_b108zh.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 57, mapped 27, omitted 26, open 4.
- Spec actions 42, mapped 11, omitted 31.
- Controls 0. Value-list samples 29. Named fault codes 0.
- Generated cases include 38 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 2/7 clean-times, 2/16 mode, 4/1 alarm, 6/7 carpet-avoidance.
- Known defects left xfailed: H-01, M-02, M-03, M-04, C-01, H-02.

### mijia.vacuum.v1

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:mijia-v1:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/v1.json`. Suite: `tests/xiaomi/deep/test_deep_v1.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 31, mapped 22, omitted 9, open 0.
- Spec actions 9, mapped 9, omitted 0.
- Controls 14. Value-list samples 6. Named fault codes 13.
- Generated cases include 31 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.
- No spec/code mismatch beyond those known defects.

### mijia.vacuum.v2

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:mijia-v2:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/v2.json`. Suite: `tests/xiaomi/deep/test_deep_v2.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 31, mapped 22, omitted 9, open 0.
- Spec actions 9, mapped 9, omitted 0.
- Controls 14. Value-list samples 6. Named fault codes 13.
- Generated cases include 31 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.
- No spec/code mismatch beyond those known defects.

### mijia.vacuum.v3

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:mijia-v3:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/v3.json`. Suite: `tests/xiaomi/deep/test_deep_v3.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 31, mapped 22, omitted 9, open 0.
- Spec actions 9, mapped 9, omitted 0.
- Controls 14. Value-list samples 6. Named fault codes 13.
- Generated cases include 31 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.b106bk

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b106bk:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/b106bk.json`. Suite: `tests/xiaomi/deep/test_deep_b106bk.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 125, mapped 34, omitted 80, open 11.
- Spec actions 52, mapped 8, omitted 44.
- Controls 29. Value-list samples 9. Named fault codes 0.
- Generated cases include 45 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 7/47 carpet-avoid, 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.b106eu

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b106eu:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/b106eu.json`. Suite: `tests/xiaomi/deep/test_deep_b106eu.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 125, mapped 34, omitted 80, open 11.
- Spec actions 52, mapped 8, omitted 44.
- Controls 29. Value-list samples 9. Named fault codes 0.
- Generated cases include 45 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 7/47 carpet-avoid, 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.b108gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b108gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/b108gl.json`. Suite: `tests/xiaomi/deep/test_deep_b108gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 69, mapped 28, omitted 35, open 6.
- Spec actions 47, mapped 11, omitted 36.
- Controls 0. Value-list samples 28. Named fault codes 0.
- Generated cases include 39 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 2/7 clean-times, 2/16 mode, 2/17 edge-swing-tail-sweep, 2/18 edge-sweep-frequency, 2/21 carpet-discriminate, 4/1 alarm.
- Known defects left xfailed: H-01, M-02, M-03, M-04, C-01, H-02.

### xiaomi.vacuum.b112

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b112:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/b112.json`. Suite: `tests/xiaomi/deep/test_deep_b112.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 112, mapped 28, omitted 74, open 10.
- Spec actions 46, mapped 8, omitted 38.
- Controls 23. Value-list samples 9. Named fault codes 0.
- Generated cases include 39 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.b112bk

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b112bk:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/b112bk.json`. Suite: `tests/xiaomi/deep/test_deep_b112bk.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 112, mapped 28, omitted 74, open 10.
- Spec actions 46, mapped 8, omitted 38.
- Controls 23. Value-list samples 9. Named fault codes 0.
- Generated cases include 39 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.b112gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-b112gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/b112gl.json`. Suite: `tests/xiaomi/deep/test_deep_b112gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 112, mapped 28, omitted 74, open 10.
- Spec actions 46, mapped 8, omitted 38.
- Controls 23. Value-list samples 9. Named fault codes 0.
- Generated cases include 39 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.c101

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c101:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/c101.json`. Suite: `tests/xiaomi/deep/test_deep_c101.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 139, mapped 38, omitted 86, open 15.
- Spec actions 57, mapped 8, omitted 49.
- Controls 33. Value-list samples 13. Named fault codes 0.
- Generated cases include 49 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 7/47 carpet-avoid, 7/57 sweep-avoid, 7/58 mop-avoid, 7/62 back-wash-area, 7/63 dry-time, 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.c101eu

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c101eu:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/c101eu.json`. Suite: `tests/xiaomi/deep/test_deep_c101eu.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 144, mapped 38, omitted 91, open 15.
- Spec actions 58, mapped 8, omitted 50.
- Controls 33. Value-list samples 13. Named fault codes 0.
- Generated cases include 49 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 7/47 carpet-avoid, 7/57 sweep-avoid, 7/58 mop-avoid, 7/62 back-wash-area, 7/63 dry-time, 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.c103

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c103:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/c103.json`. Suite: `tests/xiaomi/deep/test_deep_c103.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 133, mapped 36, omitted 84, open 13.
- Spec actions 58, mapped 8, omitted 50.
- Controls 31. Value-list samples 11. Named fault codes 0.
- Generated cases include 47 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 7/47 carpet-avoid, 7/57 sweep-avoid, 7/58 mop-avoid, 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.c104

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c104:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/c104.json`. Suite: `tests/xiaomi/deep/test_deep_c104.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 127, mapped 34, omitted 82, open 11.
- Spec actions 53, mapped 8, omitted 45.
- Controls 29. Value-list samples 9. Named fault codes 0.
- Generated cases include 45 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 7/47 carpet-avoid, 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.c107

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c107:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/c107.json`. Suite: `tests/xiaomi/deep/test_deep_c107.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 126, mapped 84, omitted 42, open 0.
- Spec actions 68, mapped 33, omitted 35.
- Controls 72. Value-list samples 39. Named fault codes 0.
- Generated cases include 117 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.c108

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-c108:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/c108.json`. Suite: `tests/xiaomi/deep/test_deep_c108.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 31, mapped 20, omitted 11, open 0.
- Spec actions 13, mapped 10, omitted 3.
- Controls 15. Value-list samples 7. Named fault codes 16.
- Generated cases include 30 mapped-address checks.
- Fault names were Dreame labels. Fixed in `15d0c30`. The suite now requires each spec description.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.d101

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-d101:3`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/d101.json`. Suite: `tests/xiaomi/deep/test_deep_d101.py`.
- Catalog released versions: [1, 2, 3]. Mapped version: 3.
- Spec properties 89, mapped 53, omitted 36, open 0.
- Spec actions 63, mapped 27, omitted 36.
- Controls 41. Value-list samples 42. Named fault codes 0.
- Generated cases include 80 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.d102ev

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-d102ev:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/d102ev.json`. Suite: `tests/xiaomi/deep/test_deep_d102ev.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 107, mapped 68, omitted 39, open 0.
- Spec actions 62, mapped 29, omitted 33.
- Controls 53. Value-list samples 39. Named fault codes 0.
- Generated cases include 97 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.d102gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-d102gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/d102gl.json`. Suite: `tests/xiaomi/deep/test_deep_d102gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 114, mapped 70, omitted 44, open 0.
- Spec actions 64, mapped 29, omitted 35.
- Controls 55. Value-list samples 39. Named fault codes 0.
- Generated cases include 99 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.d106gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-d106gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/d106gl.json`. Suite: `tests/xiaomi/deep/test_deep_d106gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 138, mapped 36, omitted 89, open 13.
- Spec actions 59, mapped 8, omitted 51.
- Controls 31. Value-list samples 11. Named fault codes 0.
- Generated cases include 47 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 7/47 carpet-avoid, 7/57 sweep-avoid, 7/58 mop-avoid, 8/2 enable, 8/3 day, 8/4 hour, 8/5 minute, 8/6 repeat, 8/7 clean-way, 8/8 suction, 8/9 water, 8/10 twice-clean, 10/1 remember-state.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05.

### xiaomi.vacuum.d109gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-d109gl:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/d109gl.json`. Suite: `tests/xiaomi/deep/test_deep_d109gl.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 120, mapped 32, omitted 59, open 29.
- Spec actions 64, mapped 13, omitted 51.
- Controls 0. Value-list samples 39. Named fault codes 0.
- Generated cases include 45 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 2/8 clean-times, 2/21 carpet-avoidance, 2/28 enable-mop-wash, 2/29 frequency-mop-wash, 2/30 water-output-for-washing-mop, 2/31 drying-time, 2/34 auto-mop-dry, 2/35 auto-water-change, 2/36 use-detergent, 2/59 detergent-self-delivery, 2/60 mop-water-output-level-no-tank, 2/61 frequency-mop-wash-no-tank, 2/71 detergent-depletion-reminder, 2/74 sweep-route, 2/75 obstacle-avoidance-strategy, 2/76 carpet-deep-cleaning, 2/77 carpet-discriminate, 2/78 sweep-carpet-first, 2/79 mop-outer-swing, 2/80 mop-outer-swing-frequency, 2/81 frequency-mop-wash-by-time, 2/82 auto-dust-arrest-power-level, 2/83 worry-free-clean-mode, 2/84 wash-mop-water-temperature, 4/1 alarm, 18/2 detergent-self-delivery, 18/3 detergent-self-delivery-level, 20/7 sewage-self-cleaning, 20/8 self-cleaning-time.
- Known defects left xfailed: H-01, M-02, M-03, M-04, C-01, H-02.

### xiaomi.vacuum.e101gb

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-e101gb:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/e101gb.json`. Suite: `tests/xiaomi/deep/test_deep_e101gb.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 148, mapped 98, omitted 50, open 0.
- Spec actions 85, mapped 38, omitted 47.
- Controls 88. Value-list samples 46. Named fault codes 0.
- Generated cases include 136 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.ov21cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov21cn:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov21cn.json`. Suite: `tests/xiaomi/deep/test_deep_ov21cn.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 175, mapped 117, omitted 58, open 0.
- Spec actions 101, mapped 42, omitted 59.
- Controls 111. Value-list samples 46. Named fault codes 0.
- Generated cases include 159 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.ov21gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov21gl:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov21gl.json`. Suite: `tests/xiaomi/deep/test_deep_ov21gl.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 172, mapped 115, omitted 57, open 0.
- Spec actions 100, mapped 42, omitted 58.
- Controls 109. Value-list samples 46. Named fault codes 0.
- Generated cases include 157 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.ov31cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov31cn:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov31cn.json`. Suite: `tests/xiaomi/deep/test_deep_ov31cn.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 147, mapped 92, omitted 54, open 1.
- Spec actions 85, mapped 41, omitted 44.
- Controls 85. Value-list samples 46. Named fault codes 0.
- Generated cases include 133 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 20/10 precise-diagnosis.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.ov31gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov31gl:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov31gl.json`. Suite: `tests/xiaomi/deep/test_deep_ov31gl.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 145, mapped 91, omitted 53, open 1.
- Spec actions 85, mapped 41, omitted 44.
- Controls 84. Value-list samples 46. Named fault codes 0.
- Generated cases include 132 mapped-address checks.
- Live fetch inserts a doubled space in Frequency Mop Wash No Tank descriptions. Values are unchanged.
- Unmapped writable properties, xfailed as open questions: 20/10 precise-diagnosis.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.ov42cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov42cn:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov42cn.json`. Suite: `tests/xiaomi/deep/test_deep_ov42cn.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 167, mapped 108, omitted 58, open 1.
- Spec actions 90, mapped 41, omitted 49.
- Controls 101. Value-list samples 46. Named fault codes 0.
- Generated cases include 149 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 20/13 water-level-remind.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.ov42gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov42gl:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov42gl.json`. Suite: `tests/xiaomi/deep/test_deep_ov42gl.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 161, mapped 108, omitted 52, open 1.
- Spec actions 89, mapped 41, omitted 48.
- Controls 101. Value-list samples 46. Named fault codes 0.
- Generated cases include 149 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 20/13 water-level-remind.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.ov43gb

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov43gb:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov43gb.json`. Suite: `tests/xiaomi/deep/test_deep_ov43gb.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 167, mapped 114, omitted 53, open 0.
- Spec actions 96, mapped 42, omitted 54.
- Controls 108. Value-list samples 46. Named fault codes 0.
- Generated cases include 156 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.ov51gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov51gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov51gl.json`. Suite: `tests/xiaomi/deep/test_deep_ov51gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 148, mapped 98, omitted 50, open 0.
- Spec actions 88, mapped 41, omitted 47.
- Controls 91. Value-list samples 46. Named fault codes 0.
- Generated cases include 139 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.ov71gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov71gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov71gl.json`. Suite: `tests/xiaomi/deep/test_deep_ov71gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 129, mapped 81, omitted 48, open 0.
- Spec actions 82, mapped 37, omitted 45.
- Controls 73. Value-list samples 46. Named fault codes 0.
- Generated cases include 118 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.ov81cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov81cn:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov81cn.json`. Suite: `tests/xiaomi/deep/test_deep_ov81cn.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 102, mapped 50, omitted 52, open 0.
- Spec actions 63, mapped 21, omitted 42.
- Controls 29. Value-list samples 36. Named fault codes 0.
- Generated cases include 71 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.ov81gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-ov81gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/ov81gl.json`. Suite: `tests/xiaomi/deep/test_deep_ov81gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 149, mapped 99, omitted 50, open 0.
- Spec actions 88, mapped 41, omitted 47.
- Controls 92. Value-list samples 46. Named fault codes 0.
- Generated cases include 140 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.pv11cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv11cn:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/pv11cn.json`. Suite: `tests/xiaomi/deep/test_deep_pv11cn.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 178, mapped 112, omitted 64, open 2.
- Spec actions 104, mapped 41, omitted 63.
- Controls 106. Value-list samples 44. Named fault codes 0.
- Generated cases include 153 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 20/10 precise-diagnosis, 20/13 water-level-remind.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.pv11gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv11gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/pv11gl.json`. Suite: `tests/xiaomi/deep/test_deep_pv11gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 169, mapped 110, omitted 57, open 2.
- Spec actions 101, mapped 40, omitted 61.
- Controls 103. Value-list samples 43. Named fault codes 0.
- Generated cases include 150 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 20/10 precise-diagnosis, 20/13 water-level-remind.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.pv21cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv21cn:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/pv21cn.json`. Suite: `tests/xiaomi/deep/test_deep_pv21cn.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 170, mapped 107, omitted 61, open 2.
- Spec actions 101, mapped 38, omitted 63.
- Controls 101. Value-list samples 44. Named fault codes 0.
- Generated cases include 145 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 20/10 precise-diagnosis, 20/13 water-level-remind.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.pv21gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv21gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/pv21gl.json`. Suite: `tests/xiaomi/deep/test_deep_pv21gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 167, mapped 108, omitted 57, open 2.
- Spec actions 100, mapped 39, omitted 61.
- Controls 103. Value-list samples 44. Named fault codes 0.
- Generated cases include 147 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 20/10 precise-diagnosis, 20/13 water-level-remind.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.pv31cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv31cn:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/pv31cn.json`. Suite: `tests/xiaomi/deep/test_deep_pv31cn.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 169, mapped 108, omitted 61, open 0.
- Spec actions 91, mapped 40, omitted 51.
- Controls 100. Value-list samples 46. Named fault codes 0.
- Generated cases include 148 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.pv32cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv32cn:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/pv32cn.json`. Suite: `tests/xiaomi/deep/test_deep_pv32cn.py`.
- Catalog released versions: [1, 2]. Mapped version: 2.
- Spec properties 140, mapped 81, omitted 59, open 0.
- Spec actions 86, mapped 35, omitted 51.
- Controls 75. Value-list samples 40. Named fault codes 0.
- Generated cases include 116 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.pv32gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv32gl:2`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/pv32gl.json`. Suite: `tests/xiaomi/deep/test_deep_pv32gl.py`.
- Catalog released versions: [1]. Mapped version: 2.
- Spec properties 140, mapped 81, omitted 59, open 0.
- Spec actions 86, mapped 34, omitted 52.
- Controls 74. Value-list samples 40. Named fault codes 0.
- Generated cases include 115 mapped-address checks.
- Live fetch inserts a doubled space in Frequency Mop Wash No Tank descriptions. Values are unchanged.
- Mapped version is not in the released instance-catalog list. Open question, xfailed.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.pv51gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv51gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/pv51gl.json`. Suite: `tests/xiaomi/deep/test_deep_pv51gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 111, mapped 61, omitted 50, open 0.
- Spec actions 69, mapped 24, omitted 45.
- Controls 40. Value-list samples 49. Named fault codes 0.
- Generated cases include 85 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.pv81gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-pv81gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/pv81gl.json`. Suite: `tests/xiaomi/deep/test_deep_pv81gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 106, mapped 56, omitted 50, open 0.
- Spec actions 67, mapped 22, omitted 45.
- Controls 36. Value-list samples 49. Named fault codes 0.
- Generated cases include 78 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.qv12cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-qv12cn:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/qv12cn.json`. Suite: `tests/xiaomi/deep/test_deep_qv12cn.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 179, mapped 112, omitted 65, open 2.
- Spec actions 105, mapped 41, omitted 64.
- Controls 108. Value-list samples 33. Named fault codes 0.
- Generated cases include 153 mapped-address checks.
- Unmapped writable properties, xfailed as open questions: 20/10 precise-diagnosis, 20/13 water-level-remind.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, H-02.

### xiaomi.vacuum.qv41cn

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-qv41cn:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/qv41cn.json`. Suite: `tests/xiaomi/deep/test_deep_qv41cn.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 139, mapped 80, omitted 59, open 0.
- Spec actions 86, mapped 35, omitted 51.
- Controls 74. Value-list samples 40. Named fault codes 0.
- Generated cases include 115 mapped-address checks.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.
- No spec/code mismatch beyond those known defects.

### xiaomi.vacuum.qv41gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-qv41gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/qv41gl.json`. Suite: `tests/xiaomi/deep/test_deep_qv41gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 140, mapped 81, omitted 59, open 0.
- Spec actions 87, mapped 35, omitted 52.
- Controls 75. Value-list samples 40. Named fault codes 0.
- Generated cases include 116 mapped-address checks.
- Live fetch inserts a doubled space in Frequency Mop Wash No Tank descriptions. Values are unchanged.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

### xiaomi.vacuum.qv42gl

- Spec: `urn:miot-spec-v2:device:vacuum:0000A006:xiaomi-qv42gl:1`
- Fetch date: 2026-11-04. File: `tests/xiaomi/specs/qv42gl.json`. Suite: `tests/xiaomi/deep/test_deep_qv42gl.py`.
- Catalog released versions: [1]. Mapped version: 1.
- Spec properties 127, mapped 77, omitted 50, open 0.
- Spec actions 77, mapped 32, omitted 45.
- Controls 67. Value-list samples 49. Named fault codes 0.
- Generated cases include 109 mapped-address checks.
- Live fetch inserts a doubled space in Frequency Mop Wash No Tank descriptions. Values are unchanged.
- Known defects left xfailed: H-01, M-02, M-03, M-04, M-05, C-01, H-02.

