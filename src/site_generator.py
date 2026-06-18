import os
from datetime import datetime, timedelta, timezone
from src.config import OUTPUT_DIR, SITE_CONFIG, DATA_DIR
from src.aggregator import load_by_date, load_all, list_dates

CSS = """\
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#f5f5f7;--surface:#fff;--text:#1d1d1f;--text2:#86868b;--border:#d2d2d7;--accent:#0066cc;--accent2:#5856d6;--radius:14px;--card-radius:12px}
@media(prefers-color-scheme:dark){:root{--bg:#1c1c1e;--surface:#2c2c2e;--text:#f5f5f7;--text2:#98989d;--border:#38383a;--accent:#0a84ff;--accent2:#5e5ce6}}
body{font-family:-apple-system,BlinkMacSystemFont,"SF Pro","Helvetica Neue","Noto Sans SC",sans-serif;background:var(--bg);color:var(--text);line-height:1.6;-webkit-font-smoothing:antialiased}
.container{max-width:960px;margin:0 auto;padding:0 20px}
header{padding:40px 0 10px;text-align:center}
header h1{font-size:28px;font-weight:700;letter-spacing:-.3px}
header h1 span{background:linear-gradient(135deg,#0066cc,#5856d6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.date-bar{display:flex;justify-content:center;gap:16px;color:var(--text2);font-size:14px;margin-top:4px;flex-wrap:wrap}
.summary{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:20px 24px;margin:20px 0;text-align:center;font-size:14px;color:var(--text2);line-height:1.7}
.summary strong{color:var(--accent);font-weight:600}
.section{margin-bottom:32px}
.section-header{display:flex;align-items:baseline;gap:10px;margin-bottom:14px;padding-bottom:8px;border-bottom:1px solid var(--border)}
.section-header h2{font-size:19px;font-weight:700}
.section-header .count{margin-left:auto;font-size:13px;color:var(--text2)}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--card-radius);padding:16px 20px;margin-bottom:10px;transition:border-color .2s;text-decoration:none;color:inherit;display:block}
.card:hover{border-color:var(--accent)}
.card-featured{background:var(--surface);border:1px solid var(--border);border-radius:var(--card-radius);padding:20px 24px;margin-bottom:12px;transition:border-color .2s;text-decoration:none;color:inherit;display:block}
.card-featured:hover{border-color:var(--accent)}
.badge{display:inline-block;font-size:11px;font-weight:600;padding:2px 10px;border-radius:20px;margin-bottom:6px;letter-spacing:.2px}
.badge-paper{background:#e8f0fe;color:#1967d2}
.badge-model{background:#fef7e0;color:#e37400}
.badge-oss{background:#e6f4ea;color:#137333}
.badge-news{background:#f3e8fd;color:#7c3aed}
@media(prefers-color-scheme:dark){.badge-paper{background:#1a2a4a;color:#8ab4f8}.badge-model{background:#3a2a0a;color:#fdd663}.badge-oss{background:#1a3a2a;color:#81c995}.badge-news{background:#2a1a4a;color:#c58af9}}
.card-title{font-size:16px;font-weight:600;line-height:1.4;margin-bottom:4px;color:var(--text)}
.card-featured .card-title{font-size:18px}
.card-desc{font-size:13px;color:var(--text2);line-height:1.5;margin-bottom:6px}
.card-meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12px;color:var(--text2);margin-top:4px}
.card-meta .sep{opacity:.4;margin:0 2px}
.tag{font-size:11px;background:var(--border);padding:1px 8px;border-radius:4px;color:var(--text2)}
.abstract{font-size:13px;color:var(--text2);line-height:1.6;margin-top:8px;padding-top:8px;border-top:1px solid var(--border);display:none}
.abstract.show{display:block}
.abstract-toggle{font-size:12px;color:var(--accent);cursor:pointer;background:none;border:none;padding:4px 0;margin-top:4px;font-weight:500}
.abstract-toggle:hover{text-decoration:underline}
.paper-meta{font-size:12px;color:var(--text2);margin-top:4px}
.paper-meta a{color:var(--accent);text-decoration:none}
.paper-meta a:hover{text-decoration:underline}
.archive-nav{display:flex;gap:8px;justify-content:center;flex-wrap:wrap;margin:16px 0}
.archive-nav a{display:inline-block;padding:6px 14px;border:1px solid var(--border);border-radius:20px;font-size:13px;color:var(--text2);text-decoration:none;transition:all .2s}
.archive-nav a:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
.archive-nav a.active{background:var(--accent);color:#fff;border-color:var(--accent)}
footer{text-align:center;padding:32px 0;font-size:13px;color:var(--text2);border-top:1px solid var(--border);margin-top:16px;line-height:2}
@media(max-width:640px){header h1{font-size:24px}.card-featured{padding:16px 18px}.card{padding:14px 16px}.container{padding:0 14px}}
"""


def badge(label: str, css_class: str) -> str:
    return f'<span class="badge {css_class}">{label}</span>'


def esc(s: str) -> str:
    if s is None:
        return ""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#39;")


def fmt_date(s: str) -> str:
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
        return d.strftime("%m-%d")
    except Exception:
        return s[:10] if s else ""


def render_card(item: dict, featured: bool = False) -> str:
    title = esc(item.get("title") or item.get("name", ""))
    url = esc(item.get("url", "#"))
    desc = esc((item.get("description") or item.get("summary", ""))[:300] if not featured else (item.get("description") or item.get("summary", ""))[:400])
    source = item.get("source", "")
    item_type = item.get("type", "paper")

    tag_map = {"paper": "badge-paper", "model": "badge-model", "oss": "badge-oss", "news": "badge-news"}
    tag_cls = tag_map.get(item_type, "badge-paper")
    tag_html = badge(source or "Paper", tag_cls)

    meta = []
    pub = item.get("published", item.get("updated_at", ""))
    if pub:
        meta.append(fmt_date(pub))
    authors = item.get("authors", [])
    if authors:
        a_list = [esc(a) for a in authors[:3]]
        if len(authors) > 3:
            a_list.append(f"+{len(authors)-3}")
        meta.append(" · ".join(a_list))
    stars = item.get("stars", item.get("likes", 0))
    if stars:
        meta.append(f'&#9733; {stars}')
    pipeline = item.get("pipeline_tag", "")
    if pipeline:
        meta.append(esc(pipeline))
    lang = item.get("language", "")
    if lang:
        meta.append(esc(lang))
    meta_html = '<span class="sep">·</span>'.join(meta) if meta else ""

    # Paper extra details
    extra = ""
    if item_type == "paper":
        pdf = item.get("pdf_url", "")
        abstract = item.get("abstract", "")
        cats = item.get("categories", [])
        abstract_id = f"abs-{hash(title)%100000:05d}"

        cats_html = ""
        if cats:
            c_list = [esc(c) for c in cats[:5]]
            cats_html = "".join(f'<span class="tag">{c}</span>' for c in c_list)

        pdf_link = ""
        if pdf:
            pdf_link = f'<a href="{esc(pdf)}" target="_blank">PDF</a>'

        abstract_html = ""
        if abstract and len(abstract) > 200:
            abstract_html = (
                f'<div class="abstract" id="{abstract_id}">{esc(abstract)}</div>'
                f'<button class="abstract-toggle" onclick="'
                f'document.getElementById(\'{abstract_id}\').classList.toggle(\'show\');'
                f'this.textContent=this.textContent==\'展开摘要\'?\'收起摘要\':\'展开摘要\'">'
                f'展开摘要</button>'
            )

        extra = f'<div class="paper-meta">{cats_html} {pdf_link}</div>{abstract_html}'

    topics = item.get("topics", item.get("tags", []))
    topics_html = ""
    if topics:
        chips = "".join(f'<span class="tag">{esc(str(t))}</span>' for t in topics[:4])
        topics_html = f'<div style="margin-top:4px">{chips}</div>'

    cls = "card-featured" if featured else "card"
    return (
        f'<div class="{cls}">'
        f'{tag_html}{topics_html}'
        f'<a href="{url}" target="_blank" rel="noopener" style="text-decoration:none;color:inherit">'
        f'<h3 class="card-title">{title}</h3>'
        f'<p class="card-desc">{desc}</p>'
        f'</a>'
        f'{extra}'
        f'<div class="card-meta">{meta_html}</div>'
        f'</div>'
    )


def pick_featured(data: dict, n: int = 5) -> list[dict]:
    candidates = []
    for key, items in data.items():
        for it in items:
            score = 0
            stars_str = it.get("stars", "0")
            if isinstance(stars_str, str):
                stars_str = stars_str.replace(",", "")
            try:
                score += int(stars_str)
            except ValueError:
                pass
            score += it.get("likes", 0) or 0
            it["_score"] = score
            candidates.append(it)
    candidates.sort(key=lambda x: x.get("_score", 0), reverse=True)
    return candidates[:n]


def generate_archive_page(dates: list[str]) -> str:
    parts = []
    a = parts.append
    a("<!DOCTYPE html><html lang='zh-CN'><head>")
    a("<meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>")
    a(f"<title>{esc(SITE_CONFIG['title'])} - \u5f52\u6863</title>")
    a(f"<style>{CSS}</style></head><body><div class='container'>")
    a(f"<header><h1><span>\u5f52\u6863</span></h1>")
    a(f'<div class="date-bar"><a href="./" style="color:var(--accent)">\u2190 \u8fd4\u56de\u4eca\u65e5</a></div></header>')

    for d in dates:
        data = load_by_date(d)
        total = sum(len(v) for v in data.values())
        if total == 0:
            continue
        a(f'<a href="archive/{d}.html" style="display:block;padding:14px 18px;background:var(--surface);border:1px solid var(--border);border-radius:var(--card-radius);margin-bottom:8px;text-decoration:none;color:inherit;transition:border-color .2s" onmouseover="this.style.borderColor=\'var(--accent)\'" onmouseout="this.style.borderColor=\'\'">')
        a(f'<div style="font-size:15px;font-weight:600">{d}</div>')
        a(f'<div style="font-size:13px;color:var(--text2);margin-top:2px">{total} \u6761\u5185\u5bb9</div>')
        a("</a>")

    a("</div></body></html>")
    return "\n".join(parts)


def generate_archive_detail(date: str, all_dates: list[str]) -> str:
    data = load_by_date(date)
    total = sum(len(v) for v in data.values())
    if total == 0:
        return ""

    has_prev = False
    has_next = False
    prev_date = ""
    next_date = ""
    for i, d in enumerate(all_dates):
        if d == date:
            if i > 0:
                next_date = all_dates[i-1]
                has_next = True
            if i < len(all_dates)-1:
                prev_date = all_dates[i+1]
                has_prev = True
            break

    parts = []
    a = parts.append
    a("<!DOCTYPE html><html lang='zh-CN'><head>")
    a("<meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>")
    a(f"<title>{esc(SITE_CONFIG['title'])} - {date}</title>")
    a(f"<style>{CSS}</style></head><body><div class='container'>")
    a(f"<header><h1><span>{date}</span></h1>")
    a(f'<div class="date-bar"><a href="../" style="color:var(--accent)">\u2190 \u5f52\u6863</a> | <a href="../index.html" style="color:var(--accent)">\u4eca\u65e5</a></div></header>')

    # Prev/next navigation
    nav = '<div class="archive-nav">'
    if has_prev:
        nav += f'<a href="{prev_date}.html">\u2190 {prev_date}</a>'
    if has_next:
        nav += f'<a href="{next_date}.html">{next_date} \u2192</a>'
    nav += "</div>"
    a(nav)

    featured = pick_featured(data)
    if featured:
        a(f'<section class="section"><div class="section-header"><h2>\U0001f525 \u7cbe\u9009</h2><span class="count">{len(featured)}</span></div>')
        for it in featured:
            a(render_card(it, featured=True))
        a("</section>")

    sections = [
        ("arxiv", "\U0001f4d6", "\u7814\u7a76\u8bba\u6587"),
        ("hf_papers", "\U0001f4c4", "HF \u8bba\u6587"),
        ("hf_models", "\U0001f916", "\u65b0\u6a21\u578b"),
        ("github_trending", "\u2b50", "\u5f00\u6e90\u9879\u76ee"),
        ("rss_news", "\U0001f4f0", "\u884c\u4e1a\u65b0\u95fb"),
    ]
    for key, icon, label in sections:
        items = data.get(key, [])
        if items:
            a(f'<section class="section"><div class="section-header"><h2>{icon} {label}</h2><span class="count">{len(items)}</span></div>')
            for it in items[:12]:
                a(render_card(it))
            a("</section>")

    a(nav)
    a("</div></body></html>")
    return "\n".join(parts)


def generate_site():
    data = load_all()
    now = datetime.utcnow()
    dates = list_dates()
    if not dates:
        dates = [now.strftime("%Y-%m-%d")]

    today = dates[0] if dates else now.strftime("%Y-%m-%d")
    featured = pick_featured(data)
    total = sum(len(v) for v in data.values())

    # Previous day link
    prev_date = dates[1] if len(dates) > 1 else ""

    date_str = now.strftime("%Y-%m-%d")

    parts = []
    a = parts.append
    a("<!DOCTYPE html><html lang='zh-CN'><head>")
    a("<meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>")
    a(f"<title>{esc(SITE_CONFIG['title'])} \u00b7 {date_str}</title>")
    a(f"<meta name='description' content='AI \u8d44\u8baf\u6c47\u603b - {date_str}'>")
    a(f"<style>{CSS}</style></head><body><div class='container'>")
    a(f"<header><h1><span>{esc(SITE_CONFIG['title'])}</span></h1>")
    a(f'<div class="date-bar"><span>\U0001f4c5 {date_str}</span><span>\U0001f4ca {total} \u6761</span>'
      f'<a href="archive.html" style="color:var(--accent);text-decoration:none">\u5f52\u6863</a></div></header>')

    # Summary
    sources_str = " \u00b7 ".join(f"{k} {len(v)}" for k, v in data.items() if v)
    a(f'<div class="summary">\U0001f916 <strong>AI News Hub</strong> \u6bcf\u65e5\u81ea\u52a8\u91c7\u96c6<br><span style="font-size:13px">{sources_str}</span></div>')

    # Archive navigation
    nav = '<div class="archive-nav">'
    if prev_date:
        nav += f'<a href="archive/{prev_date}.html">\u2190 {prev_date}</a>'
    nav += f'<a href="archive.html" class="active">\u5f52\u6863</a>'
    nav += "</div>"
    a(nav)

    # Featured
    if featured:
        a(f'<section class="section"><div class="section-header"><h2>\U0001f525 \u4eca\u65e5\u7cbe\u9009</h2><span class="count">{len(featured)}</span></div>')
        for it in featured:
            a(render_card(it, featured=True))
        a("</section>")

    # Research papers (with abstract toggle)
    papers = data.get("hf_papers", []) + data.get("arxiv", [])
    papers.sort(key=lambda x: x.get("published", ""), reverse=True)
    if papers:
        a(f'<section class="section"><div class="section-header"><h2>\U0001f4d6 \u6700\u65b0\u7814\u7a76\u8bba\u6587</h2><span class="count">{len(papers)}</span></div>')
        for it in papers[:15]:
            a(render_card(it))
        a("</section>")

    # Models
    models = data.get("hf_models", [])
    if models:
        a(f'<section class="section"><div class="section-header"><h2>\U0001f916 \u65b0\u53d1\u5e03\u6a21\u578b</h2><span class="count">{len(models)}</span></div>')
        for it in models[:12]:
            a(render_card(it))
        a("</section>")

    # OSS
    repos = data.get("github_trending", [])
    if repos:
        a(f'<section class="section"><div class="section-header"><h2>\u2b50 \u70ed\u95e8\u5f00\u6e90\u9879\u76ee</h2><span class="count">{len(repos)}</span></div>')
        for it in repos[:12]:
            a(render_card(it))
        a("</section>")

    # News
    news = data.get("rss_news", [])
    if news:
        a(f'<section class="section"><div class="section-header"><h2>\U0001f4f0 \u884c\u4e1a\u65b0\u95fb</h2><span class="count">{len(news)}</span></div>')
        for it in news[:10]:
            a(render_card(it))
        a("</section>")

    a(f'<footer>{esc(SITE_CONFIG["title"])} \u00b7 \u6bcf\u65e5 UTC 02:00 \u81ea\u52a8\u66f4\u65b0<br>Data: Hugging Face \u00b7 arXiv \u00b7 GitHub \u00b7 RSS</footer>')
    a("</div></body></html>")

    html = "\n".join(parts)

    # Generate archive pages
    os.makedirs(os.path.join(OUTPUT_DIR, "archive"), exist_ok=True)

    archive_html = generate_archive_page(dates)
    with open(os.path.join(OUTPUT_DIR, "archive.html"), "w", encoding="utf-8") as f:
        f.write(archive_html)

    for d in dates:
        detail = generate_archive_detail(d, dates)
        if detail:
            with open(os.path.join(OUTPUT_DIR, "archive", f"{d}.html"), "w", encoding="utf-8") as f:
                f.write(detail)

    # Main page
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n[site_generator] Site generated: {path} ({len(html)} bytes, {total} items)")
    print(f"[site_generator] Archive: {len(dates)} days")
    return path


if __name__ == "__main__":
    generate_site()
