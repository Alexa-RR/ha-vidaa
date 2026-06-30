# VIDAA TV for Home Assistant

A Home Assistant integration for **Hisense / Toshiba / VIDAA OS** televisions.

It connects **directly** to the TV's built-in MQTT broker over TLS — there is no
cloud, no external MQTT broker, and no bridge to configure. Pairing is done once
with the PIN shown on screen.

## Features

- `media_player` entity: power off, volume (step / set / mute), input source
  selection, play / pause / stop
- `remote` entity: send any supported key code (`KEY_HOME`, `KEY_OK`,
  `KEY_NETFLIX`, …)
- Wake-on-LAN power on (when a MAC address is provided)
- Live push updates from the TV (state, volume, source)

## Requirements

- A Hisense / Toshiba TV running VIDAA OS with "mobile remote" / phone-app
  control enabled in the TV settings
- The TV reachable on your network on port `36669`
- Home Assistant 2024.6 or newer

## Installation

### HACS (recommended)

1. In HACS, add this repository as a custom repository (category: *Integration*).
2. Install **VIDAA TV**.
3. Restart Home Assistant.

### Manual

Copy `custom_components/vidaa` into your Home Assistant `config/custom_components`
directory and restart.

## Setup

1. Make sure the TV is **on**.
2. Go to **Settings → Devices & Services → Add Integration → VIDAA TV**.
3. Enter the TV's **IP address** (and optionally its MAC address for
   Wake-on-LAN).
4. A **PIN** appears on the TV — type it into the dialog to pair.

## How it works

VIDAA televisions expose a local MQTT broker on port `36669` secured with mutual
TLS. The integration authenticates with the standard mobile-client certificate
and the broker credentials, then speaks the TV's `remoteapp` topic protocol to
read state and send commands.

## Notes

- The TV's MQTT broker is only reachable while the TV is on (or in networked
  standby). Use the Wake-on-LAN power-on if your set supports it.
- Source and app lists are populated by the TV after the first connection.

## License

[MIT](LICENSE)
