# 🧼 Dish Genie  
*A smart dishwasher timer for the Adafruit MagTag (CircuitPython 10.x+)*

Dish Genie is a simple but fun MagTag project that lets you set a timer for your dishwasher cycle and get notified when it’s done — complete with custom e-Ink graphics, NeoPixel LED feedback, and button-driven control.

---

## ✨ Features
- 🕒 **Adjustable timer** — Add 1-hour or 30-minute increments, or reset to default (1 hour).  
- 🧽 **Visual dishwasher states** — “Dirty”, “Cleaning…”, and “Clean!” screens with custom BMP images.  
- 💡 **LED notifications** — MagTag’s built-in NeoPixels blink in different colors for each state.  
- 🔔 **Completion alert** — Audible tone plays when the cleaning timer finishes.  
- 🌐 **Real-time tracking** — Fetches the current time from Adafruit IO’s time integration.  
- 🔋 **Low power sleep** — Uses `alarm` deep-sleep to conserve power between cycles.  

---
## 💾 How It Works

1. On boot, the MagTag displays the Home screen (Dish Genie logo).
2. Press the **Cleaning** button to start the dishwasher timer.
3. The device fetches the current time via Adafruit IO and calculates the estimated finish time.
4. The MagTag goes into deep sleep until the timer expires (or a button is pressed).
5. When the timer ends, LEDs flash yellow, a tone plays, and the Clean! screen appears.

---

## 🧩 Hardware Requirements
- [Adafruit MagTag](https://www.adafruit.com/product/4800)  
- USB-C cable for programming/power  
- Optional: 3D-printed stand or magnetic mount for your dishwasher door  

---

## 🧰 Software Requirements
- **CircuitPython 10.0+**
- **Libraries:**
  - `adafruit_magtag`
  - `adafruit_requests`
  - `adafruit_io`
  - `wifi`
  - `alarm`
  - `socketpool`
  - `displayio`
  - `terminalio`

You can install these from the [Adafruit CircuitPython Bundle](https://circuitpython.org/libraries).

---

## 💤 Power & Sleep
- Uses alarm.exit_and_deep_sleep_until_alarms() to conserve battery life.
- Can be woken early by pressing Button A or B.
- Automatically stores the last timer duration in timer.txt for next use.

---

## License
Copyright © 2025 Adam Neighbors

Released under the GNU General Public License v3.0 (GPLv3).
See the [LICENSE](LICENSE) file for details.
