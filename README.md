# SawyerRooneyWebsite
[Website for Sawyer Rooney](https://sawyerr-mit.github.io/SawyerRooneyWebsite/)

Liquid-glass portfolio over a blue-violet backdrop. Plain HTML, CSS and JS with no build step.

## Pages

- `index.html` is the home page. **View projects** and the **Projects** nav button open `projects.html`.
- `projects.html` lists every project and can be sorted by **Recency** or **Scale**.
- `projects/<name>.html` is each project's own sub-site (overview, highlights, full source code, downloads).

## Sorting

Each card in `projects.html` has `data-date="YYYY-MM"` (start date, used for Recency) and `data-scale="1-3"` (3 Large, 2 Medium, 1 Small). Edit those two attributes, plus the visible "Scale:" chip and date text, to change how a project sorts.

## Images

Projects with real images keep them in `assets/projects/<name>/`. The Cold-gas RCS, Smith-Purcell and chess robot cards show a dashed placeholder until you add `assets/project-rcs.jpg`, `assets/project-photonics.jpg` and `assets/project-chess.jpg` (16:9, under about 500 KB). `assets/hero.jpg` is the home page portrait.

## Downloads

The six Python projects ship with their full source in `assets/projects/<name>/` (individual files plus a `-source.zip` of the whole folder). The three non-code projects look for `assets/files/<name>-report.pdf`, `-slides.pdf` and `-files.zip`; on the live site a missing file shows "Coming soon". The resume is `assets/Sawyer-Rooney-Resume.pdf`.

## Preview locally

Open `index.html` in a browser. Everything works from the file.

## Deploy on GitHub Pages

1. Create a repo named `YOUR-USERNAME.github.io` (or any name for a project site).
2. Put `index.html`, `projects.html`, `styles.css`, `script.js`, the `projects/` folder and the `assets/` folder in the repo root and push.
3. Repo **Settings → Pages → Build and deployment**: Source = *Deploy from a branch*, Branch = `main`, folder `/ (root)`.
4. Visit `https://YOUR-USERNAME.github.io` after a minute or two.

## Before publishing

- Your phone number is intentionally left off the public site.
