import { buttonsApi, type ButtonState } from "~/lib/api/buttons";

function hexToRgb(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return { r, g, b };
}

function timeSince(iso?: string): string {
  if (!iso) return "—";
  const secs = Math.floor((Date.now() - new Date(iso).getTime()) / 1000);
  if (secs < 5) return "nu";
  if (secs < 60) return `${secs}s geleden`;
  return `${Math.floor(secs / 60)}m geleden`;
}

function batteryBar(pct?: number | null): string {
  if (pct === undefined || pct === null || pct < 0) return '<span class="text-gray-500 text-xs">—</span>';
  const color = pct > 50 ? "bg-green-400" : pct > 20 ? "bg-yellow-400" : "bg-red-400";
  const icon = pct <= 20 ? "⚠️ " : "";
  return `
    <div class="flex items-center gap-1">
      <div class="w-16 h-2 bg-white/10 rounded-full overflow-hidden">
        <div class="${color} h-full rounded-full" style="width:${pct}%"></div>
      </div>
      <span class="text-xs text-gray-400">${icon}${pct}%</span>
    </div>`;
}

function renderButton(btn: ButtonState, color: string): string {
  const dot = btn.online
    ? '<span class="inline-block w-2.5 h-2.5 rounded-full bg-green-400 shrink-0"></span>'
    : '<span class="inline-block w-2.5 h-2.5 rounded-full bg-red-400 shrink-0"></span>';

  return `
    <div class="border border-white/10 rounded-xl p-4 space-y-3" data-btn-id="${btn.id}">
      <div class="flex items-center gap-2">
        ${dot}
        <span class="font-semibold">${btn.id}</span>
        <span class="text-xs text-gray-400 ml-auto">${btn.online ? "online" : "offline"}</span>
      </div>

      <div class="grid grid-cols-2 gap-2 text-sm">
        <div>
          <span class="text-gray-400">Batterij</span>
          <div>${batteryBar(btn.battery)}</div>
        </div>
        <div>
          <span class="text-gray-400">Laatste druk</span>
          <div class="text-white text-xs last-press" data-ts="${btn.last_press ?? ""}">${timeSince(btn.last_press ?? undefined)}</div>
        </div>
        <div>
          <span class="text-gray-400">Laatste activiteit</span>
          <div class="text-white text-xs last-seen" data-ts="${btn.last_seen ?? ""}">${timeSince(btn.last_seen)}</div>
        </div>
        <div>
          <span class="text-gray-400">RSSI</span>
          <div class="text-xs ${(btn.rssi ?? 0) > -70 ? 'text-green-400' : (btn.rssi ?? 0) > -85 ? 'text-yellow-400' : 'text-red-400'}">${btn.rssi != null ? btn.rssi + ' dBm' : '—'}</div>
        </div>
      </div>

      <div class="flex flex-wrap gap-2 pt-1">
        <button data-action="fill" data-id="${btn.id}"
          class="text-xs px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition">
          Fill
        </button>
        <button data-action="flash" data-id="${btn.id}"
          class="text-xs px-3 py-1.5 rounded-lg bg-white/10 hover:bg-white/20 transition">
          Flash
        </button>
        <button data-action="stop" data-id="${btn.id}"
          class="text-xs px-3 py-1.5 rounded-lg bg-red-900/50 hover:bg-red-900/80 transition">
          Stop
        </button>
      </div>
    </div>`;
}

function initButtonsPage() {
  const grid = document.getElementById("btn-grid");
  const msgEl = document.getElementById("btn-msg");
  const colorPicker = document.getElementById("btn-color") as HTMLInputElement | null;
  const brightnessSlider = document.getElementById("btn-brightness") as HTMLInputElement | null;
  const brightnessLabel = document.getElementById("btn-brightness-val");

  if (!grid) return;

  const setMsg = (t: string, err = false) => {
    if (!msgEl) return;
    msgEl.textContent = t;
    msgEl.className = err ? "text-red-400 text-sm" : "text-green-400 text-sm";
    setTimeout(() => { if (msgEl) msgEl.textContent = ""; }, 3000);
  };

  const getColor = () => hexToRgb(colorPicker?.value ?? "#00ff00");
  const getBrightness = () => Number(brightnessSlider?.value ?? 200);

  if (brightnessSlider && brightnessLabel) {
    brightnessLabel.textContent = brightnessSlider.value;
    brightnessSlider.addEventListener("input", () => {
      if (brightnessLabel) brightnessLabel.textContent = brightnessSlider.value;
    });
  }

  function attachActions() {
    grid?.querySelectorAll<HTMLButtonElement>("button[data-action]").forEach((btn) => {
      if (btn.dataset.bound === "1") return;
      btn.dataset.bound = "1";

      btn.addEventListener("click", async () => {
        const id = btn.dataset.id!;
        const action = btn.dataset.action!;
        const { r, g, b } = getColor();
        const brightness = getBrightness();

        try {
          if (action === "fill") {
            await buttonsApi.fill(id, r, g, b, brightness);
            setMsg(`Fill verstuurd naar ${id}`);
          } else if (action === "flash") {
            await buttonsApi.flash(id, r, g, b, 3, 150, brightness);
            setMsg(`Flash verstuurd naar ${id}`);
          } else if (action === "stop") {
            await buttonsApi.stop(id);
            setMsg(`Gestopt: ${id}`);
          }
        } catch (e) {
          setMsg(String(e), true);
        }
      });
    });
  }

  async function refresh() {
    try {
      const { buttons } = await buttonsApi.list();
      const color = colorPicker?.value ?? "#00ff00";

      if (buttons.length === 0) {
        grid.innerHTML = '<p class="text-gray-400 text-sm col-span-full">Geen knoppen gevonden</p>';
      } else {
        grid.innerHTML = buttons.map((b) => renderButton(b, color)).join("");
        attachActions();
      }
    } catch (e) {
      grid.innerHTML = '<p class="text-red-400 text-sm col-span-full">Fout bij laden</p>';
    }
  }

  // Broadcast knoppen
  document.getElementById("btn-all-fill")?.addEventListener("click", async () => {
    const { r, g, b } = getColor();
    try { await buttonsApi.fillAll(r, g, b, getBrightness()); setMsg("Fill verstuurd naar alle knoppen"); }
    catch (e) { setMsg(String(e), true); }
  });
  document.getElementById("btn-all-flash")?.addEventListener("click", async () => {
    const { r, g, b } = getColor();
    try { await buttonsApi.flashAll(r, g, b, 3, 150, getBrightness()); setMsg("Flash verstuurd naar alle knoppen"); }
    catch (e) { setMsg(String(e), true); }
  });
  document.getElementById("btn-all-stop")?.addEventListener("click", async () => {
    try { await buttonsApi.stopAll(); setMsg("Alle knoppen gestopt"); }
    catch (e) { setMsg(String(e), true); }
  });

  // Refresh timestamp labels every 5s without full reload
  setInterval(() => {
    grid.querySelectorAll<HTMLElement>(".last-seen, .last-press").forEach((el) => {
      el.textContent = timeSince(el.dataset.ts || undefined);
    });
  }, 5000);

  refresh();
  setInterval(refresh, 4000);
}

initButtonsPage();
document.addEventListener("astro:page-load", initButtonsPage);
