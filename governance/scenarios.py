"""تحميل السيناريوهات (YAML) والتحقق من بنيتها."""
from pathlib import Path

import yaml

from . import config as C

REQUIRED = ("id", "setup", "stages")


def load(path_or_id):
    p = Path(path_or_id)
    if p.suffix != ".yaml" or not p.exists():
        p = C.SCENARIO_DIR / f"{Path(str(path_or_id)).stem}.yaml"
    sc = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(sc, dict):
        raise ValueError(f"scenario {p.name}: not a mapping")
    for k in REQUIRED:
        if k not in sc:
            raise ValueError(f"scenario {p.name}: missing '{k}'")
    from .agents import load_personas
    valid = set(load_personas()) | {"all"}
    for st in sc["stages"]:
        if "id" not in st or not st.get("release"):
            raise ValueError(f"scenario {p.name}: every stage needs id and release")
        for rel in st["release"]:
            if not isinstance(rel.get("to"), list) or not rel.get("info_en"):
                raise ValueError(f"scenario {p.name} stage {st['id']}: release needs a list 'to' + info_en")
            bad = [a for a in rel["to"] if a not in valid]
            if bad:                               # غلطة إملائية = المعلومة ما بتوصل لحدا بصمت
                raise ValueError(f"scenario {p.name} stage {st['id']}: unknown agent(s) {bad}")
    return sc


def list_all():
    out = []
    for p in sorted(C.SCENARIO_DIR.glob("*.yaml")):
        try:
            sc = load(p)
        except Exception as e:
            print(f"[scenario error] {p.name}: {e}")
            out.append({"id": p.stem, "error": "invalid"})
            continue
        out.append({"id": sc["id"], "title_en": sc.get("title_en", sc["id"]), "title_ar": sc.get("title_ar", ""),
                    "summary_en": sc.get("summary_en", ""), "summary_ar": sc.get("summary_ar", ""),
                    "stages": [{"id": s["id"], "title_en": s.get("title_en", ""), "title_ar": s.get("title_ar", ""),
                                "to": sorted({a for r in s["release"] for a in r["to"]})} for s in sc["stages"]]})
    return out
