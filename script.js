// Footer year
document.getElementById("yr").textContent = new Date().getFullYear();

// Highlight the nav link for the section in view
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

// Glass highlight follows the pointer
const fine = matchMedia("(hover: hover) and (pointer: fine)").matches;
const calm = matchMedia("(prefers-reduced-motion: reduce)").matches;
if (fine && !calm) {
  document.querySelectorAll(".glass").forEach(el => {
    el.addEventListener("pointermove", e => {
      const r = el.getBoundingClientRect();
      el.style.setProperty("--mx", ((e.clientX - r.left) / r.width * 100).toFixed(1) + "%");
      el.style.setProperty("--my", ((e.clientY - r.top) / r.height * 100).toFixed(1) + "%");
    });
    el.addEventListener("pointerleave", () => {
      el.style.removeProperty("--mx");
      el.style.removeProperty("--my");
    });
  });
}
