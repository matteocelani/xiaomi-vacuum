# Marketplace submission

Do not open a pull request to [hacs/default](https://github.com/hacs/default) until GitHub Release **v2.1.0** exists and its asset `dreame_vacuum.zip` is attached. A catalog pull request opened earlier fails the release check.

The Home Assistant Marketplace (2026.11 and newer) uses this same catalog. Custom-repository installs work before that pull request. Default-catalog installs do not.

## What this repository already prepares

- `hacs.json` name is `Xiaomi Vacuum`, `zip_release` is true, and `filename` is `dreame_vacuum.zip`.
- `manifest.json` domain stays `dreame_vacuum`. Name is `Xiaomi Vacuum`. Documentation is the README in this repository. Issue tracker is `https://github.com/matteocelani/xiaomi-vacuum/issues`. Code owners are `@matteocelani` and `@tasshack`. Version is `v2.1.0`. `categories` is `appliances_cleaning.cleaning` (robot vacuums and mops).
- `.github/workflows/validate.yaml` runs the HACS action with no `ignore` key.
- `.github/workflows/hassfest.yaml` runs hassfest.
- `.github/workflows/release.yaml` builds the zip when a GitHub Release is published. Files are at the archive root because HACS calls `extractall()` into `custom_components/dreame_vacuum/` and does not strip a leading folder.
- `custom_components/dreame_vacuum/brand/icon.png` is a generic robot-vacuum mark for the brands check. See [Brand icon](#brand-icon).

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

## Publish v2.1.0

Merge the packaging pull request into `master` first. The release workflow is read from the default branch.

1. On `master`, confirm `custom_components/dreame_vacuum/manifest.json` says `"version": "v2.1.0"` and `custom_components/dreame_vacuum/dreame/__init__.py` says `VERSION = "v2.1.0"`.
2. Confirm Actions for hassfest, HACS validation, and Xiaomi tests are green on that commit, with no `ignore` input on the HACS action.
3. Create a GitHub Release, not only a tag. Tag name and release title: `v2.1.0`. Target: the merge commit on `master`. This is a full release, not a pre-release and not a draft. Do not reuse `v2.0.0b*` or `v2.0.2`.
4. Publishing the release runs `.github/workflows/release.yaml`. It checks out tag `v2.1.0`, zips `custom_components/dreame_vacuum/` with paths at the archive root, and uploads `dreame_vacuum.zip`.
5. Open the release and confirm the asset name is exactly `dreame_vacuum.zip`. `unzip -Z1 dreame_vacuum.zip` must list `manifest.json` and `brand/icon.png`, and must not list a leading `dreame_vacuum/` or `custom_components/` directory.

Commands, from a checkout of `master` after the merge:

```bash
git fetch origin
git checkout master
git pull origin master
git tag v2.1.0
git push origin v2.1.0
gh release create v2.1.0 --target master --title "v2.1.0" --notes "First Xiaomi Vacuum release. Home Assistant domain remains dreame_vacuum. HACS asset: dreame_vacuum.zip."
```

`gh release create` publishes the release, which starts the workflow. Wait until that workflow is green, then download the asset and check the layout:

```bash
gh release download v2.1.0 --pattern dreame_vacuum.zip --dir /tmp
unzip -Z1 /tmp/dreame_vacuum.zip | head
```

If the workflow fails the tag/version check, the tag is not `v2.1.0` or the manifest on that tag was not bumped. Delete the unpublished attempt only if no one has installed it, fix `master`, and cut a new tag. Do not move `v2.1.0` once it has been installed.

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

`Tasshack/dreame-vacuum` is already in that file. It uses the same Home Assistant domain, `dreame_vacuum`, and the same install folder. This fork does not override a core integration. It does occupy the same custom-component slot as the upstream project, on purpose, so existing config entries keep working. Say that in the catalog pull request. Users should not install both.

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

Link to current release: https://github.com/matteocelani/xiaomi-vacuum/releases/tag/v2.1.0
Link to successful HACS action (without the `ignore` key): <paste the green Validate run>
Link to successful hassfest action (if integration): <paste the green hassfest run>

## Notes

`matteocelani/xiaomi-vacuum` is a maintained fork of `Tasshack/dreame-vacuum`. The Home Assistant domain stays `dreame_vacuum` so installed config entries keep working. It is not an override of a core integration. It uses the same custom-component folder as the upstream repository, which is already in this list. Display name in `hacs.json` is Xiaomi Vacuum. Dreame, MOVA, Mijia, and TROUVER devices from the upstream project still configure through this integration.
```

Fill the two action links from the `master` commit that the `v2.1.0` tag points at. Check every box only after it is true. A misrepresentation gets the pull request closed.

## Brand icon

`custom_components/dreame_vacuum/brand/icon.png` (256×256) and `icon@2x.png` (512×512) are an original geometric top-down vacuum: a slate-blue disc, a light lidar turret, and a front bumper arc. No logo file existed in the repository. This is not the Xiaomi wordmark, not the Dreame logo, and not a Home Assistant logo.

Home Assistant older than 2026.3 does not read `brand/` from a custom integration. Those installs still show the image at `https://brands.home-assistant.io/dreame_vacuum/icon.png`, which is the upstream Dreame icon for this domain. Replacing that CDN image is a separate pull request to [home-assistant/brands](https://github.com/home-assistant/brands) and is optional. Local files take over on 2026.3 and newer.

## UI punch list still open

Fixed in the packaging change:

- Integration name in the manifest and in HACS is Xiaomi Vacuum. The config-flow header uses that name.
- English and Italian device-picker and reauthentication copy no longer call the integration Dreame Vacuum.
- Issue templates assign `@matteocelani`.
- The map-decryption log points at this repository's issue tracker.

Left for a later change, or for artwork only Matteo can supply:

- Other locales still say Dreame Vacuum in the device picker and the reauthentication step. `strings.json` is updated. Those catalogs were not mass-edited.
- The Dreame Vacuum Card step, its license field, its preview string, and the persistent notification still name that upstream card and link to `dreame-vacuum-card.tasshack.com`. That card is a separate product. The link resolves. It is not an official Xiaomi interface.
- Map color schemes and icon sets named Dreame, Dreamehome, and Dreame old stay. They are the real Dreame map themes.
- README hero images are upstream files. They redirect to `dv.tasshack.com` and return HTTP 200. Alt text credits Tasshack. A fork-specific hero image would replace them if the upstream art should not lead the page.
- Entity icons are Material Design Icons already in the integration (`mdi` room and vacuum icons). None were missing files.
- `new_model_support.md` no longer says the request is only for a Dreame device. Card issue templates still describe the Dreame Vacuum Card, which is accurate.
