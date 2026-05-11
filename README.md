# laureberti.github.io/website

Personal academic website for Laure Berti-Équille (IRD, DR1).

---

## Adding a New Publication

`add_paper.py` updates four files in one command and keeps them in sync:

| File | What changes |
|---|---|
| `publications.html` | New `<li>` inserted at the top of the correct year section |
| `js/network.js` | New entry prepended to `referencesBibliographiques` |
| `index.html` | New news item inserted in `#news` |
| `bubble-timeline.html` | New CSV row appended after the header |

### Usage

```bash
cd /Users/laureberti/Git/website

# Minimal (reference text only)
python add_paper.py \
  --ref "L. Berti-Équille, J. Doe. My Paper Title. ICDE, 2026."

# Full (with PDF, DOI, citation count, topic override)
python add_paper.py \
  --ref "L. Berti-Équille, J. Doe. My Paper Title. ICDE, 2026." \
  --pdf path/to/paper.pdf \
  --doi https://doi.org/10.xxxx/xxxxx \
  --citations 0 \
  --topic "Fact-Checking / Truth Discovery"

# Preview without writing any file
python add_paper.py --ref "..." --dry-run
```

### Arguments

| Argument | Required | Description |
|---|---|---|
| `--ref` | yes | Full reference string: `"Authors. Title. Venue, Year."` |
| `--pdf` | no | Path to PDF — copied to `pub/YEAR_filename.pdf` |
| `--doi` | no | DOI or URL for the paper |
| `--citations` | no | Current citation count (default: 0) |
| `--topic` | no | Override auto-detected topic for bubble-timeline |
| `--venue-url` | no | URL for the venue (used in news item) |
| `--dry-run` | no | Print what would change, write nothing |

### Auto-detected topics

If `--topic` is omitted, the script infers the topic from keywords in the title and reference:

| Keywords | Topic |
|---|---|
| data quality, profiling, dirty data, repair … | Data Quality / Data Cleaning |
| fact-check, truth discovery, veracity, fake news … | Fact-Checking / Truth Discovery |
| knowledge graph, ontology, RDF, SPARQL … | Knowledge Engineering |
| multimodal, fusion, evidential, set-valued | Multimodal Fusion & Learning |
| *(anything else)* | Applied Data Analytics & ML |

### After running

Review the four modified files, then commit and push:

```bash
git diff
git add publications.html js/network.js index.html bubble-timeline.html
git commit -m "Add paper: <short title>"
git push
```

> **Note:** PDFs copied to `pub/` must also be staged if a `--pdf` argument was used:
> ```bash
> git add pub/YEAR_filename.pdf
> ```

---

## Prerequisites

- Python 3.x (stdlib only — no extra packages required)
- Git push access to the `laureberti/website` repository
