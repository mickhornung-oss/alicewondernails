(function () {
  "use strict";

  var revealBlocks = document.querySelectorAll(".reveal");
  var mediaCards = document.querySelectorAll(".media-card");
  var splash = document.getElementById("logoSplash");
  var splashVisibleMs = 3000;
  var splashFadeMs = 680;

  if (splash) {
    document.body.classList.add("has-splash");

    window.setTimeout(function () {
      splash.classList.add("is-fading");
    }, splashVisibleMs);

    window.setTimeout(function () {
      if (splash.parentNode) {
        splash.parentNode.removeChild(splash);
      }
      document.body.classList.remove("has-splash");
    }, splashVisibleMs + splashFadeMs);
  }

  mediaCards.forEach(function (card, index) {
    card.style.setProperty("--card-delay", (index * 65) + "ms");
  });

  if ("IntersectionObserver" in window) {
    var observer = new IntersectionObserver(function (entries, obs) {
      entries.forEach(function (entry) {
        if (entry.isIntersecting) {
          entry.target.classList.add("is-visible");
          obs.unobserve(entry.target);
        }
      });
    }, { threshold: 0.14 });

    revealBlocks.forEach(function (block) {
      observer.observe(block);
    });
  } else {
    revealBlocks.forEach(function (block) {
      block.classList.add("is-visible");
    });
  }

  // Kontakt und Early Access laufen aktuell über E-Mail oder Instagram.
})();
