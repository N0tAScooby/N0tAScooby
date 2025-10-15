import json
import re
from datetime import datetime
import requests

ORCID_JSON_PATH = "orcid.json"
README_PATH = "README.md"
START_MARKER = "<!-- ORCID-PUBS:START -->"
END_MARKER = "<!-- ORCID-PUBS:END -->"

def extract_publications(data):
    """Extracts publication details (title, year, authors, DOI) from ORCID JSON."""
    works = data.get("group", [])
    pubs = []
    for work in works:
        summary = work.get("work-summary", [])[0]
        title = summary.get("title", {}).get("title", {}).get("value", "Untitled")
        year = summary.get("publication-date", {}).get("year", {}).get("value")

        # Extract DOI
        doi = None
        for ext_id in summary.get("external-ids", {}).get("external-id", []):
            if ext_id.get("external-id-type") == "doi":
                doi = ext_id.get("external-id-value")
                break
        url = f"https://doi.org/{doi}" if doi else None

        # Extract authors
        url = f"""https://pub.orcid.org/v3.0{summary.get("path", "")}"""
        headers = {"Accept": "application/json"}
        resp = requests.get(url, headers=headers)
        work_data = resp.json()

        authors = []
        for c in work_data.get("contributors", {}).get("contributor", []):
            name = c.get("credit-name", {}).get("value")
            if name:
                authors.append(name)

        authors = ", ".join(authors)

        # Abstract 

        abstract = work_data.get("short-description")
        if abstract:
            abstract = abstract.replace("\n", " ").strip()

        pubs.append({
            "title": title,
            "authors": authors,
            "year": year,
            "url": url,
            "authors": authors,
            "abstract": abstract
        })

    # Sort by year descending
    pubs.sort(key=lambda x: x["year"] or "0000", reverse=True)
    return pubs

def format_publications(pubs):
    """Formats publications as a Markdown list."""
    lines = []
    for p in pubs:
        line = f"- {p['year']}: *{p['title']}* — {p['authors']}"
        if p["url"]:
            line += f" [DOI]({p['url']})"
        if p.get("abstract"):
            line += f"\n  <details>\n    <summary>Abstract</summary>\n\n    {p['abstract']}\n  </details>"
        lines.append(line)
    return "\n".join(lines)

def update_readme(publications_md):
    """Replaces the section in README between the markers."""
    with open(README_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    new_section = f"{START_MARKER}\n{publications_md}\n{END_MARKER}"
    new_content = re.sub(
        f"{START_MARKER}.*?{END_MARKER}",
        new_section,
        content,
        flags=re.DOTALL
    )

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(new_content)

def main():
    with open(ORCID_JSON_PATH, "r", encoding="utf-8") as f:
        data = json.load(f)
    pubs = extract_publications(data)
    publications_md = format_publications(pubs)
    update_readme(publications_md)
    print(f"Updated README with {len(pubs)} publications at {datetime.now()}")

if __name__ == "__main__":
    main()
