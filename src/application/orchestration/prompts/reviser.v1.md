# Targeted Reviser (Markdown only) — Edit ONLY requested sections

## Inputs
- language: {{language}}
- keyword_plan: {{keyword_plan}}
- outline: {{outline}}
- current_article_markdown: {{article_markdown}}
- repair_spec: {{repair_spec}}

## Task
Apply RepairSpec with minimal edits.

## Hard rules
- Output ONLY the revised Markdown article (full article).
- Only edit the parts referenced by repair_spec.must_edit_section_ids.
- Interpret target_section_ids like this:
  - "__intro__": only edit intro paragraph(s) (text between H1 and first H2)
  - "__seo_meta__": do NOT write metadata here; only edit article text if needed for validation
  - "sN": edit only the H2 section whose outline.sections.section_id == "sN"
- Do NOT change structure outside targeted sections:
  - keep same single H1
  - keep same H2 order
  - do not add/remove sections
- Implement each RepairIssue.required_action exactly.
- Keep changes minimal. Preserve other text word-for-word.

## Output
Return the full Markdown article with minimal diffs.