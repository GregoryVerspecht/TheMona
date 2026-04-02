import { ledstripApi, type LedstripStatus } from "~/lib/api/ledstrip";

function hexToRgb(hex: string) {
  const r = parseInt(hex.slice(1, 3), 16);
  const g = parseInt(hex.slice(3, 5), 16);
  const b = parseInt(hex.slice(5, 7), 16);
  return { r, g, b };
}

function initLedstripPage() {
  const statusAvail = document.getElementById("ls-available");
  const statusAnimating = document.getElementById("ls-animating");
  const statusLedCount = document.getElementById("ls-count");
  const statusBrightness = document.getElementById("ls-brightness-val");
  const msgEl = document.getElementById("ls-msg");

  const colorPicker = document.getElementById("ls-color") as HTMLInputElement | null;
  const brightnessSlider = document.getElementById("ls-brightness") as HTMLInputElement | null;
  const brightnessLabel = document.getElementById("ls-brightness-label");
  const speedSlider = document.getElementById("ls-speed") as HTMLInputElement | null;
  const speedLabel = document.getElementById("ls-speed-label");

  if (!statusAvail) return;

  const setMsg = (t: string, err = false) => {
    if (!msgEl) return;
    msgEl.textContent = t;
    msgEl.className = err ? "text-red-400 text-sm" : "text-green-400 text-sm";
    setTimeout(() => { if (msgEl) msgEl.textContent = ""; }, 3000);
  };

  const dot = (ok: boolean) => ok
    ? '<span class="inline-block w-2.5 h-2.5 rounded-full bg-green-400 mr-2"></span>'
    : '<span class="inline-block w-2.5 h-2.5 rounded-full bg-red-400 mr-2"></span>';

  function applyStatus(s: LedstripStatus) {
    if (statusAvail) statusAvail.innerHTML = dot(s.available) + (s.available ? "Beschikbaar" : "Niet beschikbaar");
    if (statusAnimating) statusAnimating.innerHTML = dot(s.animating) + (s.animating ? "Bezig" : "Stilstaand");
    if (statusLedCount) statusLedCount.textContent = String(s.led_count);
    if (statusBrightness) statusBrightness.textContent = String(s.brightness);
  }

  if (brightnessSlider && brightnessLabel) {
    brightnessLabel.textContent = brightnessSlider.value;
    brightnessSlider.addEventListener("input", () => {
      if (brightnessLabel) brightnessLabel.textContent = brightnessSlider.value;
    });
  }

  if (speedSlider && speedLabel) {
    speedLabel.textContent = speedSlider.value;
    speedSlider.addEventListener("input", () => {
      if (speedLabel) speedLabel.textContent = speedSlider.value;
    });
  }

  const getColor = () => hexToRgb(colorPicker?.value ?? "#00ff00");
  const getBrightness = () => Number(brightnessSlider?.value ?? 200);
  const getSpeed = () => Number(speedSlider?.value ?? 20);

  // Fill
  document.getElementById("ls-fill")?.addEventListener("click", async () => {
    const { r, g, b } = getColor();
    try { await ledstripApi.fill(r, g, b, getBrightness()); setMsg("Fill verstuurd"); await refreshStatus(); }
    catch (e) { setMsg(String(e), true); }
  });

  // Off
  document.getElementById("ls-off")?.addEventListener("click", async () => {
    try { await ledstripApi.off(); setMsg("Strip uit"); await refreshStatus(); }
    catch (e) { setMsg(String(e), true); }
  });

  // Brightness
  document.getElementById("ls-brightness-set")?.addEventListener("click", async () => {
    try { await ledstripApi.brightness(getBrightness()); setMsg(`Helderheid: ${getBrightness()}`); await refreshStatus(); }
    catch (e) { setMsg(String(e), true); }
  });

  // Animate rainbow
  document.getElementById("ls-rainbow")?.addEventListener("click", async () => {
    try { await ledstripApi.animate("rainbow", 0, 0, 0, getSpeed()); setMsg("Rainbow gestart"); await refreshStatus(); }
    catch (e) { setMsg(String(e), true); }
  });

  // Animate pulse
  document.getElementById("ls-pulse")?.addEventListener("click", async () => {
    const { r, g, b } = getColor();
    try { await ledstripApi.animate("pulse", r, g, b, getSpeed()); setMsg("Pulse gestart"); await refreshStatus(); }
    catch (e) { setMsg(String(e), true); }
  });

  // Status presets
  document.querySelectorAll<HTMLButtonElement>("button[data-status]").forEach((btn) => {
    btn.addEventListener("click", async () => {
      const status = btn.dataset.status as "idle" | "running" | "success" | "fail" | "off";
      try { await ledstripApi.setStatus(status); setMsg(`Status: ${status}`); await refreshStatus(); }
      catch (e) { setMsg(String(e), true); }
    });
  });

  async function refreshStatus() {
    try {
      const s = await ledstripApi.status();
      applyStatus(s);
    } catch (e) {
      if (statusAvail) statusAvail.textContent = "Fout bij laden";
    }
  }

  refreshStatus();
  setInterval(refreshStatus, 3000);
}

initLedstripPage();
document.addEventListener("astro:page-load", initLedstripPage);
