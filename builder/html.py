"""HTML builder: Convert resume dict into a fully ASCII-safe HTML string"""

from __future__ import annotations


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

    skill_rows = [
        ("Languages",           skills.get("languages", [])),
        ("Libraries / Frameworks", skills.get("frameworks", [])),
        ("Tools",               skills.get("tools", [])),
        ("Data &amp; Analysis", skills.get("data", [])),
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
        projects_html += f"""
<div class="entry">
  <div class="row"><span class="entry-title">{_t(p["name"])}</span><span class="date">{_t(p.get("year",""))}</span></div>
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

    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
* {{ margin:0; padding:0; box-sizing:border-box; }}
body {{
  font-family: 'Inter', 'Segoe UI', Arial, sans-serif;
  font-size: 11pt;
  color: #1a1a1a;
  line-height: 1.35;
  padding: 8mm 8mm;
}}

/* ── Header ─────────────────────────────── */
.header {{ text-align:center; margin-bottom:9px; padding-bottom:7px; border-bottom:2px solid #1a56a0; }}
.name {{ font-size:1.9em; font-weight:700; letter-spacing:.5px; color:#111; margin-bottom:4px; }}
.contact {{ font-size:0.99em; color:#555; }}
.contact a {{ color:#1a56a0; text-decoration:none; }}
.contact a:hover {{ text-decoration:underline; }}

/* ── Section ─────────────────────────────── */
.section {{ margin-bottom:7px; }}
.section-title {{
  font-size:1em; font-weight:700;
  text-transform:uppercase; letter-spacing:1.2px;
  color:#1a56a0;
  border-bottom:1px solid #c8d9ef;
  padding-bottom:2px; margin-bottom:4px;
}}

/* ── Skills ──────────────────────────────── */
.skill-row {{ font-size:0.97em; margin-bottom:1.5px; line-height:1.35; }}
.sk-label {{ font-weight:600; color:#1a56a0; }}

/* ── Entry ───────────────────────────────── */
.entry {{ margin-bottom:5px; }}
.row {{ display:flex; justify-content:space-between; align-items:baseline; }}
.entry-title {{ font-weight:700; font-size:1em; color:#111; }}
.date {{ font-size:0.88em; color:#1a56a0; font-weight:600; white-space:nowrap; margin-left:8px; }}
.subtitle {{ font-size:0.92em; color:#555; margin-bottom:1px; }}
ul {{ padding-left:14px; margin-top:2px; }}
li {{ margin-bottom:1px; line-height:1.35; }}
.tech {{ font-size:0.88em; color:#555; margin-top:2px; }}
.tech strong {{ color:#1a56a0; font-weight:600; }}

/* ── Certifications — 2 columns ─────────── */
.cert-list {{ padding-left:14px; columns:2; column-gap:16px; }}
.cert-list li {{ margin-bottom:2px; break-inside:avoid; font-size:0.97em; }}

@page {{ size: A4; margin: 0; }}
@media print {{ body {{ padding: 11mm 14mm; }} }}
</style>
</head>
<body>

<div class="header">
  <div class="name">{name}</div>
  <div class="contact">
    {location} &nbsp;|&nbsp; {phone} &nbsp;|&nbsp;
    <a href="mailto:{email}">{email}</a> &nbsp;|&nbsp;
    GitHub: <a href="{github}">{github_s}</a> &nbsp;|&nbsp;
    Portfolio: <a href="{portfolio}">{portfolio_s}</a>
  </div>
</div>

<div class="section">
  <div class="section-title">Summary</div>
  <div>{summary}</div>
</div>

<div class="section">
  <div class="section-title">Education</div>
  <div style="font-weight:600">{education}</div>
</div>

<div class="section">
  <div class="section-title">Technical Skills</div>
  {skills_html}
</div>

<div class="section">
  <div class="section-title">Projects</div>
  {projects_html}
</div>

<div class="section">
  <div class="section-title">Experience</div>
  {exp_html}
</div>

<div class="section">
  <div class="section-title">Certifications &amp; Training</div>
  <ul class="cert-list">{certs_html}</ul>
</div>

</body>
</html>"""
