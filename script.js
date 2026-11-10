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
