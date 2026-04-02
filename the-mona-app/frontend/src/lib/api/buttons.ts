import { apiGet, apiPost } from "../http";

export interface ButtonState {
  id: string;
  online: boolean;
  battery?: number | null;
  last_seen?: string;
  last_press?: string | null;
  last_event?: string;
  rssi?: number | null;
}

export const buttonsApi = {
  list() {
    return apiGet<{ buttons: ButtonState[] }>("/api/v1/buttons");
  },
  get(id: string) {
    return apiGet<ButtonState>(`/api/v1/buttons/${id}`);
  },
  fill(id: string, r: number, g: number, b: number, brightness = 200) {
    return apiPost(`/api/v1/buttons/${id}/fill`, { r, g, b, brightness });
  },
  flash(id: string, r: number, g: number, b: number, times = 3, interval_ms = 150, brightness = 200) {
    return apiPost(`/api/v1/buttons/${id}/flash`, { r, g, b, times, interval_ms, brightness });
  },
  stop(id: string) {
    return apiPost(`/api/v1/buttons/${id}/stop`, { clear: true });
  },
  requestState(id: string) {
    return apiPost(`/api/v1/buttons/${id}/request-state`, {});
  },
  fillAll(r: number, g: number, b: number, brightness = 200) {
    return apiPost("/api/v1/buttons/all/fill", { r, g, b, brightness });
  },
  flashAll(r: number, g: number, b: number, times = 3, interval_ms = 150, brightness = 200) {
    return apiPost("/api/v1/buttons/all/flash", { r, g, b, times, interval_ms, brightness });
  },
  stopAll() {
    return apiPost("/api/v1/buttons/all/stop", { clear: true });
  },
};
