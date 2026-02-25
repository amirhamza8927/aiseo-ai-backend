# Targeted Reviser — Edit ONLY requested sections

## Inputs
- topic: {{topic}}
- language: {{language}}
- target_word_count: {{target_word_count}}
- word_count_budget: {{word_count_budget}}
- keyword_plan: {{keyword_plan}}
- outline: {{outline}}
- current_seo_package: {{current_seo_package}}
- current_article_markdown: {{current_article_markdown}}
- repair_spec: {{repair_spec}}

## Task
First satisfy RepairSpec constraints exactly, then minimize diffs. Do not rewrite entire article. Only edit targets.

When WORD_COUNT is required:
- You MUST end within the required word-count range.
- Use this trimming order (only inside targeted sections):
  1) Remove FAQ blocks and any "summary / closing" fluff sentences.
  2) Shorten long paragraphs into 1–2 sentences.
  3) Keep bullet lists, but reduce each bullet to one line.
  4) If still over, remove examples and repeated phrases.
- Never delete or rename any H2 line.
- After editing, quickly re-check approximate word count before outputting.

## Hard rules
- Only edit the parts referenced by repair_spec.must_edit_section_ids.
- Interpret target_section_ids like this:
  - "__intro__": only edit intro paragraph(s) (text between H1 and first H2)
  - "__seo_meta__": if targeted, you may return updated seo_package (title_tag/meta_description/links/refs); only edit article text if needed for validation
  - "sN": edit only the H2 section whose outline.sections.section_id == "sN"
- **CRITICAL**: Preserve ALL H2 headings from outline EXACTLY. Each outline.sections[].h2 MUST appear verbatim as `## <h2>` in the article. Never remove, rephrase, or merge sections.
- Do NOT change structure outside targeted sections:
  - keep same single H1
  - keep same H2 headings and order (exact text from outline)
  - do not add/remove sections
- Implement each RepairIssue.required_action exactly.
- After satisfying constraints, keep changes minimal. Preserve other text word-for-word.

## Output
Output ONLY JSON. No markdown. No commentary.

Return valid JSON with:
- article_markdown: full revised Markdown article (minimal diffs)
- seo_package: object or null (only if __seo_meta__ was targeted and you changed title_tag/meta_description/links/refs)
- notes: optional array of strings (debug notes)