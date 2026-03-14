(() => {
  const STORAGE_KEYS = {
    preferredLanguage: "preferred-site-language-v6",
  };

  const pageLanguage = (document.documentElement.lang || "en").toLowerCase();

  function rememberLanguage(language) {
    localStorage.setItem(STORAGE_KEYS.preferredLanguage, language);
  }

  function wireLanguageLinks() {
    const languageLinks = document.querySelectorAll("[data-site-language]");

    languageLinks.forEach((link) => {
      link.addEventListener("click", () => {
        const { siteLanguage } = link.dataset;

        if (siteLanguage) {
          rememberLanguage(siteLanguage);
        }
      });
    });
  }

  function closeLanguageNotice(notice) {
    notice.classList.remove("is-visible");
    window.setTimeout(() => {
      notice.remove();
    }, 220);
  }

  function wireLanguageNotice(notice) {
    if (!notice || notice.dataset.wired === "true") {
      return;
    }

    notice.dataset.wired = "true";

    const closeButton = notice.querySelector(".language-notice-close");
    const secondaryButton = notice.querySelector(".language-notice-secondary");
    const primaryLink = notice.querySelector(".language-notice-primary");

    if (primaryLink) {
      primaryLink.addEventListener("click", () => {
        rememberLanguage("tr");
      });
    }

    if (closeButton) {
      closeButton.addEventListener("click", () => {
        rememberLanguage("en");
        closeLanguageNotice(notice);
      });
    }

    if (secondaryButton) {
      secondaryButton.addEventListener("click", () => {
        rememberLanguage("en");
        closeLanguageNotice(notice);
      });
    }

    document.addEventListener("keydown", (event) => {
      if (event.key === "Escape" && document.body.contains(notice)) {
        rememberLanguage("en");
        closeLanguageNotice(notice);
      }
    });
  }

  function createLanguageNotice() {
    const notice = document.createElement("aside");
    notice.className = "language-notice";
    notice.id = "language-notice";
    notice.setAttribute("role", "dialog");
    notice.setAttribute("aria-labelledby", "language-notice-title");
    notice.setAttribute("aria-live", "polite");

    notice.innerHTML = `
      <div class="language-notice-inner">
        <button class="language-notice-close" type="button" aria-label="Close language reminder">
          <span aria-hidden="true">&times;</span>
        </button>
        <div class="language-notice-head">
          <div class="language-notice-avatar-wrap" aria-hidden="true">
            <div class="language-notice-switchmark">
              <span class="language-notice-switchmark-lang language-notice-switchmark-lang-tr">TR</span>
              <span class="language-notice-switchmark-arrow">&harr;</span>
              <span class="language-notice-switchmark-lang language-notice-switchmark-lang-en">EN</span>
            </div>
          </div>
          <p class="language-notice-kicker">Language option</p>
        </div>
        <h2 id="language-notice-title">Bu sitenin Türkçe versiyonu da hazır.</h2>
        <p class="language-notice-copy">
          İlk ziyaretinizde hatırlatma olarak bırakıyorum. İsterseniz içeriği Türkçe sürümden devam ettirebilirsiniz.
        </p>
        <div class="language-notice-actions">
          <a class="button button-primary language-notice-primary" href="index-tr.html" data-site-language="tr">
            Türkçe aç
          </a>
          <button class="language-notice-secondary" type="button">
            İngilizce kal
          </button>
        </div>
      </div>
    `;

    document.body.appendChild(notice);
    wireLanguageNotice(notice);

    requestAnimationFrame(() => {
      notice.classList.add("is-visible");
    });
  }

  function maybeShowLanguageNotice() {
    if (pageLanguage !== "en") {
      return;
    }

    const existingNotice = document.getElementById("language-notice");

    if (existingNotice) {
      wireLanguageNotice(existingNotice);
      return;
    }

    window.setTimeout(() => {
      createLanguageNotice();
    }, 180);
  }

  wireLanguageLinks();

  if (pageLanguage === "tr") {
    rememberLanguage("tr");
  }

  maybeShowLanguageNotice();
})();
