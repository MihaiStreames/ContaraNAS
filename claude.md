# Claude Development Guidelines for ContaraNAS

## Code Organization Principles

### 1. Code Splitting
- **Always split code into smaller, manageable modules**
- Break down large components into smaller, focused sub-components
- Extract reusable logic into utility functions
- Separate business logic from presentation logic
- Keep files under 300 lines when possible

### 2. Constants Management
- **Use constants across the app for each module**
- Define module-specific constants in dedicated constant files
- Group related constants together (e.g., `steam.constants.ts`, `monitoring.constants.ts`)
- Use TypeScript enums or const objects for related values
- Avoid magic numbers and strings - always use named constants

### 3. Codebase Cleanliness
- Maintain consistent code structure across modules
- Remove unused imports, variables, and code
- Follow established patterns in the codebase
- Keep components focused on a single responsibility
- Use descriptive names for variables, functions, and components

## File Structure Best Practices

```
module/
├── components/          # UI components
├── constants/          # Module constants
├── types/             # TypeScript types/interfaces
├── utils/             # Helper functions
└── services/          # API calls and business logic
```

## Example Constant Organization

```typescript
// steam.constants.ts
export const STEAM_SORT_OPTIONS = {
  SIZE: 'size',
  NAME: 'name',
  LAST_PLAYED: 'lastPlayed'
} as const;

export const STEAM_GRID_COLUMNS = 4;
export const STEAM_CACHE_EXPIRY = 3600000; // 1 hour
```

## General Guidelines
- Prefer composition over inheritance
- Use TypeScript strictly - avoid `any` types
- Write self-documenting code with clear naming
- Extract complex logic into well-named functions
- Keep the UI layer thin and delegate to helper functions
