!(function () {
  const e = () => localStorage.getItem("theme"),
    t = document.documentElement.getAttribute("data-bss-forced-theme"),
    a = () => {
      if (t) return t;
      const a = e();
      if (a) return a;
      const r = document.documentElement.getAttribute("data-bs-theme");
      return (
        r ||
        (window.matchMedia("(prefers-color-scheme: dark)").matches
          ? "dark"
          : "light")
      );
    },
    r = (e) => {
      "auto" === e && window.matchMedia("(prefers-color-scheme: dark)").matches
        ? document.documentElement.setAttribute("data-bs-theme", "dark")
        : document.documentElement.setAttribute("data-bs-theme", e);
    };
  r(a());
  const c = (e, t = !1) => {
    const a = [].slice.call(document.querySelectorAll(".theme-switcher"));
    if (a.length) {
      document.querySelectorAll("[data-bs-theme-value]").forEach((e) => {
        e.classList.remove("active"), e.setAttribute("aria-pressed", "false");
      });
      for (const t of a) {
        const a = t.querySelector('[data-bs-theme-value="' + e + '"]');
        a &&
          (a.classList.add("active"), a.setAttribute("aria-pressed", "true"));
      }
    }
  };
  window
    .matchMedia("(prefers-color-scheme: dark)")
    .addEventListener("change", () => {
      const t = e();
      "light" !== t && "dark" !== t && r(a());
    }),
    window.addEventListener("DOMContentLoaded", () => {
      c(a()),
        document.querySelectorAll("[data-bs-theme-value]").forEach((e) => {
          e.addEventListener("click", (t) => {
            t.preventDefault();
            const a = e.getAttribute("data-bs-theme-value");
            ((e) => {
              localStorage.setItem("theme", e);
            })(a),
              r(a),
              c(a);
          });
        });
    });
})();
