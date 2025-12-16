from __future__ import annotations
import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Optional

import paho.mqtt.client as mqtt

log = logging.getLogger(__name__)

@dataclass
class MqttConfig:
    host: str
    port: int = 1883
    username: Optional[str] = None
    password: Optional[str] = None
    client_id: str = "mona-api"

class PahoMqttService:
    def __init__(self, cfg: MqttConfig) -> None:
        self.cfg = cfg
        self._client = mqtt.Client(client_id=cfg.client_id, clean_session=True)
        if cfg.username:
            self._client.username_pw_set(cfg.username, cfg.password)

        self._on_event: Optional[Callable[[str, dict], None]] = None
        self._on_state: Optional[Callable[[str, dict], None]] = None

        self._client.on_connect = self._handle_connect
        self._client.on_message = self._handle_message
        self._client.on_disconnect = self._handle_disconnect

    def set_handlers(
        self,
        on_event: Callable[[str, dict], None],
        on_state: Callable[[str, dict], None],
    ) -> None:
        self._on_event = on_event
        self._on_state = on_state

    def start(self) -> None:
        log.info("MQTT connecting to %s:%s", self.cfg.host, self.cfg.port)
        self._client.connect(self.cfg.host, self.cfg.port, keepalive=30)
        self._client.loop_start()

    def stop(self) -> None:
        try:
            self._client.loop_stop()
            self._client.disconnect()
        except Exception:
            pass

    def publish(self, topic: str, payload: dict[str, Any], qos: int = 0, retain: bool = False) -> None:
        data = json.dumps(payload, separators=(",", ":")).encode("utf-8")
        self._client.publish(topic, data, qos=qos, retain=retain)

    # ---------- callbacks (paho thread) ----------
    def _handle_connect(self, client: mqtt.Client, userdata, flags, rc) -> None:
        if rc == 0:
            log.info("MQTT connected")
            # subscribe to incoming telemetry
            client.subscribe("mona/buttons/+/event")
            client.subscribe("mona/buttons/+/state")
        else:
            log.error("MQTT connect failed rc=%s", rc)

    def _handle_disconnect(self, client, userdata, rc) -> None:
        log.warning("MQTT disconnected rc=%s", rc)

    def _handle_message(self, client, userdata, msg: mqtt.MQTTMessage) -> None:
        try:
            payload = json.loads(msg.payload.decode("utf-8"))
        except Exception:
            log.warning("MQTT invalid JSON topic=%s payload=%r", msg.topic, msg.payload[:80])
            return

        # topic: mona/buttons/<id>/event or /state
        parts = msg.topic.split("/")
        if len(parts) < 4:
            return
        btn_id = parts[2]
        kind = parts[3]

        # route to registry handlers
        try:
            if kind == "event" and self._on_event:
                self._on_event(btn_id, payload)
            elif kind == "state" and self._on_state:
                self._on_state(btn_id, payload)
        except Exception:
            log.exception("MQTT handler error for %s", msg.topic)
