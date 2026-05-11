#!/usr/bin/env python3
"""
add_paper.py — Add a new paper to Laure Berti-Équille's website (local Git only).

Usage:
    python add_paper.py \\
        --ref "L. Berti-Équille, J. Doe. My Paper Title. ICDE, 2026." \\
        [--pdf path/to/paper.pdf] \\
        [--doi https://doi.org/...] \\
        [--citations 0] \\
        [--topic "Data Quality / Data Cleaning"] \\
        [--venue-url https://conference.org] \\
        [--dry-run]

Updates (before any git push):
    1. publications.html         — <li> in the correct year section
    2. js/network.js             — referencesBibliographiques entry
    3. index.html                — news item at top of #news section
    4. bubble-timeline.html      — CSV data row
"""

from __future__ import annotations

import argparse
import re
import shutil
from datetime import datetime
from pathlib import Path

WEBSITE = Path(__file__).parent

# ---------------------------------------------------------------------------
# Topic keyword mapping for bubble-timeline
# ---------------------------------------------------------------------------
TOPIC_KEYWORDS: list[tuple[list[str], str]] = [
    (["data quality", "data cleaning", "mesqual", "learn2clean",
      "profil", "dirty data", "data preparation", "data repair"],
     "Data Quality / Data Cleaning"),
    (["fact-check", "truth discovery", "veracity", "fake news",
      "misinformation", "conflicting", "crowdsourc"],
     "Fact-Checking / Truth Discovery"),
    (["knowledge graph", "ontolog", "semantic web", "rdf", "sparql",
      "linked data", "knowledge engineer"],
     "Knowledge Engineering"),
    (["multimodal", "fusion", "evidential", "set-valued"],
     "Multimodal Fusion & Learning"),
]
DEFAULT_TOPIC = "Applied Data Analytics & ML"


def classify_topic(title: str, ref: str) -> str:
    text = (title + " " + ref).lower()
    for keywords, topic in TOPIC_KEYWORDS:
        if any(k in text for k in keywords):
            return topic
    return DEFAULT_TOPIC


# ---------------------------------------------------------------------------
# Reference parser
# ---------------------------------------------------------------------------
MONTH_MAP = {
    1: "Jan", 2: "Feb", 3: "March", 4: "April", 5: "May", 6: "June",
    7: "July", 8: "Aug", 9: "Sept", 10: "Oct", 11: "Nov", 12: "Dec",
}


def _is_name_token(s: str) -> bool:
    """Return True if s looks like a person's name (1–4 words, starts with capitals)."""
    s = s.strip()
    if not s or re.search(r"\d", s):
        return False
    words = s.split()
    if not (1 <= len(words) <= 4):
        return False
    particles = {"de", "van", "von", "le", "la", "du", "del", "dos", "das", "di"}
    return all(w[0].isupper() or w.lower() in particles for w in words if w)


def parse_ref(ref: str) -> dict:
    """
    Parse a reference string into structured fields.

    Handles two formats:
      1. One-line:  "Authors. Title. Venue, Year."
      2. Multi-line (Elsevier/ScienceDirect style):
            Author1, Author2, ...,
            Title,
            Journal Name,
            Volume N,
            Year,
            ...
            https://doi.org/...

    Returns keys: authors_str, authors_list, title, venue, year, doi, n_authors
    """
    ref = ref.strip().replace("Berti-Équille", "Berti-Equille")

    # ── Year and DOI — extracted from full text regardless of format ──────────
    year_match = re.search(r"\b(19[89]\d|20[0-3]\d)\b", ref)
    year = int(year_match.group(1)) if year_match else datetime.now().year

    doi = ""
    doi_match = re.search(r"(https?://doi\.org/\S+|10\.\d{4,}/\S+)", ref)
    if doi_match:
        doi = doi_match.group(1).rstrip(".,;)(")

    # ── Multi-line format detection ───────────────────────────────────────────
    lines = [l.strip().rstrip(",") for l in ref.splitlines() if l.strip()]

    if len(lines) >= 3:
        # Line 0: comma-separated author list
        # Line 1: title
        # Line 2: journal / venue  (stop before "Volume", digits, ISSN, URLs)
        authors_str = lines[0]
        title = lines[1]

        # Venue: first non-author, non-title line that isn't volume/year/ISSN/URL
        venue = ""
        for line in lines[2:]:
            if re.match(r"^(Volume|Vol\.?|Issue|ISSN|https?://|\d)", line, re.I):
                break
            venue = line
            break

        raw_authors = re.sub(r"\s+and\s+|\s+&\s+", ", ", authors_str)
        authors_list = [a.strip() for a in raw_authors.split(",")
                        if a.strip() and _is_name_token(a)]

        return {
            "authors_str": authors_str,
            "authors_list": authors_list,
            "title": title,
            "venue": venue,
            "year": year,
            "doi": doi,
            "n_authors": len(authors_list),
        }

    # ── One-line format: split on ". " ────────────────────────────────────────
    parts = [p.strip() for p in ref.split(". ") if p.strip()]

    authors_str = parts[0] if parts else ""
    title = parts[1] if len(parts) > 1 else ""
    venue = parts[2] if len(parts) > 2 else ""
    venue = re.sub(r"\b(19|20)\d{2}\b.*", "", venue).strip().rstrip(",.")

    raw_authors = re.sub(r"\s+and\s+|\s+&\s+", ", ", authors_str)
    authors_list = [a.strip() for a in raw_authors.split(",") if a.strip()]

    return {
        "authors_str": authors_str,
        "authors_list": authors_list,
        "title": title,
        "venue": venue,
        "year": year,
        "doi": doi,
        "n_authors": len(authors_list),
    }


# ---------------------------------------------------------------------------
# 1. publications.html
# ---------------------------------------------------------------------------
def update_publications(p: dict, pdf_rel: str, doi: str, dry_run: bool) -> None:
    path = WEBSITE / "publications.html"
    html = path.read_text(encoding="utf-8")

    # Build download span
    downloads = ""
    if pdf_rel:
        downloads += f'\n      <span class="pub_downloads">\n'
        downloads += f'        Download: <a href="{pdf_rel}" target="_blank">[pdf]</a>\n'
        if doi:
            downloads += f'        &nbsp;<a href="{doi}" target="_blank">[DOI]</a>\n'
        downloads += "      </span>"
    elif doi:
        downloads += f'\n      <span class="pub_downloads">\n'
        downloads += f'        <a href="{doi}" target="_blank">[DOI]</a>\n'
        downloads += "      </span>"

    new_li = (
        f"    <li>\n"
        f"      {p['authors_str']}. {p['title']}. <i>{p['venue']}</i>, {p['year']}.{downloads}\n"
        f"    </li>"
    )

    year = p["year"]
    year_header = f"<h5>{year}</h5>"

    if year_header in html:
        # Find the <ul> after this year's header and insert at top
        insert_after = f"{year_header}"
        # Find the <ul> following this header
        idx = html.index(year_header)
        ul_idx = html.index("<ul>", idx)
        insert_pos = ul_idx + len("<ul>")
        new_html = html[:insert_pos] + "\n" + new_li + "\n" + html[insert_pos:]
    else:
        # Create a new year section before the current first year
        first_table = html.index("<table width=\"140\">")
        new_section = (
            f'<table width="140">\n<tbody>\n<tr>\n'
            f'<div align=center class="year">\n<h5>{year}</h5>\n</div>\n'
            f'</tr>\n</tbody>\n</table>\n<ul>\n{new_li}\n</ul>\n\n'
        )
        new_html = html[:first_table] + new_section + html[first_table:]

    if dry_run:
        print(f"[DRY-RUN] publications.html — would insert:\n{new_li}\n")
    else:
        path.write_text(new_html, encoding="utf-8")
        print(f"✓ publications.html updated (year {year})")


# ---------------------------------------------------------------------------
# 2. js/network.js
# ---------------------------------------------------------------------------
def update_network(p: dict, dry_run: bool) -> None:
    path = WEBSITE / "js" / "network.js"
    js = path.read_text(encoding="utf-8")

    authors_js = ", ".join(f'"{a}"' for a in p["authors_list"])
    venue_short = p["venue"].split(",")[0].split("(")[0].strip()[:40]
    titre = f"{venue_short} {p['year']}"

    new_entry = (
        f"  {{\n"
        f"    titre: \"{titre}\",\n"
        f"    auteurs: [{authors_js}]\n"
        f"  }},\n"
    )

    # Insert at top of the array (after the opening `[`)
    insert_marker = "const referencesBibliographiques = \n     ["
    if insert_marker not in js:
        # Fallback: simpler marker
        insert_marker = "const referencesBibliographiques ="
        idx = js.index(insert_marker)
        bracket_idx = js.index("[", idx)
    else:
        bracket_idx = js.index("[", js.index(insert_marker))

    insert_pos = bracket_idx + 1
    new_js = js[:insert_pos] + "\n" + new_entry + js[insert_pos:]

    if dry_run:
        print(f"[DRY-RUN] js/network.js — would insert:\n{new_entry}")
    else:
        path.write_text(new_js, encoding="utf-8")
        print(f"✓ js/network.js updated")


# ---------------------------------------------------------------------------
# 3. index.html — News section
# ---------------------------------------------------------------------------
def update_news(p: dict, doi: str, dry_run: bool) -> None:
    path = WEBSITE / "index.html"
    html = path.read_text(encoding="utf-8")

    month = MONTH_MAP[datetime.now().month]
    year = p["year"]
    venue_short = p["venue"].split(",")[0].strip()

    if doi:
        link = f'<a href="{doi}" target="_blank">{venue_short}</a>'
    else:
        link = f"<i>{venue_short}</i>"

    # Shorten author list for news (first author + et al. if >2)
    authors_display = p["authors_list"][0] if p["authors_list"] else ""
    if len(p["authors_list"]) > 2:
        authors_display += " et al."
    elif len(p["authors_list"]) == 2:
        authors_display += f" &amp; {p['authors_list'][1]}"

    new_item = (
        f'    <div class="item"><p class="date">{month}, {year}</p>\n'
        f'        <p><i class="fa fa-newspaper-o"></i> Paper accepted at {link} '
        f'entitled &ldquo;{p["title"]}&rdquo; with {authors_display}.\n'
        f'        </p>\n'
        f'    </div>'
    )

    # Insert after <div class="news-items">
    marker = '<div class="news-items">'
    insert_pos = html.index(marker) + len(marker)
    new_html = html[:insert_pos] + "\n\n" + new_item + "\n" + html[insert_pos:]

    if dry_run:
        print(f"[DRY-RUN] index.html — would insert news:\n{new_item}\n")
    else:
        path.write_text(new_html, encoding="utf-8")
        print(f"✓ index.html (news) updated")


# ---------------------------------------------------------------------------
# 4. bubble-timeline.html
# ---------------------------------------------------------------------------
def update_timeline(p: dict, topic: str, citations: int, dry_run: bool) -> None:
    path = WEBSITE / "bubble-timeline.html"
    html = path.read_text(encoding="utf-8")

    venue_short = p["venue"].split(",")[0].strip()
    title_clean = p["title"].replace("`", "'")
    new_row = (
        f"{topic},{venue_short},{p['year']},{citations},"
        f"{p['n_authors']},{title_clean}"
    )

    # Insert after CSV header line
    header = "topic,venue,year,citations,authors,title"
    idx = html.index(header)
    insert_pos = idx + len(header)
    new_html = html[:insert_pos] + "\n" + new_row + html[insert_pos:]

    if dry_run:
        print(f"[DRY-RUN] bubble-timeline.html — would insert CSV row:\n{new_row}\n")
    else:
        path.write_text(new_html, encoding="utf-8")
        print(f"✓ bubble-timeline.html updated")


# ---------------------------------------------------------------------------
# PDF handling
# ---------------------------------------------------------------------------
def stage_pdf(pdf_src: str, year: int) -> str:
    """Copy PDF to website/pub/ and return the relative href."""
    src = Path(pdf_src)
    if not src.exists():
        print(f"⚠ PDF not found: {pdf_src} — skipping")
        return ""
    dest_dir = WEBSITE / "pub"
    dest_dir.mkdir(exist_ok=True)
    # Avoid double-prefix if file is already named YEAR_...
    if src.name.startswith(f"{year}_"):
        dest = dest_dir / src.name
    else:
        dest = dest_dir / f"{year}_{src.name}"
    shutil.copy2(src, dest)
    print(f"✓ PDF copied → pub/{dest.name}")
    return f"./pub/{dest.name}"


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
# HAL deposit email
# ---------------------------------------------------------------------------
def draft_hal_email(p: dict, doi: str, full_ref: str, dry_run: bool) -> None:
    """Print a ready-to-send email asking the HAL team to deposit the paper."""
    doi_line = f"DOI : {doi}" if doi else "DOI : (not yet available)"
    pdf_note = "(please attach the author's accepted manuscript PDF)"

    email = f"""\
To      : assistance@ccsd.cnrs.fr
Subject : Dépôt HAL — {p['title']} ({p['year']})

Madame, Monsieur,

Je souhaite déposer la publication suivante dans HAL :

  {full_ref.strip()}

  {doi_line}

Merci de bien vouloir procéder au dépôt ou de m'indiquer la procédure
à suivre pour un dépôt en accès ouvert.
{pdf_note}

Cordialement,
Laure Berti-Équille
Directrice de Recherche, IRD
laure.berti@ird.fr
"""
    PENDING_EMAILS = Path("/Users/laureberti/Projects/RBoost/pending/emails")
    if dry_run:
        print(f"[DRY-RUN] HAL email draft:\n{email}")
    else:
        PENDING_EMAILS.mkdir(parents=True, exist_ok=True)
        out = PENDING_EMAILS / f"hal_email_{p['year']}_{p['title'][:30].replace(' ','_')}.txt"
        out.write_text(email, encoding="utf-8")
        print(f"✓ HAL email draft saved → pending/emails/{out.name}")
        print("  (open the file, attach the PDF, and send to assistance@ccsd.cnrs.fr)")


# ---------------------------------------------------------------------------
def main() -> None:
    ap = argparse.ArgumentParser(description="Add a paper to the website.")
    ap.add_argument("--ref", required=True,
                    help='Full reference text: "Authors. Title. Venue, Year."')
    ap.add_argument("--pdf", default="",
                    help="Path to the PDF file (will be copied to pub/)")
    ap.add_argument("--doi", default="",
                    help="DOI or URL for the paper")
    ap.add_argument("--citations", type=int, default=0,
                    help="Current citation count (default: 0)")
    ap.add_argument("--topic", default="",
                    help="Override topic category for bubble-timeline")
    ap.add_argument("--venue-url", default="",
                    help="URL for the venue (used in news item)")
    ap.add_argument("--dry-run", action="store_true",
                    help="Preview changes without writing any file")
    args = ap.parse_args()

    p = parse_ref(args.ref)

    # Override DOI if provided separately
    if args.doi:
        p["doi"] = args.doi
    doi = p["doi"]

    topic = args.topic or classify_topic(p["title"], args.ref)

    print(f"\n{'='*60}")
    print(f"  Title   : {p['title']}")
    print(f"  Authors : {p['authors_str']}")
    print(f"  Venue   : {p['venue']}")
    print(f"  Year    : {p['year']}")
    print(f"  Topic   : {topic}")
    print(f"  DOI     : {doi or '(none)'}")
    print(f"  #Authors: {p['n_authors']}")
    print(f"{'='*60}\n")

    # Stage PDF
    pdf_rel = ""
    if args.pdf and not args.dry_run:
        pdf_rel = stage_pdf(args.pdf, p["year"])
    elif args.pdf:
        src_name = Path(args.pdf).name
        if src_name.startswith(f"{p['year']}_"):
            pdf_rel = f"./pub/{src_name}"
        else:
            pdf_rel = f"./pub/{p['year']}_{src_name}"

    update_publications(p, pdf_rel, doi, args.dry_run)
    update_network(p, args.dry_run)
    update_news(p, doi, args.dry_run)
    update_timeline(p, topic, args.citations, args.dry_run)
    draft_hal_email(p, doi, args.ref, args.dry_run)

    if not args.dry_run:
        print(f"\n✓ All 4 files updated locally.")
        print("  Review the changes, then push with:")
        print("    cd /Users/laureberti/Git/website && git add -A && git commit -m 'Add paper: ...' && git push")


if __name__ == "__main__":
    main()
