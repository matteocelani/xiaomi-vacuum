"""Open the virtual lab dashboard and save screenshots of each family."""

from __future__ import annotations

import json
import logging
import os
from pathlib import Path

_LOGGER = logging.getLogger("virtual_lab.frontend")
_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CONFIG = _ROOT / ".virtual-lab"
_FAMILIES = ("station", "sweep", "essential", "robot", "roller", "mijia-cn", "dreame")


def main() -> None:
    """Log in, open the lab view, and screenshot vacuum cards and maps."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    from playwright.sync_api import sync_playwright

    base = os.environ.get("VIRTUAL_LAB_URL", "http://127.0.0.1:8123")
    config = Path(os.environ.get("VIRTUAL_LAB_CONFIG", _DEFAULT_CONFIG))
    out = Path(os.environ.get("VIRTUAL_LAB_SHOTS", "/opt/cursor/artifacts/virtual-lab"))
    out.mkdir(parents=True, exist_ok=True)
    devices = json.loads((config / "lab-devices.json").read_text(encoding="utf-8"))
    username = os.environ.get("VIRTUAL_LAB_USER", "lab")
    password = os.environ.get("VIRTUAL_LAB_PASSWORD", "lab")
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport={"width": 1400, "height": 900})
        _login(page, base, username, password)
        notes: list[str] = []
        for language in ("en", "it"):
            _set_language(page, language)
            page.goto(f"{base}/lovelace/lab", wait_until="domcontentloaded")
            page.wait_for_selector("ha-card", timeout=30000)
            page.screenshot(path=str(out / f"dashboard-{language}.png"), full_page=True)
            if language == "en":
                page.screenshot(path=str(out / "dashboard.png"), full_page=True)
            missing: list[str] = []
            for device in devices:
                if device["family"] not in _FAMILIES:
                    continue
                entity_id = device["entity_id"]
                card = (
                    page.locator("ha-card")
                    .filter(has=page.get_by_text(device["name"], exact=True))
                    .filter(has=page.get_by_role("button"))
                    .first
                )
                if card.count() == 0:
                    missing.append(entity_id)
                else:
                    card.screenshot(
                        path=str(out / f"{device['family']}-card-{language}.png")
                    )
                    if language == "en":
                        card.screenshot(path=str(out / f"{device['family']}-card.png"))
                picture = page.locator(f"img[alt='{device['family']} map']").first
                if picture.count():
                    picture.screenshot(
                        path=str(out / f"{device['family']}-map-{language}.png")
                    )
                    if language == "en":
                        picture.screenshot(
                            path=str(out / f"{device['family']}-map.png")
                        )
                else:
                    missing.append(f"{device['family']} map")
                if not _open_more_info(page, entity_id, device["name"]):
                    missing.append(f"{entity_id} more-info")
                else:
                    page.screenshot(
                        path=str(out / f"{device['family']}-entity-{language}.png")
                    )
                    notes.extend(_layout_notes(page, device["family"], language))
                    page.keyboard.press("Escape")
                    page.wait_for_timeout(300)
            if missing and language == "en":
                _LOGGER.warning("missing %s", ", ".join(missing))
        mobile = browser.new_page(viewport={"width": 390, "height": 844})
        _login(mobile, base, username, password)
        _set_language(mobile, "it")
        mobile.goto(f"{base}/lovelace/lab", wait_until="domcontentloaded")
        mobile.wait_for_selector("ha-card", timeout=30000)
        mobile.screenshot(path=str(out / "dashboard-mobile-it.png"), full_page=True)
        station = next(item for item in devices if item["family"] == "station")
        _open_more_info(mobile, station["entity_id"], station["name"])
        mobile.screenshot(path=str(out / "station-entity-mobile-it.png"))
        notes.extend(_layout_notes(mobile, "station", "it-mobile"))
        (out / "layout-notes.json").write_text(
            json.dumps(notes, indent=2), encoding="utf-8"
        )
        browser.close()
        if notes:
            _LOGGER.warning("layout %s", notes[:12])
        else:
            _LOGGER.info("screenshots %s", out)


def _set_language(page: object, language: str) -> None:
    page.evaluate(
        """async (language) => {
            const hass = document.querySelector("home-assistant").hass;
            await hass.callWS({
                type: "frontend/set_user_data",
                key: "language",
                value: {
                    language,
                    number_format: "language",
                    time_format: "language",
                    date_format: "language",
                    time_zone: "local",
                    first_weekday: "language",
                },
            });
        }""",
        language,
    )
    page.reload(wait_until="domcontentloaded")
    page.wait_for_selector("home-assistant", timeout=30000)


def _open_more_info(page: object, entity_id: str, name: str) -> bool:
    del entity_id
    row = page.locator(".info.pointer").filter(has=page.get_by_text(name, exact=True))
    if row.count() == 0:
        return False
    row.first.click(timeout=5000)
    from playwright.sync_api import TimeoutError as PlaywrightTimeout

    labels = (
        "Vacuum cleaner commands",
        "Comandi dell'aspirapolvere",
        "Comandi aspirapolvere",
    )
    try:
        page.get_by_text(labels[0]).or_(page.get_by_text(labels[1])).or_(
            page.get_by_text(labels[2])
        ).first.wait_for(timeout=8000)
    except PlaywrightTimeout:
        page.keyboard.press("Escape")
        return False
    return True


def _layout_notes(page: object, family: str, language: str) -> list[str]:
    found = page.evaluate(
        """() => {
            const notes = [];
            const visit = (node) => {
                const root = node.shadowRoot;
                if (!root) {
                    return;
                }
                for (const el of root.querySelectorAll("*")) {
                    const text = (el.innerText || "").trim();
                    if (text && /\\bxiaomi_[a-z0-9_]+\\b/.test(text) && text.length < 80) {
                        notes.push("raw " + text);
                    }
                    if (el.clientWidth > 40 && el.scrollWidth > el.clientWidth + 8 && text) {
                        notes.push("overflow " + text.slice(0, 80));
                    }
                    visit(el);
                }
            };
            const dialog = document.querySelector("ha-more-info-dialog");
            if (dialog) {
                visit(dialog);
            }
            return notes.slice(0, 8);
        }"""
    )
    return [f"{family} {language} {item}" for item in found]


def _login(page: object, base: str, username: str, password: str) -> None:
    page.goto(f"{base}/lovelace/lab", wait_until="domcontentloaded")
    page.wait_for_timeout(1500)
    username_box = page.locator("input[name='username']")
    if username_box.count() == 0:
        return
    username_box.fill(username)
    password_box = page.locator("input[name='password']")
    if password_box.count() == 0:
        page.locator("ha-button, mwc-button, button").first.click()
        password_box.wait_for(timeout=10000)
    password_box.fill(password)
    page.locator("ha-button, mwc-button, button").last.click()
    page.wait_for_selector("home-assistant", timeout=30000)


if __name__ == "__main__":
    main()
