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

## Preview locally

Open `index.html` in a browser. Everything works from the file.

## Deploy on GitHub Pages

1. Create a repo named `YOUR-USERNAME.github.io` (or any name for a project site).
2. Put `index.html`, `styles.css`, `script.js` and the `assets/` folder in the repo root and push.
3. Repo **Settings → Pages → Build and deployment**: Source = *Deploy from a branch*, Branch = `main`, folder `/ (root)`.
4. Visit `https://YOUR-USERNAME.github.io` after a minute or two.

## Before publishing

- Replace `YOUR-USERNAME` and `YOUR-HANDLE` in the Contact section.
- Your phone number is intentionally left off the public site.
