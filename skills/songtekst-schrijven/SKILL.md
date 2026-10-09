---
name: songtekst-schrijven
description: Write or improve original song lyrics for a personal occasion (birthday, wedding, retirement, farewell, a pet, a team), mainly in Dutch, with a singable structure, consistent line lengths and real rhymes. Also checks existing lyrics for syllable counts, rhyme scheme and expected sung length. Use when the user asks for a songtekst, a lied or liedje text, a rap verse or a chorus.
---

# Write lyrics people can actually sing

The goal is a text that fits a melody: lines of similar length within a section, a chorus that returns unchanged, rhymes that sound right when sung, and details that only fit this one person or moment. Good occasion lyrics are specific: the cat's name beats "je lieve huisdier".

## 1. Gather the material first

Ask only for what is missing, in one short message:
- occasion and who it is for (names, how to pronounce unusual names)
- two or three concrete details: a habit, a running joke, a place, a shared memory
- tone: cheerful, moving, funny, roast (and what is off limits)
- language, genre and approximate length (a 1 minute toast or a full 3 minute song)

Never ask for or use the lyrics of an existing song, and never write "in the style of" a named artist or imitate a famous voice. Describe genre, mood, tempo and instruments instead. Parodies of existing songs are out of scope for this skill; offer an original song instead.

## 2. Choose a structure

Read [references/structuur.md](references/structuur.md) for song forms and the length table. Default for a personal song:

```
[Couplet 1]   4 lines
[Refrein]     4 lines, contains the name or hook
[Couplet 2]   4 lines
[Refrein]     identical
[Brug]        2 to 4 lines, optional, a change of view
[Refrein]     identical, the last line may change once
```

Use English tags ([Verse], [Chorus], [Bridge]) when the user will paste the text into an English-language music tool; otherwise keep the Dutch tags.

## 3. Write

- Keep lines within one section within about two syllables of each other. Chorus lines may be shorter and punchier.
- Put the hook (often the name) at the start or end of the chorus, where it lands on a strong beat.
- Rhyme on sound, not spelling: "dag" rhymes with "lach", "staan" with "gaan". Avoid forced word order to make a rhyme.
- Use spoken Dutch. Write numbers out ("tachtig", not "80"), avoid abbreviations, and avoid long compound words that are hard to sing.
- Each verse adds a new concrete detail; the chorus sums up the feeling.
- No clichés as filler ("de tijd vliegt voorbij", "je bent een kanjer") unless the user asks for them.

## 4. Check before showing

Pass the lyrics to the bundled checker on standard input. Call `python3` directly with the full path of `scripts/check_lyrics.py` in this skill folder (no `cd` first):

```sh
python3 scripts/check_lyrics.py <<'LYRICS'
[Couplet 1]
...
LYRICS
```

A file path works too (`python3 scripts/check_lyrics.py songtekst.txt`). The checker reads only that input and makes no network requests. It reports syllables per line, flags lines that differ strongly from the rest of their section, shows the rhyme scheme per section, checks that the chorus is consistent, and estimates the sung length. The estimate (45 seconds plus 0.72 seconds per sung word) comes from 86 finished songs and is a guide, not a promise of any music tool. Syllables and rhymes are counted from spelling; read doubtful lines aloud.

Fix flagged lines yourself, then present:

1. **Title**
2. **Style line**: genre, mood, tempo, instruments and voice, for example "vrolijke akoestische pop, 110 bpm, gitaar en handgeklap, warme vrouwenstem". No artist names.
3. **Lyrics** with section tags
4. One line with the expected length and anything the user should check (pronunciation of a name, an inside joke).

## 5. Revise on request

When the user asks for changes ("korter", "minder zoetsig", "noem de fiets"), change only what was asked, keep the chorus stable unless asked, and run the checker again.

The lyrics belong to the user. This skill does not store, send or publish them.
