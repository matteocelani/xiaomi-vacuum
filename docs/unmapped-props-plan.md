# Plan for the 180 unmapped writable properties

Approved as written on 2026-11-04. The owner accepted 85 entities, one `xiaomi_add_schedule` service for the 90 order fields, and the 5 uncertain properties left unmapped with documented omission reasons. `xiaomi.vacuum.pv32gl` stays on spec version 2. `ota-info` (siid 20, aiid 16) is not exposed.

Implemented after PR #37 (`14c364a`) and PR #35 (`7edbf2f`) landed on `master`. The branch is rebased onto `7edbf2f`.

What shipped:

- 85 entities from shared family descriptors. X20 Max selects 27 station controls and replaces worry-free mode and mop-swing frequency with `control_with_options`. S20+ has its own tuple: edge swing is siid 2 piid 17 and edge-sweep frequency is siid 2 piid 18. Sweep write-only settings and the remember-map switch are opt-in additions on the models that publish them. The two custom bools are one descriptor each and are diagnostic. Write-only controls are not polled. They stay enabled so a user can set them; the state is the last accepted write.
- One service, `xiaomi_add_schedule`. It calls add-ii (siid 8, aiid 4) with one validated payload. A field that is not in that model's add-ii `in` list, including twice-clean on every model and clean-way, suction, and water outside the E10 trio, is rejected before any protocol call.
- The 5 uncertain properties stay unmapped. The deep suite records the omission and names this document.
- `pv32gl` stays on spec version 2. `ota-info` is not a button.

One spec correction: the committed `b108zh` document publishes fan mode `1 Silent, 2 Basic, 4 Full Speed`, the same list as `b108za` and `b108zb`. It does not publish wire 3. `b108zh` therefore stays an alias of the 2S record. Offering Strong (3) would send a value the spec does not publish.

Day remains a weekday bitmask, 0..255. The spec still does not say which bit is Monday. The service is available, and the field description says to confirm the bit order on a real robot.

Fetched 2026-11-04 from `https://miot-spec.org/miot-spec-v2/instance?type=<urn>`. These are the properties the deep suite xfailed as "published writable, no map, no omission rule": 180 property instances, 59 distinct spec shapes, 24 models. The other 24 models have none.

python-miio's Dreame MIoT map does not describe this Xiaomi order service or these siid/piid pairs. Tasshack's entity list is the Dreame cloud surface (`switch.carpet_avoidance`, scheduled-cleanup editor) and does not address these Xiaomi siids. Xiaomi Home and hass-xiaomi-miot treat schedules as one action with a parameter list, not as ten properties.

## Counts by family

| Family | Instances | What they are |
| --- | --- | --- |
| Order service, siid 8, 10 models | 90 | Inputs of schedule `add` / `add-ii`. Write-only. |
| X20 Max `d109gl` | 29 | Station settings already described on `EXTENDED_STATION_CONTROLS`, plus two unnamed custom fields. |
| Sweep service, siid 7, write-only | 19 | Carpet, sweep, and mop avoid, back-wash area, dry time. |
| S20+ `b108gl` / `b108za` / `b108zb` / `b108zh` | 18 | Clean times, fan mode, alarm, edge sweep, carpet. |
| Custom service, siid 20 | 14 | `precise-diagnosis` (7) and `water-level-remind` (7). |
| Map service `remember-state`, siid 10 piid 1 | 10 | Map-memory switch. Three of them publish only Close. |

Per model: `d109gl` 29, `c101` and `c101eu` 15, `c103` and `d106gl` 13, `b106bk`, `b106eu`, and `c104` 11, `b112`, `b112bk`, and `b112gl` 10, `b108gl` 6, `b108za`, `b108zb`, and `b108zh` 4, `pv11cn`, `pv11gl`, `pv21cn`, `pv21gl`, and `qv12cn` 2, `ov31cn`, `ov31gl`, `ov42cn`, and `ov42gl` 1.

## Do not expose these as entities

**90 order-service fields (siid 8, piid 2 through 10).** The service is `urn:xiaomi-spec:service:order`. Every one of these properties has `access: ["write"]` and an empty description. They are not device state. On `b112` the `add` action takes piids 1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 12, 14, 17, 19. `add-ii` is the same set. Piid 10 (`twice-clean`) is not in either action's `in` list. On `c101eu`, `add` is only piids 1, 2, 3, 4, 5, 6, 11, 12, 14, 16, so clean-way, suction, and water are not even action inputs there. Writing `hour` by itself does not create a schedule, and Home Assistant cannot read the value back.

Map them as one shared schedule action, not as 90 entities. The action descriptor lives once on the sweep family. Value lists that differ (suction, water) are `control_with_options` on the variant. Fields the spec already omitted (`order-id`, map id, timezone) belong in that same schema even though they are not in the 180, or `add` cannot be called. `day` is a uint8 `0..255`, a weekday bitmask, not a day of the month. The spec does not say which bit is Monday. Do not make it a number entity. Confirm the bit order on hardware before the schedule service is enabled by default.

**3 map `remember-state` rows on `b112`, `b112bk`, `b112gl`.** The value-list is only `0: Close`. A switch that cannot turn on is meaningless.

**`d109gl` siid 20 piid 8, `self-cleaning-time`.** Unnamed `uint32`, range `0..4294967295`, no unit, on the `custom` service next to `get-history-obj` and `set-stop-upload-map`. An arbitrary uint32 write has no safe meaning.

**`d109gl` siid 20 piid 7, `sewage-self-cleaning`.** Unnamed bool on that same service. Nothing in python-miio, Tasshack, or the spec text says whether `true` starts a station cycle. Leave it unmapped until the meaning is known.

That is 95 instances to represent only inside a schedule action, or not at all. The other 85 become entities.

## pv32gl spec version

`xiaomi.vacuum.pv32gl` version 2 is a strict superset of version 1. Diff of the two committed documents: version 2 adds one action, siid 20 aiid 16 `ota-info`, and changes nothing else. No property, value-list, or access bit differs. The instance catalog (`status=all`) lists only version 1 as released. The version 2 URN still returns HTTP 200.

Keep mapping version 2. A robot that is still on version 1 simply does not have `ota-info`. Do not retarget the model to version 1. Do not expose `ota-info` as a button. Calling it can start or query an update, and the action is not one of the 180 properties. The catalog lag is an open question for the release notes, not a reason to drop version 2.

The doubled space in "Frequency Mop Wash No Tank" descriptions is text only. Values `0..5` match.

## How to implement after #37

One descriptor per family, composed onto models. No per-model copies of the same siid/piid.

1. Rebase onto `master` after #37 merges. Do not edit `value_limits.py`, `model.py`, `profile.py`, `sweep.py`, or `device.py` before that.
2. Attach existing `EXTENDED_STATION_CONTROLS` to X20 Max with `select_controls` for the keys whose addresses are in the `d109gl` spec. Replace worry-free mode and mop-swing frequency where the value-list is shorter or swapped (below). Do not copy the control bodies into `d109gl.py`.
3. Add an S20+ control tuple on `b108gl.py`. `b108za`, `b108zb`, and `b108zh` are `regional_variant`s and only `control_omitted` / `control_with_options`. Edge swing on this spec is siid 2 piid 17, not the S40 address piid 55. Edge-sweep frequency is piid 18, not piid 68. Reuse the translation keys `xiaomi_edge_swing_tail_sweep` and `xiaomi_edge_sweep_frequency`. Do not reuse the S40 control objects.
4. Add write-only sweep selects once in `sweep.py`. Models that lack `sweep-avoid`, `mop-avoid`, `back-wash-area`, or `dry-time` omit those keys.
5. Add two bools once in `profile.py` for siid 20 piid 10 and piid 13. The seven models that publish each one take them with `control_additions`.
6. Fail-closed: every new writable descriptor registers its spec value-list or value-range with the #37 `value_limits` path. Direct controls must not go through the global +1 codec. `convert_outgoing` stays for `CLEANING_MODE` and `SUCTION_LEVEL` only. A write outside the list or range raises before `set_property`.
7. Tests: delete the open-question xfail for each mapped property. Generate, from that model's spec, one case per value-list entry, the range endpoints, and one step past each end. In-range writes appear on the fake device. Out-of-range writes raise and leave `fake.writes` unchanged. The 95 instances recommended above stay omitted, with a reason that names this document, so those xfails become documented omissions instead of entities.

Entity shell, matching `xiaomi_controls.py` today: writable controls are `entity_category: config`. Sensors would be `diagnostic`. `entity_registry_enabled_default` is true for a readable user setting and false for a write-only property, because the state cannot be read back.

## X20 Max, 29 instances, all on `d109gl`

These match `EXTENDED_STATION_CONTROLS` except worry-free (three values, not five) and mop-swing frequency (labels swapped). Platform is `switch` for bools and `select` for value-lists. `frequency-mop-wash-by-time` is a `number`. Category `config`. Enabled by default, because access includes read and notify.

| siid/piid | Spec name | Format | Access | Values or range | Proposed entity |
| --- | --- | --- | --- | --- | --- |
| 2/8 | clean-times, Clean Times | uint8 | read, write, notify | 1 One Time, 2 Two Time, 3 Three Time | `select.xiaomi_clean_times`, reuse the station descriptor |
| 2/21 | carpet-avoidance, Carpet Avoidance | bool | read, notify, write | | `switch.xiaomi_carpet_avoidance` |
| 2/28 | enable-mop-wash, Enable Mop Wash | bool | read, write, notify | | `switch.xiaomi_enable_mop_wash` |
| 2/29 | frequency-mop-wash, Frequency Mop Wash | uint8 | read, write, notify | 0 By Room, 1 By Area, 2 By Time | `select.xiaomi_mop_wash_frequency` |
| 2/30 | water-output-for-washing-mop | uint8 | read, write, notify | 0 Deep, 1 Daily, 2 Save Water | `select.xiaomi_wash_water_output` |
| 2/31 | drying-time, Drying Time | uint8 | read, write, notify | 1 = 2 hours, 2 = 3 hours, 3 = 4 hours | `select.xiaomi_drying_time` |
| 2/34 | auto-mop-dry, Auto Mop Dry | bool | read, write, notify | | `switch.xiaomi_auto_mop_dry` |
| 2/35 | auto-water-change, Auto Water Change | bool | read, write, notify | | `switch.xiaomi_auto_water_change` |
| 2/36 | use-detergent, Use Detergent | bool | read, write, notify | | `switch.xiaomi_use_detergent` |
| 2/59 | detergent-self-delivery | bool | read, write, notify | | `switch.xiaomi_detergent_self_delivery` |
| 2/60 | mop-water-output-level-no-tank | uint8 | read, write, notify | 0 Daily, 1 Deep | `select.xiaomi_mop_water_no_tank` |
| 2/61 | frequency-mop-wash-no-tank | uint8 | read, write, notify | 0 five m², 1 ten, 2 eight, 3 fifteen, 4 twenty, 5 twenty-five | `select.xiaomi_mop_wash_area` |
| 2/71 | detergent-depletion-reminder | bool | read, write, notify | | `switch.xiaomi_detergent_reminder` |
| 2/74 | sweep-route, Sweep Route | uint8 | read, write, notify | 1 Quick, 2 Daily, 3 Careful | `select.xiaomi_sweep_route` |
| 2/75 | obstacle-avoidance-strategy | uint8 | read, write, notify | 0 Less Collisions, 1 High Coverage | `select.xiaomi_obstacle_strategy` |
| 2/76 | carpet-deep-cleaning | bool | read, write, notify | | `switch.xiaomi_carpet_deep_cleaning` |
| 2/77 | carpet-discriminate | bool | read, write, notify | | `switch.xiaomi_carpet_discriminate` |
| 2/78 | sweep-carpet-first | bool | read, write, notify | | `switch.xiaomi_sweep_carpet_first` |
| 2/79 | mop-outer-swing | bool | read, write, notify | | `switch.xiaomi_mop_outer_swing` |
| 2/80 | mop-outer-swing-frequency | uint8 | read, write, notify | 1 Every Time, 2 7 Sweeps | `select.xiaomi_mop_swing_frequency` with this model's order. The shared tuple labels 1 as seven sweeps and 2 as every time. Do not reuse that tuple here. |
| 2/81 | frequency-mop-wash-by-time | uint8 | read, write, notify | 0..255 step 1, no unit | `number.xiaomi_mop_wash_interval` |
| 2/82 | auto-dust-arrest-power-level | uint8 | read, write, notify | 0 Silent, 1 Normal, 2 Strong | `select.xiaomi_dust_arrest_power` |
| 2/83 | worry-free-clean-mode | uint8 | read, write, notify | 0 Silent, 1 Deep Clean, 2 Standard | `select.xiaomi_worry_free_mode` via `control_with_options`. The shared control also offers butler and pet, which this spec does not. |
| 2/84 | wash-mop-water-temperature | uint8 | read, write, notify | 0 Ordinary, 1 Warm, 2 Hot, 3 Smart | `select.xiaomi_wash_water_temperature` |
| 4/1 | alarm, Alarm | bool | read, write, notify | | `switch.xiaomi_alarm` |
| 18/2 | detergent-self-delivery | bool | read, write, notify | | `switch.xiaomi_detergent_delivery`. Different address from 2/59. |
| 18/3 | detergent-self-delivery-level | uint8 | read, write, notify | 0 Few, 1 Standard, 2 Many, 3 Lots Of | `select.xiaomi_detergent_level` |
| 20/7 | sewage-self-cleaning, no description | bool | read, notify, write | | Do not expose. See above. |
| 20/8 | self-cleaning-time, no description | uint32 | read, notify, write | 0..4294967295 step 1, no unit | Do not expose. See above. |

## S20+ layout, 18 instances

Base record `b108gl`. Variants drop the properties their spec does not publish. `b108za` and `b108zb` share the mode list `1 Silent, 2 Basic, 4 Full Speed` (no 3). `b108zh` and `b108gl` use `1 Silent, 2 Basic, 3 Strong`. Clean-times on `b108gl` says "Two Time"; the three variants say "Two Times". Same values 1 and 2. Category `config`, enabled by default.

| siid/piid | Models | Spec name | Format | Access | Values | Proposed entity |
| --- | --- | --- | --- | --- | --- | --- |
| 2/7 | `b108gl`, `b108za`, `b108zb`, `b108zh` | clean-times, Clean Times | uint8 | read, write, notify | 1 One Time, 2 Two Time(s) | `select.xiaomi_clean_times`. Address is piid 7, not the station piid 8. New descriptor, same translation key. |
| 2/16 | same four | mode, Mode | uint8 | read, write, notify | gl/zh: 1 Silent, 2 Basic, 3 Strong. za/zb: 1 Silent, 2 Basic, 4 Full Speed | `select.xiaomi_fan_mode`. This is not `SUCTION_LEVEL` (that is piid 8 and already mapped, and gl adds Full Speed). Do not run it through the +1 codec. |
| 2/17 | `b108gl` only | edge-swing-tail-sweep, Edge Swing Tail Sweep | bool | read, write, notify | | `switch.xiaomi_edge_swing_tail_sweep` at piid 17 |
| 2/18 | `b108gl` only | edge-sweep-frequency, Edge Sweep Frequency | uint8 | read, write, notify | 1 = 7 Sweeps, 2 = Every Time | `select.xiaomi_edge_sweep_frequency` at piid 18. Option order matches `_OUTSWING_FREQUENCY_OPTIONS`. |
| 2/21 | `b108gl` only | carpet-discriminate, Carpet Discriminate | bool | read, write, notify | | `switch.xiaomi_carpet_discriminate` at piid 21, not the station piid 77 |
| 4/1 | all four, and `d109gl` above | alarm, Alarm | bool | read, write, notify | | `switch.xiaomi_alarm`. One shared descriptor, siid 4 piid 1. |
| 6/7 | `b108za`, `b108zb`, `b108zh` | carpet-avoidance | bool | read, notify, write | | `switch.xiaomi_carpet_avoidance` at siid 6 piid 7. The station descriptor is siid 2 piid 21. Same key, different address, so a second descriptor on the S20+ tuple. |

## Custom bools, 14 instances

Readable bools, empty description, service `custom`. python-miio and Tasshack do not name them. Expose them, but `diagnostic` and disabled by default, so a user does not toggle an unnamed station flag by accident. One descriptor each in `profile.py`.

| siid/piid | Models | Token | Format | Access | Proposed entity |
| --- | --- | --- | --- | --- | --- |
| 20/10 | `ov31cn`, `ov31gl`, `pv11cn`, `pv11gl`, `pv21cn`, `pv21gl`, `qv12cn` | precise-diagnosis | bool | read, notify, write | `switch.xiaomi_precise_diagnosis` |
| 20/13 | `ov42cn`, `ov42gl`, `pv11cn`, `pv11gl`, `pv21cn`, `pv21gl`, `qv12cn` | water-level-remind | bool | read, notify, write | `switch.xiaomi_water_level_remind` |

`pv11cn`, `pv11gl`, `pv21cn`, `pv21gl`, and `qv12cn` publish both. `ov31cn` and `ov31gl` publish only precise diagnosis. `ov42cn` and `ov42gl` publish only the water reminder.

## Sweep write-only settings, 19 instances

Service `sweep`, siid 7. `access` is `["write"]` only, so the entity state is assumed. Category `config`, disabled by default. One tuple in `sweep.py`. Value lists are Close/Open except where noted. Writes must reject anything outside that list.

| siid/piid | Models | Token | Format | Values or range | Proposed entity |
| --- | --- | --- | --- | --- | --- |
| 7/47 | `b106bk`, `b106eu`, `c101`, `c101eu`, `c103`, `c104`, `d106gl` | carpet-avoid | uint8 | 0 Close, 1 Open | `select.xiaomi_carpet_avoid` |
| 7/57 | `c101`, `c101eu`, `c103`, `d106gl` | sweep-avoid | uint8 | 0 Close, 1 Open | `select.xiaomi_sweep_avoid` |
| 7/58 | same four | mop-avoid | uint8 | 0 Close, 1 Open | `select.xiaomi_mop_avoid` |
| 7/62 | `c101`, `c101eu` | back-wash-area | uint8 | 5 Five, 10 Ten | `select.xiaomi_back_wash_area` |
| 7/63 | `c101` (description `dry-time`), `c101eu` (empty description) | dry-time | uint8 | 4..12 step 1, unit hours | `number.xiaomi_dry_time`, unit h |

`b112`, `b112bk`, and `b112gl` do not publish these five. Do not give them the tuple.

## Map remember-state, 10 instances

siid 10 piid 1, service `map`, token `remember-state`, uint8, access read, notify, write. No description.

| Models | Value-list | Proposal |
| --- | --- | --- |
| `b106bk`, `b106eu`, `c101`, `c101eu`, `c103`, `c104`, `d106gl` | 0 Close, 1 Open | `switch.xiaomi_remember_map`, category `config`, enabled by default. It is the only readable map toggle in this set. Map drawing stays unmapped. |
| `b112`, `b112bk`, `b112gl` | 0 Close only | Do not expose. |

## Order service, 90 instances, not entities

Ten models: `b106bk`, `b106eu`, `b112`, `b112bk`, `b112gl`, `c101`, `c101eu`, `c103`, `c104`, `d106gl`. Service siid 8, `order`. All are uint8, `access: ["write"]`, description empty, no unit except where noted.

| piid | Token | Range or value-list | Models that differ |
| --- | --- | --- | --- |
| 2 | enable | 0 Disable, 1 Enable | all 10 |
| 3 | day | 0..255 step 1 | all 10. Weekday bitmask. Bit order is not in the spec. |
| 4 | hour | 0..23 step 1 | all 10 |
| 5 | minute | 0..59 step 1 | all 10 |
| 6 | repeat | 0 Disable, 1 Enable | all 10. Repeat the schedule, not a second cleaning pass. |
| 7 | clean-way | 0 Sweep, 1 Sweep Mop, 2 Mop | all 10 |
| 8 | suction | `b106bk`, `b106eu`, `c104`: 0 Slient, 1 Normal, 2 Medium, 3 Turbo. `b112`, `b112bk`, `b112gl`: 0 Close, 1 One, 2 Two, 3 Three, 4 Forth. `c101`, `c101eu`, `c103`, `d106gl`: 0 Silent, 1 Normal, 2 Medium, 3 Turbo | the "Slient" spelling is the spec |
| 9 | water | seven models `b106bk`, `b106eu`, `c101`, `c101eu`, `c103`, `c104`, `d106gl`: 0 Low, 1 Mid, 2 High. E10 trio: 0 Close, 1 One, 2 Two, 3 Three | |
| 10 | twice-clean | 0 Disable, 1 Enable | all 10. Not an `in` parameter of `add` or `add-ii` on `b112` or `c101eu`. |

Proposed Home Assistant surface: one service, `xiaomi_add_schedule`, implemented once for the sweep family. The schema is the action `in` list for that model's `add-ii`, plus these fields where the spec publishes them. Suction and water options come from the variant. The service calls the action with every required piid in one payload. It does not call `set_property` on a single field. Disabled in the UI until a real sweep-family robot confirms the day bitmask. That is the mapping. It is not 90 entities.

## What phase 2 must not copy

`xiaomi_alarm` at 4/1 is one object shared by S20+ and X20 Max. `xiaomi_clean_times`, `xiaomi_carpet_avoidance`, and `xiaomi_carpet_discriminate` need one object per address, because S20+ and the station spec do not use the same piid. Edge-sweep frequency on S20+ uses the shared option tuple and a new address. Mop-swing frequency and worry-free mode on `d109gl` need `control_with_options`, not the wider shared lists.
