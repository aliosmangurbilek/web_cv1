(() => {
  function closeLanguageNotice(notice) {
    notice.classList.remove("is-visible");
    window.setTimeout(() => {
      notice.hidden = true;
    }, 220);
  }

  function initLanguageNotice() {
    const notice = document.getElementById("language-notice");

    if (!notice) {
      return;
    }

    const closeButton = notice.querySelector(".language-notice-close");
    const secondaryButton = notice.querySelector(".language-notice-secondary");

    if (closeButton) {
      closeButton.addEventListener("click", () => {
        closeLanguageNotice(notice);
      });
    }

    if (secondaryButton) {
      secondaryButton.addEventListener("click", () => {
        closeLanguageNotice(notice);
      });
    }

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && !notice.hidden) {
        closeLanguageNotice(notice);
      }
    });
  }

  initLanguageNotice();
})();
