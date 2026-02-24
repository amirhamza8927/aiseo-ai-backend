# Targeted Reviser — Edit ONLY requested sections

## Inputs
- topic: {{topic}}
- language: {{language}}
- keyword_plan: {{keyword_plan}}
- outline: {{outline}}
- current_seo_package: {{current_seo_package}}
- current_article_markdown: {{current_article_markdown}}
- repair_spec: {{repair_spec}}

## Task
Apply RepairSpec with minimal edits. Do not rewrite entire article. Only edit targets.

## Hard rules
- Only edit the parts referenced by repair_spec.must_edit_section_ids.
- Interpret target_section_ids like this:
  - "__intro__": only edit intro paragraph(s) (text between H1 and first H2)
  - "__seo_meta__": if targeted, you may return updated seo_package (title_tag/meta_description/links/refs); only edit article text if needed for validation
  - "sN": edit only the H2 section whose outline.sections.section_id == "sN"
- Do NOT change structure outside targeted sections:
  - keep same single H1
  - keep same H2 order
  - do not add/remove sections
- Implement each RepairIssue.required_action exactly.
- Keep changes minimal. Preserve other text word-for-word.

## Output
Output ONLY JSON. No markdown. No commentary.

Return valid JSON with:
- article_markdown: full revised Markdown article (minimal diffs)
- seo_package: object or null (only if __seo_meta__ was targeted and you changed title_tag/meta_description/links/refs)
- notes: optional array of strings (debug notes)