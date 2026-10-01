(() => {
  function initSpatialCards() {
    const reducedMotion = window.matchMedia("(prefers-reduced-motion: reduce)");
    const precisePointer = window.matchMedia("(hover: hover) and (pointer: fine)");

    if (reducedMotion.matches || !precisePointer.matches) {
      return;
    }

    const cards = document.querySelectorAll(
      ".hero-copy, .focus-panel, .summary-card, .timeline-card, .project-card, .stack-card, .contact-card"
    );

    cards.forEach((card) => {
      let frame = null;

      if (card.classList.contains("reveal")) {
        card.addEventListener("animationend", () => card.classList.remove("reveal"), { once: true });
      }

      const updateTilt = (event) => {
        const bounds = card.getBoundingClientRect();
        const pointerX = (event.clientX - bounds.left) / bounds.width;
        const pointerY = (event.clientY - bounds.top) / bounds.height;
        const rotateX = (0.5 - pointerY) * 6;
        const rotateY = (pointerX - 0.5) * 6;

        if (frame) {
          window.cancelAnimationFrame(frame);
        }

        frame = window.requestAnimationFrame(() => {
          card.style.setProperty("--tilt-x", `${rotateX.toFixed(2)}deg`);
          card.style.setProperty("--tilt-y", `${rotateY.toFixed(2)}deg`);
          card.style.setProperty("--glare-x", `${(pointerX * 100).toFixed(1)}%`);
          card.style.setProperty("--glare-y", `${(pointerY * 100).toFixed(1)}%`);
        });
      };

      card.classList.add("spatial-card");
      card.addEventListener("pointerenter", () => card.classList.add("is-tilting"));
      card.addEventListener("pointermove", updateTilt);
      card.addEventListener("pointerleave", () => {
        card.classList.remove("is-tilting");
        card.style.setProperty("--tilt-x", "0deg");
        card.style.setProperty("--tilt-y", "0deg");
        card.style.setProperty("--glare-x", "50%");
        card.style.setProperty("--glare-y", "50%");
      });
    });
  }

  initSpatialCards();
})();
