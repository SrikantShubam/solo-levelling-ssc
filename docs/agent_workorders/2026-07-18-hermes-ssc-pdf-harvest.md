# Hermes Research Work Order: SSC CGL PYQ PDF Harvest

You are Hermes, in RESEARCH + SOURCING mode. This is a pure research/download
task. Do NOT do anything else — no Telegram/WhatsApp/Slack messaging, no
posting, no contacting anyone, no bot work. Only find and download files.

## Goal

Source **SSC CGL previous-year question paper PDFs** (with answer keys /
response sheets / solutions) from FREE, PUBLIC sources, to expand a study
corpus. Real downloaded PDFs only — a URL alone does not count.

## Priority order

1. **SSC CGL Tier-1 shift papers** (highest value — the study system's
   foundation baseline needs Tier-1 breadth). Maximize the number of
   DISTINCT shifts/dates/years.
2. SSC CGL Tier-2 papers (Math/DI, English, Reasoning) — secondary.

Prefer papers that INCLUDE the correct answer key / response sheet /
solutions in the same or a companion PDF. A question paper with no answer
key is low value.

## Already in the corpus — you may still fetch DIFFERENT shifts of these
years, but do not waste time re-downloading these exact ones:

- 2019 Tier1 (prepp shift1); 2019 Tier2 (prepp english, prepp quant)
- 2020 Tier1 (prepp shift1); 2020 Tier2 (kdcampus)
- 2021 Tier1 (prepp shift1, sscportal shift1); 2021 Tier2 (prepp english)
- 2022 Tier1 (prepp shift1); 2022 Tier2 (prepp paper1)
- 2023 Tier1 (prepp shift1); 2023 Tier2 (prepp paper1)
- 2024 Tier1 (prepp shift1, sscportal sep09 shift1, appx answer key);
  2024 Tier2 (prepp paper1, sscportal jan18/jan19/jan20)

Biggest gaps to fill: additional 2022/2023/2024 Tier-1 SHIFTS (each exam had
many days × 2–3 shifts), and older years 2016–2018 if available.

## Allowed sources (free/public only)

prepp.in, sscportal.in, testbook.com, oliveboard.in, kdcampus, careerpower,
adda247 (free PDFs only), and official SSC response sheets on ssc.nic.in.
If a source requires login, payment, or a paywall — SKIP it. Do not create
accounts.

## Delivery

- Download into `~/ssc-pdf-harvest/` on this machine (create it).
- Name each file descriptively: `YYYY_tier1_<source>_<shiftOrDate>.pdf`
  (e.g. `2023_tier1_prepp_2023-07-14_shift2.pdf`).
- **Verify each download is a real multi-page PDF**, not an HTML error page
  or a 1-page landing/ad. Use a quick check (file type + page count). Delete
  anything that isn't a genuine question-paper PDF.

## Output (required)

Write `~/ssc-pdf-harvest/manifest.csv` with one row per successfully
downloaded, verified PDF:

`filename, year, tier, shift_or_date, source_url, page_count, has_answer_key(yes/no/unknown)`

End your run with a short summary: how many PDFs downloaded, spanning which
years/tiers, and any notable gaps you could not fill from free sources.

## Hard lines

- Never invent URLs, filenames, page counts, or "downloaded" files. If a
  download failed, say so — do not fake it.
- No messaging, posting, or outbound contact of any kind.
- Free/public only. No logins, no payments, no paywalls.
- Stay within `~/ssc-pdf-harvest/`. Do not touch other folders.
