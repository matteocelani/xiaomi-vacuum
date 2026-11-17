# Hardware test: Xiaomi S20+ and X20 Max

This is the procedure for a real Xiaomi Robot Vacuum S20+ (`xiaomi.vacuum.b108gl`) and Xiaomi Robot Vacuum X20 Max (`xiaomi.vacuum.d109gl`) after the local miIO map in this repository. It is a manual check on the owner's LAN. It is not a substitute for the simulator tests, and it does not add map, room, or zone support.

Use a local token and the robot's LAN address. Leave cloud property writes off: these robots ignore `set_properties` sent through the cloud, so a cloud fallback can look successful while the robot did nothing. Do not paste the token, the device id, or a map dump into an issue, a log, or a commit.

## Timers to watch

| Timer | Value | What it means |
| --- | --- | --- |
| Xiaomi property call | 5.0 seconds | One local `get_properties` or `set_properties`. A miss does not retry inside that call. |
| Shared miIO call | 2 seconds | `miIO.info` and other calls that still use the shared Dreame protocol. |
| Local probe backoff | 30 seconds | After the host does not answer, later property calls return immediately until this window ends, then local is tried again. |
| Coordinator poll | about 5 seconds while idle, about 3 seconds while a task is active | Home Assistant state lags the robot by one poll. |
| Startup with a wrong token | one probe, then stop | The log says `Local miIO token was rejected` once. Later calls must not sit for about 15 seconds each. |

A host that is off the network pays one 5 second timeout on the first property call, then the integration stays loaded and tries local again after the 30 second backoff. That is a reachability failure, not a bad token.

## Before you start

1. Confirm the model string in the device info is `xiaomi.vacuum.b108gl` or `xiaomi.vacuum.d109gl`.
2. Note the current map list in the vendor app. This procedure must not delete a map, reset a consumable, or start dust collection except where a step says so.
3. Export or screenshot the Home Assistant config entry so it can be restored. Disable automations that call vacuum services.
4. Put the robot on the dock, charged enough to leave the dock and return. Clear the floor in front of the dock.
5. Watch Home Assistant logs for `xiaomi_robot_vacuum` at info. A line that includes the token or the raw datagram is a failure of the logging rules, even if the robot behaved.

If anything in a later phase fails, stop and follow [Rollback](#rollback). Do not "try the map button" to recover.

## Phase 1 — Read only

Estimated time: 2 minutes. Do not call a service.

Pass:

- The vacuum entity becomes available within about 30 seconds and shows docked, not paused and not an error.
- Battery is a percentage that matches the robot, within one coordinator poll (about 5 seconds).
- No Do Not Disturb time entity and no off-peak charging time entity. Those Dreame slots are a bool or a packed number on these models, and creating them used to crash with `'bool' object has no attribute 'split'`.
- The log has no warning storm on each poll. One warning that the local probe failed is allowed only when the host was actually unreachable.

Fail:

- The entity stays unavailable for more than a minute while the robot answers the vendor app on the same LAN.
- The state flips between paused and docked while the robot has not moved.
- A time entity appears for Do Not Disturb or off-peak charging.

## Phase 2 — Safe commands

Estimated time: 4 minutes, plus the time the robot takes to speak when located. Run these one at a time and wait for the entity before the next one.

| Step | What you do | Wait | Pass | Fail |
| --- | --- | --- | --- | --- |
| Start | Start the vacuum | up to 30 seconds | State becomes cleaning. The robot leaves the dock. | No motion after 30 seconds, or the vendor app shows a deleted map or a new scheduled clean. |
| Pause | Pause | up to 15 seconds | State becomes paused. The robot stays where it is. | It returns to the dock or starts a different task. |
| Resume | Start again, while it is paused | up to 15 seconds | It continues the same run. It does not start a second full clean from the dock. | It sends start-sweep again from the beginning, or it does not move. |
| Return | Return to dock | up to 3 minutes | State becomes returning, then docked. | It is still cleaning after 3 minutes, or it starts dust collection, a voice download, or a history fetch. |
| Locate | Locate | up to 15 seconds | The robot plays the locate sound. The map list in the vendor app is unchanged. | A map disappears. On the S20+ the old volume path was the delete-permanent-map slot. |
| Volume | Change the volume slider by a small step, then put it back | up to 15 seconds | The spoken or indicated volume matches the slider. No map change and no extra sound action beyond what the robot itself does for that property. | A map is deleted or a scheduled clean is added. |

S20+ resume must be continue-sweep at action 6.1. X20 Max resume must be continue-sweep at action 2.8. Start-sweep is 2.1 on both and is only correct when the robot was idle or docked, not when it was paused.

## Phase 3 — Dock cycle

Estimated time: 5 to 8 minutes, mostly robot travel.

With the robot docked, run start, wait until it is cleaning and has moved at least a short distance (about 20 to 40 seconds), pause, resume, then return to dock. The same pass and fail rows as phase 2 apply. At the end the robot is on the dock, the entity is docked, and the vendor app shows the same maps as before the phase.

Do this once per model. Do not chain it with a second start until the entity has been docked for one idle poll (about 5 seconds).

## Phase 4 — Maps, later

Estimated time: none in this release. Do not run it.

Map, room, and zone services are not supported for these two models. The Dreame addresses for map data, map backup, and map request land on different Xiaomi slots (including delete-map and add-order-clean on the S20+). Calling them is a failure even if Home Assistant still shows the button from an older install. Skip any camera or map-editor check. A later change can add maps only when the spec slot is the map itself and a council record allows it.

## What must stay disabled

These inherited Dreame commands are not mapped. Home Assistant must not create the entity, or the entity must stay unavailable, and the command must not be sent:

- Play sound, backup map, request map, update map data, and Wi-Fi map.
- Do Not Disturb start and end times, and off-peak charging times.
- Silver-ion reset. On the X20 Max that Dreame slot is reset-dust-bag life.
- Detergent reset on the S20+. On the X20 Max, reset detergent is mapped only to the spec's reset-detergent action, not to the history-object slot.
- Auto-empty start on the S20+. On the X20 Max, start auto empty is mapped only to start dust arrest, not to download-voice.
- The status property that used to read an alarm bool and show the robot paused while docked.

Charging-state value 3 means not chargeable in both specs. It must not be shown as docked or fully charged. A robot that reports status "charged" is docked through the status value, not through charging-state 3.

## Rollback

1. Stop sending commands. If the robot is off the dock, use the physical button or the vendor app to return it to the dock. Do not send a map, reset, or voice command from Home Assistant to "undo" a bad action.
2. Disable the config entry. That stops the poll. Unloading takes a few seconds.
3. If the entry itself is wrong (host or token), restore the screenshot or the previous entry data. Do not delete the entry unless the host and token were never valid; installed users keep the same entry id.
4. Compare the vendor app map list with the note from the start. If a map is missing, restore it from the vendor app, not from this integration.
5. Reload the previous version of the integration only after the robot is docked and the entry is disabled.

A failed probe or a refused token is rolled back by correcting the host or token and reloading the entry. The first bad call is one 5 second timeout or one rejected probe, not a 15 second hang on every poll.
