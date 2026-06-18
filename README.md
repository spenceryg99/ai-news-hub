# AI News Hub

> 每天醒来，AI 世界又变了。这个项目帮你抓住重点。

## 这是什么

AI 的发展速度快到令人窒息。每天都有新的论文、模型、开源项目和行业新闻。你不可能刷遍 Hugging Face、arXiv、GitHub、TechCrunch 和 Reddit。**AI News Hub** 就是为解决这个问题而生的——它像一个自动化的研究助手，每天从多个源头采集高质量的 AI 资讯，整合成一份结构清晰、易于阅读的每日摘要。

### 它做了什么

通过 GitHub Actions，每天 UTC 02:00（北京时间 10:00），系统自动：

1. **采集** — 从 Hugging Face Daily Papers、arXiv、GitHub Trending、Hugging Face Models、TechCrunch AI、Reddit 等多个源获取最新内容
2. **整理** — 自动分类为「研究论文」「新模型」「热门开源」「行业新闻」，并计算热度排序
3. **归档** — 每天的内容独立保存，支持回溯历史
4. **展示** — 生成响应式静态 HTML 站点，通过 GitHub Pages 免费托管

### 为什么值得用

| 问题 | 我们的方案 |
|---|---|
| 信息来源太多，刷不过来 | 多源自动聚合，一个页面看全 |
| 论文只有标题链接，需要点开才知道好不好 | 展示完整摘要、作者、PDF链接，还有「展开摘要」按钮 |
| 昨天看了什么？前几天有什么？ | 自动归档，支持日期导航和回溯 |
| 好的开源项目容易被淹没 | 按热度排序，今日精选置顶 |
| 部署维护麻烦 | 全自动 GitHub Actions + Pages，零成本零维护 |

## 技术架构

```
                    ┌─────────────────────────┐
                    │   数据源 (Sources)        │
                    │ HF Papers · arXiv · GH    │
                    │ HF Models · RSS           │
                    └──────────┬───────────────┘
                               │ Python 采集器
                    ┌──────────▼───────────────┐
                    │   存储层 (Data Layer)     │
                    │ data/YYYY-MM-DD/source.json│
                    │ data/manifest.json        │
                    └──────────┬───────────────┘
                               │ GitHub Actions Cache
                    ┌──────────▼───────────────┐
                    │   生成层 (Generator)      │
                    │ aggregator → site_generator│
                    └──────────┬───────────────┘
                               │ 输出 static HTML
                    ┌──────────▼───────────────┐
                    │   展示层 (Presentation)   │
                    │ GitHub Pages (free)       │
                    │ index.html + archive/     │
                    └─────────────────────────┘
```

### 项目结构

```
├── .github/workflows/daily.yml   GitHub Actions 工作流（每天自动运行）
├── src/                           Python 源码
│   ├── collector_base.py          采集器基类
│   ├── collector_arxiv.py         arXiv 论文采集（含完整摘要、PDF链接）
│   ├── collector_hf_papers.py     Hugging Face 每日论文
│   ├── collector_hf_models.py     Hugging Face 新模型
│   ├── collector_github.py        GitHub Trending AI 项目
│   ├── collector_rss.py           RSS 新闻采集
│   ├── aggregator.py              聚合器（运行所有采集器 -> 生成 JSON）
│   ├── site_generator.py          站点生成器（JSON -> 静态 HTML）
│   └── config.py                  配置文件
├── data/                          采集数据缓存（GitHub Actions Cache 持久化）
└── output/                        生成的静态站点
```

### 使用的技术

- **Python 3.11** — 主要开发语言
- **requests + BeautifulSoup** — 网页和 API 数据抓取
- **arxiv.py** — arXiv API 的 Python 封装
- **feedparser** — RSS 解析
- **GitHub Actions** — 自动化调度和部署
- **GitHub Pages** — 免费静态站点托管
- **GitHub Actions Cache** — 历史数据跨运行持久化

## 部署

这个项目可以 fork 后直接使用。部署步骤：

1. Fork 本仓库
2. 进入仓库 Settings → Pages → Source 选择 **GitHub Actions**
3. 首次工作流会自动触发，或者在 Actions 标签页手动触发
4. 站点会在几分钟内部署到 `https://<你的用户名>.github.io/ai-news-hub`

### 自定义配置

编辑 `src/config.py`：

- `RSS_FEEDS` — 添加/修改新闻源
- `COLLECTORS` — 启用/禁用特定采集器
- `HF_ENDPOINT` — 设置 Hugging Face 镜像（国内用户可设为 `https://hf-mirror.com`）

## 数据源

| 来源 | 类型 | 内容 |
|---|---|---|
| Hugging Face Daily Papers | 论文 | 社区评分最高的 AI 论文 |
| arXiv (cs.AI/LG/CL/CV) | 论文 | 最新预印本，含完整摘要和 PDF |
| Hugging Face Models | 模型 | 新发布的开源模型 |
| GitHub Trending | 开源项目 | 今日热门的 AI 相关仓库 |
| TechCrunch AI | 行业新闻 | AI 产业动态 |
| Reddit r/MachineLearning | 讨论 | 社区讨论和分享 |

## 本地开发

```bash
pip install -r requirements.txt
python run.py
# 或者只生成站点（使用缓存数据）：
python -c "from src.site_generator import generate_site; generate_site()"
open output/index.html
```

## 许可证

MIT
