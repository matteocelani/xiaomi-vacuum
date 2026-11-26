# Model audit

Each released model was compared with its spec fetched on 2026-11-04. The comparison covers mapped properties and actions, control options, ranges, access, units, and the English and Italian catalogs. An address that the spec tests already classify as identity, map, needs council, or no Home Assistant meaning stays omitted. That includes remote control, map edits, order fields (the `xiaomi_add_schedule` service), voltage, the echoed child-lock reading, duplicate sweep-only start actions, and `qv12cn` enter-check-mode, which takes a parameter. `docs/unmapped-props-plan.md` still names the five properties that stay unmapped.

`mijia.vacuum.v2` publishes brush life at siid 14 piid 2 as days. The same address on v1 and v3 is minutes, with the same 0..18000 range and the description "Brush Left Time". The entity stays minutes. Cleaning area stays square meters where the spec publishes no unit. Sweep cleaning time at siid 7 piid 22 publishes no unit and stays minutes.

A new install shows the spec unit. An install that already registered the old unit keeps that display unit, and Home Assistant converts. In the lab, 80 days of b108 brush life is shown as 1920 h, and 80 hours of detergent life is shown as 3.3 d.

| Model | Status | What changed |
| --- | --- | --- |
| mijia.vacuum.b108za | fixed | Cleaning time is seconds. Brush, filter, and mop life are days. |
| mijia.vacuum.b108zb | fixed | Cleaning time is seconds. Brush, filter, and mop life are days. |
| mijia.vacuum.b108zh | fixed | Cleaning time is seconds. Brush, filter, and mop life are days. |
| mijia.vacuum.v1 | audited | Units, options, and ranges already match the spec. |
| mijia.vacuum.v2 | audited | Brush life stays minutes. See the note above. |
| mijia.vacuum.v3 | audited | Units, options, and ranges already match the spec. |
| xiaomi.vacuum.b106bk | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.b106eu | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.b108gl | fixed | Cleaning time is seconds. Brush, filter, and mop life are days. |
| xiaomi.vacuum.b112 | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.b112bk | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.b112gl | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.c101 | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.c101eu | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.c103 | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.c104 | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.c107 | fixed | Cleaning time is seconds. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.c108 | audited | Units, options, and ranges already match the spec. |
| xiaomi.vacuum.d101 | fixed | Cleaning time is seconds. |
| xiaomi.vacuum.d102ev | fixed | Cleaning time is seconds. Dust-bag time is hours. |
| xiaomi.vacuum.d102gl | fixed | Cleaning time is seconds. Dust-bag time is hours. |
| xiaomi.vacuum.d106gl | fixed | Volume is a 0..10 level. The spec says percentage, but the range is not 0..100. |
| xiaomi.vacuum.d109gl | fixed | Cleaning time is seconds. |
| xiaomi.vacuum.e101gb | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.ov21cn | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.ov21gl | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.ov31cn | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.ov31gl | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.ov42cn | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.ov42gl | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.ov43gb | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.ov51gl | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.ov71gl | fixed | Cleaning time is seconds. Dry time left is minutes. |
| xiaomi.vacuum.ov81cn | fixed | Cleaning time is seconds. |
| xiaomi.vacuum.ov81gl | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.pv11cn | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life, dust-bag time, and roller time are hours. |
| xiaomi.vacuum.pv11gl | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life, dust-bag time, and roller time are hours. |
| xiaomi.vacuum.pv21cn | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life, dust-bag time, and roller time are hours. |
| xiaomi.vacuum.pv21gl | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life, dust-bag time, and roller time are hours. |
| xiaomi.vacuum.pv31cn | fixed | Cleaning time is seconds. Dry time left is minutes. Detergent life and dust-bag time are hours. |
| xiaomi.vacuum.pv32cn | fixed | Cleaning time is seconds. Dry time left is minutes. Dust-bag time and roller time are hours. |
| xiaomi.vacuum.pv32gl | fixed | Cleaning time is seconds. Dry time left is minutes. Dust-bag time and roller time are hours. |
| xiaomi.vacuum.pv51gl | fixed | Cleaning time is seconds. Dust-bag time is hours. |
| xiaomi.vacuum.pv81gl | fixed | Cleaning time is seconds. |
| xiaomi.vacuum.qv12cn | fixed | Cleaning time is seconds. Dry time left is minutes. Roller time is hours. Screen brightness shows percent. Enter-check-mode stays omitted. |
| xiaomi.vacuum.qv41cn | fixed | Cleaning time is seconds. Dry time left is minutes. Dust-bag time and roller time are hours. |
| xiaomi.vacuum.qv41gl | fixed | Cleaning time is seconds. Dry time left is minutes. Dust-bag time and roller time are hours. |
| xiaomi.vacuum.qv42gl | fixed | Cleaning time is seconds. Dry time left is minutes. Dust-bag time and roller time are hours. |
| dreame.vacuum.p2008 | audited | Catalog model with no MIoT spec. Dreame sensor units are unchanged. |
