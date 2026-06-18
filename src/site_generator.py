import os
from datetime import datetime
from src.config import OUTPUT_DIR, SITE_CONFIG
from src.aggregator import load_all

CSS = """\
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#f5f5f7;--surface:#fff;--text:#1d1d1f;--text2:#86868b;--border:#d2d2d7;--accent:#0066cc;--accent2:#5856d6;--radius:14px;--card-bg:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#1c1c1e;--surface:#2c2c2e;--text:#f5f5f7;--text2:#98989d;--border:#38383a;--accent:#0a84ff;--accent2:#5e5ce6;--card-bg:#2c2c2e}}
body{font-family:-apple-system,BlinkMacSystemFont,"SF Pro","Helvetica Neue","Noto Sans SC",sans-serif;background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased}
.container{max-width:900px;margin:0 auto;padding:0 20px}
header{padding:48px 0 12px;text-align:center}
header h1{font-size:28px;font-weight:700;letter-spacing:-.3px}
header h1 span{background:linear-gradient(135deg,#0066cc,#5856d6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.date-bar{display:flex;justify-content:center;gap:20px;color:var(--text2);font-size:14px;margin-top:6px;flex-wrap:wrap}
.summary{background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius);padding:20px 24px;margin:24px 0;text-align:center;font-size:15px;color:var(--text2);line-height:1.7}
.summary strong{color:var(--accent);font-weight:600}
.section{margin-bottom:36px}
.section-header{display:flex;align-items:baseline;gap:10px;margin-bottom:16px;padding-bottom:8px;border-bottom:1px solid var(--border)}
.section-header h2{font-size:20px;font-weight:700;letter-spacing:-.2px}
.section-header .count{margin-left:auto;font-size:13px;color:var(--text2);font-weight:400}
.card{background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius);padding:18px 20px;margin-bottom:10px;transition:all .2s;display:block;text-decoration:none;color:inherit}
.card:hover{border-color:var(--accent);transform:translateY(-1px)}
.card-featured{background:var(--card-bg);border:1px solid var(--border);border-radius:var(--radius);padding:24px 28px;margin-bottom:14px;transition:all .2s;display:block;text-decoration:none;color:inherit;position:relative}
.card-featured:hover{border-color:var(--accent);transform:translateY(-2px)}
.badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 10px;border-radius:20px;margin-bottom:8px;letter-spacing:.2px}
.badge-paper{background:#e8f0fe;color:#1967d2}
.badge-model{background:#fef7e0;color:#e37400}
.badge-oss{background:#e6f4ea;color:#137333}
.badge-news{background:#f3e8fd;color:#7c3aed}
@media(prefers-color-scheme:dark){.badge-paper{background:#1a2a4a;color:#8ab4f8}.badge-model{background:#3a2a0a;color:#fdd663}.badge-oss{background:#1a3a2a;color:#81c995}.badge-news{background:#2a1a4a;color:#c58af9}}
.card-title{font-size:16px;font-weight:600;line-height:1.4;margin-bottom:6px;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
.card-featured .card-title{font-size:18px}
.card-desc{font-size:14px;color:var(--text2);line-height:1.5;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;margin-bottom:8px}
.card-featured .card-desc{-webkit-line-clamp:3}
.card-meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12px;color:var(--text2);margin-top:4px}
.card-meta .sep{opacity:.4;margin:0 2px}
.tag{font-size:11px;background:var(--border);padding:1px 8px;border-radius:4px;color:var(--text2)}
footer{text-align:center;padding:40px 0;font-size:13px;color:var(--text2);border-top:1px solid var(--border);margin-top:16px;line-height:2}
@media(max-width:640px){header h1{font-size:24px}.card-featured{padding:18px 20px}.card{padding:14px 16px}.container{padding:0 14px}}
"""


def badge(label: str, css_class: str) -> str:
    return f'<span class="badge {css_class}">{label}</span>'


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def fmt_date(s: str) -> str:
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d.strftime("%m-%d")
    except Exception:
        return s[:10] if s else ""


def render_card(item: dict, featured: bool = False) -> str:
    title = esc(item.get("title") or item.get("name", ""))
    url = esc(item.get("url", "#"))
    desc = esc((item.get("description") or "")[:300])
    source = item.get("source", "")
    tag_cls = "badge-paper"

    s = source.lower()
    if "model" in s:
        tag_cls = "badge-model"
    elif "github" in s or "trending" in s:
        tag_cls = "badge-oss"
    elif "techcrunch" in s or "reddit" in s or "mit" in s or "rss" in s or "blog" in s:
        tag_cls = "badge-news"

    tag = badge(source or "Paper", tag_cls)

    meta = []
    pub = item.get("published", item.get("updated_at", ""))
    if pub:
        meta.append(fmt_date(pub))
    authors = item.get("authors")
    if authors and len(authors) > 0:
        meta.append(esc(" · ".join(authors[:2])))
    stars = item.get("stars", item.get("likes", 0))
    if stars:
        meta.append(f'&#9733; {stars}')
    pipeline = item.get("pipeline_tag", "")
    if pipeline:
        meta.append(esc(pipeline))

    topics_html = ""
    topics = item.get("topics", item.get("tags", []))
    if topics:
        chips = "".join(f'<span class="tag">{esc(str(t))}</span>' for t in topics[:3])
        topics_html = f'<div style="margin-top:6px">{chips}</div>'

    meta_html = '<span class="sep">·</span>'.join(meta) if meta else ""

    cls = "card-featured" if featured else "card"
    return (
        f'<a href="{url}" target="_blank" rel="noopener" class="{cls}">'
        f"{tag}{topics_html}"
        f'<h3 class="card-title">{title}</h3>'
        f'<p class="card-desc">{desc}</p>'
        f'<div class="card-meta">{meta_html}</div>'
        f"</a>"
    )


def pick_featured(data: dict, n: int = 5) -> list[dict]:
    candidates = []
    for key, items in data.items():
        for it in items:
            score = 0
            stars = int(str(it.get("stars", 0)).replace(",", "")) if it.get("stars") else 0
            likes = it.get("likes", 0) or 0
            if stars:
                score += stars
            if likes:
                score += likes
            it["_sort_score"] = score
            it["_source_key"] = key
            candidates.append(it)
    candidates.sort(key=lambda x: x.get("_sort_score", 0), reverse=True)
    return candidates[:n]


def generate_site():
    data = load_all()
    now = datetime.utcnow()

    featured = pick_featured(data)
    total = sum(len(v) for v in data.values())
    date_str = now.strftime("%Y-%m-%d")

    # count by source
    counts = {k: len(v) for k, v in data.items()}

    parts = []
    a = parts.append
    a("<!DOCTYPE html>")
    a('<html lang="zh-CN">')
    a("<head>")
    a('<meta charset="UTF-8">')
    a('<meta name="viewport" content="width=device-width, initial-scale=1.0">')
    a(f"<title>{esc(SITE_CONFIG['title'])} \u00b7 {date_str}</title>")
    a(f'<meta name="description" content="AI \u8d44\u8baf\u6c47\u603b - {date_str}">')
    a(f"<style>{CSS}</style>")
    a("</head>")
    a("<body>")
    a('<div class="container">')
    a(f"<header><h1><span>{esc(SITE_CONFIG['title'])}</span></h1>")
    a(f'<div class="date-bar"><span>\U0001f4c5 {date_str}</span><span>\U0001f4ca {total} \u6761</span></div></header>')

    a(f'<div class="summary">\U0001f916 <strong>AI News Hub</strong> \u6bcf\u65e5\u81ea\u52a8\u91c7\u96c6\u6700\u65b0AI\u8d44\u8baf\u3001\u5f00\u6e90\u6a21\u578b\u3001\u7814\u7a76\u8bba\u6587\u548c\u884c\u4e1a\u52a8\u6001\u3002\u5171\u91c7\u96c6\u6765\u81ea Hugging Face\u3001arXiv\u3001GitHub \u7b49\u591a\u4e2a\u6e90\u7684 {total} \u6761\u5185\u5bb9\u3002</div>')

    a(f'<section class="section"><div class="section-header"><h2>\U0001f525 \u4eca\u65e5\u7cbe\u9009</h2><span class="count">{len(featured)} \u6761</span></div>')
    for it in featured:
        a(render_card(it, featured=True))
    a("</section>")

    hf_papers = data.get("hf_papers", [])
    arxiv = data.get("arxiv", [])
    papers = hf_papers + arxiv
    papers.sort(key=lambda x: x.get("published", ""), reverse=True)
    if papers:
        a(f'<section class="section"><div class="section-header"><h2>\U0001f4d6 \u6700\u65b0\u7814\u7a76\u8bba\u6587</h2><span class="count">{len(papers)} \u6761</span></div>')
        for it in papers[:15]:
            a(render_card(it))
        a("</section>")

    models = data.get("hf_models", [])
    if models:
        a(f'<section class="section"><div class="section-header"><h2>\U0001f916 \u65b0\u53d1\u5e03\u6a21\u578b</h2><span class="count">{len(models)} \u6761</span></div>')
        for it in models[:12]:
            a(render_card(it))
        a("</section>")

    repos = data.get("github_trending", [])
    if repos:
        a(f'<section class="section"><div class="section-header"><h2>\u2b50 \u70ed\u95e8\u5f00\u6e90\u9879\u76ee</h2><span class="count">{len(repos)} \u6761</span></div>')
        for it in repos[:12]:
            a(render_card(it))
        a("</section>")

    news = data.get("rss_news", [])
    if news:
        a(f'<section class="section"><div class="section-header"><h2>\U0001f4f0 \u884c\u4e1a\u65b0\u95fb</h2><span class="count">{len(news)} \u6761</span></div>')
        for it in news[:10]:
            a(render_card(it))
        a("</section>")

    a(f'<footer>\U0001f916 {esc(SITE_CONFIG["title"])} \u00b7 \u6bcf\u65e5 UTC 02:00 \u81ea\u52a8\u66f4\u65b0<br>Data from Hugging Face &middot; arXiv &middot; GitHub &middot; RSS</footer>')
    a("</div>")
    a("</body>")
    a("</html>")

    html = "\n".join(parts)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n[site_generator] Site generated: {path} ({len(html)} bytes, {total} items)")
    return path


if __name__ == "__main__":
    generate_site()
