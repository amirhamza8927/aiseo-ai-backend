# Outline Builder (JSON only) — MUST match Plan section IDs exactly

## Inputs
- topic: {{topic}}
- language: {{language}}
- plan: {{plan}}
- themes (optional): {{themes}}

## Task
Generate an Outline derived from the Plan.
You MUST:
- output h1
- optional intro_h2 (or null)
- output sections in the SAME ORDER as plan.sections
- use EXACT same section_id values from plan.sections
- For each section:
  - section_id must match plan.sections.section_id
  - **h2 MUST be exactly plan.sections[i].heading (verbatim, same punctuation/case)**
  - h3 can be added as supportive bullets

## Hard rules
- Output ONLY valid JSON.
- Do NOT invent new section_id values.
- Do NOT drop any plan sections.
- **h2 MUST equal the matching plan.sections.heading exactly (no paraphrase).**
- H2 text must be non-empty.
- Language: {{language}}.

## Output JSON shape (must match Outline exactly)
{
  "h1": "string",
  "intro_h2": null,
  "sections": [
    {
      "section_id": "s1",
      "h2": "string",
      "h3": ["string"]
    }
  ]
}