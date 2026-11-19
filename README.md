# Yilong Fan · Academic Homepage

基于 [Google Scholar](https://scholar.google.com/citations?user=1bKyJZQAAAAJ&hl=zh-CN) 和 [GitHub 公开资料](https://github.com/fyl0715) 制作的学术主页。采用静态 HTML、CSS 和 JavaScript，提供英文与中文界面、论文检索及 BibTeX。

本仓库包含页面源码和生成的静态网页。目标仓库为 `fyl0715/fyl0715.github.io`，发布成功后的默认地址为 `https://fyl0715.github.io/`。

## GitHub Pages

站点通过 `main` 分支根目录发布。修改内容后运行 `python3 scripts/build.py`，将源文件与生成的 `index.html` 和 `publications.bib` 一并提交到 `main`。

## 本地查看和更新

可直接打开根目录的 `index.html` 查看已生成的页面。修改源文件后，在本目录运行：

```sh
python3 scripts/build.py
```

构建会更新根目录 `index.html`，并生成用于发布的 `dist/`。如需通过本地 HTTP 访问：

```sh
python3 -m http.server 8000 --directory dist
```

随后访问 `http://localhost:8000/`，按 `Ctrl+C` 停止服务器。上述命令在本地预览，不会发布到互联网。

## 内容维护

| 文件 | 用途 |
| --- | --- |
| `data/profile.json` | 姓名、机构、个人简介、研究方向、教育经历、公开链接及 Scholar 指标 |
| `data/sources.json` | 逐篇论文的核验来源与元数据差异说明 |
| `data/publications.json` | 论文标题、作者、年份、发表状态、期刊或会议、论文链接和引文信息 |
| `assets/papers/` | 论文配图：原图裁切或明确标注的概念示意图 |
| `data/figure-sources.json` | 每张配图的来源、图号与处理方式 |
| `assets/portrait.jpg` | 从本人公开 Scholar 主页获取的头像 |
| `template.html` | 网页结构 |
| `assets/site.css` | 排版、颜色与手机布局 |
| `assets/site.js` | 语言切换和论文检索等交互 |
| `scripts/build.py` | 使用 Python 标准库生成可直接访问的静态页面 |

更新内容时保持 JSON 原有字段结构。新增论文可复制现有同类论文记录，替换唯一的 `id`、`title`、完整 `authors` 名单、`year`、发表信息及真实链接。`id` 只使用小写字母、数字和连字符；`kind` 取 `conference`、`journal` 或 `preprint`。`authors` 中本人姓名应与 `profile.json` 的 `name` 完全一致，页面据此加粗本人姓名。

BibTeX 和可下载的 `publications.bib` 会由构建脚本自动生成，无需手写 BibTeX 字段。请维护相应的 `venue`、`doi`、`pages`、`volume`、`article_number`、`arxiv` 等原始书目信息。论文按年份倒序展示，同一年保持 JSON 中的排列顺序。预印本正式发表后，应同时更新 `kind`、期刊或会议名称与链接。仅加入已验证的代码或 PDF 地址；没有链接时保留 `null`。

引用次数与 h-index 是获取时的快照，不会自动变化。更新 `metrics` 中的数字时，应同步修改 `updated` 日期（`YYYY-MM-DD`）。中英文介绍需要一起维护；英文论文题名和作者姓名保留原文。

个人介绍的首段保存在 `profile.json` 的 `about` 中，后续段落保存在 `aboutDetails` 数组中，每段均包含 `en` 和 `zh`。构建脚本会按顺序生成段落，页面语言切换会同步显示对应版本。

建议编辑数据和源模板后重新构建；直接改生成的 `index.html` 会在下一次构建时被覆盖。分支发布使用根目录生成的页面，无需提交 `dist/`。

## 资料来源和部署参考

- [本人 Google Scholar](https://scholar.google.com/citations?user=1bKyJZQAAAAJ&hl=zh-CN)
- [本人 GitHub](https://github.com/fyl0715)
- [GitHub：创建 Pages 站点](https://docs.github.com/en/pages/getting-started-with-github-pages/creating-a-github-pages-site)
- [GitHub：使用自定义 Pages 工作流](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages)

网站中的个人资料与论文信息应以本人和原始发表来源的最新记录为准。

## 论文配图

每篇论文的 `image` 字段配置 `path`、`kind`、`source`、`figure`、`alt`、`caption`、`width` 和 `height`。`kind` 为 `original` 时显示“论文原图”，为 `concept` 时显示“概念示意图”。`alt` 和 `caption` 均包含 `en`、`zh` 两种语言。

原图保留完整图中信息，并提供原文来源；概念示意图用于暂未取得原图的论文，不代表原论文实验结果。替换时将图保存到 `assets/papers/`、更新对应元数据与来源记录，然后运行构建脚本。图片支持点击放大、Esc 或关闭按钮退出，禁用 JavaScript 时仍可打开完整图片。
