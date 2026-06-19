import os
from datetime import datetime, timedelta, timezone
from collections import defaultdict
from src.config import OUTPUT_DIR, DATA_DIR, SITE_CONFIG
from src.aggregator import load_by_date, list_dates
from src.topics import classify_item, get_topic_info, TOPIC_RULES


def esc(s):
    if s is None: return ""
    return str(s).replace("&","&amp;").replace("<","&lt;").replace(">","&gt;").replace('"',"&quot;")

def fmt(s):
    try:
        d = datetime.fromisoformat(s.replace("Z","+00:00"))
        return d.strftime("%m-%d")
    except: return s[:10] if s else ""


CSS = """\
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
:root{--bg:#f5f5f7;--surface:#fff;--text:#1d1d1f;--text2:#86868b;--border:#d2d2d7;--accent:#0066cc;--accent2:#5856d6;--radius:16px;--card-radius:12px}
@media(prefers-color-scheme:dark){:root{--bg:#1c1c1e;--surface:#2c2c2e;--text:#f5f5f7;--text2:#98989d;--border:#38383a;--accent:#0a84ff;--accent2:#5e5ce6}}
body{font-family:-apple-system,BlinkMacSystemFont,"SF Pro","Helvetica Neue","Noto Sans SC",sans-serif;background:var(--bg);color:var(--text);line-height:1.7;-webkit-font-smoothing:antialiased}
.container{max-width:960px;margin:0 auto;padding:0 20px}
header{padding:40px 0;text-align:center;border-bottom:1px solid var(--border);margin-bottom:32px}
header h1{font-size:30px;font-weight:700;letter-spacing:-.5px}
header h1 span{background:linear-gradient(135deg,#0066cc,#5856d6);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.subtitle{color:var(--text2);font-size:15px;margin-top:4px}
.meta-line{display:flex;justify-content:center;gap:20px;color:var(--text2);font-size:13px;margin-top:8px;flex-wrap:wrap}
.meta-line a{color:var(--accent);text-decoration:none}
.meta-line a:hover{text-decoration:underline}
.hero{background:var(--surface);border:1px solid var(--border);border-radius:var(--radius);padding:28px 32px;margin-bottom:32px}
.hero h2{font-size:22px;font-weight:700;margin-bottom:10px}
.hero p{font-size:15px;color:var(--text2);line-height:1.7}
.hero .stats{display:flex;gap:24px;margin-top:16px;flex-wrap:wrap}
.hero .stat{text-align:center}
.hero .stat-num{font-size:28px;font-weight:700;color:var(--accent)}
.hero .stat-label{font-size:13px;color:var(--text2);margin-top:2px}
.section{margin-bottom:36px}
.section-header{display:flex;align-items:baseline;gap:8px;margin-bottom:14px;padding-bottom:10px;border-bottom:2px solid var(--accent)}
.section-header h2{font-size:20px;font-weight:700}
.section-header .count{margin-left:auto;font-size:13px;color:var(--text2)}
.topic-trend{font-size:12px;color:var(--text2);margin-left:8px}
.topic-trend .up{color:#22c55e}
.topic-trend .down{color:#ef4444}
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--card-radius);padding:16px 20px;margin-bottom:10px;transition:all .15s}
.card:hover{border-color:var(--accent)}
.card-main{text-decoration:none;color:inherit;display:block}
.card-title{font-size:16px;font-weight:600;line-height:1.4;margin-bottom:4px}
.card-desc{font-size:13px;color:var(--text2);line-height:1.5;margin-bottom:6px}
.card-meta{display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:12px;color:var(--text2);margin-top:4px}
.card-meta .sep{opacity:.4;margin:0 2px}
.badge{display:inline-block;font-size:10px;font-weight:600;padding:2px 8px;border-radius:12px;margin-bottom:4px;letter-spacing:.2px}
.badge-paper{background:#e8f0fe;color:#1967d2}
.badge-model{background:#fef7e0;color:#e37400}
.badge-oss{background:#e6f4ea;color:#137333}
.badge-news{background:#f3e8fd;color:#7c3aed}
@media(prefers-color-scheme:dark){.badge-paper{background:#1a2a4a;color:#8ab4f8}.badge-model{background:#3a2a0a;color:#fdd663}.badge-oss{background:#1a3a2a;color:#81c995}.badge-news{background:#2a1a4a;color:#c58af9}}
.source-tag{font-size:11px;color:var(--text2);background:var(--border);padding:1px 6px;border-radius:4px;margin-right:4px}
.topic-chip{display:inline-block;font-size:12px;padding:4px 12px;border-radius:20px;background:var(--surface);border:1px solid var(--border);margin:0 4px 6px 0;transition:all .15s;text-decoration:none;color:var(--text)}
.topic-chip:hover{background:var(--accent);color:#fff;border-color:var(--accent)}
.abstract{font-size:13px;color:var(--text2);line-height:1.6;margin-top:8px;padding-top:8px;border-top:1px solid var(--border);display:none}
.abstract.show{display:block}
.abs-toggle{font-size:12px;color:var(--accent);cursor:pointer;background:none;border:none;padding:2px 0;margin-top:2px;font-weight:500}
.abs-toggle:hover{text-decoration:underline}
.timeline{position:relative;padding-left:20px;margin:12px 0}
.timeline::before{content:'';position:absolute;left:6px;top:0;bottom:0;width:2px;background:var(--border)}
.timeline-item{position:relative;margin-bottom:6px;font-size:13px;color:var(--text2)}
.timeline-item::before{content:'';position:absolute;left:-17px;top:6px;width:8px;height:8px;border-radius:50%;background:var(--accent)}
.timeline-date{font-weight:600;color:var(--text);margin-right:6px}
footer{text-align:center;padding:40px 0;font-size:13px;color:var(--text2);border-top:1px solid var(--border);margin-top:16px;line-height:2}
@media(max-width:640px){header{padding:28px 0}header h1{font-size:26px}.hero{padding:20px 22px}.hero h2{font-size:18px}.hero .stat-num{font-size:22px}.container{padding:0 14px}}
"""


EXPAND = "\u5c55\u5f00"
COLLAPSE = "\u6536\u8d77"
EXPAND_TEXT = EXPAND + "\u6458\u8981"
COLLAPSE_TEXT = COLLAPSE + "\u6458\u8981"

def render_abstract(item: dict) -> str:
    abstract = item.get("abstract", "")
    title = item.get("title", "")
    if not abstract or len(abstract) < 100:
        return ""
    abs_id = f"a{abs(hash(title))%99999:05d}"
    return (
        f'<div class="abstract" id="{abs_id}">{esc(abstract)}</div>'
        f'<button class="abs-toggle" onclick="'
        f"document.getElementById('{abs_id}').classList.toggle('show');"
        f"this.textContent=this.textContent.includes('{EXPAND}')?'{COLLAPSE_TEXT}':'{EXPAND_TEXT}'"
        f'">{EXPAND_TEXT}</button>'
    )


def render_card(item: dict) -> str:
    title = esc(item.get("title") or item.get("name",""))
    url = item.get("url","#")
    desc = esc((item.get("description") or item.get("summary",""))[:280])
    source = item.get("source","")
    itype = item.get("type","paper")

    cmap = {"paper":"badge-paper","model":"badge-model","oss":"badge-oss","news":"badge-news"}
    tag = f'<span class="badge {cmap.get(itype,"badge-paper")}">{esc(source or "Paper")}</span>'

    meta = []
    pub = item.get("published","")
    if pub: meta.append(fmt(pub))
    authors = item.get("authors",[])
    if authors:
        a = [esc(x) for x in authors[:2]]
        if len(authors)>2: a.append("...")
        meta.append(" · ".join(a))
    stars = item.get("stars","") or item.get("likes",0)
    if stars: meta.append(f"\u2605 {stars}")
    if item.get("pipeline_tag"): meta.append(esc(item["pipeline_tag"]))
    if item.get("language"): meta.append(esc(item["language"]))

    ext = ""
    if itype == "paper":
        cats = "".join(f'<span class="source-tag">{esc(c)}</span>' for c in item.get("categories",[])[:4])
        pdf = item.get("pdf_url","")
        pl = f'<a href="{esc(pdf)}" target="_blank" style="color:var(--accent);font-size:12px;margin-left:4px">PDF</a>' if pdf else ""
        ext = f'<div style="margin-top:4px">{cats}{pl}</div>'
        ext += render_abstract(item)

    topics = item.get("topics",item.get("tags",[]))
    t_html = ""
    if topics:
        t_html = "".join(f'<span class="source-tag">{esc(str(t))}</span>' for t in topics[:4])

    sep = "<span class=sep>\u00b7</span>"
    return (
        f'<div class="card">'
        f'{tag}{t_html}'
        f'<a href="{url}" target="_blank" rel="noopener" class="card-main">'
        f'<h3 class="card-title">{title}</h3>'
        f'<p class="card-desc">{desc}</p></a>'
        f'{ext}'
        f'<div class="card-meta">{sep.join(meta)}</div>'
        f"</div>"
    )


def generate_archive(all_dates: list[str]):
    parts = []
    a = parts.append
    a("<!DOCTYPE html><html lang='zh-CN'><head>")
    a("<meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>")
    a(f"<title>{esc(SITE_CONFIG['title'])} - \u5386\u53f2\u5f52\u6863</title>")
    a(f"<style>{CSS}</style></head><body><div class='container'>")
    a("<header>")
    a(f"<h1>\U0001f4c2 \u5386\u53f2\u5f52\u6863</h1>")
    a(f'<p class="subtitle"><a href="index.html" style="color:var(--accent)">\u2190 \u8fd4\u56de\u672c\u5468\u62a5\u544a</a></p>')
    a("</header>")

    # Group by week
    weeks = defaultdict(list)
    for d in all_dates:
        dt = datetime.strptime(d, "%Y-%m-%d")
        week_key = dt.strftime("%Y-W%V")
        weeks[week_key].append(d)

    for wk in sorted(weeks.keys(), reverse=True):
        dates = weeks[wk]
        total = 0
        for d in dates:
            data = load_by_date(d)
            total += sum(len(v) for v in data.values())
        start, end = dates[-1], dates[0]
        a(f'<div class="card" style="margin-bottom:8px;cursor:pointer;padding:14px 20px" onclick="location.href=\'index.html\'">')
        a(f'<div class="card-title">{start} ~ {end} (\u7b2c{wk.split("W")[1]}\u5468)</div>')
        a(f'<div class="card-desc">\U0001f4ca {total} \u6761\u5185\u5bb9 \u00b7 {len(dates)} \u5929\u6570\u636e</div>')
        a("</div>")

    a(f'<footer>{esc(SITE_CONFIG["title"])} \u00b7 \u6bcf\u65e5\u81ea\u52a8\u91c7\u96c6</footer>')
    a("</div></body></html>")

    path = os.path.join(OUTPUT_DIR, "archive.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(parts))
    print(f"[site_generator] Archive generated: {path}")


def generate_site():
    all_dates = list_dates()
    now = datetime.utcnow()
    today_s = now.strftime("%Y-%m-%d")

    # Use the most recent available date as reference
    if not all_dates:
        all_dates = [today_s]
        ref_date = today_s
    else:
        ref_date = all_dates[0]

    week_start = (datetime.strptime(ref_date, "%Y-%m-%d") - timedelta(days=6)).strftime("%Y-%m-%d")
    week_end = ref_date
    week_dates = [d for d in all_dates if d >= week_start and d <= week_end]

    # Collect all items and classify by topic
    topic_items = defaultdict(list)
    topic_weekly_counts = defaultdict(int)
    all_items = []
    total_unique = 0

    seen_titles = set()
    for d in week_dates:
        data = load_by_date(d)
        for sname, items in data.items():
            for item in items:
                title = item.get("title","") or item.get("name","")
                if title in seen_titles:
                    continue
                seen_titles.add(title)
                total_unique += 1
                topics = classify_item(item)
                for t in topics:
                    topic_items[t].append(item)
                    topic_weekly_counts[t] += 1
                all_items.append((d, item))

    # Topic summary for analysis
    topic_summary = []
    for topic in TOPIC_RULES:
        tid = topic["id"]
        count = topic_weekly_counts.get(tid, 0)
        topic_summary.append({**topic, "count": count})

    topic_summary.sort(key=lambda x: x["count"], reverse=True)
    top_topics = [t for t in topic_summary if t["count"] > 0][:8]

    # Generate HTML
    parts = []
    a = parts.append
    a("<!DOCTYPE html><html lang='zh-CN'><head>")
    a("<meta charset='UTF-8'><meta name='viewport' content='width=device-width,initial-scale=1'>")
    a(f"<title>{esc(SITE_CONFIG['title'])} \u5468\u62a5 \u00b7 {week_start} ~ {week_end}</title>")
    a(f"<style>{CSS}</style></head><body><div class='container'>")

    a(f"<header>")
    a(f"<h1><span>{esc(SITE_CONFIG['title'])}</span></h1>")
    a(f'<p class="subtitle">\u6bcf\u5468AI\u8d44\u8baf\u6df1\u5ea6\u5206\u6790 \u00b7 \u4e3b\u9898\u8ffd\u8e2a</p>')
    a(f'<div class="meta-line">'
      f'<span>\U0001f4c5 {week_start} ~ {week_end}</span>'
      f'<span>\U0001f4ca {total_unique} \u6761\u72ec\u7acb\u5185\u5bb9</span>'
      f'<span>\U0001f4c1 {len(week_dates)} \u5929\u6570\u636e</span>'
      f'<a href="archive.html">\u5386\u53f2\u5468\u62a5</a>'
      f"</div></header>")

    # Hero section
    a(f'<div class="hero">')
    a(f"<h2>\U0001f9e0 \u672c\u5468 AI \u8981\u95fb</h2>")
    a(f"<p>{week_start} ~ {week_end} \u8fd9\u5468\uff0cAI \u9886\u57df\u5171\u6709 {total_unique} \u6761\u503c\u5f97\u5173\u6ce8\u7684\u52a8\u6001\u3002\u4ece\u7814\u7a76\u8bba\u6587\u5230\u5f00\u6e90\u9879\u76ee\uff0c\u4ece\u65b0\u6a21\u578b\u5230\u884c\u4e1a\u65b0\u95fb\uff0c\u4ee5\u4e0b\u662f\u672c\u5468\u7684\u91cd\u70b9\u6c47\u603b\u3002</p>")
    a('<div class="stats">')
    for t in top_topics[:5]:
        a(f'<div class="stat"><div class="stat-num">{t["count"]}</div><div class="stat-label">{t["emoji"]} {t["name"]}</div></div>')
    a("</div></div>")

    # Featured items (this week's highlights)
    scored = []
    for d, item in all_items:
        score = 0
        s = str(item.get("stars","0")).replace(",","")
        try: score += int(s)*2
        except: pass
        score += (item.get("likes",0) or 0)*2
        score += (item.get("downloads",0) or 0)//1000
        scored.append((score, d, item))
    scored.sort(key=lambda x: x[0], reverse=True)

    a(f'<section class="section"><div class="section-header"><h2>\U0001f525 \u672c\u5468\u91cd\u70b9</h2><span class="count">{len(scored[:8])} \u6761</span></div>')
    for score, d, item in scored[:8]:
        a(render_card(item))
    a("</section>")

    # Topic deep-dives
    for t in top_topics:
        items = topic_items[t["id"]]
        items.sort(key=lambda x: x.get("stars",0) if isinstance(x.get("stars"),(int,float)) else 0, reverse=True)
        a(f'<section class="section">')
        a(f'<div class="section-header"><h2>{t["emoji"]} {t["name"]}</h2><span class="count">{len(items)} \u6761</span></div>')
        for item in items[:10]:
            a(render_card(item))
        a("</section>")

    # Weekly timeline
    a(f'<section class="section"><div class="section-header"><h2>\U0001f4c5 \u5468\u5ea6\u65f6\u95f4\u7ebf</h2><span class="count">{len(week_dates)} \u5929</span></div>')
    a('<div class="timeline">')
    for d in reversed(week_dates):
        data = load_by_date(d)
        day_total = sum(len(v) for v in data.values())
        a(f'<div class="timeline-item"><span class="timeline-date">{d}</span>{day_total} \u6761\u5185\u5bb9</div>')
    a("</div></section>")

    # Footer
    a(f'<footer>')
    a(f'{esc(SITE_CONFIG["title"])} \u00b7 \u6bcf\u65e5\u81ea\u52a8\u91c7\u96c6 \u00b7 \u6bcf\u5468\u6df1\u5ea6\u5206\u6790<br>')
    a(f'Data: Hugging Face \u00b7 arXiv \u00b7 GitHub \u00b7 RSS</footer>')
    a("</div></body></html>")

    html = "\n".join(parts)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, "index.html")
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)

    print(f"\n[site_generator] Weekly report generated: {path}")
    print(f"[site_generator]   Period: {week_start} ~ {week_end}")
    print(f"[site_generator]   Items: {total_unique}")
    print(f"[site_generator]   Topics: {len(top_topics)} active")

    generate_archive(all_dates)

    return path


if __name__ == "__main__":
    generate_site()
