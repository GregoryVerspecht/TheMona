import { gameApi, type GameStatus } from "~/lib/api/game";

const STATE_LABELS: Record<string, string> = {
  idle: "Idle",
  arming: "Starting...",
  wait_random: "Wachten...",
  show_target: "Druk!",
  success: "Goed!",
  fail: "Fout!",
  done: "Klaar",
};

function initGamePage() {
  const btnStart = document.getElementById("btn-start") as HTMLButtonElement | null;
  const btnStop = document.getElementById("btn-stop") as HTMLButtonElement | null;
  const elState = document.getElementById("game-state");
  const elRound = document.getElementById("game-round");
  const elScoreOk = document.getElementById("game-score-ok");
  const elScoreFail = document.getElementById("game-score-fail");
  const elMsg = document.getElementById("game-msg");

  if (!btnStart) return; // niet op deze pagina

  let pollInterval: ReturnType<typeof setInterval> | null = null;

  function applyStatus(s: GameStatus) {
    if (elState) elState.textContent = STATE_LABELS[s.state] ?? s.state;
    if (elRound) elRound.textContent = `${s.round} / ${s.rounds_total}`;
    if (elScoreOk) elScoreOk.textContent = String(s.score_ok);
    if (elScoreFail) elScoreFail.textContent = String(s.score_fail);

    const running = s.state !== "idle" && s.state !== "done";
    if (btnStart) btnStart.disabled = running;
    if (btnStop) btnStop.disabled = !running;
  }

  async function poll() {
    try {
      const s = await gameApi.status();
      applyStatus(s);
      if (s.state === "done" || s.state === "idle") {
        stopPolling();
      }
    } catch (e) {
      if (elMsg) elMsg.textContent = String(e);
    }
  }

  function startPolling() {
    if (pollInterval) return;
    pollInterval = setInterval(poll, 1000);
  }

  function stopPolling() {
    if (pollInterval) {
      clearInterval(pollInterval);
      pollInterval = null;
    }
  }

  if (btnStart.dataset.bound !== "1") {
    btnStart.dataset.bound = "1";
    btnStart.addEventListener("click", async () => {
      if (elMsg) elMsg.textContent = "";
      try {
        await gameApi.start();
        startPolling();
        await poll();
      } catch (e) {
        if (elMsg) elMsg.textContent = String(e);
      }
    });
  }

  if (btnStop && btnStop.dataset.bound !== "1") {
    btnStop.dataset.bound = "1";
    btnStop.addEventListener("click", async () => {
      try {
        await gameApi.stop();
        stopPolling();
        await poll();
      } catch (e) {
        if (elMsg) elMsg.textContent = String(e);
      }
    });
  }

  // Initieel status ophalen
  poll();
}

initGamePage();
document.addEventListener("astro:page-load", initGamePage);
