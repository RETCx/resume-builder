#!/usr/bin/env python3
"""Resume Builder CLI — JSON -> HTML -> PDF"""

from __future__ import annotations

import sys

# Force UTF-8 output on Windows Thai locale (cp874) to allow Rich to print Unicode
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except AttributeError:
    pass

import argparse
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

console = Console()

# Default: Point to resume.json in the same folder
_HERE = Path(__file__).parent
DEFAULT_RESUME = _HERE / "resume.json"


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="resume-builder",
        description="Convert resume.json -> HTML -> PDF via Playwright",
    )
    parser.add_argument(
        "--resume",
        default=str(DEFAULT_RESUME),
        help=f"Path to resume JSON (default: {DEFAULT_RESUME})",
    )
    parser.add_argument(
        "--output",
        default="output/resume.pdf",
        help="Path for PDF output (default: output/resume.pdf)",
    )
    parser.add_argument(
        "--projects",
        type=int,
        default=5,
        help="Max number of projects to display in PDF (default: 5)",
    )
    parser.add_argument(
        "--certs",
        type=int,
        default=4,
        help="Max number of certifications to display in PDF (default: 4)",
    )
    parser.add_argument(
        "--max-bullets",
        type=int,
        default=2,
        help="Max number of bullets per project (default: 2)",
    )
    parser.add_argument(
        "--scale",
        type=float,
        default=None,
        help="Explicitly set scale, e.g., 0.85 or 1.0 (default: auto)",
    )
    parser.add_argument(
        "--no-open",
        action="store_true",
        help="Do not auto-open PDF after generation",
    )
    parser.add_argument(
        "--html-only",
        action="store_true",
        help="Generate only HTML preview, do not export to PDF",
    )

    args = parser.parse_args()

    console.print(Panel(
        "[bold]Resume Builder[/bold] — JSON -> HTML -> PDF",
        subtitle=f"resume: {args.resume}",
    ))

    if args.html_only:
        # HTML only mode
        from builder.loader import load_resume
        from builder.html import build_html

        resume = load_resume(args.resume)
        html = build_html(resume, n_projects=args.projects, n_certs=args.certs)

        out = Path(args.output)
        html_path = out.parent / (out.stem + "_preview.html")
        html_path.parent.mkdir(parents=True, exist_ok=True)
        html_path.write_text(html, encoding="utf-8")
        console.print(f"\n  [bold green][OK] HTML saved -> {html_path.resolve()}[/bold green]")
    else:
        from builder.pdf import build_pdf

        build_pdf(
            resume_path=args.resume,
            output_path=args.output,
            n_projects=args.projects,
            n_certs=args.certs,
            max_bullets=args.max_bullets,
            open_after=not args.no_open,
            manual_scale=args.scale,
        )


if __name__ == "__main__":
    main()
