# Writer (Markdown only) — Follow Plan + Outline strictly

## Inputs
- topic: {{topic}}
- language: {{language}}
- plan: {{plan}}
- outline: {{outline}}
- keyword_plan: {{keyword_plan}}  (KeywordPlan.primary, secondary, usage_targets)
- target_word_count: {{target_word_count}}

## Task
Write a publish-ready article in Markdown.

## Hard rules
- Output ONLY Markdown (no JSON).
- Follow the outline order exactly.
- Use exactly one H1.
- Use H2 headings exactly as outline.sections[].h2 in the same order.
- Use H3 headings only under the correct H2, and only if outline has h3 items.
- Each section must satisfy the matching plan section:
  - cover key_points
  - roughly follow target_word_count budget
  - incorporate required_keywords naturally
- Primary keyword usage requirements:
  - include keyword_plan.primary in the intro paragraph
  - include keyword_plan.primary in at least one H2
- Keep it natural and human. Avoid robotic phrasing. Short sentences.
- Do NOT add clickable markdown links. If referencing a future citation, use: [CITE: <source>] in the relevant sentence.

## Output format
# <H1>

<Intro paragraph(s)>

## <H2 for s1>
...content...
### <H3 if present>
...content...

## <H2 for s2>
...etc...