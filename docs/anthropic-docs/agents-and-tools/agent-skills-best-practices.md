---
source: https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices
scraped: 2026-03-23
section: agents-and-tools
---

# Skill authoring best practices

Learn how to write effective Skills that Claude can discover and use successfully.

## Core principles

### Concise is key

The context window is a public good. Your Skill shares the context window with everything else Claude needs to know. Only add context Claude doesn't already have.

**Good example: Concise** (~50 tokens):
````markdown
## Extract PDF text

Use pdfplumber for text extraction:

```python
import pdfplumber

with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```
````

**Bad example: Too verbose** (~150 tokens):
```markdown
## Extract PDF text

PDF (Portable Document Format) files are a common file format that contains
text, images, and other content. To extract text from a PDF, you'll need to
use a library...
```

### Set appropriate degrees of freedom

Match the level of specificity to the task's fragility and variability.

**High freedom** (text-based instructions): Use when multiple approaches are valid or decisions depend on context.

**Low freedom** (specific scripts, few parameters): Use when operations are fragile and error-prone, or consistency is critical.

### Test with all models you plan to use

Skills act as additions to models, so effectiveness depends on the underlying model. Test your Skill with Claude Haiku, Sonnet, and Opus.

## Skill structure

### Naming conventions

Use consistent naming patterns. Consider using **gerund form** (verb + -ing) for Skill names:

- `processing-pdfs`
- `analyzing-spreadsheets`
- `managing-databases`

The `name` field must use lowercase letters, numbers, and hyphens only. Maximum 64 characters.

### Writing effective descriptions

The `description` field enables Skill discovery. **Always write in third person** — the description is injected into the system prompt.

- **Good:** "Processes Excel files and generates reports"
- **Avoid:** "I can help you process Excel files"

Be specific and include key terms. Include both what the Skill does and specific triggers/contexts for when to use it.

**PDF Processing skill:**
```yaml
description: Extract text and tables from PDF files, fill forms, merge documents. Use when working with PDF files or when the user mentions PDFs, forms, or document extraction.
```

**Excel Analysis skill:**
```yaml
description: Analyze Excel spreadsheets, create pivot tables, generate charts. Use when analyzing Excel files, spreadsheets, tabular data, or .xlsx files.
```

### Progressive disclosure patterns

SKILL.md serves as an overview that points Claude to detailed materials as needed. Keep SKILL.md body under 500 lines for optimal performance.

#### Pattern 1: High-level guide with references

````markdown
---
name: pdf-processing
description: Extracts text and tables from PDF files...
---

# PDF Processing

## Quick start

Extract text with pdfplumber:
```python
import pdfplumber
with pdfplumber.open("file.pdf") as pdf:
    text = pdf.pages[0].extract_text()
```

## Advanced features

**Form filling**: See [FORMS.md](FORMS.md) for complete guide
**API reference**: See [REFERENCE.md](REFERENCE.md) for all methods
````

#### Pattern 2: Domain-specific organization

For Skills with multiple domains, organize content by domain:

```text
bigquery-skill/
├── SKILL.md (overview and navigation)
└── reference/
    ├── finance.md (revenue, billing metrics)
    ├── sales.md (opportunities, pipeline)
    ├── product.md (API usage, features)
    └── marketing.md (campaigns, attribution)
```

### Avoid deeply nested references

Keep references one level deep from SKILL.md. Deeply nested files may cause Claude to only partially read content.

### Structure longer reference files with table of contents

For reference files longer than 100 lines, include a table of contents at the top.

## Workflows and feedback loops

### Use workflows for complex tasks

Break complex operations into clear, sequential steps. For particularly complex workflows, provide a checklist:

````markdown
## PDF form filling workflow

Copy this checklist and check off items as you complete them:

```
Task Progress:
- [ ] Step 1: Analyze the form (run analyze_form.py)
- [ ] Step 2: Create field mapping (edit fields.json)
- [ ] Step 3: Validate mapping (run validate_fields.py)
- [ ] Step 4: Fill the form (run fill_form.py)
- [ ] Step 5: Verify output (run verify_output.py)
```
````

### Implement feedback loops

**Common pattern:** Run validator → fix errors → repeat

```markdown
## Document editing process

1. Make your edits to `word/document.xml`
2. **Validate immediately**: `python ooxml/scripts/validate.py unpacked_dir/`
3. If validation fails:
   - Review the error message carefully
   - Fix the issues in the XML
   - Run validation again
4. **Only proceed when validation passes**
```

## Content guidelines

### Avoid time-sensitive information

Don't include information that will become outdated. Use an "old patterns" section with `<details>` tags for legacy content.

### Use consistent terminology

Choose one term and use it throughout the Skill:

- Always "API endpoint" (not mix of "URL", "API route", "path")
- Always "field" (not mix of "box", "element", "control")
- Always "extract" (not mix of "pull", "get", "retrieve")

## Common patterns

### Template pattern

For strict requirements:
````markdown
## Report structure

ALWAYS use this exact template structure:

```markdown
# [Analysis Title]

## Executive summary
[One-paragraph overview of key findings]

## Key findings
- Finding 1 with supporting data
```
````

### Examples pattern

For Skills where output quality depends on seeing examples, provide input/output pairs:

````markdown
## Commit message format

**Example 1:**
Input: Added user authentication with JWT tokens
Output:
```
feat(auth): implement JWT-based authentication

Add login endpoint and token validation middleware
```
````

## Evaluation and iteration

### Build evaluations first

Create evaluations BEFORE writing extensive documentation. This ensures your Skill solves real problems.

**Evaluation-driven development:**
1. Identify gaps: Run Claude on representative tasks without a Skill
2. Create evaluations: Build three scenarios that test these gaps
3. Establish baseline: Measure Claude's performance without the Skill
4. Write minimal instructions: Create just enough content to address the gaps
5. Iterate: Execute evaluations, compare against baseline, and refine

### Develop Skills iteratively with Claude

Work with one instance of Claude ("Claude A") to create a Skill that is used by other instances ("Claude B"). This works because Claude models understand both how to write effective agent instructions and what information agents need.

## Anti-patterns to avoid

### Avoid Windows-style paths

Always use forward slashes in file paths, even on Windows:

- Good: `scripts/helper.py`, `reference/guide.md`
- Avoid: `scripts\helper.py`, `reference\guide.md`

### Avoid offering too many options

Don't present multiple approaches unless necessary. Provide a default with an escape hatch:

```markdown
"Use pdfplumber for text extraction:
```python
import pdfplumber
```

For scanned PDFs requiring OCR, use pdf2image with pytesseract instead."
```

## Checklist for effective Skills

### Core quality
- [ ] Description is specific and includes key terms
- [ ] Description includes both what the Skill does and when to use it
- [ ] SKILL.md body is under 500 lines
- [ ] Additional details are in separate files (if needed)
- [ ] No time-sensitive information (or in "old patterns" section)
- [ ] Consistent terminology throughout
- [ ] Examples are concrete, not abstract
- [ ] File references are one level deep
- [ ] Progressive disclosure used appropriately
- [ ] Workflows have clear steps

### Testing
- [ ] At least three evaluations created
- [ ] Tested with Haiku, Sonnet, and Opus
- [ ] Tested with real usage scenarios
- [ ] Team feedback incorporated (if applicable)
