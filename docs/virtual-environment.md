# Virtual vacuum lab

The lab runs this integration against a simulated robot for every supported Xiaomi and Mijia model, plus one Dreame model from the inherited catalog. Nothing in the lab contacts a real robot or Xiaomi cloud. Tokens, MACs, and serial numbers are the fixed lab values `00` repeated and `LAB000000`.

## What a simulated robot does

Each robot is built from that model's MIoT spec file in `tests/xiaomi/specs/`. Older spec versions (`*_v1.json`, `*_v2.json`) are included as sub-models in the test suite. A robot:

- Publishes every property at a value the spec allows, then overlays the wires the integration's family codec expects (charging, battery, consumable life).
- Refuses a write outside the spec value list or range.
- Moves status when a start, pause, dock, or stop action arrives, including sweep and mop tokens.
- Publishes a fault code and the error status.
- Puts a generated two-room floor plan on string map, room, and segment properties. The same frame is what the Dreame map decoder and renderer draw.
- Answers the same properties through a cloud client after the local token is rejected. The client never dials `api.io.mi.com`.

The Home Assistant process loads the canonical model for each robot, one address in `127.0.0.0/8`, port 54321. Sub-model specs are exercised by pytest rather than as extra config entries, because they share the canonical model string.

## Tests

From the repository root, with the same packages continuous integration installs:

```bash
python3 -m venv .venv
.venv/bin/pip install ruff pytest pytest-asyncio hypothesis pycryptodome \
  python-miio numpy pillow py-mini-racer paho-mqtt cryptography \
  "pytest-homeassistant-custom-component==0.13.205"
.venv/bin/python -m pytest tests/virtual
```

`tests/virtual/test_spec_contract.py` walks every spec file. `test_device_cycle.py` connects the integration to every canonical model and runs clean, dock, schedule (where the model has it), consumables, and a fault. `test_cloud_fallback.py` rejects the local token and reads the same values from the cloud client. `test_floor_plan.py` decodes and renders the generated map. `test_ha_lab.py` sets up one Home Assistant entry per family.

## Home Assistant process

Install Home Assistant into the same virtualenv (`pytest-homeassistant-custom-component` already pulls it in), then:

```bash
.venv/bin/python tests/virtual/run_instance.py
```

The process writes `.virtual-lab/` (gitignored), symlinks this checkout in as the custom component, and listens on `http://127.0.0.1:8123/lovelace/lab`. The dashboard has a vacuum tile and the rendered floor plan for each family, and an entities card for every model. `lab-devices.json` in that directory lists entity ids.

On a fresh config, create the owner account when Home Assistant asks (the lab screenshots use username `lab` and password `lab`). Override the config path with `VIRTUAL_LAB_CONFIG`.

## Frontend check

With the instance running:

```bash
.venv/bin/pip install playwright
.venv/bin/playwright install chromium
.venv/bin/python tests/virtual/check_frontend.py
```

Screenshots land in `/opt/cursor/artifacts/virtual-lab` unless `VIRTUAL_LAB_SHOTS` is set. The script checks the lab dashboard, one card per family, and the rendered map image.
