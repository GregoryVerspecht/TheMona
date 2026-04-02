# Games — The Mona

Alle games gebruiken dezelfde hardware: 6 draadloze knoppen met NeoPixel LEDs, een WS2812B LED strip (20 LEDs), JBL Bluetooth speaker, en de Raspberry Pi als server.

Elke game erft van `GameBase` en implementeert `start()`, `stop()`, `on_button_pressed()` en `status()`.

---

## Game 1 — Reaction *(al gebouwd)*

### Concept
Één knop licht op. Druk zo snel mogelijk. Wie te vroeg of te laat drukt verliest een punt.

### Spelverloop
1. Alle knoppen dim blauw — wacht op willekeurig moment
2. Eén knop licht groen op — druk zo snel mogelijk
3. Correct → witte flash op knop, groen op strip, success sound
4. Fout/timeout → rode flash, fail sound
5. Na N rondes → rainbow + eindstand

### States
```
arming → wait_random → show_target → [success | fail] → (herhaal) → done
```

### Visuele feedback knoppen
| Moment | Knop die oplicht | Alle andere knoppen |
|--------|-----------------|---------------------|
| Wachten | — | Dim blauw |
| Target | Helder groen | Dim blauw |
| Success | Wit flash (4x) | Kort groen |
| Fail/timeout | Rood flash | Rood flash |

### Config parameters
| Parameter | Default | Beschrijving |
|-----------|---------|--------------|
| `rounds` | 5 | Aantal rondes |
| `reaction_timeout_s` | 2.0 | Tijd om te drukken (s) |
| `min_delay_s` | 1.5 | Minimale wachttijd voor target |
| `max_delay_s` | 4.0 | Maximale wachttijd voor target |
| `celebration_s` | 4.0 | Duur rainbow animatie na einde |

### Min. knoppen
2 (maar leuker met meer)

---

## Game 2 — Memory

### Concept
De Pi toont een reeks oplichtende knoppen. De speler herhaalt de reeks in dezelfde volgorde. Elke ronde wordt de reeks één stap langer.

### Spelverloop
1. Ronde 1: Pi licht 1 knop op (bijv. knop 03)
2. Speler drukt op knop 03 → correct
3. Ronde 2: Pi licht 03 → 05 op (2 knoppen in volgorde)
4. Speler drukt 03 → 05 → correct
5. Fout op een knop → rood flash, spel stopt, eindstand
6. Spel eindigt na N correcte rondes of bij fout

### States
```
arming → show_sequence (één knop per keer tonen) → player_turn → 
  [next_in_sequence correct → volgende] | [wrong → fail → done]
→ sequence_done → (volgende ronde, reeks +1) → done
```

### Interne state
```python
sequence: list[str]        # bv. ["03", "05", "01", "03"]
player_input: list[str]    # wat speler tot nu toe heeft gedrukt
current_step: int          # welke positie in de reeks we verwachten
```

### Visuele feedback knoppen
| Moment | Knop | Strip |
|--------|------|-------|
| Sequence tonen | Knop licht op (500ms aan, 200ms uit) | Kleur van huidige knop |
| Wacht op input | Alle knoppen dim wit | Idle |
| Correcte druk | Kort groen flash | Groen pulse |
| Verkeerde druk | Alle rood flash | Rood |
| Ronde gewonnen | Alle knoppen groen flash | Rainbow kort |

### Config parameters
| Parameter | Default | Beschrijving |
|-----------|---------|--------------|
| `start_length` | 1 | Beginlengte van de reeks |
| `max_length` | 10 | Maximale reekslengte voor winnaar |
| `show_interval_ms` | 600 | Hoe lang elke knop oplicht bij tonen |
| `input_timeout_s` | 5.0 | Tijd per druk tijdens input fase |

### Min. knoppen
3 (meer = moeilijker want minder herhaling van dezelfde knop)

---

## Game 3 — Battle (1 vs 1)

### Concept
Twee spelers kiezen elk een knop. De Pi licht willekeurig één van de twee op. Wie het snelst zijn eigen knop indrukt wint het punt. Eerste speler met X punten wint.

### Spelverloop
1. Speler 1 kiest knop A, speler 2 kiest knop B (via frontend of eerste druk registreren)
2. Beide knoppen pulseren zacht — klaar staan
3. Pi kiest willekeurig knop A of B en laat die oplichten
4. Juiste speler drukt → punt, knop wit flash
5. Verkeerde speler drukt → punt verlies of neutrale fail
6. Eerste bij X punten wint → grote eindanimatie

### States
```
setup (knoppen registreren) → arming → wait_random → show_target →
  [correct_player → score → next] | [wrong_player → penalty → next] → done
```

### Interne state
```python
player1_btn: str           # bv. "01"
player2_btn: str           # bv. "04"
score_p1: int
score_p2: int
target_btn: str | None     # welke speler moet drukken
```

### Visuele feedback knoppen
| Moment | Speler 1 knop | Speler 2 knop | Andere knoppen |
|--------|--------------|--------------|----------------|
| Setup | Blauw pulse | Blauw pulse | Uit |
| Wachten | Dim blauw | Dim blauw | Uit |
| Target P1 | Helder groen | Dim blauw | Uit |
| Target P2 | Dim blauw | Helder groen | Uit |
| P1 wint punt | Wit flash | Rood | Uit |
| P2 wint punt | Rood | Wit flash | Uit |
| Winnaar | Rainbow flash | Rainbow flash | Uit |

### Strip feedback
| Moment | Strip |
|--------|-------|
| Wachten | Half blauw (P1 kant) / half rood (P2 kant) |
| P1 target | Groen pulse |
| P2 target | Groen pulse |
| P1 wint ronde | Linkerhelft groen flash |
| P2 wint ronde | Rechterhelft groen flash |
| Eindwinnaar | Rainbow |

### Config parameters
| Parameter | Default | Beschrijving |
|-----------|---------|--------------|
| `points_to_win` | 5 | Punten nodig om te winnen |
| `reaction_timeout_s` | 2.5 | Tijd om te drukken |
| `min_delay_s` | 1.0 | Min wachttijd |
| `max_delay_s` | 3.5 | Max wachttijd |
| `penalty_wrong_press` | true | Verliest de verkeerde speler een punt? |

### Min. knoppen
Exact 2 (de twee spelers), maar werkt ook als de andere 4 knoppen gewoon genegeerd worden

---

## Vergelijkingstabel

| | Reaction | Memory | Battle |
|---|---------|--------|--------|
| Sleutel (`key`) | `reaction` | `memory` | `battle` |
| Min. knoppen | 2 | 3 | 2 |
| Spelers | 1+ | 1 | 2 |
| Moeilijkheid | Laag–Midden | Midden–Hoog | Laag |
| Willekeur | Hoog | Laag (geheugen) | Hoog |
| Speelduur | ~2 min | ~5 min | ~3 min |
| Uniek element | Snelheid | Geheugen | Competitie |

---

## Gedeelde technische structuur

Elke game implementeert `GameBase`:

```python
class MemoryGame(GameBase):
    key = "memory"

    def __init__(self, mqtt, audio, registry, ledstrip, on_finished, cfg=None):
        ...

    async def start(self, params: dict) -> None: ...
    async def stop(self) -> None: ...
    async def on_button_pressed(self, btn_id: str) -> None: ...
    def status(self) -> dict: ...
```

Registreren in `app_factory.py`:
```python
memory = MemoryGame(mqtt=mqtt, audio=audio, registry=registry,
                    ledstrip=ledstrip, on_finished=on_finished_memory)
engine.register("memory", memory)

battle = BattleGame(mqtt=mqtt, audio=audio, registry=registry,
                    ledstrip=ledstrip, on_finished=on_finished_battle)
engine.register("battle", battle)
```

---

## Geluiden per game

| Event | Sound |
|-------|-------|
| Correct druk | `success` |
| Fout / timeout | `fail` |
| Einde spel (winnaar) | `sea_shanty_2` |
| Sequence tonen Memory | *(optioneel: korte toon per knop)* |

> Nieuwe sounds kunnen toegevoegd worden door `.wav` / `.ogg` / `.mp3` bestanden in `backend/mona/audio/sfx/` te plaatsen. Ze worden automatisch geladen bij opstart.
