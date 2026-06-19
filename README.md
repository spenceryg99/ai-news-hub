# AI News Hub

> AI 变化太快？这里帮你抓住重点，理清脉络。

## 这是什么

这是一个 **AI 资讯深度分析工具**，和你见过的普通聚合器不一样。

### 普通聚合器 vs AI News Hub

| 普通聚合器 | AI News Hub |
|---|---|
| 每天抛给你一堆链接 | **每周深度报告**，精选本周最重要的动态 |
| 按来源分类（arXiv / GitHub / 新闻） | **按主题分类**（LLM / Agent / 多模态 / RAG...），看清每个方向的演进 |
| 标题 + 链接，看完就忘 | **完整摘要 + PDF 链接**，点开就能读论文 |
| 每天的内容互相独立 | **历史归档 + 主题追踪**，同一个主题持续跟进 |
| 需要自己判断"这个重要吗" | **热度排序 + 精选置顶**，先看最重要的 |

### 核心功能

**\uD83D\uDCCA 主题追踪** — 自动归类每篇论文、每个项目到 AI 子主题：
- 大语言模型、AI Agent、多模态、RAG、推理部署、代码开发...
- 每周自动统计各主题热度变化

**\uD83D\uDCC4 论文深度阅读** — 每篇论文展示：
- 完整摘要（可展开/收起）
- 作者列表
- PDF 下载链接
- arXiv 分类标签

**\uD83D\uDCC6 周度报告** — 每周自动生成报告：
- 本期重点（本周热度最高的 8 条内容）
- 主题深度分析（每个主题一个板块）
- 周度时间线（每天采集了哪些内容）

**\uD83D\uDCC1 历史追溯** — 数据跨周持久化：
- 所有历史数据通过 GitHub Actions Cache 保留
- 可以对比不同周的主题热度变化

## 技术架构

```
数据源 (每天 UTC 02:00 采集)
  ├── Hugging Face Daily Papers  →  src/collector_hf_papers.py
  ├── arXiv (AI/LG/CL/CV)        →  src/collector_arxiv.py
  ├── GitHub Trending (AI repos) →  src/collector_github.py
  ├── Hugging Face Models         →  src/collector_hf_models.py
  └── RSS Feeds                   →  src/collector_rss.py
         │
         ▼
  src/aggregator.py  — 统一存储到 data/YYYY-MM-DD/
         │
         ▼
  src/topics.py  — 自动分类（LLM / Agent / Vision / RAG...）
         │
         ▼
  src/site_generator.py  — 生成每周深度分析 HTML
         │
         ▼
  GitHub Pages (免费托管)
```

## 快速开始

```bash
pip install -r requirements.txt
python run.py
# 或只生成报告（使用缓存数据）：
python -c "from src.site_generator import generate_site; generate_site()"
open output/index.html
```

## 自定义

- **`src/config.py`** — 修改 RSS 源、开关采集器
- **`src/topics.py`** — 添加/修改主题分类规则
- 环境变量 `HF_ENDPOINT` — 设置 Hugging Face 镜像（国内用户设为 `https://hf-mirror.com`）

## License

MIT
