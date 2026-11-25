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
        page.goto(f"{base}/lovelace/lab", wait_until="domcontentloaded")
        page.wait_for_selector("ha-card", timeout=30000)
        page.screenshot(path=str(out / "dashboard.png"), full_page=True)
        missing: list[str] = []
        for device in devices:
            if device["family"] not in _FAMILIES:
                continue
            entity_id = device["entity_id"]
            more = (
                page.locator("ha-card")
                .filter(has=page.get_by_text(device["name"], exact=True))
                .filter(has=page.get_by_role("button"))
                .first
            )
            if more.count() == 0:
                missing.append(entity_id)
                continue
            more.screenshot(path=str(out / f"{device['family']}-card.png"))
            picture = page.locator(f"img[alt='{device['family']} map']").first
            if picture.count():
                picture.screenshot(path=str(out / f"{device['family']}-map.png"))
            else:
                missing.append(f"{device['family']} map")
        page.goto(f"{base}/developer-tools/state", wait_until="domcontentloaded")
        search = page.locator("input").first
        if search.count():
            search.fill("vacuum.lab_")
            page.screenshot(path=str(out / "states.png"), full_page=True)
        browser.close()
    if missing:
        _LOGGER.warning("missing %s", ", ".join(missing))
    else:
        _LOGGER.info("screenshots %s", out)


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
