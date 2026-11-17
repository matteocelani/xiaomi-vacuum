# Marketplace submission

The catalog review that follows the domain change needs a published GitHub Release **v2.2.1** whose asset is `xiaomi_robot_vacuum.zip`. v2.2.0 shipped the domain rename. v2.1.2 and earlier shipped `dreame_vacuum.zip`. Do not retag those releases.

The Home Assistant Marketplace (2026.11 and newer) uses this same catalog. Custom-repository installs work before that pull request. Default-catalog installs do not.

## What this repository already prepares

- `hacs.json` name is `Xiaomi Vacuum`, `zip_release` is true, and `filename` is `xiaomi_robot_vacuum.zip`.
- `manifest.json` domain is `xiaomi_robot_vacuum`. Name is `Xiaomi Vacuum`. Documentation is the README in this repository. Issue tracker is `https://github.com/matteocelani/xiaomi-vacuum/issues`. Code owners are `@matteocelani` and `@tasshack`. Version is `v2.2.1`. `categories` is `appliances_cleaning.cleaning` (robot vacuums and mops).
- `.github/workflows/validate.yaml` runs the HACS action with no `ignore` key.
- `.github/workflows/hassfest.yaml` runs hassfest.
- `.github/workflows/release.yaml` builds the zip when a GitHub Release is published. Files are at the archive root because HACS calls `extractall()` into `custom_components/xiaomi_robot_vacuum/` and does not strip a leading folder.
- `custom_components/xiaomi_robot_vacuum/brand/icon.png` is a generic robot-vacuum mark for the brands check. See [Brand icon](#brand-icon).

## Repository settings Matteo sets by hand

GitHub repository settings are not changed from a pull request or from the API in this change. On `https://github.com/matteocelani/xiaomi-vacuum/settings`:

| Setting | Value |
| --- | --- |
| Description | Home Assistant integration for Xiaomi, Dreame, MOVA, Mijia, and TROUVER robot vacuums. |
| Website / homepage | Optional. `https://github.com/matteocelani/xiaomi-vacuum#readme` |
| Topics | `home-assistant`, `hacs`, `homeassistant`, `xiaomi`, `dreame`, `vacuum`, `mijia`, `custom-integration` |
| Issues | Enabled. Features → Issues. The catalog check fails when issues are disabled. |
| Discussions | Optional. Not required for the catalog. |

Confirm the repository is public, not archived, and that GitHub detects the MIT license in `LICENSE`.

## Publish v2.2.1

Merge the review fixes into `master` first. The release workflow is read from the default branch. The maintainer publishes the release after that merge. This pull request does not cut the tag. Leave the published `v2.2.0` tag where it is.

1. On `master`, confirm `custom_components/xiaomi_robot_vacuum/manifest.json` says `"version": "v2.2.1"` and `custom_components/xiaomi_robot_vacuum/dreame/__init__.py` says `VERSION = "v2.2.1"`.
2. Confirm Actions for hassfest, HACS validation, and Xiaomi tests are green on that commit, with no `ignore` input on the HACS action.
3. Create a GitHub Release, not only a tag. Tag name and release title: `v2.2.1`. Target: the merge commit on `master`. This is a full release, not a pre-release and not a draft. Do not move `v2.2.0` or any earlier tag.
4. Publishing the release runs `.github/workflows/release.yaml`. It checks out tag `v2.2.1`, zips `custom_components/xiaomi_robot_vacuum/` with paths at the archive root, and uploads `xiaomi_robot_vacuum.zip`.
5. Open the release and confirm the asset name is exactly `xiaomi_robot_vacuum.zip`. `unzip -Z1 xiaomi_robot_vacuum.zip` must list `manifest.json` and `brand/icon.png`, and must not list a leading `xiaomi_robot_vacuum/` or `custom_components/` directory.

v2.1.2 and earlier attached `dreame_vacuum.zip` from `custom_components/dreame_vacuum`. Those assets stay as they were.

## Edit in hacs/default

File: [`integration`](https://github.com/hacs/default/blob/master/integration) (JSON array of `owner/repo` strings, not YAML).

As of 2026-11-05 the alphabetical neighbors are `"MattDahEpic/ha-midas"` and `"matteoopc/pienone-homeassistant"`. Re-check the file the day you open the pull request. The catalog lint rejects an unsorted list. Sort is case-insensitive. `matteocelani` belongs between those two because `c` comes before `o`.

Insert one line:

```json
 "matteocelani/xiaomi-vacuum",
```

so the neighbors read:

```json
 "MattDahEpic/ha-midas",
 "matteocelani/xiaomi-vacuum",
 "matteoopc/pienone-homeassistant",
```

`Tasshack/dreame-vacuum` stays in that file on domain `dreame_vacuum`. This fork uses `xiaomi_robot_vacuum` and `custom_components/xiaomi_robot_vacuum`, so the two catalog entries do not share a folder. `xiaomi_vacuum` is already taken by `roquerodrigo/ha-xiaomi-vacuum`. Existing `dreame_vacuum` config entries are not migrated. Say that in the catalog pull request.

## Catalog pull request

Only the repository owner, or a major contributor, should open it. Use a personal account. Fork `hacs/default`, branch from its `master`, and do not commit on the fork's `master`. Leave the pull request editable.

Links the template asks for:

- Publishing docs: https://hacs.xyz/docs/publish/start
- Integration requirements: https://hacs.xyz/docs/publish/integration
- Default-catalog steps: https://hacs.xyz/docs/publish/include
- HACS action: https://hacs.xyz/docs/publish/action
- Marketplace catalog: https://contributors.home-assistant.io/marketplace/
- How the catalog is used: https://contributors.home-assistant.io/marketplace/how-it-works/
- Template source: https://github.com/hacs/default/blob/master/.github/PULL_REQUEST_TEMPLATE.md

Ready-to-paste body:

```markdown
## Checklist

- [ ] I've read the [publishing documentation](https://hacs.xyz/docs/publish/start).
- [ ] I've added the [HACS action](https://hacs.xyz/docs/publish/action) to my repository.
- [ ] (For integrations only) I've added the [hassfest action](https://developers.home-assistant.io/blog/2020/04/16/hassfest/) to my repository.
- [ ] The actions are passing without any disabled checks in my repository.
- [ ] I've added a link to the action run on my repository below in the links section.
- [ ] I've created a new release of the repository after the validation actions were run successfully.

## Links

Link to current release: https://github.com/matteocelani/xiaomi-vacuum/releases/tag/v2.2.1
Link to successful HACS action (without the `ignore` key): <paste the green Validate run>
Link to successful hassfest action (if integration): <paste the green hassfest run>

## Notes

`matteocelani/xiaomi-vacuum` is a maintained fork of `Tasshack/dreame-vacuum`. The Home Assistant domain is `xiaomi_robot_vacuum` and the folder is `custom_components/xiaomi_robot_vacuum`. It does not replace an existing `dreame_vacuum` install. Users add the device again. It is not an override of a core integration. `xiaomi_vacuum` is already used by `roquerodrigo/ha-xiaomi-vacuum`. Display name in `hacs.json` is Xiaomi Vacuum. Dreame, MOVA, Mijia, and TROUVER devices from the upstream project still configure through this integration.
```

Fill the two action links from the `master` commit that the `v2.2.1` tag points at. Check every box only after it is true. A misrepresentation gets the pull request closed.

## Brand icon

`custom_components/xiaomi_robot_vacuum/brand/icon.png` (256×256) and `icon@2x.png` (512×512) are an original geometric top-down vacuum: a slate-blue disc, a light lidar turret, and a front bumper arc. No logo file existed in the repository. This is not the Xiaomi wordmark, not the Dreame logo, and not a Home Assistant logo.

Home Assistant older than 2026.3 does not read `brand/` from a custom integration. Those installs look up `https://brands.home-assistant.io/xiaomi_robot_vacuum/icon.png`. That CDN path is empty until a brands submission exists. The upstream Dreame icon remains at `https://brands.home-assistant.io/dreame_vacuum/icon.png` and belongs to the other domain. Local files take over on 2026.3 and newer.

## UI punch list still open

Fixed in the packaging change:

- Integration name in the manifest and in HACS is Xiaomi Vacuum. The config-flow header uses that name.
- English and Italian device-picker and reauthentication copy no longer call the integration Dreame Vacuum.
- Issue templates assign `@matteocelani`.
- The map-decryption log points at this repository's issue tracker.

Left for a later change, or for artwork only Matteo can supply:

- Other locales still say Dreame Vacuum in the device picker and the reauthentication step. `strings.json` is updated. Those catalogs were not mass-edited.
- The closed-source Dreame Vacuum Card, its license field, and the upgrade notification are not part of this integration.
- Map color schemes and icon sets named Dreame, Dreamehome, and Dreame old stay. They are the real Dreame map themes.
- README hero images are upstream files. They redirect to `dv.tasshack.com` and return HTTP 200. Alt text credits Tasshack. A fork-specific hero image would replace them if the upstream art should not lead the page.
- Entity icons are Material Design Icons already in the integration (`mdi` room and vacuum icons). None were missing files.
- `new_model_support.md` no longer says the request is only for a Dreame device.
