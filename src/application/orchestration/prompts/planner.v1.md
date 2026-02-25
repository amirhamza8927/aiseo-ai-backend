# Planner (JSON only) — Plan is the source of truth

## Inputs
- topic: {{topic}}
- primary_keyword: {{primary_keyword}}
- language: {{language}}
- target_word_count: {{target_word_count}}
- themes: {{themes}}
- serp_results (top 10): {{serp_results}}

## Task
Create a strict Plan that will drive the outline and article.
The Plan MUST:
- satisfy the same search intent as the SERP winners
- cover all key topic_clusters
- **CRITICAL**: intro_target_word_count + sum(sections.target_word_count) MUST be between 0.75× and 1.25× of target_word_count (e.g. for target 500: total 375–625 words)
- **CRITICAL**: At least one plan.sections.heading MUST include primary_keyword exactly once (case-insensitive).
- include stable section_id values that NEVER change later
- include internal link plan + external citation plan + FAQ plan

## Hard rules
- Output ONLY valid JSON.
- section_id must be stable strings like: "s1", "s2", "s3"... (no spaces).
- section_id values MUST be unique.
- intro_target_word_count and target_word_count values MUST be integers > 0.
- Total budget (intro + all sections) MUST be in range [target_word_count × 0.75, target_word_count × 1.25]. Count before submitting.
- internal_links/external_citations/faqs placement_section_id MUST reference an existing plan.sections.section_id.
- All key_points arrays must be non-empty.
- At least one plan.sections.heading MUST contain primary_keyword ({{primary_keyword}}). Count and ensure it appears in that heading exactly once.
- Language: {{language}}.

## Output JSON shape (must match Plan exactly)
Budget math: intro_target_word_count + sum(each section.target_word_count) = total. Total MUST be 0.75×–1.25× target_word_count.
Example: target 500 → total 375–625. With 4 sections: intro 100 + sections 100+100+100+100 = 500.
{
  "h1": "string",
  "intro_target_word_count": 100,
  "sections": [
    {
      "section_id": "s1",
      "heading": "string",
      "purpose": "string",
      "key_points": ["string"],
      "target_word_count": 100,
      "required_keywords": ["string"]
    }
  ],
  "internal_links": [
    {
      "anchor_text": "string",
      "target_topic": "string",
      "placement_section_id": "s1"
    }
  ],
  "external_citations": [
    {
      "source_type": "string",
      "suggested_source": "string",
      "url": null,
      "claim_supported": "string",
      "placement_section_id": "s1"
    }
  ],
  "faqs": [
    {
      "question": "string",
      "placement_section_id": "s1"
    }
  ]
}