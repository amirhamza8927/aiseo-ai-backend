# Themes Extractor (JSON only)

## Inputs
- topic: {{topic}}
- language: {{language}}
- serp_results (top 10): {{serp_results}}

## Task
Analyze the SERP results to infer what is ranking and why. Extract:
- search_intent: what the searcher wants
- topic_clusters: recurring topics and angles
- common_sections: common headings/sections seen across results
- ranking_patterns: formats that rank (listicle, comparison, pricing, pros/cons, etc.)
- differentiation_angles: how our article can add value beyond the SERP

## Output rules (strict)
- Output ONLY valid JSON.
- No markdown, no commentary, no extra text.
- Use short phrases, not paragraphs.
- All arrays must be non-empty.
- Language: {{language}}.

## Output JSON shape (must match exactly)
{
  "search_intent": "string",
  "topic_clusters": ["string"],
  "common_sections": ["string"],
  "ranking_patterns": ["string"],
  "differentiation_angles": ["string"]
}