# Resume Builder

Convert `resume.json` → HTML → PDF via **Playwright**.  
A standalone, fully automated tool to generate beautiful, tailored resumes.

---

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/resume-builder.git
cd resume-builder
pip install -r requirements.txt
playwright install chromium
```

---

## Usage

```bash
# Run (uses the included resume.json by default)
python main.py

# Specify your own JSON file
python main.py --resume path/to/my_resume.json

# Combine options (e.g., using a relative path and forcing a specific scale)
python main.py --scale 0.78 --resume "..\folder\resume.json"

# Additional options
python main.py --projects 5        # Set max projects displayed
python main.py --certs 3           # Set max certifications displayed
python main.py --scale 0.95        # Force PDF scale (e.g., 95%) 
python main.py --output cv.pdf     # Set output filename
python main.py --no-open           # Prevent auto-opening the PDF
python main.py --html-only         # Generate HTML preview only without rendering PDF
```

### Output

| File | Description |
|---|---|
| `output/resume_preview.html` | HTML preview (viewable in browser) |
| `output/resume.pdf` | Ready-to-send PDF |

---

## Project Structure

```
resume-builder/
├── main.py              CLI entry point
├── requirements.txt
├── builder/
│   ├── loader.py        JSON parser
│   ├── html.py          HTML & CSS generator
│   └── pdf.py           Playwright PDF exporter
└── output/              Generated files
```

---

## Technical Details: PDF Auto-Scaling

The script ensures your content fits perfectly on a single A4 page:
1. Renders the HTML in Playwright using a virtual A4 viewport.
2. Evaluates the actual document height.
3. Automatically calculates the ideal `scale` factor (scaling down if it overflows, or scaling up if there is too much whitespace).
4. Exports the PDF using the calculated scale.

## Note on Windows Thai Locale

On Windows Thai locale, Python uses `cp874` (TIS-620) as the default encoding. This causes certain characters (like `–`, `—`, `²`) to be decoded incorrectly and appear broken in the PDF.

This project resolves the encoding issue using 3 strategies:

| Scope | Solution |
|---|---|
| JSON Reading | `open(path, encoding="utf-8")` |
| HTML Generation | All strings are passed through `_t()` → converting them to `&#NNN;` entities |
| Terminal Output | `sys.stdout.reconfigure(encoding="utf-8")` |
