#!/usr/bin/env python3
"""
Axios Audit Skill Implementation
Scans a repository for axios usage and generates a comprehensive report
"""

import os
import json
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime

class AxiosAuditor:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.direct_deps: Dict[str, str] = {}  # package -> version
        self.transitive_deps: Dict[str, List[str]] = {}  # package -> list of packages that depend on it
        self.code_usage: List[Tuple[str, int, str]] = []  # (file, line_number, match_text)

    def audit(self, folders: List[str]) -> str:
        """Run complete audit and return markdown report"""
        # Scan all folders for package files
        for folder in folders:
            self._scan_packages(folder)
            self._scan_code(folder)

        return self._generate_report()

    def _scan_packages(self, folder_path: str) -> None:
        """Scan folder for package.json and lock files"""
        folder = Path(folder_path)
        if not folder.exists():
            return

        for package_json in folder.rglob("package.json"):
            self._parse_package_json(package_json)

        for lock_file in folder.rglob("package-lock.json"):
            self._parse_npm_lock(lock_file)

        for lock_file in folder.rglob("yarn.lock"):
            self._parse_yarn_lock(lock_file)

        for lock_file in folder.rglob("pnpm-lock.yaml"):
            self._parse_pnpm_lock(lock_file)

    def _parse_package_json(self, package_json: Path) -> None:
        """Extract axios dependencies from package.json"""
        try:
            with open(package_json, 'r') as f:
                data = json.load(f)

            pkg_name = data.get('name', package_json.parent.name)

            # Check dependencies
            for dep_type in ['dependencies', 'devDependencies', 'optionalDependencies', 'peerDependencies']:
                deps = data.get(dep_type, {})
                if 'axios' in deps:
                    self.direct_deps[pkg_name] = (deps['axios'], str(package_json))

                # Check for packages that might depend on axios
                for package, version in deps.items():
                    if package.endswith('/axios') or 'http' in package.lower():
                        self.transitive_deps.setdefault(package, []).append(pkg_name)
        except Exception as e:
            print(f"Error parsing {package_json}: {e}")

    def _parse_npm_lock(self, lock_file: Path) -> None:
        """Parse npm package-lock.json for axios references"""
        try:
            with open(lock_file, 'r') as f:
                data = json.load(f)

            packages = data.get('packages', {})
            for pkg_path, pkg_info in packages.items():
                deps = pkg_info.get('dependencies', {})
                if 'axios' in deps:
                    pkg_name = pkg_path.split('/')[-1] if pkg_path else 'root'
                    self.transitive_deps.setdefault(f"{pkg_name} (npm-lock)", []).append('root')
        except Exception as e:
            print(f"Error parsing {lock_file}: {e}")

    def _parse_yarn_lock(self, lock_file: Path) -> None:
        """Parse yarn.lock for axios references"""
        try:
            with open(lock_file, 'r') as f:
                content = f.read()

            # Simple regex to find axios entries
            if 'axios' in content:
                lines = content.split('\n')
                for i, line in enumerate(lines):
                    if 'axios' in line.lower():
                        self.transitive_deps.setdefault('axios (yarn-lock)', []).append(f'line {i}')
        except Exception as e:
            print(f"Error parsing {lock_file}: {e}")

    def _parse_pnpm_lock(self, lock_file: Path) -> None:
        """Parse pnpm-lock.yaml for axios references"""
        try:
            with open(lock_file, 'r') as f:
                content = f.read()

            if 'axios' in content:
                self.transitive_deps.setdefault('axios (pnpm-lock)', []).append(str(lock_file))
        except Exception as e:
            print(f"Error parsing {lock_file}: {e}")

    def _scan_code(self, folder_path: str) -> None:
        """Scan source code for axios imports and usage"""
        folder = Path(folder_path)
        if not folder.exists():
            return

        # Simple pattern list to check
        simple_patterns = ['axios', 'HttpService', '@nestjs/axios']

        try:
            # Find TypeScript/JavaScript files
            ts_files = list(folder.rglob('*.ts')) + list(folder.rglob('*.js')) + \
                      list(folder.rglob('*.tsx')) + list(folder.rglob('*.jsx'))

            # Limit to first 1000 files for performance
            ts_files = ts_files[:1000]

            for file_path in ts_files:
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        for line_num, line in enumerate(f, 1):
                            for pattern in simple_patterns:
                                if pattern in line:
                                    rel_path = str(Path(file_path).relative_to(self.workspace_path) if Path(file_path).is_relative_to(self.workspace_path) else file_path)
                                    self.code_usage.append((rel_path, line_num, f"{pattern}: {line.strip()[:80]}"))
                                    break
                except Exception:
                    pass
        except Exception:
            pass  # Scanning errors are non-fatal

    def _generate_report(self) -> str:
        """Generate markdown audit report"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        report = f"""# Axios Audit Report

**Generated:** {timestamp}

## Executive Summary

- **Total direct dependencies**: {len(self.direct_deps)}
- **Total transitive dependencies**: {len(self.transitive_deps)}
- **Code usage locations found**: {len(self.code_usage)}
- **Status**: {'✅ No axios detected' if not self.direct_deps and not self.transitive_deps and not self.code_usage else '⚠️ Axios usage detected'}

## Direct Dependencies

These packages explicitly require axios in their package.json:

"""

        if self.direct_deps:
            for pkg, (version, source) in self.direct_deps.items():
                report += f"- **{pkg}** (version: `{version}`)\n"
                report += f"  - Source: `{source}`\n"
        else:
            report += "No direct axios dependencies found.\n"

        report += """
## Transitive Dependencies

These packages indirectly depend on axios through other dependencies:

"""

        if self.transitive_deps:
            for pkg, dependents in self.transitive_deps.items():
                report += f"- **{pkg}**\n"
                for dep in dependents[:5]:  # Limit to 5
                    report += f"  - `{dep}`\n"
                if len(dependents) > 5:
                    report += f"  - ... and {len(dependents) - 5} more\n"
        else:
            report += "No transitive axios dependencies found.\n"

        report += """
## Code Usage Locations

Files in the codebase that import or use axios:

"""

        if self.code_usage:
            # Group by file
            by_file = {}
            for file, line, text in self.code_usage:
                if file not in by_file:
                    by_file[file] = []
                by_file[file].append((line, text))

            for file, usages in sorted(by_file.items()):
                report += f"\n### {file}\n"
                for line, text in sorted(usages):
                    report += f"- Line {line}: {text}\n"
        else:
            report += "No axios code usage found.\n"

        report += """
## Dependency Tree

```
Root
├── axios (direct dependency)
│   └── Used by: [package names]
└── Other HTTP clients
    └── [dependencies and usage]
```

## Impact Assessment

### Modules Affected by Axios Migration
"""

        if self.direct_deps or self.code_usage:
            report += f"**High**: {len(self.code_usage)} file(s) contain axios usage\n"
            report += f"**Dependencies**: {len(self.direct_deps)} package(s) require axios\n"
        else:
            report += "**None**: No axios usage or dependencies detected\n"

        report += """
## Recommendations

1. **If migrating to native fetch**:
   - Start with the modules identified above
   - Replace HttpService with fetch or alternative HTTP client
   - Update tests that mock axios

2. **If upgrading axios**:
   - Check for breaking changes in release notes
   - Test transitive dependencies for compatibility

3. **If consolidating HTTP clients**:
   - Consider standardizing on one HTTP solution
   - Gradually migrate away from axios if using multiple clients

## Next Steps

- Review the code usage locations above
- Determine which modules can be safely refactored
- Plan a migration timeline based on module dependencies
- For more details, use the migrate-axios-to-fetch skill
"""

        return report

def main():
    # Get all workspace folders
    workspace_folders = [
        "/Users/leonardo.copello/Documents/prodfin-pc-portais-bff-portais-de-credito",
        "/Users/leonardo.copello/Documents/prodfin-pc-dados-bff-credit-container-portal",
        "/Users/leonardo.copello/Documents/prodfin-pc-dados-bff-mediators-module-portal",
        "/Users/leonardo.copello/Documents/prodfin-pc-dados-bff-installments-module-portal",
        "/Users/leonardo.copello/Documents/prodfin-pc-dados-bff-common-module-portal",
        "/Users/leonardo.copello/Documents/prodfin-pc-core-node-utils",
    ]

    auditor = AxiosAuditor("/Users/leonardo.copello/Documents")
    report = auditor.audit(workspace_folders)

    print(report)

if __name__ == "__main__":
    main()
