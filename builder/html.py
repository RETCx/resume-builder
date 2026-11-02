"""HTML builder: Convert resume dict into a fully ASCII-safe HTML string"""

from __future__ import annotations

from pathlib import Path


def _t(text: str) -> str:
    """Encode text for HTML: Convert all non-ASCII characters to &#NNN; entities

    Prevents encoding issues on Windows Thai locale (cp874/TIS-620) where Playwright
    might misread file:// URL encodings — use set_content() + entities instead.
    """
    out = []
    for ch in str(text):
        if ch == "&":
            out.append("&amp;")
        elif ch == "<":
            out.append("&lt;")
        elif ch == ">":
            out.append("&gt;")
        elif ord(ch) > 127:
            out.append(f"&#{ord(ch)};")   # e.g. – → &#8211;  — → &#8212;
        else:
            out.append(ch)
    return "".join(out)


def build_html(resume: dict, n_projects: int = 4, n_certs: int = 4, max_bullets: int = 2) -> str:
    """Convert resume dict to HTML string with inline CSS"""

    skills = resume.get("skills", {})
    spoken = resume.get("spoken_languages", "")

    standard_labels = {
        "languages": "Languages",
        "frameworks": "Libraries / Frameworks",
        "tools": "Tools",
        "data": "Data &amp; Analysis",
    }

    skill_rows = [
        (standard_labels.get(k, k), items)
        for k, items in skills.items()
    ]
    skills_html = "\n".join(
        f'<div class="skill-row"><span class="sk-label">{lbl}:</span> {_t(", ".join(items))}</div>'
        for lbl, items in skill_rows if items
    )
    if spoken:
        skills_html += f'\n<div class="skill-row"><span class="sk-label">Spoken:</span> {_t(spoken)}</div>'

    projects_html = ""
    all_projects = resume.get("projects", [])
    # Sort by 'order' field if present, otherwise use the original JSON order
    if any("order" in p for p in all_projects):
        all_projects = sorted(all_projects, key=lambda p: p.get("order", 9999))
    for p in all_projects[:n_projects]:
        bullets = "".join(f"<li>{_t(b)}</li>" for b in p.get("bullets", [])[:max_bullets])
        tech = _t(", ".join(p.get("tech", [])))
        links_html = ""
        demo_url = p.get("demo") or p.get("demoUrl")
        github_url = p.get("github") or p.get("githubUrl")
        if demo_url:
            links_html += f' <a href="{demo_url}" class="project-link" target="_blank">[Demo &#8599;]</a>'
        if github_url:
            links_html += f' <a href="{github_url}" class="project-link" target="_blank">[Code &#8599;]</a>'
        projects_html += f"""
<div class="entry">
  <div class="row"><span class="entry-title">{_t(p["name"])}{links_html}</span><span class="date">{_t(p.get("year",""))}</span></div>
  <ul>{bullets}</ul>
  <div class="tech"><strong>Technologies:</strong> {tech}</div>
</div>"""

    exp_html = ""
    for e in resume.get("experience", []):
        bullets = "".join(f"<li>{_t(b)}</li>" for b in e.get("bullets", []))
        exp_html += f"""
<div class="entry">
  <div class="row"><span class="entry-title">{_t(e["role"])}</span><span class="date">{_t(e.get("period",""))}</span></div>
  <div class="subtitle">{_t(e["company"])}</div>
  <ul>{bullets}</ul>
</div>"""

    certs_html = "".join(
        f"<li>{_t(c)}</li>" for c in resume.get("certifications", [])[:n_certs]
    )

    name       = _t(resume.get("name", ""))
    email      = resume.get("email", "")
    phone      = _t(resume.get("phone", ""))
    location   = _t(resume.get("location", ""))
    github     = resume.get("github", "")
    portfolio  = resume.get("portfolio", "")
    github_s   = _t(github.replace("https://", "").replace("http://", ""))
    portfolio_s= _t(portfolio.replace("https://", "").replace("http://", ""))
    summary    = _t(resume.get("summary", ""))
    education  = _t(resume.get("education", ""))

    _HERE = Path(__file__).parent
    template_path = _HERE / "template.html"
    template = template_path.read_text(encoding="utf-8")

    replacements = {
        "{name}": name,
        "{email}": email,
        "{phone}": phone,
        "{location}": location,
        "{github}": github,
        "{portfolio}": portfolio,
        "{github_s}": github_s,
        "{portfolio_s}": portfolio_s,
        "{summary}": summary,
        "{education}": education,
        "{skills_html}": skills_html,
        "{projects_html}": projects_html,
        "{exp_html}": exp_html,
        "{certs_html}": certs_html,
    }

    for k, v in replacements.items():
        template = template.replace(k, str(v))

    return template
