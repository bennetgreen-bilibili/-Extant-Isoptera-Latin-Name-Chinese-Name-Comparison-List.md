(function () {
  "use strict";

  var DEFAULT_LANG = "zh-CN";

  function normalize(lang) {
    return lang === "en" || lang === "es" ? lang : DEFAULT_LANG;
  }

  function init(section) {
    var toolbar = section.querySelector(".taxon-literature-switch");
    if (!toolbar) return;
    var buttons = toolbar.querySelectorAll("button[data-lit-set]");
    if (!buttons.length) return;

    function setLang(lang) {
      lang = normalize(lang);
      section.setAttribute("data-lit-active", lang);
      section.setAttribute("lang", lang);

      var i;
      for (i = 0; i < buttons.length; i += 1) {
        buttons[i].setAttribute("aria-pressed", buttons[i].getAttribute("data-lit-set") === lang ? "true" : "false");
      }

      var variants = section.querySelectorAll("[data-lit-lang]");
      for (i = 0; i < variants.length; i += 1) {
        variants[i].hidden = variants[i].getAttribute("data-lit-lang") !== lang;
      }
    }

    for (var i = 0; i < buttons.length; i += 1) {
      buttons[i].addEventListener("click", function () {
        setLang(this.getAttribute("data-lit-set"));
      });
    }

    toolbar.hidden = false;
    setLang(section.getAttribute("data-lit-active") || DEFAULT_LANG);
  }

  var sections = document.querySelectorAll(".taxon-literature");
  for (var i = 0; i < sections.length; i += 1) init(sections[i]);
})();
