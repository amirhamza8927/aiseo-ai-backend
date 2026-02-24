# Outline Builder (JSON only) — MUST match Plan section IDs exactly

## Inputs
- topic: {{topic}}
- language: {{language}}
- plan: {{plan}}

## Task
Generate an Outline derived from the Plan.
You MUST:
- output h1
- optional intro_h2 (or null)
- output sections in the SAME ORDER as plan.sections
- use EXACT same section_id values from plan.sections
- create a helpful H2 per section and optional H3 bullets

## Hard rules
- Output ONLY valid JSON.
- Do NOT invent new section_id values.
- Do NOT drop any plan sections.
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