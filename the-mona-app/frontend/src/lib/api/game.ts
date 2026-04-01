import { apiGet, apiPost } from "../http";

export interface GameStatus {
  state: "idle" | "arming" | "wait_random" | "show_target" | "success" | "fail" | "done";
  round: number;
  rounds_total: number;
  target: string | null;
  score_ok: number;
  score_fail: number;
}

export const gameApi = {
  list() {
    return apiGet<{ games: string[] }>("/api/v1/game/games");
  },
  status() {
    return apiGet<GameStatus>("/api/v1/game/status");
  },
  start(params?: { rounds?: number; reaction_timeout_s?: number }) {
    return apiPost<void>("/api/v1/game/start", params ?? {});
  },
  stop() {
    return apiPost<void>("/api/v1/game/stop");
  },
};
