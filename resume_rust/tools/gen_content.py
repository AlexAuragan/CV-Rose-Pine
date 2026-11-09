"""Serialize the Python resume content into JSON for the Rust port.

This keeps the existing Python content as the single source of truth during
the migration: run it from anywhere, it imports ``resume.content`` from the
repo root and writes ``resume_rust/content/*.json``.

    python3 resume_rust/tools/gen_content.py
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parents[1] / "content"
sys.path.insert(0, str(ROOT))

from resume.content import hyprlinks as links  # noqa: E402
from resume.content.en import resume_en  # noqa: E402
from resume.content.fr import resume_fr  # noqa: E402
from resume.models import HyperLink  # noqa: E402


def link_index() -> dict[tuple[str, str, str], str]:
    index: dict[tuple[str, str, str], str] = {}
    for name, value in vars(links).items():
        if isinstance(value, HyperLink):
            index.setdefault((value.title_en, value.title_fr, value.url), name)
    return index


LINKS = link_index()


def ref(link: HyperLink) -> dict[str, str]:
    return {"link": LINKS[(link.title_en, link.title_fr, link.url)]}


def node(value: object) -> object:
    if isinstance(value, str):
        return value
    if isinstance(value, HyperLink):
        return ref(value)
    if isinstance(value, list):
        return [node(item) for item in value]
    if isinstance(value, tuple):
        title, child = value
        return {"group": title, "items": node(child)}
    raise TypeError(f"unsupported node: {value!r}")


def tool(value: object) -> object:
    if isinstance(value, str):
        return value
    if isinstance(value, HyperLink):
        return ref(value)
    raise TypeError(f"unsupported tool: {value!r}")


def contact(c: object) -> dict[str, object]:
    return {"label": c.label, "value": c.value, "url": c.url}


def post(p: object) -> dict[str, object]:
    return {
        "title": p.title,
        "company": p.company,
        "company_link": LINKS[
            (p.company_link.title_en, p.company_link.title_fr, p.company_link.url)
        ],
        "start_month": p.start_month,
        "end_month": p.end_month,
        "desc": node(p.desc),
        "skills": list(p.skills),
        "tools": [tool(t) for t in p.tools],
        "region": p.region,
        "links": [
            LINKS[(l.title_en, l.title_fr, l.url)] for l in p.links
        ],
    }


def project(p: object) -> dict[str, object]:
    return {
        "title": p.title,
        "desc": node(p.desc),
        "modality": p.modality,
        "year": p.year,
        "skills": list(p.skills),
        "tools": [tool(t) for t in p.tools],
        "links": [
            LINKS[(l.title_en, l.title_fr, l.url)] for l in p.links
        ],
    }


def study(s: object) -> dict[str, object]:
    return {
        "title": s.title,
        "spe": s.spe,
        "region": s.region,
        "tags": list(s.tags),
    }


def misc(m: object) -> dict[str, object]:
    return {
        "title": m.title,
        "desc": node(m.desc),
        "tags": list(m.tags),
        "links": [
            LINKS[(l.title_en, l.title_fr, l.url)] for l in m.links
        ],
    }


def resume(r: object) -> dict[str, object]:
    return {
        "profile": {
            "name": r.profile.name,
            "title": r.profile.title,
            "region": r.profile.region,
            "ascii_art": r.profile.ascii_art.strip("\n"),
            "highlights": list(r.profile.highlights),
            "current": r.profile.current,
            "contact": [contact(c) for c in r.profile.contact],
        },
        "work_experience": [post(p) for p in r.work_experience],
        "personal_projects": [project(p) for p in r.personal_projects],
        "studies": [study(s) for s in r.studies],
        "misc": [misc(m) for m in r.misc],
    }


def dump(name: str, payload: object) -> None:
    path = OUT / name
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(f"wrote {path}")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)

    dump(
        "links.json",
        {
            name: {
                "title_en": value.title_en,
                "title_fr": value.title_fr,
                "url": value.url,
            }
            for name, value in sorted(vars(links).items())
            if isinstance(value, HyperLink)
        },
    )
    dump("en.json", resume(resume_en))
    dump("fr.json", resume(resume_fr))


if __name__ == "__main__":
    main()
