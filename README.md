# Songtekst schrijven

A skill for Claude, ChatGPT and Codex that writes original song lyrics for personal occasions, mainly in Dutch, and checks them before you use them.

- Gathers the details that make a song personal: names, habits, a running joke.
- Picks a structure (verse, chorus, bridge) and keeps lines within a section at a similar length.
- Rhymes on sound: "dag" rhymes with "lach", "staan" with "gaan".
- Runs a local checker for syllables per line, rhyme scheme, chorus consistency and an estimate of the sung length.
- Delivers a title, a style line (genre, mood, tempo, instruments, voice, no artist names) and the lyrics with section tags.

It never uses lyrics of existing songs and never imitates a named artist.

## The checker

```sh
python3 skills/songtekst-schrijven/scripts/check_lyrics.py songtekst.txt
python3 skills/songtekst-schrijven/scripts/check_lyrics.py songtekst.txt --json
```

Python 3 standard library only, no network access. Syllables and rhymes are counted from Dutch spelling; English lines get a rougher count. The length estimate (45 seconds plus 0.72 seconds per sung word) is a linear fit on 86 finished songs from muziekmakenmetai.nl, measured in September 2026. It is a planning guide, not a promise of any music tool.

## Example prompts

- Schrijf een verjaardagslied voor oma Truus, ze wordt tachtig en houdt van tuinieren en haar kat Moos.
- Maak een kort pensioenlied voor mijn collega Sanne. Ze fietst elke dag naar kantoor en drinkt te veel koffie.
- Check de lettergrepen en het rijm van deze songtekst en maak het refrein strakker.

## Tests

```sh
python3 -m pytest tests
```

Made by Samautomation. MIT license. Privacy: [PRIVACY.md](PRIVACY.md).
