import { apiGet } from "../http";

export interface LogEntry {
  ts: number;
  level: string;
  message: string;
}

export const logsApi = {
  get(lines = 100, unit = "the-mona") {
    return apiGet<{ logs: LogEntry[] }>(`/api/v1/logs?lines=${lines}&unit=${unit}`);
  },
};
