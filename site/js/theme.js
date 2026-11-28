// Theme: dark-first; a manual choice (localStorage) overrides prefers-color-scheme.
(function () {
  var KEY = "scl-theme";
  var root = document.documentElement;
  var saved = null;
  try { saved = localStorage.getItem(KEY); } catch (e) { /* storage blocked */ }
  if (saved === "light" || saved === "dark") root.setAttribute("data-theme", saved);
  function current() {
    var t = root.getAttribute("data-theme");
    if (t) return t;
    return window.matchMedia && window.matchMedia("(prefers-color-scheme: light)").matches ? "light" : "dark";
  }
  function sync(btn) {
    var t = current();
    btn.textContent = t === "dark" ? "Switch to light theme" : "Switch to dark theme";
  }
  document.addEventListener("DOMContentLoaded", function () {
    var btn = document.getElementById("theme-toggle");
    if (!btn) return;
    sync(btn);
    btn.addEventListener("click", function () {
      var next = current() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem(KEY, next); } catch (e) { /* ignore */ }
      sync(btn);
      document.dispatchEvent(new CustomEvent("themechange", { detail: next }));
    });
  });
})();
