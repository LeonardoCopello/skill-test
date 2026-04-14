---
name: axios-audit
description: Audit a repository for axios usage and all packages that depend on it. Use this skill whenever the user needs to understand axios dependencies (direct and transitive), find where axios is used in code, plan axios migrations, conduct security audits, or assess supply chain impact. Run this before axios removal, deprecation, or upgrade efforts.
compatibility: 
  - Requires Node.js and npm/yarn/pnpm CLI
  - Works with monorepos and single packages
---

# Axios Audit Skill

Comprehensively scan a repository to identify axios usage patterns and dependency chains. This skill generates a detailed markdown report showing where axios lives in your codebase—both as a direct dependency and through packages that depend on it.

## When to use this skill

- **Migration planning** — Before migrating from axios to native fetch or another HTTP client, understand the full scope of what's affected
- **Dependency audits** — Identify all packages in your codebase that use axios, including transitive dependencies
- **Supply chain security** — Assess the blast radius of axios vulnerabilities or updates
- **Dependency consolidation** — Find redundant or conflicting HTTP client libraries
- **Upgrade planning** — Understand the impact before upgrading axios to a new major version

## What the skill does

1. **Scans package files** across the entire workspace (supports npm, yarn, pnpm)
   - Detects direct dependencies on axios
   - Resolves transitive dependencies (packages that depend on axios)
   - Distinguishes between direct and transitive with clear labels

2. **Searches code** for axios imports and usage patterns
   - Finds `import axios` statements
   - Finds `require('axios')` statements
   - Finds `HttpService` injections (NestJS patterns)
   - Identifies usage locations and patterns

3. **Generates a comprehensive report** in markdown format showing:
   - Direct axios dependencies (which packages explicitly require axios)
   - Transitive dependencies (which packages indirectly pull in axios through their own dependencies)
   - Code locations where axios is imported or used
   - Suggested next steps for remediation or migration

## How to trigger the skill

Ask the user to run the audit and include context about what they want to accomplish:

- "Find all axios usage in my repository"
- "I need to understand the scope of our axios dependencies before we migrate to fetch"
- "Audit the codebase — how many packages depend on axios?"
- "Give me a full inventory of axios usage so we can plan the migration"

## The audit process

### Step 1: Gather package information

Search all `package.json` files in the workspace and parse `package-lock.json` / `yarn.lock` / `pnpm-lock.yaml` files if present. Extract:
- Direct axios dependencies
- All transitive axios dependencies (packages that list axios as a dependency)
- Version numbers and source packages

### Step 2: Search code for imports

Use grep patterns to identify:
- `import.*axios` statements (including destructuring)
- `require.*axios` statements
- `HttpService` injections (NestJS @nestjs/axios pattern)
- Any other axios usage patterns in `.ts`, `.js`, `.tsx`, `.jsx` files

Record file paths and line numbers for each match.

### Step 3: Build dependency tree

Create a hierarchical view:
- **Direct dependencies**: packages that explicitly have axios in package.json
- **Transitive dependencies**: packages brought in through other packages' dependencies

Organize by:
- Which package introduces the dependency
- How many levels deep in the tree
- All consumers within your codebase

### Step 4: Generate markdown report

Create a well-structured report with:
1. **Executive summary** — Total count of packages using axios, code usage locations
2. **Direct dependencies** — Your own packages that directly require axios with versions
3. **Transitive dependencies** — Full dependency chain (e.g., "package A requires package B which requires axios")
4. **Code usage locations** — Every file and line where axios is imported/used
5. **Impact assessment** — Which modules would be affected by axios removal or upgrade
6. **Recommendations** — Next steps based on findings (migrate, consolidate, update, etc.)

## Example usage

**User prompt:**
> "I need to audit our repository for axios usage. We're planning to migrate to native fetch and I need to understand the full scope."

**Skill execution:**
1. Scans all package.json files in the monorepo
2. Parses lock files to find transitive dependencies
3. Searches all source code for axios imports
4. Generates:
   ```
   # Axios Audit Report
   
   ## Executive Summary
   - Total packages using axios: 7 (2 direct, 5 transitive)
   - Code usage locations: 14 files
   - ...
   
   ## Direct Dependencies
   ### @app/core-http (^0.4.2)
   Direct dependency in: src/http/client.ts + 3 other files
   
   ...
   ```

## Important notes

- **Transitive dependencies matter**: If package X depends on package Y which depends on axios, removing axios directly may break package Y. The report distinguishes these so you can make informed decisions.
- **Monorepo support**: The skill automatically detects and processes multiple package.json files across the workspace.
- **Multiple package managers**: Works with npm, yarn, and pnpm workspaces seamlessly.
- **Version mismatches**: The report flags if different packages require different versions of axios (can cause conflicts).

## Output format

The skill always outputs a **Markdown (.md) file** named `axios-audit-report.md` with:
- Clear section headers
- Code blocks with file paths and line numbers
- Hierarchical dependency trees
- Actionable recommendations
- Timestamp of when the audit was run

Use the report to plan your next steps—whether that's a migration to fetch, consolidating HTTP clients, or understanding the impact of an axios update.
