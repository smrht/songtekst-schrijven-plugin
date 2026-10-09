import json, subprocess, sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "skills/songtekst-schrijven/scripts/check_lyrics.py"
sys.path.insert(0, str(SCRIPT.parent))
from check_lyrics import analyse, rhyme_key, syllables  # noqa: E402

SONG = """[Couplet 1]
In de tuin tussen de rozen
Staat ze 's ochtends al heel vroeg
Handen in de zwarte aarde
Van haar bloemen krijgt ze nooit genoeg

[Refrein]
Hiep hiep hoera voor oma Truus
Tachtig jaar en nog zo fit
Met Moos op schoot voelt het als thuis
Wij zijn blij dat jij er bent

[Couplet 2]
Moos ligt lui tussen de tulpen
Kijkt hoe oma water geeft
Samen in het zonnetje
Dat is hoe je tachtig jaren leeft

[Refrein]
Hiep hiep hoera voor oma Truus
Tachtig jaar en nog zo fit
Met Moos op schoot voelt het als thuis
Wij zijn blij dat jij er bent
"""


def test_dutch_syllables():
    cases = {"oma": 2, "tachtig": 2, "verjaardag": 3, "nieuw": 1, "mooie": 2, "koffie": 2,
             "België": 3, "tuinieren": 3, "pensioen": 2, "eeuwig": 2, "lachen": 2}
    assert {w: syllables(w) for w in cases} == cases


def test_rhyme_on_sound():
    assert rhyme_key("staan") == rhyme_key("gaan")
    assert rhyme_key("een mooie dag") == rhyme_key("met een lach")
    assert rhyme_key("hand") == rhyme_key("kant")
    assert rhyme_key("Truus") != rhyme_key("huis")


def test_structure_and_estimate():
    r = analyse(SONG)
    assert [s["name"] for s in r["sections"]] == ["Couplet 1", "Refrein", "Couplet 2", "Refrein"]
    assert r["sung_words"] == 101
    assert r["estimated_seconds"] == round(45 + 0.72 * 101)
    assert not any("verschillen" in n for n in r["notes"])
    assert r["sections"][1]["scheme"][0] != "-"


def test_flags_outlier_line_and_missing_chorus():
    text = "[Couplet]\nKort\nDit is een gewone regel van acht\nDit is een gewone regel van acht\nDit is een veel te lange regel die maar doorgaat en doorgaat zonder adem\n"
    r = analyse(text)
    offs = [row["line"] for row in r["sections"][0]["lines"] if row["off"]]
    assert any("veel te lange" in o for o in offs)
    assert any("Geen [Refrein]" in n for n in r["notes"])


def test_cli_json_and_empty(tmp_path):
    f = tmp_path / "s.txt"
    f.write_text(SONG, encoding="utf-8")
    out = subprocess.run([sys.executable, str(SCRIPT), str(f), "--json"], capture_output=True, text=True, check=True)
    assert json.loads(out.stdout)["sung_words"] == 101
    empty = tmp_path / "e.txt"
    empty.write_text("  \n", encoding="utf-8")
    assert subprocess.run([sys.executable, str(SCRIPT), str(empty)], capture_output=True).returncode == 2
