# Planner (JSON only) — Plan is the source of truth

## Inputs
- topic: {{topic}}
- language: {{language}}
- target_word_count: {{target_word_count}}
- themes: {{themes}}

## Task
Create a strict Plan that will drive the outline and article.
The Plan MUST:
- satisfy the same search intent as the SERP winners
- cover all key topic_clusters
- specify section-by-section budgets that roughly sum to target_word_count
- include stable section_id values that NEVER change later
- include internal link plan + external citation plan + FAQ plan

## Hard rules
- Output ONLY valid JSON.
- section_id must be stable strings like: "s1", "s2", "s3"... (no spaces).
- section_id values MUST be unique.
- intro_target_word_count and target_word_count values MUST be integers > 0.
- internal_links/external_citations/faqs placement_section_id MUST reference an existing plan.sections.section_id.
- All key_points arrays must be non-empty.
- Language: {{language}}.

## Output JSON shape (must match Plan exactly)
{
  "h1": "string",
  "intro_target_word_count": 200,
  "sections": [
    {
      "section_id": "s1",
      "heading": "string",
      "purpose": "string",
      "key_points": ["string"],
      "target_word_count": 250,
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