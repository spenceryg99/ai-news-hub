# AI News Hub

Daily aggregation of AI news, papers, open-source models, and trending GitHub repos.

## Architecture

```
.github/workflows/daily.yml  ← GitHub Actions (UTC 02:00 daily)
├── src/
│   ├── collector_hf_papers.py   ← Hugging Face Daily Papers
│   ├── collector_arxiv.py       ← arXiv latest papers (cs.AI, cs.LG, cs.CL, cs.CV)
│   ├── collector_github.py      ← GitHub Trending AI repos
│   ├── collector_hf_models.py   ← New models on Hugging Face
│   ├── collector_rss.py         ← RSS feeds (TechCrunch AI, Reddit, etc.)
│   ├── aggregator.py            ← Merge all data
│   └── site_generator.py        ← Generate static HTML
├── run.py                       ← Entry point
├── requirements.txt
└── .github/workflows/daily.yml
```

## Setup

### 1. Push to GitHub

```bash
git init
git add .
git commit -m "init"
gh repo create ai-news-hub --public --push
```

### 2. Enable GitHub Pages

- Go to repo → Settings → Pages
- Source: **GitHub Actions**

### 3. Run

The workflow runs daily at UTC 02:00. You can also trigger it manually from Actions tab.

Your site will be at: `https://<username>.github.io/ai-news-hub`

## Local Development

```bash
pip install -r requirements.txt
python run.py
open output/index.html
```

## Customization

- Edit `src/config.py` to add/remove RSS feeds
- Set env `HF_ENDPOINT=https://hf-mirror.com` to use HF mirror (China users)
- Adjust `COLLECTORS` dict to enable/disable sources
