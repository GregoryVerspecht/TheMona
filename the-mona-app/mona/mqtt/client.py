import asyncio
import json
import logging
from typing import Callable

import paho.mqtt.client as mqtt

from mona.config.loader import settings
from .topics import (
    buttons_status, buttons_hb, buttons_events,
    cmd_rgb, cmd_flash, cmd_rgb_all, app_status
)
from .models import ButtonStatus, Heartbeat, ButtonEvent, CmdRgb, CmdFlash
from .discovery import DeviceRegistry

log = logging.getLogger(__name__)

class MqttClient:
    def __init__(self, cfg=settings):
        self.cfg = cfg
        self.client = mqtt.Client(client_id=cfg.mqtt.client_id, clean_session=True)
        if cfg.mqtt.username:
            self.client.username_pw_set(cfg.mqtt.username, cfg.mqtt.password or "")
        self._loop = asyncio.get_event_loop()
        self.registry = DeviceRegistry(cfg.mqtt.heartbeat_timeout_sec)

        # event callbacks (set by engine/web)
        self.on_button_event: Callable[[str, ButtonEvent], None] | None = None
        self.on_presence_update: Callable[[], None] | None = None

        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect

    async def start(self):
        self.client.connect(self.cfg.mqtt.host, self.cfg.mqtt.port, keepalive=30)
        self.client.loop_start()
        # publiceer app status retained
        self._publish(app_status(self.cfg.mqtt.topic_prefix),
                      {"state": "IDLE", "version": "0.1.0"}, qos=1, retain=True)
        # achtergrond task: presence refresh
        self._presence_task = asyncio.create_task(self._presence_loop())

    async def stop(self):
        self.client.loop_stop()
        self.client.disconnect()
        if hasattr(self, "_presence_task"):
            self._presence_task.cancel()

    def _subscribe_all(self):
        pref = self.cfg.mqtt.topic_prefix
        self.client.subscribe(buttons_status(pref), qos=1)
        self.client.subscribe(buttons_hb(pref), qos=0)
        self.client.subscribe(buttons_events(pref), qos=1)
        log.info({"msg": "mqtt subscribed", "prefix": pref})

    def _on_connect(self, client, userdata, flags, rc):
        log.info({"msg": "mqtt connected", "rc": rc})
        self._subscribe_all()

    def _on_disconnect(self, client, userdata, rc):
        log.warning({"msg": "mqtt disconnected", "rc": rc})

    def _on_message(self, client, userdata, msg):
        topic = msg.topic
        payload = msg.payload.decode("utf-8") if msg.payload else ""
        try:
            data = json.loads(payload) if payload else {}
        except Exception:
            log.exception({"msg": "invalid json", "topic": topic, "payload": payload})
            return

        # rudimentaire parsing van device-id
        parts = topic.split("/")
        # .../buttons/<id>/status|heartbeat|events
        dev_id = parts[2] if len(parts) >= 4 and parts[1] == "buttons" else None

        if topic.endswith("/status") and dev_id:
            try:
                st = ButtonStatus(**data)
                self.registry.apply_status(dev_id, st.model_dump())
                if self.on_presence_update:
                    self.on_presence_update()
            except Exception:
                log.exception({"msg": "status parse error", "topic": topic})

        elif topic.endswith("/heartbeat") and dev_id:
            try:
                hb = Heartbeat(**data)
                self.registry.heartbeat(dev_id, hb.ts)
                if self.on_presence_update:
                    self.on_presence_update()
            except Exception:
                log.exception({"msg": "heartbeat parse error", "topic": topic})

        elif topic.endswith("/events") and dev_id:
            try:
                ev = ButtonEvent(**data)
                if self.on_button_event:
                    self.on_button_event(dev_id, ev)
            except Exception:
                log.exception({"msg": "event parse error", "topic": topic})

    async def _presence_loop(self):
        while True:
            self.registry.mark_offline_if_stale()
            await asyncio.sleep(5)

    # Publishes
    def _publish(self, topic: str, obj: dict, qos: int = 1, retain: bool = False):
        self.client.publish(topic, json.dumps(obj), qos=qos, retain=retain)

    def set_rgb(self, button_id: str, cmd: CmdRgb):
        self._publish(cmd_rgb(self.cfg.mqtt.topic_prefix, button_id), cmd.model_dump(), qos=1)

    def flash(self, button_id: str, cmd: CmdFlash):
        self._publish(cmd_flash(self.cfg.mqtt.topic_prefix, button_id), cmd.model_dump(), qos=1)

    def set_rgb_all(self, cmd: CmdRgb):
        self._publish(cmd_rgb_all(self.cfg.mqtt.topic_prefix), cmd.model_dump(), qos=1)

    def list_devices(self):
        return self.registry.list_devices()
