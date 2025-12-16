import { apiGet, apiPost } from "../http";

export const audioApi = {
  list() {
    return apiGet<{ sounds: string[] }>("/api/v1/audio/list");
  },
  status() {
    return apiGet<Record<string, unknown>>("/api/v1/audio/status");
  },
  playSfx(name: string) {
    return apiPost("/api/v1/audio/sfx/play", { name });
  },
  stopSfx(name?: string, fade_ms = 200) {
    return apiPost("/api/v1/audio/sfx/stop", { name: name ?? null, fade_ms });
  },
  setVolume(volume: number) {
    return apiPost("/api/v1/audio/volume", { volume });
  },
    // VOLUME
  getVolume() {
    return apiGet<{ volume: number }>("/api/v1/audio/volume");
  },
};
