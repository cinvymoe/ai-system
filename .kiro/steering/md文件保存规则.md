---
inclusion: always
---
---
inclusion: fileMatch
fileMatchPattern: ['**/*.md']
---

# Markdown Documentation Rules

## File Organization

### Documentation Placement

- **Root-level docs**: Project-wide documentation (README.md, NAVIGATION_GUIDE.md, etc.)
- **Backend docs**: Place in `backend/` for backend-specific guides
- **Frontend docs**: Place in `src/` or `src/guidelines/` for frontend-specific guides
- **Module docs**: Place within module directories for module-specific documentation (e.g., `backend/src/broker/LOGGING_README.md`)

### Naming Conventions

- Use descriptive, uppercase names for important guides: `README.md`, `QUICK_START.md`, `API_DOCUMENTATION.md`
- Use lowercase with underscores for implementation summaries: `implementation_summary.md`, `test_report.md`
- Chinese documentation is acceptable in `doc/` directory

## Content Guidelines

### Structure

- Start with a clear title (# heading)
- Include a brief overview or introduction
- Use hierarchical headings (##, ###) for organization
- Add code examples in fenced code blocks with language identifiers

### Code Examples

```python
# Use language-specific syntax highlighting
def example_function():
    pass
```

```typescript
// TypeScript examples for frontend
const example: string = "value";
```

### Documentation Types

1. **README files**: Overview, setup instructions, usage examples
2. **GUIDE files**: Step-by-step instructions for specific tasks
3. **API_DOCUMENTATION**: Endpoint descriptions, request/response schemas
4. **SUMMARY files**: Implementation summaries, test reports, completion notes
5. **QUICK_START/QUICK_REFERENCE**: Condensed reference material

## Best Practices

- Keep documentation up-to-date with code changes
- Include practical examples and use cases
- Document API endpoints with request/response examples
- Provide troubleshooting sections for complex features
- Use tables for structured data (configuration options, API parameters)
- Link to related documentation files when relevant

## Avoid

- Do not create redundant documentation files
- Do not create summary markdown files unless explicitly requested by the user
- Avoid overly verbose explanations; be concise and actionable
- Do not duplicate information that exists in code comments or docstrings
