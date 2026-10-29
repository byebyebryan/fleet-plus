"use strict";

const readScenes = {
  local: ["Local cached read", "A separately running Observer service publishes host-local facts. Your utility reads that cache; reading does not start a daemon or renew native evidence.", "complete"],
  fleet: ["Optional fleet delivery", "Mesh carries already published observations over configured IPC/SSH routes. Host outcomes, source identities and independently expiring evidence remain visible.", "complete"],
  partial: ["Partial or expired evidence", "An unavailable source or incomplete membership census stays explicit. A missing row cannot establish an empty working set, idle work or a removed session.", "partial"]
};
const routes = {
  desk: ["Desk → Tower · Desk → Laptop", "Desk can read both peers. Neither peer has a configured route back to Desk."],
  tower: ["Tower → Laptop", "Tower can reach Laptop. Desk is outside Tower's configured roster."],
  laptop: ["Laptop → Tower", "Laptop can reach Tower. Its route to Tower does not grant access to Desk."]
};

document.querySelectorAll("[data-read-path]").forEach((root) => {
  root.querySelector(".controls").hidden = false;
  root.querySelectorAll("button[data-scene]").forEach((button) => {
    button.addEventListener("click", () => {
      const scene = readScenes[button.dataset.scene];
      root.querySelectorAll("button[data-scene]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      root.querySelector("[data-scene-title]").textContent = scene[0];
      root.querySelector("[data-scene-text]").textContent = scene[1];
      root.querySelector("[data-scene-status]").dataset.kind = scene[2];
    });
  });
});

document.querySelectorAll("[data-routes]").forEach((root) => {
  root.querySelector(".controls").hidden = false;
  root.querySelectorAll("button[data-host]").forEach((button) => {
    button.addEventListener("click", () => {
      const route = routes[button.dataset.host];
      root.querySelectorAll("button[data-host]").forEach((item) => item.setAttribute("aria-pressed", String(item === button)));
      root.querySelector("[data-route-list]").textContent = route[0];
      root.querySelector("[data-route-text]").textContent = route[1];
    });
  });
});

document.querySelectorAll("[data-media-toggle]").forEach((button) => {
  const picture = document.getElementById(button.dataset.mediaToggle);
  let playing = false;
  button.hidden = false;
  function stop() {
    playing = false;
    picture.src = picture.dataset.still;
    button.textContent = "Play rendered demo";
    button.setAttribute("aria-pressed", "false");
  }
  button.addEventListener("click", () => {
    if (playing) { stop(); return; }
    playing = true;
    picture.src = picture.dataset.motion;
    button.textContent = "Pause rendered demo";
    button.setAttribute("aria-pressed", "true");
  });
  document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); });
  window.matchMedia("(prefers-reduced-motion: reduce)").addEventListener("change", stop);
});

document.querySelectorAll("[data-terminal-showcase]").forEach((root) => {
  const poster = root.querySelector("[data-terminal-poster]");
  const image = poster?.querySelector("img");
  const video = root.querySelector("[data-terminal-video]");
  const button = root.querySelector("[data-terminal-toggle]");
  if (!poster || !image || !video || !button) return;

  const compact = window.matchMedia("(max-width: 650px)");
  const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
  const updateAlt = () => {
    image.alt = compact.matches ? image.dataset.compactAlt : image.dataset.wideAlt;
  };
  const pause = () => {
    if (!video.paused) video.pause();
  };

  updateAlt();
  compact.addEventListener("change", updateAlt);
  button.hidden = false;
  button.addEventListener("click", async () => {
    if (video.hidden) {
      video.hidden = false;
      poster.hidden = true;
      button.textContent = "Show terminal still";
      button.setAttribute("aria-expanded", "true");
      if (!reducedMotion.matches) {
        try {
          await video.play();
        } catch {
          // Keep native controls available if media decoding is unavailable.
        }
      }
      return;
    }
    pause();
    video.hidden = true;
    poster.hidden = false;
    button.textContent = "Play terminal demo";
    button.setAttribute("aria-expanded", "false");
  });

  document.addEventListener("visibilitychange", () => {
    if (document.hidden) pause();
  });
  reducedMotion.addEventListener("change", (event) => {
    if (event.matches) pause();
  });
  const visibility = new IntersectionObserver((entries) => {
    if (entries.some((entry) => !entry.isIntersecting)) pause();
  });
  visibility.observe(root);
});
