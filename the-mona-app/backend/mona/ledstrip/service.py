from __future__ import annotations
import asyncio
import logging
from typing import Optional

log = logging.getLogger(__name__)

# GPIO18 = PWM channel 0, most reliable for WS2812B on Pi
LED_COUNT   = 20
LED_PIN     = 18
LED_FREQ    = 800_000   # WS2812B signal frequency
LED_DMA     = 10
LED_INVERT  = False
LED_CHANNEL = 0

# Status colours
COLOUR_IDLE    = (0,   0,  40)   # dim blue
COLOUR_RUNNING = (0,  40,   0)   # dim green
COLOUR_SUCCESS = (0, 255,   0)   # bright green
COLOUR_FAIL    = (255,  0,   0)  # red
COLOUR_OFF     = (0,   0,   0)


def _wheel(pos: int) -> tuple[int, int, int]:
    """Rainbow colour wheel, pos 0-255."""
    pos = 255 - pos
    if pos < 85:
        return (255 - pos * 3, 0, pos * 3)
    if pos < 170:
        pos -= 85
        return (0, pos * 3, 255 - pos * 3)
    pos -= 170
    return (pos * 3, 255 - pos * 3, 0)


class LedStripService:
    def __init__(self, led_count: int = LED_COUNT, gpio_pin: int = LED_PIN):
        self._count = led_count
        self._pin = gpio_pin
        self._strip = None
        self._available = False
        self._brightness = 50        # 0-255
        self._animate_task: Optional[asyncio.Task] = None

    def start(self) -> None:
        try:
            from rpi_ws281x import PixelStrip, Color  # type: ignore
            self._strip = PixelStrip(
                self._count, self._pin, LED_FREQ, LED_DMA,
                LED_INVERT, self._brightness, LED_CHANNEL
            )
            self._strip.begin()
            self._available = True
            log.info("LED strip ready", extra={"count": self._count, "pin": self._pin})
        except Exception as e:
            log.warning(f"LED strip not available (running on non-Pi?): {e}")
            self._available = False

    def stop(self) -> None:
        self._cancel_animation()
        if self._available:
            self._fill(*COLOUR_OFF)

    # ── Public API ─────────────────────────────────────────────────────────────

    def fill(self, r: int, g: int, b: int, brightness: Optional[int] = None) -> None:
        self._cancel_animation()
        if brightness is not None:
            self._set_brightness(brightness)
        self._fill(r, g, b)

    def set_pixel(self, index: int, r: int, g: int, b: int) -> None:
        self._cancel_animation()
        if not self._available:
            return
        from rpi_ws281x import Color
        self._strip.setPixelColor(index % self._count, Color(r, g, b))
        self._strip.show()

    def off(self) -> None:
        self._cancel_animation()
        self._fill(*COLOUR_OFF)

    def set_brightness(self, brightness: int) -> None:
        self._set_brightness(brightness)
        if self._available:
            self._strip.show()

    def animate_rainbow(self, speed_ms: int = 20) -> None:
        self._cancel_animation()
        self._animate_task = asyncio.create_task(self._rainbow_loop(speed_ms))

    def animate_pulse(self, r: int, g: int, b: int, speed_ms: int = 30) -> None:
        self._cancel_animation()
        self._animate_task = asyncio.create_task(self._pulse_loop(r, g, b, speed_ms))

    # Status helpers
    def set_status_idle(self)    -> None: self.fill(*COLOUR_IDLE,    brightness=60)
    def set_status_running(self) -> None: self.animate_pulse(*COLOUR_RUNNING, speed_ms=30)
    def set_status_success(self) -> None: self.fill(*COLOUR_SUCCESS, brightness=200)
    def set_status_fail(self)    -> None: self.fill(*COLOUR_FAIL,    brightness=200)
    def set_status_off(self)     -> None: self.off()

    def status(self) -> dict:
        return {
            "available": self._available,
            "led_count": self._count,
            "gpio_pin": self._pin,
            "brightness": self._brightness,
            "animating": self._animate_task is not None and not self._animate_task.done(),
        }

    # ── Internals ──────────────────────────────────────────────────────────────

    def _fill(self, r: int, g: int, b: int) -> None:
        if not self._available:
            return
        from rpi_ws281x import Color
        c = Color(r, g, b)
        for i in range(self._count):
            self._strip.setPixelColor(i, c)
        self._strip.show()

    def _set_brightness(self, brightness: int) -> None:
        self._brightness = max(0, min(255, brightness))
        if self._available:
            self._strip.setBrightness(self._brightness)

    def _cancel_animation(self) -> None:
        if self._animate_task and not self._animate_task.done():
            self._animate_task.cancel()
        self._animate_task = None

    async def _rainbow_loop(self, speed_ms: int) -> None:
        try:
            pos = 0
            while True:
                if self._available:
                    from rpi_ws281x import Color
                    for i in range(self._count):
                        r, g, b = _wheel((i * 256 // self._count + pos) & 255)
                        self._strip.setPixelColor(i, Color(r, g, b))
                    self._strip.show()
                pos = (pos + 1) & 255
                await asyncio.sleep(speed_ms / 1000)
        except asyncio.CancelledError:
            pass

    async def _pulse_loop(self, r: int, g: int, b: int, speed_ms: int) -> None:
        try:
            step = 2
            brightness = 0
            direction = step
            while True:
                self._set_brightness(brightness)
                self._fill(r, g, b)
                brightness += direction
                if brightness >= 180:
                    direction = -step
                elif brightness <= 10:
                    direction = step
                await asyncio.sleep(speed_ms / 1000)
        except asyncio.CancelledError:
            pass
