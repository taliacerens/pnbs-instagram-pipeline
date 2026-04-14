# Directive: Weekly Instagram Competitor Analysis & Content Strategy

## Objective
Analyze 6 competitor French business school Instagram accounts weekly, identify top-performing content patterns, and generate a fully actionable weekly content calendar + creation guides for PNBS Campus.

## Brand Context — PNBS (Paris Nord Business School)
- **Full name**: PNBS — Paris Nord Business School
- **Instagram**: @pnbs.officiel
- **Website**: https://www.pnbs.fr/
- **Tagline**: "La Business School pour tous"
- **Type**: CFA (Centre de Formation d'Apprentis) — 100% alternance, no initial track
- **Target audience**: 18-25 ans, post-Bac (général/pro/techno), cherchant une formation PAYÉE en commerce/business. Secondary: parents, personnes en reconversion.
- **Tone**: Motivant, direct, humain — parle comme un ami ("tu"), jamais institutionnel
- **Language**: French for ALL student-facing content

### Programs (Bac+2 to Bac+5, all 100% alternance)
| Diplôme | Niveau | Spécialité |
|---------|--------|------------|
| BTS MCO | Bac+2 | Management des Unités Commerciales |
| BTS NDRC | Bac+2 | Négociation et Digitalisation de la Relation Client |
| Titre Pro Négociateur Technico-Commercial | Bac+2 | Vente B2B |
| Bachelor Responsable d'établissement marchand | Bac+3 | Management commerce |
| Master Manager de Business Unit | Bac+5 | Stratégie, finance, management 360° |

### Key selling points (always refer to these)
1. **0€ de frais d'inscription**
2. **775€ à 1 802€/mois** de salaire en alternance (hors primes)
3. **85% de taux de réussite** (2024)
4. **75% en CDI/CDD** dans les 6 mois post-diplôme
5. **60% en poste de responsabilité** dans les 6 mois
6. **300 entreprises partenaires** (Monoprix, Franprix, Euromaster, Cocci Market, Polylangues…)
7. **10 campus** : Saint-Denis (Paris), Marseille, Lille, Metz, Rouen, Lyon, Toulouse, Montpellier, Bordeaux, Aix-en-Provence
8. **QUALIOPI certifié** — diplômes reconnus par l'État (RNCP)

### 5 Content Pillars
1. Alternance & Argent (salaires, 0€ frais, être payé pour apprendre)
2. Programmes & Formations (BTS/Bachelor/Master, différences, débouchés)
3. Témoignages étudiants (journée type, before/after, retours d'expérience)
4. Entreprises partenaires (offres dispo, secteurs qui recrutent, conseils entretien)
5. Vie PNBS (campus, événements, JPO, ambiance, coulisses)

## Competitor Accounts
| Handle | URL |
|--------|-----|
| ecole_studi | https://www.instagram.com/ecole_studi/ |
| iscod.fr | https://www.instagram.com/iscod.fr/ |
| digitalcollege | https://www.instagram.com/digitalcollege/ |
| isefac.national | https://www.instagram.com/isefac.national/ |
| nuevo_cfa | https://www.instagram.com/nuevo_cfa/ |
| campus_des_ecoles | https://www.instagram.com/campus_des_ecoles/ |

## Pipeline (3 Steps)

### Step 1 — Scrape (`execution/scrape_instagram.py`)
- **Input**: List of competitor usernames (hardcoded in script)
- **Tool**: `instaloader` Python library
- **What it fetches**: Last 20 posts per account — post type, likes, comments, caption, hashtags, date
- **Output**: `.tmp/scraped/competitor_posts_{YYYY-MM-DD}.json`
- **Rate limiting**: 1.5s delay between posts, 5s delay between accounts
- **Auth**: Optional Instagram login via `.env` (`INSTAGRAM_USERNAME`, `INSTAGRAM_PASSWORD`)
  - Use a dedicated dummy account — never your main account
  - Without login: works but may hit rate limits faster

### Step 2 — Analyze (`execution/analyze_competitors.py`)
- **Input**: Latest `.tmp/scraped/competitor_posts_{date}.json`
- **Tool**: Claude API (`claude-opus-4-6`)
- **What it produces**:
  - Content type breakdown per account (reels, carousels, images, testimonials, etc.)
  - Top-performing formats by engagement rate
  - Posting pattern analysis (best days/times)
  - Hashtag strategy
  - Tone & caption structure of high-performers
  - Actionable insights + what to adopt/avoid for PNBS
- **Output**: `.tmp/analysis/competitor_analysis_{YYYY-MM-DD}.json`

### Step 3 — Generate Strategy (`execution/generate_strategy.py`)
- **Input**: Latest `.tmp/analysis/competitor_analysis_{date}.json`
- **Tool**: Claude API (`claude-opus-4-6`)
- **What it produces**:
  - 5-post weekly content calendar (Mon–Fri)
  - Per post: caption (FR, ready to copy-paste), visual guidelines, shot list (reels), slide structure (carousels), objective, adaptation logic
  - Weekly summary table
  - Content strategy notes + hashtag rotation groups
- **Output**: `.tmp/strategy/weekly_strategy_{YYYY-MM-DD}.md`

### Master Runner (`execution/run_pipeline.py`)
Chains steps 1→2→3. Accepts `--skip-scrape` flag to reuse existing scraped data (useful if scraping was already done today).

## Schedule
- **When**: Every Monday at 08:00 AM
- **Command**: `cd "C:/Users/Taliha Sahin/Desktop/Weakly Instagram Posts PNBS" && python execution/run_pipeline.py`
- **Log**: `.tmp/pipeline_{YYYY-MM-DD}.log`

## Output Location
- Raw scraped data: `.tmp/scraped/`
- Competitor analysis: `.tmp/analysis/`
- **Weekly strategy (deliverable)**: `.tmp/strategy/weekly_strategy_{date}.md`
  - Open this file each Monday to get the full content plan

## Environment Variables Required
```
ANTHROPIC_API_KEY=         # Required — for analysis + strategy generation
INSTAGRAM_USERNAME=        # Optional — dedicated scraping account
INSTAGRAM_PASSWORD=        # Optional — dedicated scraping account
```

## Known Issues & Edge Cases

### Instagram Rate Limiting
- Without login: ~30-50 posts before getting a 429. Add `time.sleep()` between requests.
- With login: much more generous limits, but use a dedicated account (not your main).
- If you get `LoginRequiredException`, the account is private — skip it and log a warning.
- If you get repeated 429s, increase `SCRAPE_DELAY_SECONDS` in the script.

### Username Format
- `iscod.fr` — dots are valid in Instagram usernames, instaloader handles them fine.
- If a profile disappears or gets renamed, update the `COMPETITOR_ACCOUNTS` list in `scrape_instagram.py`.

### Instagram Scraping Alternatives (if instaloader fails)
- **Apify Instagram Scraper**: Most reliable, paid (~$0.50/1000 posts). Set `APIFY_API_KEY` in `.env` and rewrite the scrape step.
- **PhantomBuster**: GUI-based Instagram scraper, easier setup.
- If switching to Apify: create `execution/scrape_instagram_apify.py` and update this directive.

## Known Issues & Fixes

### JSON Truncation from Claude (fixed 2026-04-14)
- **Symptom**: `Unterminated string starting at: line N column N` in step 2/3
- **Root cause**: `max_tokens=4096` was too low for 6-account competitor data → Claude's JSON response was cut off mid-stream
- **Fix applied**: Raised to `max_tokens=8192` in `analyze_competitors.py`. Added 3-tier JSON repair:
  1. Parse as-is
  2. Auto-close unclosed brackets/braces via `_repair_truncated_json()`
  3. Walk backwards to find last valid JSON object
  - If all fail: saves raw response to `.tmp/analysis/debug_raw_response.txt` and raises with clear instructions
- **If it recurs**: Check `.tmp/analysis/debug_raw_response.txt`, then reduce `POSTS_PER_ACCOUNT` in `scrape_instagram.py` (fewer posts = smaller prompt = less output needed)

## Self-Annealing Notes
- Update this directive whenever you discover new API constraints, rate limit patterns, or better content categories.
- If a competitor account goes private or disappears, remove it from the list and log it here.
- If the Claude analysis prompt produces inconsistent JSON, tighten the schema in `analyze_competitors.py`.
