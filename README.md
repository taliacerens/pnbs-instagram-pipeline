# 📱 PNBS Instagram Strategy Pipeline

> **An agentic AI workflow** that monitors 6 competitor French business school Instagram accounts weekly, extracts content patterns, and auto-generates a fully production-ready content calendar for PNBS Campus — complete with French captions, visual guidelines, reel shot lists, and carousel structures.

Built with Claude (Anthropic) + Python. Runs every Monday at 08:00.

---

## 🎯 What It Does

Every week, this pipeline:

1. **Scrapes** the last 20 posts from 6 competitor Instagram accounts
2. **Analyzes** content types, engagement rates, posting patterns, and hashtag strategies using Claude
3. **Generates** a 5-post weekly content calendar tailored to PNBS's brand — captions in French, ready to copy-paste

The output is a `.md` file you open Monday morning and hand directly to your content team.

---

## 📋 Example Output

Here's what the pipeline generates every Monday:

---

### POST 1 — Lundi, 20 Avril

| Champ | Valeur |
|-------|--------|
| Format | Carousel (6 slides) |
| Pilier | Alternance & Argent |
| Objectif | Engagement + Conversion |
| Reach potentiel | Élevé |

**Caption complète :**
```
Tu sais combien tu gagnes en BTS en alternance chez PNBS ? 👇

En première année : entre 492€ et 759€ par mois.
En deuxième année : jusqu'à 1 823€ selon ton âge.
Et tout ça, sans payer un centime de frais de scolarité.

Chez nous, tu apprends ET tu gagnes ta vie dès le premier mois.

👉 Clique sur le lien en bio pour candidater — la prochaine rentrée c'est dans 3 semaines.

#alternance #BTS #BTSMCO #BTSNDRC #PNBS #apprendreetêtrepayé #zérofrais
#formationalternance #étudiant #postbac #orientation #BTScommerce #alternance2025
```

**Structure Carousel :**
| Slide | Contenu |
|-------|---------|
| 1 (Hook) | "T'as déjà été payé pour apprendre ?" — fond bleu marine, texte blanc bold |
| 2 | Salaires BTS 1ère année selon l'âge (tableau visuel) |
| 3 | Salaires BTS 2ème année selon l'âge |
| 4 | "0€ de frais d'inscription — financé par ton entreprise et l'État" |
| 5 | Témoignage court : "Théo, 19 ans, BTS MCO chez Monoprix : 1 100€/mois" |
| 6 (CTA) | "Rentrée ce mois-ci — Lien en bio 👉" + logo PNBS |

---

### POST 2 — Mardi, 21 Avril

| Champ | Valeur |
|-------|--------|
| Format | Reel (25 secondes) |
| Pilier | Témoignages étudiants |
| Objectif | Notoriété + Communauté |

**Caption complète :**
```
De terminale pro à 1 400€/mois en entreprise à 18 ans 🔥

Sarah avait pas prévu de faire des études longues.
Aujourd'hui elle manage une équipe en alternance chez Franprix et passe son Bachelor REM.

C'est ça, l'alternance chez PNBS.

💬 Dis-moi en commentaire : t'es en quelle terminale ?

#alternance #PNBS #témoignage #bachelor #vieetudiante #réussite #jeunesse #étudiant
```

**Plan de tournage :**
| Scène | Durée | Description |
|-------|-------|-------------|
| 1 | 3s | Gros plan visage souriant, texte overlay : "1 400€/mois à 18 ans" |
| 2 | 5s | Étudiant en rayon / en réunion avec responsable |
| 3 | 7s | Interview face caméra : "Ce que j'ai appris en 6 mois..." |
| 4 | 5s | Téléphone montrant virement bancaire (flou sur montant) |
| 5 | 5s | CTA : "Ton tour → lien en bio", logo PNBS |

---

### [+ 3 autres posts : Mercredi, Jeudi, Vendredi]

---

## 🏗️ Architecture

The pipeline follows a **3-layer agentic architecture** that separates intent, decision-making, and execution:

```
┌─────────────────────────────────────────────────────────┐
│  LAYER 1 — DIRECTIVES  (What to do)                     │
│  directives/                                            │
│  ├── instagram_competitor_analysis.md  ← Main SOP      │
│  └── pnbs_brand.md  ← Brand guardrails (single truth)  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  LAYER 2 — ORCHESTRATION  (Claude Code / Claude)        │
│  Reads directives → decides order → handles errors      │
│  → updates directives with learnings (self-annealing)   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│  LAYER 3 — EXECUTION  (Deterministic Python)            │
│  execution/                                             │
│  ├── run_pipeline.py         ← Master orchestrator     │
│  ├── scrape_instagram.py     ← Step 1: Collect data    │
│  ├── analyze_competitors.py  ← Step 2: Claude analysis │
│  └── generate_strategy.py   ← Step 3: Claude strategy  │
└─────────────────────────────────────────────────────────┘
```

**Why this works:** Instead of letting the LLM do everything (and compounding errors), business logic lives in deterministic Python. The LLM focuses on what it's actually good at: pattern recognition and creative generation.

---

## 🔄 Pipeline Flow

```
Every Monday 08:00
       │
       ▼
[1/3] scrape_instagram.py
  └─ instaloader fetches last 20 posts/account
  └─ Output: .tmp/scraped/competitor_posts_{date}.json
       │
       ▼
[2/3] analyze_competitors.py
  └─ Claude analyzes: content types, engagement rates,
     posting patterns, hashtag clusters, tone
  └─ Output: .tmp/analysis/competitor_analysis_{date}.json
       │
       ▼
[3/3] generate_strategy.py
  └─ Claude generates: 5-post calendar, FR captions,
     visual guidelines, reel shot lists, carousel structures
  └─ Reads directives/pnbs_brand.md as hard guardrails
  └─ Output: .tmp/strategy/weekly_strategy_{date}.md
       │
       ▼
  📄 Open weekly_strategy_{date}.md
  → Hand to content team → Post on Instagram
```

---

## 🏢 Brand Context

PNBS — Paris Nord Business School is a 100% work-study (*alternance*) business school:

| | |
|--|--|
| **Model** | 100% alternance, Bac → Bac+5 |
| **Key pitch** | 0€ tuition, students earn 492€–1,823€/month |
| **Programs** | BTS MCO, BTS NDRC, TP NTC, Bachelor REM, Master MBU |
| **Campuses** | Paris, Marseille, Lille, Lyon, Toulouse, Bordeaux, Metz, Rouen, Montpellier, Aix, Amiens |
| **Target** | 16–26 year-olds, post-Bac, wanting a paid work-study path |

The `directives/pnbs_brand.md` file acts as a **hard guardrail** injected into every Claude prompt. The AI cannot suggest programs, campuses, or content angles that don't exist at PNBS.

---

## 🧬 Self-Annealing Design

When something breaks, the system fixes itself:

```
Error occurs
    │
    ▼
Read stack trace → fix the script
    │
    ▼
Test the fix
    │
    ▼
Update directive with what was learned
    │
    ▼
System is now stronger for next run
```

**Real example from this build:** Claude's JSON was getting truncated at 4,096 tokens for 6-account datasets → the `_repair_truncated_json()` function was added to `analyze_competitors.py`, `max_tokens` raised to 8,192, and the fix was documented in `directives/instagram_competitor_analysis.md` under `Known Issues`.

---

## ⚙️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/YOUR_USERNAME/pnbs-instagram-pipeline.git
cd pnbs-instagram-pipeline
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure environment

```bash
cp .env.example .env
```

Edit `.env`:

```env
ANTHROPIC_API_KEY=sk-ant-...       # Required — console.anthropic.com
INSTAGRAM_USERNAME=your_dummy_acc  # Optional — dedicated scraping account
INSTAGRAM_PASSWORD=your_password   # Optional — never use your main account
```

> ⚠️ **Instagram note:** Instagram aggressively blocks instaloader as of 2025. If scraping fails, the pipeline still runs — Claude will analyze with whatever data is available. See Known Issues below.

### 4. Run

```bash
python execution/run_pipeline.py
```

**Flags:**

```bash
# Reuse today's scrape (skip step 1)
python execution/run_pipeline.py --skip-scrape

# Regenerate strategy only (skip steps 1 + 2)
python execution/run_pipeline.py --skip-scrape --skip-analysis
```

### 5. Schedule (Windows Task Scheduler)

Run every Monday at 08:00:

```
Program: python
Arguments: execution/run_pipeline.py
Start in: C:\path\to\your\project
Trigger: Weekly, Monday, 08:00
```

---

## 📁 Project Structure

```
pnbs-instagram-pipeline/
│
├── directives/                         # Layer 1 — What to do (SOPs)
│   ├── instagram_competitor_analysis.md  # Main pipeline directive
│   └── pnbs_brand.md                     # Brand facts & guardrails
│
├── execution/                          # Layer 3 — Deterministic scripts
│   ├── run_pipeline.py                   # Master orchestrator
│   ├── scrape_instagram.py               # Step 1: Instagram scraper
│   ├── analyze_competitors.py            # Step 2: Claude analysis
│   └── generate_strategy.py              # Step 3: Strategy generator
│
├── .tmp/                               # Generated files (gitignored)
│   ├── scraped/                          # Raw competitor post data
│   ├── analysis/                         # Claude's competitor analysis
│   └── strategy/                         # Weekly content calendars ← deliverable
│
├── .env.example                        # Environment template
├── .gitignore
├── requirements.txt
└── CLAUDE.md                           # Agent instructions (also: AGENTS.md)
```

---

## 🔧 Competitor Accounts Monitored

| Account | Type | Why |
|---------|------|-----|
| `@ecole_studi` | Large online school | Benchmark for polished content |
| `@iscod.fr` | 100% online + alternance | Closest competitor model |
| `@digitalcollege` | 14 campuses, 87% alternance | Strong reel presence |
| `@isefac.national` | Events & communication | Testimonial content leader |
| `@nuevo_cfa` | Multi-sector CFA | Diverse format mix |
| `@campus_des_ecoles` | Multi-campus network | Community-building tactics |

---

## 🐛 Known Issues

### Instagram Scraping Blocked
Instagram blocks `instaloader` as of late 2024–2025 for most public accounts. The pipeline handles this gracefully: it saves an empty dataset and proceeds to steps 2 and 3 using brand context alone. 

**Workaround options:**
- Use `Apify Instagram Scraper` (~$0.50/1000 posts) — update `scrape_instagram.py` with `APIFY_API_KEY`
- Use `PhantomBuster` for GUI-based scraping

### Claude JSON Truncation
Fixed 2026-04-14. Claude responses hitting `max_tokens` are auto-repaired via `_repair_truncated_json()` in `analyze_competitors.py`.

---

## 💡 Adapting for Your School

1. Update `directives/pnbs_brand.md` with your school's programs, campuses, and brand tone
2. Update `COMPETITOR_ACCOUNTS` in `scrape_instagram.py`
3. Adjust content pillars in `generate_strategy.py`'s `STRATEGY_PROMPT`

The directive-first architecture means you can change the entire content strategy by editing one Markdown file — no code changes needed.

---

## 🛠️ Tech Stack

| Tool | Role |
|------|------|
| `Claude claude-opus-4-6` | Competitor analysis + strategy generation |
| `instaloader` | Instagram scraping |
| `python-dotenv` | Environment management |
| `anthropic` Python SDK | Claude API client |

---

## 📄 License

MIT — feel free to fork and adapt for your institution.

---

*Built by [@talihasahin](https://github.com/talihasahin) for PNBS Campus social media team.*
