# Knowledge Base - Mock Directory

This directory previously contained mock data for testing and development.

## Purpose

Place your actual knowledge base documents here in Markdown format with YAML frontmatter.

## Document Format

Each document should follow this structure:

```markdown
---
title: Document Title
url: https://source.url (optional)
category: Hardware|Software|Legislação|Normas Técnicas|etc.
date: YYYY-MM-DD (optional)
---

# Document Content

Your content here...
```

## Indexing

After adding documents, re-index the knowledge base:

```bash
python3 scripts/index_knowledge_base.py
```

## Notes

- Documents must be in Markdown format (.md)
- YAML frontmatter is recommended for better metadata tracking
- The RAG engine will chunk documents automatically
- Supported categories are flexible - use what makes sense for your domain
