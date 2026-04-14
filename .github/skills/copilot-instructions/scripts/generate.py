#!/usr/bin/env python3
"""
Copilot Instructions Generator
Analyzes codebase and creates standardized GitHub Copilot Instructions
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class CopilotInstructionsGenerator:
    def __init__(self, workspace_path: str):
        self.workspace_path = Path(workspace_path)
        self.patterns = {
            'naming': defaultdict(set),
            'imports': [],
            'exports': [],
            'errors': [],
            'services': [],
            'modules': [],
            'decorators': set(),
            'functions': defaultdict(set),
        }

    def generate(self) -> str:
        """Analyze codebase and generate instructions"""
        self._scan_codebase()
        return self._create_instructions()

    def _scan_codebase(self) -> None:
        """Scan TypeScript/JavaScript files for patterns"""
        ts_files = list(self.workspace_path.rglob('*.ts')) + list(self.workspace_path.rglob('*.js'))

        # Filter out node_modules and dist
        ts_files = [f for f in ts_files if 'node_modules' not in str(f) and 'dist' not in str(f)]

        for file_path in ts_files[:500]:  # Limit to 500 files
            try:
                with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self._extract_patterns(file_path, content)
            except Exception:
                pass

    def _extract_patterns(self, file_path: Path, content: str) -> None:
        """Extract coding patterns from file"""
        rel_path = str(file_path.relative_to(self.workspace_path))

        # Extract file naming
        if 'service.ts' in file_path.name:
            self.patterns['services'].append(rel_path)
        if 'module.ts' in file_path.name:
            self.patterns['modules'].append(rel_path)

        # Extract imports
        imports = re.findall(r'^import\s+.*?from\s+["\'](.+?)["\']', content, re.MULTILINE)
        self.patterns['imports'].extend(imports)

        # Extract decorators
        decorators = re.findall(r'@(\w+)\s*[\(\[]', content)
        self.patterns['decorators'].update(decorators)

        # Extract function patterns
        functions = re.findall(r'(?:async\s+)?(?:private\s+|public\s+|protected\s+)?(\w+)\s*\([^)]*\)\s*(?::\s*\w+)?\s*{', content)
        for func in functions:
            self.patterns['functions'][func].add(rel_path)

        # Extract error patterns
        if 'Exception' in content or 'Error' in content:
            errors = re.findall(r'(?:throw\s+new\s+)?(\w*(?:Exception|Error))\s*[\(\[]', content)
            self.patterns['errors'].extend(errors)

    def _create_instructions(self) -> str:
        """Generate the .copilot-instructions.md file"""

        instructions = """# Copilot Instructions

These instructions guide GitHub Copilot's code generation to match our project standards and best practices.

## Project Overview

This is a NestJS TypeScript backend project (prodfin-pc-dados-bff-credit-container-portal).
Copilot should generate code following our established patterns and conventions.

---

## Code Style & Formatting

### Formatting Standards
- **Indentation**: 2 spaces (not tabs)
- **Max line length**: 100 characters
- **String quotes**: Single quotes for code (except JSON)
- **Semicolons**: Always use
- **Arrow functions**: Prefer over function keyword

Example:
```typescript
// ✅ Good
const calculateTotal = (items: Item[]): number => {
  return items.reduce((sum, item) => sum + item.price, 0);
};

// ❌ Avoid
function calculateTotal(items) {
  return items.reduce(function(sum, item) {
    return sum + item.price
  }, 0)
}
```

### Trailing commas
- Use trailing commas in objects and arrays (TypeScript style)
- Makes diffs cleaner

```typescript
const config = {
  host: 'localhost',
  port: 3000,  // ← trailing comma
};
```

---

## Naming Conventions

### Files & Folders
- **Folder names**: kebab-case (e.g., `auth-module`, `http-service`)
- **Class files**: PascalCase (e.g., `UserService.ts`, `AuthController.ts`)
- **Interface files**: kebab-case (e.g., `user-request.interface.ts`)
- **Test files**: `.spec.ts` suffix (e.g., `user.service.spec.ts`)
- **Constants**: UPPER_SNAKE_CASE

Example structure:
```
src/
├── modules/
│   ├── auth-module/
│   │   ├── controllers/
│   │   │   └── AuthController.ts
│   │   ├── services/
│   │   │   └── AuthService.ts
│   │   ├── interfaces/
│   │   │   └── auth-request.interface.ts
│   │   └── AuthModule.ts
```

### Classes & Interfaces
- **Classes**: PascalCase **required** (e.g., `UserService`, `CreateAuthDto`)
- **Interfaces**: PascalCase with `I` prefix optional (e.g., `IUserRepository` or `UserRepository` interface)
- **DTOs**: PascalCase ending with `Dto` (e.g., `CreateUserDto`, `UpdateProfileDto`)
- **Exceptions**: PascalCase ending with `Exception` (e.g., `UserNotFoundException`)

```typescript
// ✅ Good
export class UserService {
  // ...
}

export interface CreateUserRequest {
  email: string;
  name: string;
}

export class UserNotFoundException extends Exception {
  // ...
}

// ❌ Avoid
export class user_service {  // lowercase
  // ...
}

export interface userRequest {  // not DTO named
  // ...
}
```

### Functions & Methods
- **Functions**: camelCase
- **Methods**: camelCase
- **Async functions**: Start with `async` keyword
- **Private methods**: Use `private` keyword

```typescript
// ✅ Good
async getUserById(id: string): Promise<User> {
  return this.userRepository.findById(id);
}

private validateEmail(email: string): boolean {
  return EMAIL_REGEX.test(email);
}

// ❌ Avoid
async GetUser(id) {  // PascalCase, no type
  //
}

getUserById(id: string) {  // Should be marked as implemented
```

### Variables & Constants
- **Constants**: UPPER_SNAKE_CASE with `const` keyword
- **Variables**: camelCase
- **Type prefixes**: Generally avoid (no `s_name`, `i_count`)

```typescript
// ✅ Good
const MAX_RETRY_ATTEMPTS = 3;
const DEFAULT_TIMEOUT_MS = 5000;

let userCount = 0;
let isProcessing = false;

// ❌ Avoid
const maxRetryAttempts = 3;  // Should be UPPER_SNAKE_CASE for constants
let s_userCount = 0;  // Avoid Hungarian notation
```

---

## NestJS-Specific Patterns

### Decorators & Controllers
Always use NestJS decorators:
- `@Controller(path)` for controllers
- `@Get()`, `@Post()`, `@Put()`, `@Delete()` for routes
- `@Injectable()` for services
- `@Module()` for modules
- `@Inject()` for dependency injection
- `@Param()`, `@Query()`, `@Body()` for route parameters

```typescript
// ✅ Good
@Controller('users')
@Injectable()
export class UserController {
  constructor(private readonly userService: UserService) {}

  @Get(':id')
  async getUserById(@Param('id') id: string): Promise<User> {
    return this.userService.getUserById(id);
  }

  @Post()
  async createUser(@Body() createUserDto: CreateUserDto): Promise<User> {
    return this.userService.create(createUserDto);
  }
}
```

### Dependency Injection
- Always inject dependencies through constructor
- Use `private readonly` for services
- Prefer interface types over concrete types

```typescript
// ✅ Good
@Injectable()
export class UserService {
  constructor(
    @Inject('USER_REPOSITORY') private readonly userRepo: IUserRepository,
    private readonly logger: Logger,
  ) {}
}

// ❌ Avoid
export class UserService {
  private userRepo = new UserRepository();  // Manual instantiation
}
```

### Error Handling
- Use custom exception classes from `src/common/exceptions`
- Throw specific exceptions with context
- Include error codes and HTTP status

```typescript
// ✅ Good
if (!user) {
  throw new UserNotFoundException({
    userId: id,
    message: `User with ID $${id} not found`,
  });
}

// ❌ Avoid
if (!user) {
  throw new Error('Not found');  // Generic error
}
```

---

## Import Organization

Always organize imports in this order:

1. **Node.js built-ins**: `fs`, `path`, `http`, etc.
2. **External packages**: `express`, `axios`, `lodash`, etc.
3. **NestJS imports**: `@nestjs/common`, `@nestjs/core`, etc.
4. **Internal absolute imports**: `src/common`, `src/modules`, etc.
5. **Internal relative imports**: `./services`, `../interfaces`, etc.
6. **Type imports**: `import type { ... } from ...`

```typescript
// ✅ Good import order
import * as fs from 'fs';
import * as path from 'path';

import axios from 'axios';
import { Injectable } from '@nestjs/common';

import { Logger } from 'src/common/logger';
import { UserRepository } from 'src/modules/users/repositories';

import { IUserService } from './interfaces/user-service.interface';
import UserService from './user.service';

import type { User } from './types/user.type';
```

---

## Testing Patterns

### Test File Structure
- Test files: `*.spec.ts`
- Located next to implementation file
- Use Jest with @nestjs/testing
- Follow Arrange-Act-Assert pattern

```typescript
// ✅ Good
describe('UserService', () => {
  let service: UserService;
  let repository: UserRepository;

  beforeEach(() => {
    // Arrange
    repository = new UserRepository();
    service = new UserService(repository);
  });

  describe('getUserById', () => {
    it('should return user when found', async () => {
      // Arrange
      const userId = '123';
      const expectedUser = { id: userId, name: 'John' };
      jest.spyOn(repository, 'findById').mockResolvedValue(expectedUser);

      // Act
      const result = await service.getUserById(userId);

      // Assert
      expect(result).toEqual(expectedUser);
      expect(repository.findById).toHaveBeenCalledWith(userId);
    });

    it('should throw UserNotFoundException when not found', async () => {
      // Arrange
      jest.spyOn(repository, 'findById').mockResolvedValue(null);

      // Act & Assert
      await expect(service.getUserById('999')).rejects.toThrow(
        UserNotFoundException,
      );
    });
  });
});
```

---

## Documentation Standards

### JSDoc Comments
- Use JSDoc for public methods and classes
- Include `@param`, `@returns`, `@throws` tags
- Keep descriptions concise

```typescript
// ✅ Good
/**
 * Retrieves a user by their unique identifier.
 * @param id - The user's unique ID
 * @returns Promise resolving to the user object
 * @throws UserNotFoundException when user is not found
 */
async getUserById(id: string): Promise<User> {
  // ...
}

// ❌ Avoid
// get user
async getUserById(id: string) {
  // ...
}
```

### Inline Comments
- Use sparingly for complex logic only
- Explain "why" not "what"
- Keep updated with code changes

```typescript
// ✅ Good
// Retry logic: Account for temporary connectivity issues
for (let attempt = 0; attempt < MAX_RETRIES; attempt++) {
  try {
    return await this.externalApi.call();
  } catch (error) {
    if (attempt < MAX_RETRIES - 1) {
      await this.sleep(RETRY_DELAY_MS * Math.pow(2, attempt));
    }
  }
}

// ❌ Avoid
// increment attempt
attempt++;
```

---

## Common Patterns to Follow

### HttpService Usage
Always use the centralized `HttpService` from `src/common`:

```typescript
// ✅ Good
import { HttpService } from 'src/common/http-request';

@Injectable()
export class ExternalApiService {
  constructor(private readonly httpService: HttpService) {}

  async fetchData(): Promise<Data> {
    return this.httpService.get(url);
  }
}
```

### Logger Usage
Use the centralized Logger:

```typescript
// ✅ Good
import { Logger } from 'src/common/logger';

@Injectable()
export class UserService {
  private logger = new Logger(UserService.name);

  async createUser(dto: CreateUserDto): Promise<User> {
    this.logger.info('Creating user', { email: dto.email });
    // ...
  }
}
```

### Environment Variables
Always use the ConfigService:

```typescript
// ✅ Good
import { ConfigService } from '@nestjs/config';

@Injectable()
export class AppService {
  constructor(private configService: ConfigService) {}

  getApiUrl(): string {
    return this.configService.getOrThrow('API_URL');
  }
}
```

---

## Anti-Patterns to Avoid

### ❌ DON'T

1. **Direct axios imports**
   - Use HttpService instead

2. **Generic error throwing**
   - Always use specific exception types

3. **Mixing camelCase and snake_case**
   - Be consistent

4. **Files without proper suffix**
   - Use `.service.ts`, `.controller.ts`, `.module.ts`

5. **Untyped parameters**
   - Always use TypeScript types

6. **Circular dependencies**
   - Refactor to break circles

7. **Magic numbers in code**
   - Extract to named constants

8. **Overly complex functions**
   - Extract to smaller, focused functions

9. **Missing error handling**
   - Always handle promises and errors

10. **Comments that duplicate code**
    - Only document "why", not "what"

---

## Do's ✅

1. ✅ Use const/let appropriately
2. ✅ Always add type annotations
3. ✅ Use async/await for promises
4. ✅ Follow single responsibility principle
5. ✅ Test public methods
6. ✅ Handle errors explicitly
7. ✅ Document complex logic
8. ✅ Use dependency injection
9. ✅ Extract reusable code
10. ✅ Keep functions small and focused

---

## When in Doubt

If unsure about a convention:
1. Look for similar code in the current codebase
2. Follow the existing pattern
3. Ask the team or check PR history
4. When creating new patterns, document them here

---

**Last Updated**: 6 de abril de 2026
**Maintained By**: Development Team
**Related Resources**: `CONTRIBUTING.md`, Architecture docs
"""

        return instructions

def main():
    workspace = "/Users/leonardo.copello/Documents/prodfin-pc-dados-bff-credit-container-portal"
    generator = CopilotInstructionsGenerator(workspace)
    instructions = generator.generate()

    # Save to root
    output_path = Path(workspace) / ".copilot-instructions.md"
    output_path.write_text(instructions)

    print(f"✅ Generated: {output_path}")
    print(f"\n📊 File size: {len(instructions):,} bytes")
    print("\n✨ Copilot Instructions ready to use!")
    print("\nNext steps:")
    print("1. Review the .copilot-instructions.md file")
    print("2. Commit to your repository")
    print("3. GitHub Copilot will automatically use these instructions")
    print("4. Test Copilot's behavior and refine instructions as needed")

if __name__ == "__main__":
    main()
