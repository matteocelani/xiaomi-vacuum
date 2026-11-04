<center>
<div align="center">

# Xiaomi Vacuum

A Home Assistant integration for Xiaomi robot vacuums, and for every Dreame, MOVA, Mijia, and TROUVER device from [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum).

Maintained by [@matteocelani](https://github.com/matteocelani). Fork of [@Tasshack](https://github.com/Tasshack)'s upstream project. Not an official Dreame or Xiaomi product.

[![Xiaomi Vacuum](https://img.shields.io/badge/Xiaomi%20Vacuum-matteocelani%2Fxiaomi--vacuum-18bcf2?style=for-the-badge&logo=HomeAssistant&logoColor=white)](https://github.com/matteocelani/xiaomi-vacuum)
[![Version](https://img.shields.io/github/manifest-json/v/matteocelani/xiaomi-vacuum?filename=custom_components%2Fdreame_vacuum%2Fmanifest.json&color=18bcf2&label=Version&style=for-the-badge)](https://github.com/matteocelani/xiaomi-vacuum)
[![HACS](https://img.shields.io/badge/HACS-Custom-orange.svg?logo=HomeAssistantCommunityStore&color=18bcf2&logoColor=white&style=for-the-badge)](https://github.com/hacs/integration)
[![Upstream](https://img.shields.io/badge/Upstream-Tasshack%2Fdreame--vacuum-18bcf2?style=for-the-badge&logo=github&logoColor=white)](https://github.com/Tasshack/dreame-vacuum)
[![Community Forum](https://img.shields.io/static/v1.svg?label=Community&message=Forum&color=18bcf2&logo=HomeAssistant&logoColor=white&style=for-the-badge)](https://community.home-assistant.io/t/custom-component-dreame-vacuum/473026)

<hr>
<a href="https://github.com/Tasshack/dreame-vacuum"><img alt="Logo of the upstream Dreame Vacuum project" src="https://dreame-vacuum.tasshack.com/logo.svg" width=400></a>
<hr>

<a href="https://github.com/Tasshack/dreame-vacuum"><img alt="Map card from the upstream Dreame Vacuum project" src="https://dreame-vacuum.tasshack.com/dvc.png" width=480 /></a>

Images and the map card are from the upstream project by [@Tasshack](https://github.com/Tasshack).

</div>
</center>

<hr>

## What this repository is

[Xiaomi Vacuum](https://github.com/matteocelani/xiaomi-vacuum) is both of these things:

- Support for every Dreame, MOVA, Mijia, and TROUVER robot vacuum and mop from [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum), including the accounts and local control that project documents.
- Xiaomi robot vacuums, added one model at a time. The models in this tree are listed under [Supported Xiaomi models](#supported-xiaomi-models).

## Home Assistant still uses `dreame_vacuum`

The project name is **Xiaomi Vacuum**. The integration shows up in Home Assistant as `dreame_vacuum`, so installed config entries, entity ids, and automations keep working. Renaming the domain needs its own council decision, recorded in [0001](.agent/council/records/0001-xiaomi-wide-rename-and-expansion.md).

| | |
| --- | --- |
| Repository | [matteocelani/xiaomi-vacuum](https://github.com/matteocelani/xiaomi-vacuum) |
| HACS repository | `https://github.com/matteocelani/xiaomi-vacuum` |
| Home Assistant domain | `dreame_vacuum` |
| Installed folder | `custom_components/dreame_vacuum` |
| Entities and services | `dreame_vacuum.*` |
| Config entries | stored on `dreame_vacuum` |
| Name in HACS and Home Assistant | Dreame Vacuum (`hacs.json` and `manifest.json`) |

`matteocelani/dreame-vacuum` redirects to `matteocelani/xiaomi-vacuum`. [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum) is the upstream project and stays at that address.

## Install

In HACS, add `https://github.com/matteocelani/xiaomi-vacuum` as a custom repository (category: Integration), then download it. HACS lists that download as Dreame Vacuum, the name in `hacs.json`. The [HACS default listing](https://github.com/hacs/default) for this kind of vacuum is the upstream repository [Tasshack/dreame-vacuum](https://github.com/Tasshack/dreame-vacuum), a different install. After Xiaomi Vacuum is installed, Home Assistant still registers the domain `dreame_vacuum`.

Minimum Home Assistant version is 2024.2.0.

### Dreame, MOVA, Mijia, and TROUVER

Configure a Dreame, MOVA, Mijia, or TROUVER vacuum with the upstream guides. Those guides match the domain `dreame_vacuum` and the behavior this fork tracks:

- [Installation](https://dreame-vacuum.tasshack.com/installation), including [HACS](https://dreame-vacuum.tasshack.com/installation/hacs) and [manual](https://dreame-vacuum.tasshack.com/installation/manually) steps for the upstream project
- [Dreamehome](https://dreame-vacuum.tasshack.com/configuration/dreamehome)
- [Xiaomi Home](https://dreame-vacuum.tasshack.com/configuration/xiaomihome), the account type many Dreame, MOVA, Mijia, and TROUVER vacuums use
- [MOVAhome](https://dreame-vacuum.tasshack.com/configuration/movahome)
- [TROUVER](https://dreame-vacuum.tasshack.com/configuration/trouver)
- [Local control](https://dreame-vacuum.tasshack.com/configuration/local) over the LAN
- [Configuration options](https://dreame-vacuum.tasshack.com/configuration-options)

### Supported Xiaomi models

`resolve_family` in `custom_components/dreame_vacuum/xiaomi/` recognizes these models. Add a row when a model is registered there.

| Marketing name | MIoT model |
| --- | --- |
| Xiaomi Robot Vacuum S20+ | `xiaomi.vacuum.b108gl` |
| Xiaomi Robot Vacuum S20 | `xiaomi.vacuum.d106gl` |
| Mijia 3C Enhanced | `xiaomi.vacuum.c103` |
| Xiaomi Robot Vacuum S12 | `xiaomi.vacuum.b106eu` |
| Xiaomi Robot Vacuum T12 | `xiaomi.vacuum.b106bk` |
| Mijia 扫拖机器人 3 | `xiaomi.vacuum.c104` |
| Xiaomi Robot Vacuum X20 | `xiaomi.vacuum.c101eu` |
| Mijia 免洗扫拖机器人 2 | `xiaomi.vacuum.c101` |
| Xiaomi Robot Vacuum X20 Max | `xiaomi.vacuum.d109gl` |
| Xiaomi Robot Vacuum X20 Pro | `xiaomi.vacuum.d102gl` |
| Mijia M30 | `xiaomi.vacuum.d102ev` |
| Mijia M30 Pro | `xiaomi.vacuum.c107` |
| Xiaomi Robot Vacuum 5 | `xiaomi.vacuum.ov31gl` |
| Mijia M40 S | `xiaomi.vacuum.ov31cn` |
| Xiaomi Robot Vacuum S40 Pro | `xiaomi.vacuum.ov71gl` |
| Xiaomi Robot Vacuum S40 | `xiaomi.vacuum.ov81gl` |
| Mijia Robot Vacuum 4 | `xiaomi.vacuum.ov81cn` |
| Xiaomi Robot Vacuum H40 | `xiaomi.vacuum.ov51gl` |
| Mijia Robot Vacuum H40 | `xiaomi.vacuum.d101` |
| Xiaomi Robot Vacuum S40C | `xiaomi.vacuum.e101gb` |
| Xiaomi Robot Vacuum H50 Pro | `xiaomi.vacuum.ov42gl` |
| Mijia 5C | `xiaomi.vacuum.ov42cn` |
| Mijia Robot Vacuum 5 | `xiaomi.vacuum.pv31cn` |
| Xiaomi Robot Vacuum 5 Pro | `xiaomi.vacuum.ov21gl` |
| Mijia 5 Pro | `xiaomi.vacuum.ov21cn` |
| Xiaomi Robot Vacuum H50 | `xiaomi.vacuum.ov43gb` |
| Xiaomi Robot Vacuum H50 Pro Roller | `xiaomi.vacuum.qv41gl` |
| Mijia 7C | `xiaomi.vacuum.qv41cn` |
| Xiaomi Robot Vacuum H50 Roller | `xiaomi.vacuum.qv42gl` |
| Xiaomi Robot Vacuum 6 | `xiaomi.vacuum.pv32gl` |
| Mijia Robot Vacuum 6 | `xiaomi.vacuum.pv32cn` |
| Xiaomi Robot Vacuum 6 Max | `xiaomi.vacuum.pv11gl` |
| Mijia 6 Max | `xiaomi.vacuum.pv11cn` |
| Mijia Robot Vacuum 7 Max | `xiaomi.vacuum.qv12cn` |
| Xiaomi Robot Vacuum 6 Pro | `xiaomi.vacuum.pv21gl` |
| Mijia 6 Pro | `xiaomi.vacuum.pv21cn` |
| Xiaomi Robot Vacuum S60+ | `xiaomi.vacuum.pv51gl` |
| Xiaomi Robot Vacuum S60 | `xiaomi.vacuum.pv81gl` |
| Xiaomi Robot Vacuum E10 | `xiaomi.vacuum.b112` |
| Xiaomi Robot Vacuum E12 | `xiaomi.vacuum.b112gl` |
| Xiaomi Robot Vacuum E10C | `xiaomi.vacuum.b112bk` |
| Xiaomi Robot Vacuum E5 | `xiaomi.vacuum.c108` |

Map, rooms, and zones are not supported yet on Xiaomi models. These models were tested on a simulated robot, not real hardware. A manual check for a real S20+ or X20 Max is [hardware-test-s20-plus-x20-max.md](hardware-test-s20-plus-x20-max.md). That procedure does not add map, room, or zone support.

## Features

What the integration does today for Dreame, MOVA, Mijia, and TROUVER vacuums inherited from upstream:

- Wide range of Dreame, MOVA, Mijia, and TROUVER robot vacuums and mops, configurable with a Dreamehome, MOVAhome, or Xiaomi Home account, or fully locally without the cloud
- Almost every setting and state exposed dynamically as auto-generated entities
- Live and multi-floor map support with zone, spot, and room cleaning
- Per-room suction, water volume, and cleaning order for customized cleaning
- Persistent notifications and events for automations
- Cleaning and cruising history, obstacle photos, map backup and recovery, and saved Wi-Fi maps
- Backend translations for 40 languages
- Interactive map editor via the embedded [Dreame Vacuum Card](https://dreame-vacuum-card.tasshack.com/)

## Documentation

These pages are the upstream documentation for Dreame, MOVA, Mijia, and TROUVER support.

- [Documentation](https://dreame-vacuum.tasshack.com/)
- [Supported devices](https://dreame-vacuum.tasshack.com/guide/more/supported-devices) for [Dreame](https://dreame-vacuum.tasshack.com/guide/more/supported-devices#dreame), [MOVA](https://dreame-vacuum.tasshack.com/guide/more/supported-devices#mova), [Mijia](https://dreame-vacuum.tasshack.com/guide/more/supported-devices#mijia), and [TROUVER](https://dreame-vacuum.tasshack.com/guide/more/supported-devices#trouver)
- [How to use](https://dreame-vacuum.tasshack.com/guide)
- [Dashboard](https://dreame-vacuum.tasshack.com/guide/dashboard), including the [Dreame Vacuum Card](https://dvc.tasshack.com/)
- [Entities](https://dreame-vacuum.tasshack.com/guide/entities), with [map](https://dreame-vacuum.tasshack.com/guide/entities/map-entities), [room](https://dreame-vacuum.tasshack.com/guide/entities/room-entities), and [consumable](https://dreame-vacuum.tasshack.com/guide/entities/consumable-entities) entities
- [Map support](https://dreame-vacuum.tasshack.com/guide/map-support), including [history](https://dreame-vacuum.tasshack.com/guide/map-support/history), [recovery](https://dreame-vacuum.tasshack.com/guide/map-support/recovery), [obstacle photos](https://dreame-vacuum.tasshack.com/guide/map-support/obstacles), and [Wi-Fi maps](https://dreame-vacuum.tasshack.com/guide/map-support/wifi-map)
- [Services](https://dreame-vacuum.tasshack.com/guide/services) for [device](https://dreame-vacuum.tasshack.com/guide/services/vacuum-services) and [map](https://dreame-vacuum.tasshack.com/guide/services/map-services) control
- [Notifications](https://dreame-vacuum.tasshack.com/guide/notifications)
- [Events](https://dreame-vacuum.tasshack.com/guide/events)
- [FAQ](https://dreame-vacuum.tasshack.com/guide/more/faq)

The [community thread](https://community.home-assistant.io/t/custom-component-dreame-vacuum/473026) is the upstream discussion.

## Credit and license

This repository is a fork of [dreame-vacuum](https://github.com/Tasshack/dreame-vacuum) by [@Tasshack](https://github.com/Tasshack). Copyright (c) 2022 Tasshack. The MIT license and that copyright notice live in [LICENSE](LICENSE) and stay with the project.

### Thanks

- [@Tasshack](https://github.com/Tasshack) for [dreame-vacuum](https://github.com/Tasshack/dreame-vacuum), the upstream integration this fork tracks
- [xiaomi_vacuum](https://github.com/pooyashahidi/xiaomi_vacuum) by [@pooyashahidi](https://github.com/pooyashahidi)
- [Xiaomi MIoT for Home Assistant](https://github.com/ha0y/xiaomi_miot_raw) by [@ha0y](https://github.com/ha0y)
- [Xiaomi Cloud Map Extractor](https://github.com/PiotrMachowski/Home-Assistant-custom-components-Xiaomi-Cloud-Map-Extractor) by [@PiotrMachowski](https://github.com/PiotrMachowski)
- Dreame cloud authentication by [@kuudori](https://github.com/kuudori)
- Mova cloud support by [@r1si](https://github.com/r1si)
