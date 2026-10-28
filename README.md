# Guess the Language

A small web game: read a sentence and guess whether it's English, German or Spanish. Ten rounds per game.

I'm building it in stages to learn how to deploy software properly. Each stage adds one deployment skill, and the last one adds AI.

**Live demo:** https://YOUR-USERNAME.github.io/guess-the-language/ *(replace with your link)*

## Roadmap

- [x] **Stage 1 – Static site.** One HTML page, deployed on GitHub Pages.
- [ ] **Stage 2 – Python backend.** Game logic moves to a FastAPI app on Render.
- [ ] **Stage 3 – Database.** A global leaderboard stored in Postgres.
- [ ] **Stage 4 – Docker + CI/CD.** Tests run on every push; the app deploys only if they pass.
- [ ] **Stage 5 – Observability.** Health check, structured logs, error tracking.
- [ ] **Stage 6 – AI.** A trained model guesses along with the player; later an LLM writes new sentences.

## Run it locally

No install needed. Either double-click `index.html`, or serve the folder (closer to how a real host works):

```bash
python -m http.server 8000
# then open http://localhost:8000
```

## Deploy to GitHub Pages

### Option A: in the browser (easiest for the first time)

1. On GitHub, click **New repository**. Name it `guess-the-language`, set it to **Public**, and create it.
2. Click **Add file → Upload files**, drag in `index.html` and `README.md`, and click **Commit changes**.
3. Go to **Settings → Pages**. Under **Build and deployment**, set **Source** to *Deploy from a branch*, choose **main** and **/ (root)**, and click **Save**.
4. Wait a minute or two, then refresh the page. Your link appears at the top: `https://YOUR-USERNAME.github.io/guess-the-language/`.

### Option B: with git in the terminal (what you'll use from Stage 2 on)

```bash
cd guess-the-language
git init
git add index.html README.md
git commit -m "Stage 1: static game"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/guess-the-language.git
git push -u origin main
```

Then do step 3 from Option A to switch on Pages.

### Updating the site

Every push to `main` redeploys automatically. Change something, commit, push, and the live site updates in about a minute. You can watch each deployment under the repo's **Actions** tab.

## How it works

Everything is in `index.html`:

- **Data:** a list of 30 sentences, each tagged with its language (`en`, `de`, `es`).
- **State:** one object holds the round, score, streak and history.
- **Rendering:** functions update the page from that state.
- **Events:** buttons or keys 1, 2, 3 to answer.

Your best score is saved in your own browser with `localStorage`. A real shared leaderboard comes in Stage 3.

## What I learned

