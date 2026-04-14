---
name: copilot-instructions
description: Create and manage GitHub Copilot Instructions files for standardizing coding patterns, conventions, and best practices across your repository. Use this skill whenever you need to establish consistent Copilot behavior, define naming conventions, document architecture patterns, or enforce coding standards for your team's AI-assisted development.
compatibility:
  - Requires GitHub Copilot
  - Works with VS Code, Claude Code, and other Copilot-compatible editors
  - Compatible with any project structure
---

# Copilot Instructions Skill

Create standardized `.copilot-instructions.md` files that guide GitHub Copilot to align with your codebase conventions, coding standards, and architectural patterns.

## When to use this skill

- **Standardize code generation** — Ensure Copilot generates code matching your team's style guide
- **Define project conventions** — Document naming patterns, folder structures, and import conventions
- **Enforce architectural patterns** — Guide Copilot to follow specific design patterns and architecture decisions
- **Document best practices** — Capture lessons learned and prevent anti-patterns in AI-generated code
- **Team onboarding** — Help new developers understand project standards through Copilot's behavior
- **Reduce review cycles** — Get better code first time by having Copilot understand requirements upfront
- **Maintain consistency** — Ensure monorepos or multi-package projects maintain unified standards

## What the skill does

1. **Analyzes your codebase** to extract existing patterns and conventions
2. **Generates comprehensive instructions** covering:
   - Code style and formatting standards
   - Naming conventions (files, functions, variables, components)
   - Architectural patterns and design decisions
   - Import and dependency organization
   - Error handling approaches
   - Testing patterns and requirements
   - Documentation standards
   - Framework-specific conventions
   - Common pitfalls to avoid
3. **Creates a `.copilot-instructions.md` file** at the repository root
4. **Provides guidance** on how to use and maintain the instructions

## How to trigger the skill

Ask to analyze your repository and create Copilot Instructions:

- "Create Copilot Instructions for this project"
- "Generate .copilot-instructions.md based on our codebase"
- "Analyze our NestJS patterns and create Copilot instructions"
- "Document our TypeScript conventions for Copilot"
- "Create standardized instructions for code generation in this monorepo"

## The instruction creation process

### Step 1: Analyze Code Patterns

Scan the repository to identify:
- Existing code style and conventions
- Naming patterns (files, functions, classes, variables)
- Folder structure and organization
- Common imports and dependencies
- Error handling patterns
- Testing approach
- Documentation style

### Step 2: Extract Best Practices

Document:
- Framework-specific conventions (NestJS, React, etc.)
- Project architecture
- Approved libraries and utilities
- Integration patterns
- Module boundaries
- Data flow patterns

### Step 3: Generate Instructions

Create detailed, actionable instructions covering:
1. **Code Style** — Formatting, spacing, quotes, semicolons
2. **Naming Conventions** — Variables, functions, classes, files, folders
3. **Architecture** — Folder structure, module boundaries, dependency flow
4. **Imports** — Order, grouping, absolute vs relative paths
5. **Error Handling** — Error types, exception throwing patterns
6. **Testing** — Test naming, structure, required coverage
7. **Documentation** — Comments, JSDoc, README patterns
8. **Framework Rules** — NestJS modules, decorators, dependency injection
9. **Utilities** — Common helpers, forbidden APIs
10. **Pitfalls** — Anti-patterns to avoid

### Step 4: Output Format

Creates `.copilot-instructions.md` with:
- Clear sections for each convention
- Real code examples from your project
- Dos and Don'ts
- Why each rule matters (context)
- Links to related files in the codebase

## Example output structure

```markdown
# Copilot Instructions for ProFin BFF

These instructions guide GitHub Copilot's code generation to match 
our project's standards and best practices.

## Code Style

### Formatting
- Use 2 spaces for indentation
- Max line length: 100 characters
- Use single quotes for strings (except JSON)
- Always use semicolons

### Naming Conventions
- **Files**: kebab-case for .ts files, PascalCase for classes
- **Functions**: camelCase for all functions
- **Variables**: camelCase for constants and variables
- **Classes**: PascalCase required
- **Folders**: kebab-case for directory names

## NestJS Patterns

### Module Structure
- One module per feature folder
- Controller, Service, Entity in same directory
- Use dependency injection via constructor
- ...

## Import Organization

Group imports in this order:
1. Node.js built-ins
2. External packages
3. Internal modules
4. Relative imports
5. Type imports

## Error Handling

Always use custom exceptions from `src/common/exceptions`:
- HTTPClientException for API errors
- ValidationException for input validation
- ...

## Do's and Don'ts

✅ DO: Use HttpService from the common module
❌ DON'T: Import axios directly in your code
✅ DO: Name services with .service.ts suffix
❌ DON'T: Create generic "utils" modules
```

## Important notes

- **Live guidance** — Copilot will reference this file when generating code
- **Monorepo support** — Can create separate instructions per package if needed
- **Living document** — Update instructions as architectural decisions change
- **Accessibility** — Place at repository root for easy Copilot discovery
- **Format matters** — Copilot reads markdown structure, keep it organized

## Integration with Copilot

1. Create `.copilot-instructions.md` at repo root
2. GitHub Copilot automatically discovers and uses it
3. Copilot will reference these patterns in suggestions
4. Test its behavior on a few pull requests
5. Refine instructions based on Copilot's output

## Best practices

- **Keep it concise** — Copilot reads the whole file for context
- **Use examples** — Show good and bad patterns with actual code
- **Be specific** — Generic advice is less useful than project-specific rules
- **Update regularly** — Keep synchronized with actual codebase evolution
- **Test it** — Verify Copilot actually follows your instructions
- **Link to sources** — Reference actual files that exemplify each pattern

## Output

The skill always outputs:
- **`.copilot-instructions.md`** at repository root
- Clear, actionable instructions organized by topic
- Real code examples from your project
- Context explaining the "why" behind each rule
- Guidance on how to maintain and update the file

Use the instructions to guide Copilot toward generating code that matches your 
team's standards, reducing review cycles and improving code consistency.
