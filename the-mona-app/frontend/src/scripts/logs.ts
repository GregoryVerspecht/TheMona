import { logsApi, type LogEntry } from "~/lib/api/logs";

const LEVEL_CLASSES: Record<string, string> = {
  DEBUG:   "text-gray-400",
  INFO:    "text-green-300",
  WARNING: "text-yellow-300",
  ERROR:   "text-red-400",
  CRITICAL:"text-red-600 font-bold",
  SYS:     "text-blue-300",
};

function formatTs(ms: number): string {
  if (!ms) return "--:--:--";
  const d = new Date(ms);
  return d.toTimeString().slice(0, 8);
}

function renderEntry(e: LogEntry): string {
  const cls = LEVEL_CLASSES[e.level] ?? "text-white";
  const level = e.level.padEnd(8);
  return `<div class="font-mono text-xs leading-5 ${cls}">`
    + `<span class="text-gray-500 mr-2">${formatTs(e.ts)}</span>`
    + `<span class="mr-2 opacity-60">[${level}]</span>`
    + `<span>${e.message}</span>`
    + `</div>`;
}

function initLogsPage() {
  const container = document.getElementById("log-container");
  const btnClear = document.getElementById("btn-clear") as HTMLButtonElement | null;
  const btnPause = document.getElementById("btn-pause") as HTMLButtonElement | null;
  const selectLines = document.getElementById("select-lines") as HTMLSelectElement | null;

  if (!container) return;

  let paused = false;
  let pollInterval: ReturnType<typeof setInterval> | null = null;
  let lastTs = 0;

  function setAutoScroll() {
    if (!paused) container.scrollTop = container.scrollHeight;
  }

  async function poll() {
    if (paused) return;
    try {
      const lines = selectLines ? parseInt(selectLines.value) : 100;
      const { logs } = await logsApi.get(lines);

      // Only re-render if there's new content
      const newest = logs.at(-1)?.ts ?? 0;
      if (newest === lastTs && logs.length > 0) return;
      lastTs = newest;

      container.innerHTML = logs.map(renderEntry).join("");
      setAutoScroll();
    } catch {
      // silently ignore poll errors
    }
  }

  if (btnClear && btnClear.dataset.bound !== "1") {
    btnClear.dataset.bound = "1";
    btnClear.addEventListener("click", () => {
      container.innerHTML = "";
      lastTs = 0;
    });
  }

  if (btnPause && btnPause.dataset.bound !== "1") {
    btnPause.dataset.bound = "1";
    btnPause.addEventListener("click", () => {
      paused = !paused;
      btnPause.textContent = paused ? "Hervatten" : "Pauzeren";
      container.style.opacity = paused ? "0.6" : "1";
      if (!paused) {
        lastTs = 0; // force re-render
        poll();
      }
    });
  }

  poll();
  pollInterval = setInterval(poll, 2000);

  document.addEventListener("astro:before-preparation", () => {
    if (pollInterval) clearInterval(pollInterval);
  });
}

initLogsPage();
document.addEventListener("astro:page-load", initLogsPage);
