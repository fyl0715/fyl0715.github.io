#!/usr/bin/env python3
"""Build a static, progressively enhanced academic homepage. No dependencies."""
from collections import Counter
from datetime import date
from html import escape
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parents[1]


def e(value):
    return escape(str(value), quote=True)


def bilingual(en, zh):
    return f'<span data-lang="en">{e(en)}</span><span data-lang="zh">{e(zh)}</span>'


def bibtex(p):
    entry_type = {"conference": "inproceedings", "journal": "article", "preprint": "misc"}[p["kind"]]
    fields = [("title", "{" + p["title"] + "}"), ("author", " and ".join(p["authors"])), ("year", str(p["year"]))]
    if p["kind"] in ("conference", "journal"):
        fields.append(("booktitle" if p["kind"] == "conference" else "journal", p["venue"]))
    if p.get("volume"):
        fields.append(("volume", p["volume"]))
    if p.get("pages") or p.get("article_number"):
        fields.append(("pages", p.get("pages", p.get("article_number")).replace("–", "--")))
    if p.get("arxiv") and p["kind"] == "preprint":
        fields.extend([("eprint", p["arxiv"]), ("archivePrefix", "arXiv")])
    elif p["kind"] == "preprint":
        fields.append(("howpublished", p["venue"]))
    if p.get("doi"):
        fields.append(("doi", p["doi"]))
    fields.append(("url", p["url"]))
    return f'@{entry_type}{{{p["id"]},\n' + ",\n".join(f"  {key} = {{{value}}}" for key, value in fields) + "\n}"


def figure_html(p):
    figure = p.get("image")
    if not figure:
        return ""
    caption = ""
    if figure.get("kind") == "adapted":
        caption = "<figcaption>" + bilingual("Redrawn method diagram", "重绘方法图") + "</figcaption>"
    return f'''<figure class="pub-figure">
      <a class="figure-link" href="{e(figure['path'])}" target="_blank" rel="noopener noreferrer" data-figure-title="{e(p['title'])}" data-caption-en="{e(figure['caption']['en'])}" data-caption-zh="{e(figure['caption']['zh'])}">
        <img src="{e(figure.get('thumbnail', figure['path']))}" width="{figure['width']}" height="{figure['height']}" loading="lazy" decoding="async" alt="{e(figure['alt']['en'])}" data-alt-en="{e(figure['alt']['en'])}" data-alt-zh="{e(figure['alt']['zh'])}">
      </a>
      {caption}
    </figure>'''


def paper_html(p, name):
    marker = set(p.get("equal_contribution_authors", []))
    authors = ", ".join((f"<strong>{e(a)}</strong>" if a == name else e(a)) + ("<sup>*</sup>" if a in marker else "") for a in p["authors"])
    kind = {"conference": ("Conference paper", "会议论文"), "journal": ("Journal article", "期刊论文"), "preprint": ("Preprint", "预印本")}[p["kind"]]
    venue = p.get("venue_short", p["venue"])
    if p.get("arxiv") and p["kind"] == "preprint":
        venue = "arXiv:" + p["arxiv"]
    if p["venue"] == "SSRN preprint":
        venue = "SSRN"
    links = [f'<a href="{e(p["url"])}" target="_blank" rel="noopener noreferrer">Paper</a>']
    for key, label in (("pdf", "PDF"), ("code", "Code"), ("project", bilingual("Project page", "项目主页"))):
        if p.get(key):
            links.append(f'<a href="{e(p[key])}" target="_blank" rel="noopener noreferrer">{label}</a>')
    links.append(f'<button class="bib-button" type="button" aria-expanded="false" aria-controls="bib-{e(p["id"])}" data-enhanced hidden>BibTeX</button>')
    note = '<p class="equal-note">' + bilingual("* Equal contribution", "* 共同第一作者") + '</p>' if marker else ""
    summary = p.get("summary")
    summary_html = f'<p class="pub-summary">{bilingual(**summary)}</p>' if summary else ""
    citation = e(bibtex(p))
    return f'''<article class="publication" id="{e(p['id'])}" data-year="{p['year']}">
      <div class="publication-row">
      {figure_html(p)}
      <div class="publication-copy">
      <h3><a href="{e(p['url'])}" target="_blank" rel="noopener noreferrer">{e(p['title'])}</a></h3>
      <p class="authors">{authors}</p>{note}
      <p class="pub-meta"><span class="venue-label">{e(venue)}{"" if str(p["year"]) in venue else ", " + str(p["year"])}</span><span class="meta-separator" aria-hidden="true">·</span>{bilingual(*kind)}</p>
      <div class="pub-links">{'<span class="pub-link-separator" aria-hidden="true">/</span>'.join(links)}</div>
      {summary_html}
      </div>
      </div>
      <div class="bib-panel" id="bib-{e(p['id'])}" hidden>
        <div class="bib-actions"><button class="copy-button" type="button">Copy BibTeX</button><span class="copy-status" role="status" aria-live="polite"></span></div>
        <pre tabindex="0">{citation}</pre>
      </div>
    </article>'''


def main():
    profile = json.loads((ROOT / "data/profile.json").read_text(encoding="utf-8"))
    publications = json.loads((ROOT / "data/publications.json").read_text(encoding="utf-8"))
    assert publications and len({p["id"] for p in publications}) == len(publications), "Duplicate or missing publication IDs"
    for p in publications:
        assert re.fullmatch(r"[a-z0-9-]+", p["id"]), "Unsafe publication ID"
        assert profile["name"] in p["authors"], "Profile author absent from publication"
        for key in ("url", "pdf", "code", "project"):
            assert not p.get(key) or p[key].startswith("https://"), "Use verified HTTPS links"
    # Preserve the source ordering within each year.
    publications.sort(key=lambda p: p["year"], reverse=True)
    years = sorted({p["year"] for p in publications}, reverse=True)
    blocks = []
    for year in years:
        papers = "\n".join(paper_html(p, profile["name"]) for p in publications if p["year"] == year)
        blocks.append(f'<div class="publication-year" aria-labelledby="year-{year}"><h3 class="year-heading" id="year-{year}">{year}</h3>{papers}</div>')
    research = "".join('<li><strong>' + bilingual(r["en"], r["zh"]) + '</strong><p>' + bilingual(r["descriptionEn"], r["descriptionZh"]) + '</p></li>' for r in profile["research"])
    about = profile["about"]
    advisor = profile.get("advisor")
    if advisor:
        url = e(advisor["url"])
        first_paragraph = (
            f'<span data-lang="en">{e(about["en"])} My advisor is <a href="{url}">{e(advisor["en"])}</a>.</span>'
            f'<span data-lang="zh">{e(about["zh"])}我的导师是<a href="{url}">{e(advisor["zh"])}</a>。</span>'
        )
    else:
        first_paragraph = bilingual(**about)
    about_paragraphs = [first_paragraph, *(bilingual(**p) for p in profile.get("aboutDetails", []))]
    about_blocks = "\n".join(f"<p>{paragraph}</p>" for paragraph in about_paragraphs)
    education = "".join(
        '<li><div class="education-heading"><h3>' + bilingual(**item["institution"])
        + '</h3><p class="education-period">' + bilingual(**item["period"])
        + '</p></div><p class="education-detail">' + bilingual(**item["degree"])
        + '<span class="education-separator" aria-hidden="true"> · </span>' + bilingual(**item["major"])
        + '</p></li>' for item in profile.get("education", [])
    )
    checked = date.fromisoformat(profile["updated"])
    counts = Counter(p["kind"] for p in publications)
    conference_papers = {}
    for paper in publications:
        if paper["kind"] == "conference":
            key = (paper.get("notification_month") or str(paper["year"]), paper.get("venue_short") or paper["venue"])
            conference_papers.setdefault(key, []).append(paper)
    news_items = []
    for (when, venue), papers in sorted(conference_papers.items(), key=lambda item: item[0][0], reverse=True):
        year, _, month = when.partition("-")
        date_label = f"{month}/{year}" if month else year
        count = len(papers)
        titles = ", ".join(
            f'<a href="#{e(paper["id"])}">{e(paper.get("short_title") or paper["title"])}</a>'
            for paper in papers
        )
        subject = "paper was" if count == 1 else "papers were"
        news_items.append(
            f'<li><time datetime="{e(when)}">{e(date_label)}</time> <div class="news-copy"><span aria-hidden="true">🎉</span> '
            f'<span data-lang="en">{count} {subject} accepted to <strong>{e(venue)}</strong> ({titles}).</span>'
            f'<span data-lang="zh"><strong>{e(venue)}</strong> 录用 {count} 篇论文（{titles}）。</span></div></li>'
        )
    intro_en = f'{counts["journal"]} journal article · {counts["conference"]} conference papers · {counts["preprint"]} preprints'
    intro_zh = f'{counts["journal"]} 篇期刊论文 · {counts["conference"]} 篇会议论文 · {counts["preprint"]} 篇预印本'
    schema = {"@context": "https://schema.org", "@type": "Person", "name": profile["name"], "url": profile["siteUrl"], "affiliation": {"@type": "CollegeOrUniversity", "name": profile["affiliation"]["en"]}, "sameAs": [profile["scholar"], profile["github"]], "knowsAbout": [r["en"] for r in profile["research"]]}
    fields = {
        "NAME": e(profile["name"]), "DESCRIPTION": e(profile["name"] + " at " + profile["affiliation"]["en"] + ". Research in deep learning, computer vision and large language models. Publications and research interests."),
        "EMAIL": e(profile["email"]),
        "AFFILIATION": bilingual(**profile["affiliation"]), "LOCATION": bilingual(**profile["location"]),
        "SCHOLAR": e(profile["scholar"]), "GITHUB": e(profile["github"]), "SITE_URL": e(profile["siteUrl"]),
        "CITATIONS": profile["metrics"]["citations"], "HINDEX": profile["metrics"]["hIndex"], "I10INDEX": profile["metrics"]["i10Index"],
        "DATE": profile["updated"], "DATE_EN": checked.strftime("%b %d, %Y"), "YEAR": checked.year,
        "NEWS": "\n".join(news_items), "ABOUT_BLOCKS": about_blocks, "RESEARCH": research, "EDUCATION": education,
        "PUBLICATION_INTRO": bilingual(intro_en, intro_zh), "PUBLICATIONS": "\n".join(blocks),
        "STRUCTURED_DATA": json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c"),
        "CSS": (ROOT / "assets/site.css").read_text(encoding="utf-8"), "JS": (ROOT / "assets/site.js").read_text(encoding="utf-8")
    }
    template = (ROOT / "template.html").read_text(encoding="utf-8")
    html = re.sub(r"@@([A-Z0-9_]+)@@", lambda m: str(fields[m[1]]), template)
    assert not re.search(r"@@[A-Z0-9_]+@@", html), "Unresolved template variable"
    (ROOT / "index.html").write_text(html, encoding="utf-8")
    bibliography = "\n\n".join(bibtex(p) for p in publications) + "\n"
    (ROOT / "publications.bib").write_text(bibliography, encoding="utf-8")
    (ROOT / ".nojekyll").touch()
    dist = ROOT / "dist"
    if dist.exists():
        shutil.rmtree(dist)
    (dist / "assets").mkdir(parents=True)
    for name in ("index.html", "publications.bib", ".nojekyll"):
        shutil.copy2(ROOT / name, dist / name)
    shutil.copy2(ROOT / "assets/portrait.jpg", dist / "assets/portrait.jpg")
    for paper in publications:
        figure = paper.get("image", {})
        for key in ("path", "thumbnail"):
            if key not in figure:
                continue
            asset = Path(figure[key])
            assert not asset.is_absolute() and ".." not in asset.parts and asset.parts[:2] == ("assets", "papers"), "Invalid figure path"
            (dist / asset.parent).mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / asset, dist / asset)
    print(f"Built {len(publications)} publications into {dist}")


if __name__ == "__main__":
    main()
