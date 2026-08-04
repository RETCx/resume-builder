"""PDF exporter: HTML -> Playwright -> PDF"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from rich.console import Console

from builder.html import build_html
from builder.loader import load_resume

console = Console()


def build_pdf(
    resume_path: str | Path = "resume.json",
    output_path: str | Path = "output/resume.pdf",
    n_projects: int = 4,
    n_certs: int = 4,
    max_bullets: int = 2,
    open_after: bool = True,
    fit_page: bool = True,
    manual_scale: float | None = None,
) -> Path:
    """Load JSON -> render HTML -> export PDF via Playwright

    Args:
        fit_page: Auto-scale content to fit exactly within one A4 page
    Returns:
        Path of the generated PDF
    """
    resume = load_resume(resume_path)
    html = build_html(resume, n_projects=n_projects, n_certs=n_certs, max_bullets=max_bullets)

    out = Path(output_path)
    out.parent.mkdir(parents=True, exist_ok=True)

    html_path = out.parent / (out.stem + "_preview.html")
    html_path.write_text(html, encoding="utf-8")
    console.print(f"  [dim]HTML preview -> {html_path.resolve()}[/dim]")

    try:
        from playwright.sync_api import sync_playwright

        with sync_playwright() as pw:
            browser = pw.chromium.launch()
            page = browser.new_page()
            # set_content() avoids TIS-620 mis-detection on Windows Thai locale
            page.set_content(html, wait_until="networkidle")

            scale = 1.0
            if manual_scale is not None:
                # Use the scale explicitly provided by the user
                scale = round(max(0.5, min(2.0, manual_scale)), 3)
                console.print(f"  [dim]manual scale: {scale}[/dim]")
            elif fit_page:
                # Measure height in print mode with an A4 viewport width (794px @ 96dpi)
                # Measuring in screen mode (1280px) causes less text wrap, leading to inaccurate height estimates
                A4_W_PX = round(210 / 25.4 * 96)   # ≈ 794 px
                A4_H_PX = round(297 / 25.4 * 96)   # ≈ 1122 px
                page.set_viewport_size({"width": A4_W_PX, "height": A4_H_PX})
                page.emulate_media(media="print")

                # scrollHeight already includes body padding → compare with full A4 height (1122px)
                body_h = page.evaluate("document.body.scrollHeight")
                # Scale for both overflow (scale down) and underflow (scale up)
                # Cap max scale at 1.25 to prevent overly large text
                raw_scale = A4_H_PX / body_h * 0.999
                scale = round(max(0.5, min(1.25, raw_scale)), 3)
                direction = "↑ scale up" if body_h < A4_H_PX else "↓ scale down"
                console.print(
                    f"  [dim]content {body_h:.0f}px / {A4_H_PX}px (A4) "
                    f"→ {direction} {scale:.3f}[/dim]"
                )

            page.pdf(
                path=str(out),
                format="A4",
                print_background=True,
                margin={"top": "0", "bottom": "0", "left": "0", "right": "0"},
                scale=scale,
            )
            browser.close()

        console.print(f"  [bold green][OK] PDF saved -> {out}[/bold green]")

        if open_after:
            _open_file(out)

    except ImportError:
        console.print("  [yellow]playwright is not installed -- opening HTML preview instead[/yellow]")
        console.print("  [dim]Install it using: pip install playwright && playwright install chromium[/dim]")
        import webbrowser
        webbrowser.open(f"file:///{html_path.resolve().as_posix()}")

    return out


def _open_file(path: Path) -> None:
    """Open file using the OS default application"""
    try:
        if sys.platform == "win32":
            subprocess.Popen(["start", "", str(path)], shell=True)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except Exception:
        pass
