#!/usr/bin/env python3
"""
Generates a fully actionable weekly Instagram content strategy for PNBS Campus.

Produces:
  - 5-post weekly content calendar (optimal days Mon–Fri)
  - Per post: ready-to-publish caption (FR), visual guidelines, shot list / carousel structure
  - Weekly summary table + hashtag rotation groups

Input:  .tmp/analysis/competitor_analysis_{date}.json  (latest, auto-detected)
Output: .tmp/strategy/weekly_strategy_{YYYY-MM-DD}.md

Usage:
    python execution/generate_strategy.py
    python execution/generate_strategy.py --input .tmp/analysis/competitor_analysis_2026-04-14.json
"""

import os
import json
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

OUTPUT_DIR = Path(".tmp/strategy")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Brand context — loaded from directives/pnbs_brand.md (single source of truth)
# ---------------------------------------------------------------------------

BRAND_FILE = Path("directives/pnbs_brand.md")


def load_brand_context() -> str:
    """
    Load PNBS brand facts from directives/pnbs_brand.md.
    This file is the single source of truth — the strategy prompt is built around it.
    Raises FileNotFoundError with a clear message if the file is missing.
    """
    if not BRAND_FILE.exists():
        raise FileNotFoundError(
            f"Brand reference file not found: {BRAND_FILE}\n"
            "Create it at directives/pnbs_brand.md before running the pipeline."
        )
    content = BRAND_FILE.read_text(encoding="utf-8")
    logger.info(f"Loaded brand context from {BRAND_FILE} ({len(content)} chars)")
    return content


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def get_latest_analysis_file() -> Path:
    files = sorted(OUTPUT_DIR.parent.glob("analysis/competitor_analysis_*.json"), reverse=True)
    # Also check relative path
    alt = sorted(Path(".tmp/analysis").glob("competitor_analysis_*.json"), reverse=True)
    candidates = files or alt
    if not candidates:
        raise FileNotFoundError(
            "No analysis file found in .tmp/analysis/. Run analyze_competitors.py first."
        )
    return candidates[0]


def get_next_week_dates() -> list[datetime]:
    """Return Mon–Sun dates for the upcoming week."""
    today = datetime.now()
    days_until_monday = (7 - today.weekday()) % 7 or 7
    monday = today + timedelta(days=days_until_monday)
    return [monday + timedelta(days=i) for i in range(7)]


# ---------------------------------------------------------------------------
# Strategy prompt
# ---------------------------------------------------------------------------

STRATEGY_PROMPT = """You are the lead social media strategist for PNBS — Paris Nord Business School (@pnbs.officiel).

## ⚠️ BRAND GUARDRAILS — READ FIRST, ENFORCE STRICTLY
The following is the ONLY authoritative reference for PNBS programs, campuses, and brand facts.
You MUST NOT invent, suggest, or reference any program, campus, format, or service not listed here.
If a competitor does something that doesn't exist at PNBS (e.g. digital marketing program, campus life, online-only), DO NOT suggest it.

{brand_context}

---

## Competitor Analysis Insights (use to inform FORMAT and TONE only — not program ideas)
{analysis}

---

## YOUR TASK
Generate a complete, execution-ready weekly Instagram content strategy for the week of {week_range}.

### Non-negotiable rules
1. Exactly **5 posts** — pick the 5 best days based on competitor posting pattern data.
2. Every caption must be **100% in French**, ready to copy-paste — no placeholders, no "[insert name]".
3. Always use "tu" (not "vous") in captions — PNBS speaks like a friend, not an institution.
4. Visual guidelines = **zero guesswork** for the content creator. If it's a reel, every scene is described. If it's a carousel, every slide is written out.
5. Every post must connect to at least one of PNBS's content pillars AND reference a real PNBS selling point.
6. Only mention programs that exist in the brand file: TP Conseiller Commercial, BTS NDRC, BTS MCO, TP NTC, Bachelor REM, Master MBU.
7. Only mention campuses that exist in the brand file. Never suggest relocation content.
8. Vary the formats: at least 1 reel, at least 2 carousels, max 1 single image.
9. At least 1 post must feature a student testimonial angle (real or scripted-realistic).
10. At least 1 post must directly address the "0€ frais + être payé" angle.
11. Salary figures must match the brand file: 492€ to 1 823€/month. Never use other numbers.
12. No vague ideas. No "add a motivating quote here". Everything is written out.

### Posting days available: {posting_days}

---

## CONTENT IDEAS BANK — draw from these for this week (pick 5, don't repeat)

### HIGH-ENGAGEMENT FORMATS (inspired by competitor best practices)
- **"Combien je gagne en alternance chez [entreprise] ?"** → Reel ou carousel. Un vrai étudiant (ou persona réaliste) révèle son salaire mensuel, ses missions, sa journée type. Hook ultra-fort.
- **"BTS vs Bachelor vs Master — lequel choisir ?"** → Carousel comparatif. Slide 1: question provocatrice. Slides 2-4: comparaison concrète (durée, salaire, débouchés). Slide finale: CTA vers lien en bio.
- **"Pourquoi j'ai choisi l'alternance plutôt que la fac"** → Reel témoignage. Vrai étudiant (ou format "POV"). Authentique, pas trop produit. Sous-titres obligatoires.
- **"0€ de frais de scolarité : comment c'est possible ?"** → Carousel éducatif. Explique le modèle alternance, le financement OPCO, le salaire. Démystifie une idée reçue.
- **"Les 5 métiers les mieux payés après un BTS commerce"** → Carousel. Hook chiffré. Données concrètes (salaires, entreprises qui recrutent). Très "saveable".
- **"Journée type d'un alternant chez Monoprix / Euromaster / [partenaire]"** → Reel. Format vlog rapide (15-30s). Montre la vraie vie en entreprise.
- **"Tu peux candidater même avec un bac pro ✅"** → Post single image ou reel court. Casse l'idée reçue. Hook fort, message inclusif.
- **"Offre d'alternance dispo cette semaine 🔥"** → Single image ou carousel. Présente 3-5 offres réelles de la semaine. Très fort pour conversions.
- **"Comment trouver ton entreprise d'alternance en 30 jours"** → Carousel tutoriel. 6-8 slides avec étapes concrètes. Très "saveable".
- **"PNBS en chiffres"** → Infographie carousel ou single image. 85% réussite, 0€ frais, 775€-1802€/mois, 300 partenaires, 10 campus.

---

For each of the 5 posts, use EXACTLY this structure:

---
## POST [N] — [WEEKDAY, DD Month]

### Overview
| Champ | Valeur |
|-------|--------|
| Format | reel / carousel / single image |
| Pilier de contenu | (Alternance & Argent / Programmes / Témoignages / Entreprises partenaires / Vie PNBS) |
| Objectif | engagement / notoriété / conversion / communauté |
| Reach potentiel | faible / moyen / élevé |
| Recyclable chaque semaine ? | oui / non |

### Pourquoi ce format cette semaine
[1-2 phrases basées sur les données concurrents. Ex: "Les carousels 'comparatif' atteignent X% d'engagement chez ISCOD et Studi — format très 'saveable' par les lycéens en phase de recherche d'école."]

### Caption complète
```
[Ligne d'accroche (hook) — max 10 mots, créée pour stopper le scroll]

[Corps du texte — 3 à 5 phrases courtes, ton ami/mentor, concret, chiffres si possible]

[Appel à l'action — une phrase directe. Ex: "👉 Lien en bio pour candidater.", "💬 Dis-moi en commentaire : tu es en quelle terminale ?", "🔖 Enregistre ce post pour y revenir."]

[Saut de ligne]

#alternance #BTS #bachelor #écoledebusiness #étudiant #formationalternance #PNBS #ParisBusiness #apprendreetêtrepayé #zérofrais #vieetudiante #jobétudiant #comercial #management #recrutement #orientation #postbac #BTScommerce #BTS2025 #bachelor2025 #alternance2025 #formaemploi #saintdenis #ilsontditouiàlalternance #pnbsofficiel
```

### Analyse du hook
- **Ligne d'accroche**: [répéter la première ligne de la caption]
- **Pourquoi ça stoppe le scroll**: [1 phrase d'explication]
- **Variante A/B possible**: [1 alternative à tester]

### Directives visuelles
- **Concept**: [Ce que montre le visuel — 2-3 phrases très précises]
- **Format**: [ex: 4:5 portrait, 1:1 carré, 9:16 vertical pour reel]
- **Palette de couleurs**: [ex: fond bleu marine #1A2C5B, texte blanc #FFFFFF, accent orange #F28C28]
- **Texte à superposer** (overlay exact): [Texte mot pour mot, placement, style de police]
- **Style / Ambiance**: [ex: "Photo réelle d'un étudiant en entreprise, lumière naturelle, sourire naturel — PAS de stock photo"]
- **À faire**: [2-3 règles visuelles spécifiques]
- **À éviter**: [1-2 interdits visuels]

### Plan de tournage *(reels uniquement — supprimer si autre format)*
| Scène | Durée | Description | Son / Musique |
|-------|-------|-------------|---------------|
| 1 | Xs | [action précise, cadrage, lieu] | [son ou voix off] |
| 2 | Xs | | |
| ... | | | |
| **Total** | **Xs** | | |
- **Sous-titres**: Oui obligatoire (texte blanc, fond semi-transparent)
- **Ratio**: 9:16 vertical
- **Durée cible**: [X secondes]

### Structure du carousel *(carousels uniquement — supprimer si autre format)*
| Slide | Rôle | Titre / Texte principal | Visuel | CTA |
|-------|------|------------------------|--------|-----|
| 1 | Hook | [Texte exact de la slide d'accroche] | [description visuelle] | — |
| 2 | Contenu | | | — |
| 3 | Contenu | | | — |
| ... | | | | |
| Dernière | CTA | "👉 Lien en bio" / "🔖 Enregistre" | [visuel PNBS branding] | Oui |
- **Nombre de slides recommandé**: [X]
- **Police**: [Bold sans-serif, ex: Montserrat Bold]
- **Arrière-plan**: [description]

---

After all 5 posts, add:

---
## RÉCAPITULATIF DE LA SEMAINE

| Jour | Format | Pilier | Objectif | Reach potentiel |
|------|--------|--------|----------|-----------------|
[table complète]

---
## NOTES DE STRATÉGIE

### Groupes de hashtags à rotation (alterner chaque semaine)
- **Groupe A — École & formation**: #PNBS #ParisBusiness #ParisnordBusinessSchool #BTS #bachelor #master #écoledebusiness #formationcommerciale #écoledeconseil
- **Groupe B — Alternance & emploi**: #alternance #apprendreetêtrepayé #contratdapprentissage #contratdeprofessionnalisation #trouveruneentreprise #alternance2025 #alternance2026 #recrutement #emploi
- **Groupe C — Vie étudiante & orientation**: #étudiant #vieetudiante #postbac #orientation #lycéen #terminale #rentréescolaire #BTScommerce #BTSMCO #BTSNDRC
- **Groupe D — Reach large**: #business #entrepreneur #marketing #management #commercial #réussite #motivation #travail #carrière #jeunesse
*Combiner toujours 2-3 groupes. Toujours inclure #PNBS et #alternance.*

### Stories à publier le même jour (pour amplifier chaque post)
[Pour chaque post : 1 phrase décrivant le contenu Story à publier le même jour]

### Tactiques d'engagement pour cette semaine
[4-6 actions concrètes : questions en caption, stickers de sondage en story, réponses aux commentaires, repost en story, collaboration avec un étudiant ambassadeur, etc.]

### Post à réutiliser / recycler
[Lequel des 5 posts peut être reposté dans 4 semaines avec une légère modification, et comment ?]

---

Toutes les captions, overlays et textes face aux étudiants sont en FRANÇAIS.
Les en-têtes stratégiques (section titles) restent en français également pour faciliter l'usage par l'équipe PNBS.
"""


# ---------------------------------------------------------------------------
# Claude generation
# ---------------------------------------------------------------------------

def generate_strategy(client: anthropic.Anthropic, analysis: dict) -> str:
    # Load brand context from file — mandatory, will raise if missing
    brand_context = load_brand_context()

    week_dates = get_next_week_dates()
    week_range = f"{week_dates[0].strftime('%B %d')} – {week_dates[6].strftime('%B %d, %Y')}"
    posting_days = ", ".join(
        d.strftime("%A %d %B") for d in week_dates[:5]  # Mon–Fri
    )

    prompt = STRATEGY_PROMPT.format(
        brand_context=brand_context,
        analysis=json.dumps(analysis, ensure_ascii=False, indent=2),
        week_range=week_range,
        posting_days=posting_days,
    )

    logger.info("Generating weekly content strategy with Claude...")
    response = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main(input_file: str | None = None) -> str:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    if input_file is None:
        input_file = get_latest_analysis_file()
    else:
        input_file = Path(input_file)

    logger.info(f"Loading analysis from: {input_file}")
    with open(input_file, "r", encoding="utf-8") as f:
        analysis = json.load(f)

    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not api_key:
        raise ValueError("ANTHROPIC_API_KEY is not set in .env")

    client = anthropic.Anthropic(api_key=api_key)
    strategy_text = generate_strategy(client, analysis)

    today = datetime.now().strftime("%Y-%m-%d")
    output_file = OUTPUT_DIR / f"weekly_strategy_{today}.md"

    header = (
        f"# PNBS Campus — Weekly Instagram Strategy\n"
        f"**Generated**: {datetime.now().strftime('%Y-%m-%d at %H:%M')}\n\n"
        f"---\n\n"
    )

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(header + strategy_text)

    logger.info(f"Strategy saved to: {output_file}")
    return str(output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate weekly Instagram strategy for PNBS Campus.")
    parser.add_argument("--input", help="Path to analysis JSON (default: latest in .tmp/analysis/)")
    args = parser.parse_args()
    main(args.input)
