// Footer year
document.getElementById("yr").textContent = new Date().getFullYear();

// Highlight the nav link for the section in view (one observer, no scroll handlers)
const links = [...document.querySelectorAll(".nav-links a[href^='#']:not(.btn)")];
const targets = links.map(a => document.querySelector(a.getAttribute("href"))).filter(Boolean);
if ("IntersectionObserver" in window && targets.length) {
  const io = new IntersectionObserver(entries => {
    entries.forEach(e => {
      if (!e.isIntersecting) return;
      links.forEach(a => a.classList.toggle("active", a.getAttribute("href") === "#" + e.target.id));
    });
  }, { rootMargin: "-40% 0px -55% 0px" });
  targets.forEach(t => io.observe(t));
}

// Project pages: show file sizes, and mark downloads that haven't been uploaded yet (deployed site only)
if (location.protocol.startsWith("http")) {
  document.querySelectorAll("a.dl[download]").forEach(a => {
    fetch(a.href, { method: "HEAD" }).then(r => {
      if (!r.ok) throw 0;
      const n = +r.headers.get("content-length");
      if (n) a.querySelector("small").append(", " + (n > 1e6 ? (n / 1e6).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1e3)) + " KB"));
    }).catch(() => {
      a.setAttribute("aria-disabled", "true");
      a.removeAttribute("href");
      a.querySelector(".pill").textContent = "Coming soon";
    });
  });
}
