#!/usr/bin/env python3
"""Controleer een songtekst: lettergrepen per regel, rijm, structuur en geschatte lengte.

Leest een tekstbestand (of stdin), maakt geen netwerkverbinding en schrijft een
rapport naar stdout. Bedoeld voor Nederlandse teksten; Engelse regels krijgen
een ruwere telling.

    python3 check_lyrics.py songtekst.txt
    python3 check_lyrics.py songtekst.txt --json

De lengteschatting komt uit een lineaire fit op 86 echte liedjes van
muziekmakenmetai.nl (september 2026): ongeveer 45 seconden plus 0,72 seconde per
gezongen woord. Het is een schatting voor de gezongen lengte met intro en outro,
geen belofte van een muziekgenerator.
"""
from __future__ import annotations

import argparse
import json
import re
import statistics
import sys
import unicodedata

SECONDS_BASE = 45.0
SECONDS_PER_WORD = 0.72

SECTION_RE = re.compile(r"^\s*\[([^\]]+)\]\s*$")
WORD_RE = re.compile(r"[A-Za-zÀ-ÿ']+")
# Klinkergroepen die in het Nederlands samen één lettergreep vormen, langste eerst.
DUTCH_GROUPS = [
    "ieuw", "eeuw", "aai", "ooi", "oei", "ioe", "ieu", "eeu", "uw",
    "aa", "ee", "oo", "uu", "ie", "oe", "eu", "ui", "ei", "ij", "ou", "au",
]
VOWELS = set("aeiouyàáâäèéêëìíîïòóôöùúûü")
CHORUS_WORDS = {"refrein", "chorus", "hook", "pre-chorus", "prechorus", "brug", "bridge", "couplet", "verse", "outro", "intro"}


def _fold(text: str) -> str:
    """Accenten weg, behalve het trema dat een lettergreepgrens aangeeft."""
    out = []
    for ch in text.lower():
        if ch in "äëïöü":
            out.append("|" + unicodedata.normalize("NFD", ch)[0])
        else:
            out.append(unicodedata.normalize("NFD", ch)[0])
    return "".join(out)


def syllables(word: str) -> int:
    w = _fold(word).replace("'", "")
    if not w.strip("|"):
        return 0
    count, i = 0, 0
    while i < len(w):
        if w[i] == "|":
            i += 1
            continue
        if w[i] in VOWELS:
            for group in DUTCH_GROUPS:
                if w.startswith(group, i):
                    i += len(group)
                    break
            else:
                i += 1
            count += 1
        else:
            i += 1
    return max(count, 1)


def rhyme_key(line: str) -> str:
    """Laatste klinkergroep plus wat erna komt van het laatste woord: 'staan' en 'gaan' -> 'aan'."""
    words = WORD_RE.findall(line)
    if not words:
        return ""
    w = _fold(words[-1]).replace("|", "").replace("'", "")
    # Zoek de start van de laatste klinkergroep.
    i = len(w) - 1
    while i >= 0 and w[i] not in VOWELS:
        i -= 1
    while i > 0 and w[i - 1] in VOWELS:
        i -= 1
    key = w[i:] if i >= 0 else w
    # Toonloze eind-e ('lachen', 'dromen'): neem de klinker ervoor mee.
    if key in {"en", "e", "er", "el", "es", "et"} and i > 0:
        j = i - 1
        while j >= 0 and w[j] not in VOWELS:
            j -= 1
        while j > 0 and w[j - 1] in VOWELS:
            j -= 1
        key = w[j:] if j >= 0 else key
    # Klankgelijk aan het woordeinde: dag/lach, hand/kant.
    for a, b in (("dt", "t"), ("d", "t"), ("g", "ch"), ("b", "p")):
        if key.endswith(a):
            key = key[: -len(a)] + b
            break
    return key


def parse(text: str) -> list[dict]:
    sections, current = [], {"name": "(zonder kop)", "lines": []}
    for raw in text.splitlines():
        m = SECTION_RE.match(raw)
        if m:
            if current["lines"] or current["name"] != "(zonder kop)":
                sections.append(current)
            current = {"name": m.group(1).strip(), "lines": []}
            continue
        if raw.strip():
            current["lines"].append(raw.strip())
    if current["lines"] or current["name"] != "(zonder kop)":
        sections.append(current)
    return sections


def scheme(keys: list[str]) -> str:
    letters, seen = [], {}
    for k in keys:
        if not k:
            letters.append("-")
            continue
        if k not in seen:
            seen[k] = chr(ord("A") + len(seen)) if len(seen) < 26 else "?"
        letters.append(seen[k])
    return "".join(letters)


def analyse(text: str) -> dict:
    sections = parse(text)
    report_sections, all_words, notes = [], 0, []
    chorus_texts = []
    for sec in sections:
        rows = []
        for line in sec["lines"]:
            words = WORD_RE.findall(line)
            all_words += len(words)
            rows.append({"line": line, "syllables": sum(syllables(w) for w in words), "words": len(words), "rhyme": rhyme_key(line)})
        counts = [r["syllables"] for r in rows]
        median = statistics.median(counts) if counts else 0
        for r in rows:
            r["off"] = bool(median) and abs(r["syllables"] - median) >= max(3, round(median * 0.3))
        report_sections.append({"name": sec["name"], "lines": rows, "median_syllables": median, "scheme": scheme([r["rhyme"] for r in rows])})
        if sec["name"].split()[0].lower() in {"refrein", "chorus"}:
            chorus_texts.append("\n".join(sec["lines"]).lower())
    names = [s["name"].split()[0].lower() for s in sections]
    if not any(n in {"refrein", "chorus"} for n in names):
        notes.append("Geen [Refrein] of [Chorus] gevonden. Een herkenbaar refrein maakt een lied meezingbaar.")
    if len(set(chorus_texts)) > 1:
        notes.append("De refreinen verschillen van elkaar. Meestal werkt een vast refrein beter; varieer hooguit de laatste regel.")
    if any(n not in CHORUS_WORDS and n != "(zonder" for n in names):
        unknown = sorted({s["name"] for s in sections if s["name"].split()[0].lower() not in CHORUS_WORDS and s["name"] != "(zonder kop)"})
        if unknown:
            notes.append("Onbekende sectiekoppen: " + ", ".join(unknown) + ". Gangbaar zijn Intro, Couplet/Verse, Pre-chorus, Refrein/Chorus, Brug/Bridge en Outro.")
    long_lines = [r["line"] for s in report_sections for r in s["lines"] if r["syllables"] > 14]
    if long_lines:
        notes.append(f"{len(long_lines)} regel(s) met meer dan 14 lettergrepen. Die worden vaak afgeraffeld of verkort gezongen.")
    seconds = SECONDS_BASE + SECONDS_PER_WORD * all_words
    return {
        "sections": report_sections,
        "sung_words": all_words,
        "estimated_seconds": round(seconds),
        "estimate_note": "Schatting: 45 s + 0,72 s per gezongen woord (fit op 86 liedjes), inclusief intro en outro.",
        "notes": notes,
    }


def render(result: dict) -> str:
    out = []
    for sec in result["sections"]:
        out.append(f"[{sec['name']}]  rijmschema {sec['scheme']}  mediaan {sec['median_syllables']:g} lettergrepen")
        for r in sec["lines"]:
            flag = "  <- wijkt af" if r["off"] else ""
            out.append(f"  {r['syllables']:>2}  {r['rhyme'] or '-':<6}  {r['line']}{flag}")
        out.append("")
    m, s = divmod(result["estimated_seconds"], 60)
    out.append(f"Gezongen woorden: {result['sung_words']}. Geschatte lengte: {m}:{s:02d} ({result['estimate_note']})")
    for n in result["notes"]:
        out.append("- " + n)
    out.append("Lettergrepen en rijm zijn een telling op spelling, geen uitspraakanalyse. Lees twijfelgevallen hardop.")
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("file", nargs="?", help="tekstbestand met de songtekst; leeg = stdin")
    ap.add_argument("--json", action="store_true", help="geef het rapport als JSON")
    args = ap.parse_args(argv)
    text = open(args.file, encoding="utf-8").read() if args.file else sys.stdin.read()
    if not text.strip():
        print("Lege songtekst.", file=sys.stderr)
        return 2
    result = analyse(text)
    print(json.dumps(result, ensure_ascii=False, indent=1) if args.json else render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
