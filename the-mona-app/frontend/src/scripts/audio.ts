import { audioApi } from "~/lib/api/audio";

function initAudioPage() {
  const msg = document.getElementById("msg");
  const setMsg = (t: string) => { if (msg) msg.textContent = t; };

  document.querySelectorAll<HTMLButtonElement>("button[data-sfx]").forEach((btn) => {
    // voorkom dubbele listeners als init meerdere keren runt
    if (btn.dataset.bound === "1") return;
    btn.dataset.bound = "1";

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

  const stop = document.getElementById("stop") as HTMLButtonElement | null;
  if (stop && stop.dataset.bound !== "1") {
    stop.dataset.bound = "1";
    stop.addEventListener("click", async () => {
      await audioApi.stopSfx();
      setMsg("Stopped");
    });
  }
}

// 1) bij echte load
initAudioPage();
// 2) bij Astro client navigatie
document.addEventListener("astro:page-load", initAudioPage);
