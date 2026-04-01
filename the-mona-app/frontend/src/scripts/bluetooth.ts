import { bluetoothApi, type BtDevice, type BtStatus } from "~/lib/api/bluetooth";

function initBluetoothPage() {
  const elAdapterAvail = document.getElementById("bt-adapter-avail");
  const elAdapterPowered = document.getElementById("bt-adapter-powered");
  const elConnectedList = document.getElementById("bt-connected-list");
  const elTrustedList = document.getElementById("bt-trusted-list");
  const elMsg = document.getElementById("bt-msg");

  if (!elAdapterAvail) return;

  const setMsg = (t: string, isError = false) => {
    if (!elMsg) return;
    elMsg.textContent = t;
    elMsg.className = isError ? "text-red-400 text-sm mt-2" : "text-green-400 text-sm mt-2";
  };

  function statusDot(ok: boolean) {
    return ok
      ? '<span class="inline-block w-2 h-2 rounded-full bg-green-400 mr-2"></span>'
      : '<span class="inline-block w-2 h-2 rounded-full bg-red-400 mr-2"></span>';
  }

  function renderDevice(d: BtDevice, showConnect: boolean): string {
    const badge = d.audio_sink
      ? '<span class="text-xs bg-blue-800 text-blue-200 rounded px-1 ml-2">A2DP</span>'
      : "";
    const btn = showConnect
      ? `<button data-mac="${d.mac}" data-action="${d.connected ? "disconnect" : "connect"}"
           class="ml-auto text-xs px-3 py-1 rounded bg-mona-alt text-white hover:opacity-80 transition">
           ${d.connected ? "Disconnect" : "Connect"}
         </button>`
      : "";
    return `
      <div class="flex items-center gap-2 py-2 border-b border-white/10 last:border-0">
        ${statusDot(d.connected)}
        <div>
          <span class="font-medium">${d.name}</span>${badge}
          <span class="block text-xs text-gray-400">${d.mac}</span>
        </div>
        ${btn}
      </div>`;
  }

  function applyStatus(s: BtStatus) {
    if (elAdapterAvail)
      elAdapterAvail.innerHTML = statusDot(s.adapter_available) + (s.adapter_available ? "Beschikbaar" : "Niet beschikbaar");
    if (elAdapterPowered)
      elAdapterPowered.innerHTML = statusDot(s.adapter_powered) + (s.adapter_powered ? "Aan" : "Uit");

    if (elConnectedList) {
      elConnectedList.innerHTML = s.devices.length
        ? s.devices.map((d) => renderDevice(d, true)).join("")
        : '<p class="text-gray-400 text-sm">Geen apparaten verbonden</p>';
    }
  }

  async function loadTrusted() {
    try {
      const { devices } = await bluetoothApi.devices();
      if (elTrustedList) {
        elTrustedList.innerHTML = devices.length
          ? devices.map((d) => renderDevice(d, true)).join("")
          : '<p class="text-gray-400 text-sm">Geen gekoppelde apparaten</p>';
      }
      attachActionButtons(elTrustedList);
    } catch (e) {
      if (elTrustedList) elTrustedList.innerHTML = '<p class="text-red-400 text-sm">Fout bij laden</p>';
    }
  }

  function attachActionButtons(container: HTMLElement | null) {
    container?.querySelectorAll<HTMLButtonElement>("button[data-action]").forEach((btn) => {
      if (btn.dataset.bound === "1") return;
      btn.dataset.bound = "1";
      btn.addEventListener("click", async () => {
        const mac = btn.dataset.mac!;
        const action = btn.dataset.action!;
        btn.disabled = true;
        try {
          if (action === "connect") {
            await bluetoothApi.connect(mac);
            setMsg(`Verbonden met ${mac}`);
          } else {
            await bluetoothApi.disconnect(mac);
            setMsg(`Losgekoppeld van ${mac}`);
          }
          await refresh();
        } catch (e) {
          setMsg(String(e), true);
          btn.disabled = false;
        }
      });
    });
  }

  async function refresh() {
    try {
      const s = await bluetoothApi.status();
      applyStatus(s);
      attachActionButtons(elConnectedList);
      await loadTrusted();
    } catch (e) {
      setMsg(String(e), true);
    }
  }

  const btnRefresh = document.getElementById("bt-refresh") as HTMLButtonElement | null;
  if (btnRefresh && btnRefresh.dataset.bound !== "1") {
    btnRefresh.dataset.bound = "1";
    btnRefresh.addEventListener("click", () => refresh());
  }

  refresh();
}

initBluetoothPage();
document.addEventListener("astro:page-load", initBluetoothPage);
