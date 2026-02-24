# SEO Packager (JSON only)

## Inputs
- topic: {{topic}}
- language: {{language}}
- article_markdown: {{article_markdown}}
- outline: {{outline}}
- keyword_plan: {{keyword_plan}}

## Task
Create SeoPackage for the article:
- seo_meta (title_tag + meta_description)
- internal_links (3–5)
- external_references (2–4)
- keyword_usage (primary, secondary, counts)

## Hard rules
- Output ONLY valid JSON.
- seo_meta.title_tag MUST include keyword_plan.primary.
- seo_meta.meta_description MUST be 140–160 characters and include keyword_plan.primary.
- internal_links must be 3–5 items.
- external_references must be 2–4 items.
- keyword_usage.counts must include an entry for keyword_plan.primary at minimum.
- Language: {{language}}.

## Output JSON shape (must match SeoPackage exactly)
{
  "seo_meta": {
    "title_tag": "string",
    "meta_description": "string"
  },
  "internal_links": [
    {
      "anchor_text": "string",
      "target_topic": "string",
      "placement_section_id": null
    }
  ],
  "external_references": [
    {
      "source_name": "string",
      "url": null,
      "placement_hint": "string",
      "credibility_reason": "string"
    }
  ],
  "keyword_usage": {
    "primary": "string",
    "secondary": ["string"],
    "counts": {
      "keyword": 3
    }
  }
}