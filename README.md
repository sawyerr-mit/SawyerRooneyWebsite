# SawyerRooneyWebsite
[Website for Sawyer Rooney](https://sawyerr-mit.github.io/SawyerRooneyWebsite/)

Liquid-glass portfolio over a blue-violet backdrop. Plain HTML, CSS and JS with no build step.

## Add your images

Create an `assets/` folder next to `index.html` and drop in these files. Each slot shows a dashed placeholder until its image exists, then the image fills the frame automatically.

| File | Where it appears | Best shape |
| --- | --- | --- |
| `assets/hero.jpg` | Hero frame, top of the page | Portrait, 4:5 |
| `assets/project-rcs.jpg` | Cold-gas RCS card | Landscape, 16:9 |
| `assets/project-photonics.jpg` | Smith-Purcell card | Landscape, 16:9 |
| `assets/project-chess.jpg` | Chess robot card | Landscape, 16:9 |
| `assets/project-ml.jpg` | Numerical methods card | Landscape, 16:9 |

Use `.jpg`, or change the filename in `index.html` for `.png` / `.webp`. Keep each under about 500 KB so the page loads fast. Any slot you don't want can be deleted: remove its whole `<div class="media ...">` block.

## Project pages and downloads

Each project card links to its own page in `projects/` (`rcs.html`, `photonics.html`, `chess.html`, `ml.html`). They reuse the card's image from `assets/`.

**Add a project:** copy `projects/_template.html` to `projects/your-slug.html`, edit the text, then add a card in `index.html` whose title links to it. GitHub Pages doesn't publish files starting with `_`, so the template never appears on the live site.

**Downloads:** put files in `assets/files/` using the names on each page (for example `rcs-report.pdf`, `rcs-slides.pdf`, `rcs-files.zip`), or change the `href`. On the live site, file sizes appear automatically and a link whose file isn't uploaded yet shows "Coming soon" instead of a broken link. Each page also has **Save page as PDF**, which opens the browser's print dialog with a clean print layout.

## Preview locally

Open `index.html` in a browser. Everything works from the file.

## Deploy on GitHub Pages

1. Create a repo named `YOUR-USERNAME.github.io` (or any name for a project site).
2. Put `index.html`, `styles.css`, `script.js`, the `projects/` folder and the `assets/` folder in the repo root and push.
3. Repo **Settings → Pages → Build and deployment**: Source = *Deploy from a branch*, Branch = `main`, folder `/ (root)`.
4. Visit `https://YOUR-USERNAME.github.io` after a minute or two.

## Before publishing

- Replace `YOUR-USERNAME` and `YOUR-HANDLE` in the Contact section.
- Your phone number is intentionally left off the public site.
