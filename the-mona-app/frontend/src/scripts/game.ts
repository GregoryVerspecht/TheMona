import { gameApi, type GameStatus } from "~/lib/api/game";
import { buttonsApi } from "~/lib/api/buttons";

const STATE_LABELS: Record<string, string> = {
  idle:        "Idle",
  arming:      "Starting...",
  wait_random: "Wachten...",
  show_target: "Druk!",
  success:     "Goed!",
  fail:        "Fout!",
  done:        "Klaar",
};

const STATE_COLORS: Record<string, string> = {
  idle:        "text-gray-300",
  arming:      "text-yellow-300",
  wait_random: "text-yellow-300",
  show_target: "text-green-300",
  success:     "text-green-400",
  fail:        "text-red-400",
  done:        "text-blue-300",
};

function initGamePage() {
  const btnStart  = document.getElementById("btn-start")  as HTMLButtonElement | null;
  const btnStop   = document.getElementById("btn-stop")   as HTMLButtonElement | null;
  const elState   = document.getElementById("game-state");
  const elRound   = document.getElementById("game-round");
  const elScoreOk = document.getElementById("game-score-ok");
  const elScoreFail = document.getElementById("game-score-fail");
  const elMsg     = document.getElementById("game-msg");
  const elButtons = document.getElementById("game-buttons");

  const cfgRounds   = document.getElementById("cfg-rounds")    as HTMLInputElement | null;
  const cfgTimeout  = document.getElementById("cfg-timeout")   as HTMLInputElement | null;
  const cfgMinDelay = document.getElementById("cfg-min-delay") as HTMLInputElement | null;
  const cfgMaxDelay = document.getElementById("cfg-max-delay") as HTMLInputElement | null;

  if (!btnStart) return;

  let pollInterval: ReturnType<typeof setInterval> | null = null;

  function applyStatus(s: GameStatus) {
    if (elState) {
      elState.textContent = STATE_LABELS[s.state] ?? s.state;
      elState.className = `font-bold text-2xl ${STATE_COLORS[s.state] ?? "text-white"}`;
    }
    if (elRound) elRound.textContent = `${s.round} / ${s.rounds_total}`;
    if (elScoreOk) elScoreOk.textContent = String(s.score_ok);
    if (elScoreFail) elScoreFail.textContent = String(s.score_fail);

    const running = s.state !== "idle" && s.state !== "done";
    if (btnStart) btnStart.disabled = running;
    if (btnStop)  btnStop.disabled  = !running;
  }

  async function refreshButtons() {
    if (!elButtons) return;
    try {
      const { buttons } = await buttonsApi.list();
      const online = buttons.filter((b) => b.online);
      if (online.length === 0) {
        elButtons.innerHTML = '<span class="text-red-400 text-sm">Geen knoppen online</span>';
      } else {
        elButtons.innerHTML = online.map((b) =>
          `<span class="inline-flex items-center gap-1 px-2 py-1 rounded-lg bg-white/10 text-xs font-mono">
            <span class="w-2 h-2 rounded-full bg-green-400 inline-block"></span>
            ${b.id}
          </span>`
        ).join("");
      }
    } catch {
      elButtons.innerHTML = '<span class="text-gray-500 text-sm">--</span>';
    }
  }

  async function poll() {
    try {
      const s = await gameApi.status();
      applyStatus(s);
      if (s.state === "done" || s.state === "idle") stopPolling();
    } catch (e) {
      if (elMsg) elMsg.textContent = String(e);
    }
  }

  function startPolling() {
    if (pollInterval) return;
    pollInterval = setInterval(poll, 800);
  }

  function stopPolling() {
    if (pollInterval) { clearInterval(pollInterval); pollInterval = null; }
  }

  if (btnStart.dataset.bound !== "1") {
    btnStart.dataset.bound = "1";
    btnStart.addEventListener("click", async () => {
      if (elMsg) elMsg.textContent = "";
      const params = {
        rounds:              Number(cfgRounds?.value  ?? 5),
        reaction_timeout_s:  Number(cfgTimeout?.value  ?? 2),
        min_delay_s:         Number(cfgMinDelay?.value ?? 1.5),
        max_delay_s:         Number(cfgMaxDelay?.value ?? 4),
      };
      try {
        await gameApi.start(params);
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

  poll();
  refreshButtons();
  setInterval(refreshButtons, 5000);
}

initGamePage();
document.addEventListener("astro:page-load", initGamePage);
