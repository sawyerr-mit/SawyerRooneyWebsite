// Footer year
const yr = document.getElementById("yr");
if (yr) yr.textContent = new Date().getFullYear();

// Home page: mark the nav button for the section in view
const links = [...document.querySelectorAll(".nav-links a[href^='#']")];
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

// Projects tab: sort by recency (start date) or scale; ties fall back to the other key
const grid = document.getElementById("grid");
if (grid) {
  const note = document.getElementById("sort-note");
  const btns = [...document.querySelectorAll("[data-sort]")];
  const notes = {
    recency: "Newest first. Each project is ordered by when it started.",
    scale: "Largest first. Projects of equal scale are ordered newest first."
  };
  const num = (el, k) => k === "date" ? +el.dataset.date.replace("-", "") : +el.dataset.scale;
  const sortBy = mode => {
    const [a, b] = mode === "scale" ? ["scale", "date"] : ["date", "scale"];
    [...grid.children].sort((x, y) => num(y, a) - num(x, a) || num(y, b) - num(x, b)).forEach(el => grid.appendChild(el));
    btns.forEach(btn => btn.setAttribute("aria-pressed", String(btn.dataset.sort === mode)));
    note.textContent = notes[mode];
  };
  btns.forEach(btn => btn.addEventListener("click", () => sortBy(btn.dataset.sort)));
  sortBy("recency");
}

// Project pages: show file sizes, and mark downloads that are not uploaded yet (deployed site only)
if (location.protocol.startsWith("http")) {
  document.querySelectorAll("a.dl[download]").forEach(a => {
    const tag = a.querySelector("small");
    fetch(a.href, { method: "HEAD" }).then(r => {
      if (!r.ok) throw 0;
      const n = +r.headers.get("content-length");
      if (n) tag.append(", " + (n > 1e6 ? (n / 1e6).toFixed(1) + " MB" : Math.max(1, Math.round(n / 1e3)) + " KB"));
    }).catch(() => {
      a.setAttribute("aria-disabled", "true");
      a.removeAttribute("href");
      tag.textContent = "Coming soon";
    });
  });
}

// Project pages: click an image to enlarge it (Esc, the Close button or a click anywhere closes it)
const shots = document.querySelectorAll(".shot img");
if (shots.length && typeof HTMLDialogElement === "function") {
  const dlg = document.createElement("dialog");
  dlg.className = "lightbox";
  dlg.setAttribute("aria-label", "Enlarged image");
  dlg.innerHTML = '<div class="lb-inner"><img alt=""><p class="lb-cap"></p><button class="btn primary small" type="button">Close</button></div>';
  document.body.appendChild(dlg);
  const big = dlg.querySelector("img"), cap = dlg.querySelector(".lb-cap");
  const openShot = img => {
    big.src = img.currentSrc || img.src;
    big.alt = img.alt;
    const fc = img.parentElement.querySelector("figcaption");
    cap.textContent = fc ? fc.textContent : "";
    document.documentElement.style.overflow = "hidden";
    dlg.showModal();
  };
  dlg.addEventListener("click", () => dlg.close());
  dlg.addEventListener("close", () => { document.documentElement.style.overflow = ""; });
  shots.forEach(img => {
    img.tabIndex = 0;
    img.setAttribute("role", "button");
    img.setAttribute("aria-label", "Enlarge image: " + img.alt);
    img.addEventListener("click", () => openShot(img));
    img.addEventListener("keydown", e => {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); openShot(img); }
    });
  });
}
