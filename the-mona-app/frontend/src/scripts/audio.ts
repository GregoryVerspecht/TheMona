import { audioApi } from "~/lib/api/audio";

const msg = document.getElementById("msg");
const setMsg = (t: string) => { if (msg) msg.textContent = t; };

document.querySelectorAll<HTMLButtonElement>("button[data-sfx]").forEach((btn) => {
  btn.addEventListener("click", async () => {
    const name = btn.dataset.sfx!;
    try {
      setMsg(`Playing ${name}...`);
      await audioApi.playSfx(name);
      setMsg(`Played ${name}`);
    } catch (e) {
      setMsg(String(e));
    }
  });
});

document.getElementById("stop")?.addEventListener("click", async () => {
  try {
    setMsg("Stopping...");
    await audioApi.stopSfx();
    setMsg("Stopped");
  } catch (e) {
    setMsg(String(e));
  }
});
