import { apiGet, apiPost } from "../http";

export interface LedstripStatus {
  available: boolean;
  led_count: number;
  gpio_pin: number;
  brightness: number;
  animating: boolean;
}

export const ledstripApi = {
  status() {
    return apiGet<LedstripStatus>("/api/v1/ledstrip/status");
  },
  fill(r: number, g: number, b: number, brightness?: number) {
    return apiPost("/api/v1/ledstrip/fill", { r, g, b, brightness });
  },
  brightness(brightness: number) {
    return apiPost("/api/v1/ledstrip/brightness", { brightness });
  },
  off() {
    return apiPost("/api/v1/ledstrip/off", {});
  },
  animate(type: "rainbow" | "pulse", r = 0, g = 255, b = 0, speed_ms = 20) {
    return apiPost("/api/v1/ledstrip/animate", { type, r, g, b, speed_ms });
  },
  setStatus(status: "idle" | "running" | "success" | "fail" | "off") {
    return apiPost("/api/v1/ledstrip/status-set", { status });
  },
};
