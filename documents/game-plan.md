# Game Plan — The Mona

## Overzicht

De app krijgt een **centrale game hub**: één pagina waar je een spel kiest, de vereisten checkt, het spel configureert en start. Elke game heeft een eigen **help/uitleg pagina**. Tijdens het spel is er een **live status scherm** met duidelijke visuele feedback.

---

## Pagina-structuur (nieuw)

```
/               → Home / overzicht (bestaand, uitbreiden)
/play           → Game hub (NIEUW) — kies spel, check requirements, start
/play/reaction  → Reaction game scherm (NIEUW, vervangt /game)
/play/[game]    → Uitbreidbaar voor toekomstige games
```

---

## Pagina 1 — `/play` Game Hub

### Wat het doet
- Toont alle beschikbare games (opgehaald via `GET /api/v1/game/games`)
- Per game: naam, beschrijving, benodigde knoppen, moeilijkheidsgraad
- **Requirements checker**: toont live hoeveel knoppen online zijn vs. hoeveel nodig
- Als requirements OK → Start knop actief
- Als requirements niet OK → Start knop disabled met uitleg
- Link naar help/uitleg pagina per game
- Instellingen per game (rondes, timing, ...)

### Requirements checker
```
Reaction Game
✅ Minimaal 2 knoppen online   [4 / 2 online]
✅ Audio beschikbaar           [JBL verbonden]
✅ LED strip beschikbaar       [20 LEDs]
──────────────────────────────
[? Uitleg]   [▶ Starten]
```

### UI flow
```
Kies spel → Check requirements → Configureer → Start → Redirect naar /play/reaction
```

---

## Pagina 2 — `/play/reaction` Game Scherm

### Wat het toont
- **Grote visuele status** (centraal, niet alleen tekst):
  - Wachten → pulserende animatie
  - Druk! → grote groene indicator + knop ID
  - Goed! → groen flash effect
  - Fout! → rood flash effect
  - Klaar → score overzicht
- Score: goed / fout / totaal rondes
- Ronde indicator
- Live online knoppen (welke actief zijn)
- Stop knop
- Terug naar hub knop (alleen als niet bezig)

### Visuele feedback states
| State | UI kleur | Tekst | LED strip |
|-------|----------|-------|-----------|
| `arming` | Geel | "Klaar maken..." | Wit pulse |
| `wait_random` | Blauw | "Wacht..." | Idle blauw |
| `show_target` | Groen knipperend | "DRUK!" + knop ID | Groen pulse |
| `success` | Groen flash | "Goed! ✓" | Success groen |
| `fail` | Rood flash | "Fout! ✗" | Fail rood |
| `done` | Paars/rainbow | Score overzicht | Rainbow |

---

## Pagina 3 — Help per game (modal of aparte pagina)

### Reaction game uitleg
- **Doel**: druk zo snel mogelijk op de oplichtende knop
- **Regels**:
  - Wacht tot een knop oplicht — druk dan zo snel mogelijk
  - Te vroeg drukken = fout (false start)
  - Verkeerde knop = fout
  - Niet op tijd = fout (timeout)
- **Score**: goed/fout per ronde, eindtotaal
- **Instellingen uitleg**: wat doet elke parameter

---

## Technische requirements per game

### Reaction Game
| Requirement | Minimum | Aanbevolen |
|-------------|---------|------------|
| Online knoppen | 2 | 4–6 |
| Audio | optioneel | JBL verbonden |
| LED strip | optioneel | aanwezig |

---

## Backend aanpassingen nodig

### 1. `game.ts` API — game naam meesturen bij start
De huidige `gameApi.start()` stuurt geen `game` veld mee maar de backend verwacht `GameStartIn { game: str, params: ... }`.

**Fix:**
```typescript
start(game: string, params?: { ... }) {
  return apiPost("/api/v1/game/start", { game, params });
}
```

### 2. Engine status uitbreiden
`GET /api/v1/game/status` geeft nu alleen de actieve game terug. Voor de hub is ook nuttig:
- Welke game actief is
- Of er een game bezig is (running: bool)

Dit zit er al in via `engine.status()` — gewoon gebruiken.

### 3. Requirements endpoint (optioneel maar handig)
`GET /api/v1/game/requirements/{game}` die teruggeeft:
```json
{
  "buttons_needed": 2,
  "buttons_online": 4,
  "audio_ready": true,
  "ledstrip_ready": true,
  "can_start": true
}
```

---

## Frontend aanpassingen nodig

### game.ts API
```typescript
start(game: string, params?: {
  rounds?: number;
  reaction_timeout_s?: number;
  min_delay_s?: number;
  max_delay_s?: number;
}) {
  return apiPost("/api/v1/game/start", { game, params: params ?? {} });
}
```

### Nieuwe pagina's
- `/play` — game hub
- `/play/reaction` — game scherm (huidige `/game` verplaatsen + uitbreiden)

### Navigatie
- `Game → Spelen` → `/play` (was `/game`)
- `/play` heeft links naar individuele game pagina's

---

## Tweede game idee — Memory

Idee voor een tweede game die goed past bij de hardware:

**Concept**: de Pi licht knoppen op in een volgorde, de speler herhaalt die volgorde.

| Aspect | Detail |
|--------|--------|
| Naam | `memory` |
| Min knoppen | 3 |
| Moeilijkheid | Neemt toe per ronde (langere reeks) |
| State machine | `show_sequence` → `player_turn` → `success` / `fail` |
| Visuele feedback | Strip toont kleur van huidige knop in reeks |

GameBase implementatie is dezelfde structuur als ReactionGame — `start()`, `stop()`, `on_button_pressed()`, `status()`.

---

## Taakverdeling morgen

### Backend (prioriteit 1)
- [ ] `game.ts` API fix: `game` veld meesturen bij start
- [ ] Requirements endpoint `GET /api/v1/game/requirements/{game}`
- [ ] Memory game `backend/mona/engine/games/memory.py` + registreren in `app_factory.py`

### Frontend (prioriteit 2)
- [ ] `/play` hub pagina met requirements checker
- [ ] `/play/reaction` game scherm met grote visuele feedback
- [ ] Help modal per game
- [ ] Navigatie aanpassen

### Testen
- [ ] Reaction game end-to-end met echte knoppen
- [ ] False start detectie
- [ ] Timeout detectie
- [ ] Eindanimatie (rainbow + sound)
- [ ] Memory game basis flow

---

## Volgorde van aanpak morgen

1. Fix `gameApi.start()` — anders start geen enkel spel correct
2. Requirements endpoint bouwen
3. `/play` hub pagina
4. `/play/reaction` scherm
5. Testen met knoppen
6. Memory game (als tijd over)
