import { apiGet, apiPost } from "../http";

export interface BtDevice {
  mac: string;
  name: string;
  connected: boolean;
  trusted: boolean;
  audio_sink: boolean;
}

export interface BtStatus {
  adapter_available: boolean;
  adapter_powered: boolean;
  devices: BtDevice[];
}

export const bluetoothApi = {
  status() {
    return apiGet<BtStatus>("/api/v1/bluetooth/status");
  },
  devices() {
    return apiGet<{ devices: BtDevice[] }>("/api/v1/bluetooth/devices");
  },
  connect(mac: string) {
    return apiPost<{ ok: boolean }>(`/api/v1/bluetooth/connect/${mac}`);
  },
  disconnect(mac: string) {
    return apiPost<{ ok: boolean }>(`/api/v1/bluetooth/disconnect/${mac}`);
  },
};
