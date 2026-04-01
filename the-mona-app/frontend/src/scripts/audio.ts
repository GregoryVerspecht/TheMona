import { audioApi } from "~/lib/api/audio";

function initAudioPage() {
  const msg = document.getElementById("msg");
  const setMsg = (t: string) => { if (msg) msg.textContent = t; };

  document.querySelectorAll<HTMLButtonElement>("button[data-sfx]").forEach((btn) => {
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

  // Volume slider (alleen aanwezig op audio-pagina)
  const slider = document.getElementById("vol") as HTMLInputElement | null;
  const label = document.getElementById("volVal");
  if (!slider || !label) return;

  audioApi.getVolume().then(({ volume }: { volume: number }) => {
    slider.value = String(volume);
    label.textContent = String(volume);
  }).catch(() => {
    label.textContent = slider.value;
  });

  let t: ReturnType<typeof setTimeout> | null = null;
  const push = async (v: string) => {
    try {
      await audioApi.setVolume(Number(v));
    } catch (e) {
      console.error(e);
    }
  };

  slider.addEventListener("input", () => {
    label.textContent = slider.value;
    if (t) clearTimeout(t);
    t = setTimeout(() => push(slider.value), 120);
  });

  slider.addEventListener("change", () => {
    push(slider.value);
  });
}

initAudioPage();
document.addEventListener("astro:page-load", initAudioPage);
