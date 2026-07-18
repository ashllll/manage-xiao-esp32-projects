# XIAO ESP32 capability routing

Use this reference before adding a peripheral or wireless feature. It adapts
the useful topic layout of the local `xiao-esp32c6` skill to this skill's
PlatformIO + ESP-IDF baseline.

## Select the board and framework first

1. Confirm C3, S3, or C6 and any Sense/Plus expansion variant.
2. Confirm the framework. The bundled template is ESP-IDF, not Arduino.
3. Check `include/xiao_pins.h` and the official board page before wiring.
4. Record the SDK/component version, Kconfig changes, power requirements, and
   pin conflicts in `docs/peripherals/`.
5. Build every affected environment and update MkDocs in the same change.

Do not translate an Arduino example mechanically. Map `pinMode`, `Wire`,
`SPI`, `WiFi`, and Arduino BLE classes to the corresponding ESP-IDF GPIO,
driver, `esp_wifi`, NimBLE/Bluedroid, or managed-component APIs.

## Common XIAO header-pin map

| XIAO | C3 | S3 | C6 | Common use |
|---|---:|---:|---:|---|
| D0 | GPIO2 | GPIO1 | GPIO0 | ADC/GPIO |
| D1 | GPIO3 | GPIO2 | GPIO1 | ADC/GPIO |
| D2 | GPIO4 | GPIO3 | GPIO2 | ADC/GPIO |
| D3 | GPIO5 | GPIO4 | GPIO21 | GPIO/chip select |
| D4 | GPIO6 | GPIO5 | GPIO22 | I2C SDA |
| D5 | GPIO7 | GPIO6 | GPIO23 | I2C SCL |
| D6 | GPIO21 | GPIO43 | GPIO16 | UART TX |
| D7 | GPIO20 | GPIO44 | GPIO17 | UART RX |
| D8 | GPIO8 | GPIO7 | GPIO19 | SPI SCK |
| D9 | GPIO9 | GPIO8 | GPIO20 | SPI MISO |
| D10 | GPIO10 | GPIO9 | GPIO18 | SPI MOSI |

Use the symbolic `XIAO_D*`, `XIAO_I2C_*`, `XIAO_UART_*`, and `XIAO_SPI_*`
definitions from `include/xiao_pins.h`. The C6 user LED is GPIO15. The S3
template maps its user LED to GPIO21; expansion boards may already consume it.
The base C3 has no equivalent user LED in this template.

## Peripheral workflow

For GPIO, ADC, PWM, UART, I2C, or SPI:

1. Check boot-strapping, USB/JTAG, and expansion-board conflicts.
2. Confirm the peripheral voltage and current. ESP32 GPIO is 3.3 V and is not
   5 V tolerant.
3. Add a reusable driver under `components/<device>/` when more than one
   application module needs it.
4. Document bus frequency, address/chip-select, initialization order, failure
   behavior, and a minimal verification procedure.
5. Test on hardware after the compile-only matrix succeeds.

## Wireless workflow

### Wi-Fi

- C3, S3, and C6 use 2.4 GHz Wi-Fi; do not assume 5 GHz support.
- Keep SSIDs and credentials in untracked configuration or provisioning/NVS,
  never in committed examples.
- Document STA/AP mode, reconnection policy, power-save mode, TLS trust source,
  and offline behavior.
- For the C6 external antenna path, verify the exact board revision and current
  official RF-switch instructions before controlling GPIO3/GPIO14.

### BLE

- Define server/client roles, service and characteristic UUIDs, properties,
  payload encoding, security, MTU expectations, and reconnect behavior.
- Prefer an ESP-IDF example matching the selected host stack and IDF version.
- Test discovery, read/write, notify/indicate, disconnect, and re-advertising.

### Zigbee, Thread, and Matter

- Select C6 when IEEE 802.15.4 is required; C3 and S3 do not provide the same
  integrated 802.15.4 radio capability.
- Record the role, channel/network settings, managed-component versions,
  partition requirements, and commissioning/reset procedure.
- Use examples matching the bundled ESP-IDF version or deliberately pin a
  separate compatible baseline. Do not copy the older skill's ESP-IDF 5.1.3
  recommendation into this template automatically.
- Verify any Wi-Fi/BLE/802.15.4 coexistence requirement against the current
  Espressif coexistence documentation and test the exact enabled combination.
  A shared 2.4 GHz radio is a design constraint, not by itself proof that two
  protocols can never be enabled together.

## Documentation deliverable

For each new capability, add or update a MkDocs page containing:

- supported board variants and tested revision;
- wiring/pin table and power notes;
- ESP-IDF APIs/components and pinned versions;
- Kconfig and partition changes;
- build, flash, and hardware-test commands;
- known conflicts and recovery steps;
- official source URLs and verification date.

Use the local C6 skill only as a discovery index. Resolve factual conflicts in
favor of current Seeed and Espressif primary documentation.
