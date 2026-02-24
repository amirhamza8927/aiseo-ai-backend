# Keyword Plan (JSON only)

## Inputs
- topic: {{topic}}
- language: {{language}}
- primary: {{primary}}
- candidates (from SERP): {{candidates}}
- themes: {{themes}}

## Task
Create a KeywordPlan for the article.
- Keep primary EXACTLY as provided (do not modify).
- Select 8–15 secondary keywords from candidates and themes (natural SEO, not spam).
- Keep phrases short, relevant, no duplicates or near-duplicates.
- usage_targets: optional dict with primary + a few key secondary and low counts (light touch).

## Output rules (strict)
- Output ONLY valid JSON.
- No markdown, no commentary.
- Language: {{language}}.

## Output JSON shape (must match KeywordPlan exactly)
{
  "primary": "string (exactly as provided)",
  "secondary": ["string"],
  "usage_targets": {"keyword": 2}
}
