# Documentation TODO List

---

## 🟢 Low Priority - Enhancements

### 1. Remove Redundant Examples

**Files to update:** `actions.md`, `modal.md`

- [ ] TaskModule example appears in both `actions.md` (complete) and partially in other files
- [ ] Consider moving complete examples to a dedicated `examples.md` or keeping in one place only
- [ ] Add cross-references instead of duplicating

### 2. Architecture Overview Page

**File to create:** `docs/docs/architecture.md` (NEW)

- [ ] Diagram showing: Module → State → commit() → WebSocket → Frontend render
- [ ] Explain the server-driven UI concept
- [ ] Document type generation pipeline (Python → OpenAPI → TypeScript)
- [ ] Document WebSocket message types (`module_ui`, `app_state`, `full_state`)

### 3. API Reference

**File to create:** `docs/docs/api/reference.md` (NEW)

- [ ] Document REST endpoints:
  - `GET /api/modules` - list modules
  - `GET /api/modules/{name}/ui` - get module UI
  - `POST /api/modules/{name}/enable` - enable module
  - `POST /api/modules/{name}/disable` - disable module
  - `POST /api/modules/{name}/action/{action}` - execute action
  - `GET /api/state` - full app state
- [ ] Document WebSocket protocol
- [ ] Document authentication (pairing flow)

---

## 🔵 Style & Consistency

### 4. Unify Documentation Style

**Files to update:** All docs in `docs/docs/`

- [ ] Mix Arch Wiki style (concise, direct, no fluff) with current style across entire documentation
- [ ] Remove unnecessary prose and filler text
- [ ] Keep code examples and tables
- [ ] Ensure consistent formatting across all pages

---

## 🔵 Verification Tasks

### 5. Cross-Reference Check

- [ ] All "See Also" links work
- [ ] All internal doc links are valid
- [ ] Navigation structure in mkdocs.yml matches actual files

---

## ✅ Completed

### Missing Props Documentation

**Files updated:** `cards.md`, `layout.md`, `interactive.md`, `modal.md`

- [x] Add `rowspan` to Tile props table
- [x] Add `grow` prop to Stack props table (already documented)
- [x] Add `on_click` prop to Stack props table (already documented)
- [x] Add `row_height` to Grid props table (already documented)
- [x] Add `icon_only` prop to Button props table
- [x] Add `size` prop to Modal props table

### Module Lifecycle Documentation

**File created:** `docs/docs/modules/lifecycle.md`

- [x] Document `initialize()` method
- [x] Document `start_monitoring()` method
- [x] Document `stop_monitoring()` method
- [x] Document `enable()` / `disable()` methods
- [x] Document `init_flag` vs `enable_flag`
- [x] Document full lifecycle flow
- [x] Add lifecycle diagram (mermaid)
- [x] Document that `initialize()` is only called once

### `module.json` Reference

**File created:** `docs/docs/modules/module-json.md`

- [x] Document all required fields
- [x] Document `engine.contaranas` version constraint
- [x] Document `platforms` array
- [x] Document `dependencies.python`
- [x] Document `dependencies.python_platform`
- [x] Document `dependencies.system`
- [x] Document `capabilities` object
- [x] Document `category`, `tags`, URLs
- [x] Document `requires_network`
- [x] Provide complete example

### Publishing Guide

**File created:** `docs/docs/modules/publishing.md`

- [x] Renamed from `community.md`
- [x] Development guidelines (code quality, state, UI, dependencies)
- [x] Marketplace placeholder
- [x] Removed tutorial content (covered by other docs)
- [x] Removed installation/troubleshooting sections

### Clean State Access Pattern

**Already documented in:** `docs/docs/modules/lifecycle.md`

- [x] `@property` pattern for state access
- [x] Explanation of avoiding None checks

### `get_modals()` Method Documentation

**File updated:** `docs/docs/modules/ui/modal.md`

- [x] Expanded `get_modals()` section with key points
- [x] Added dynamic modals example
- [x] Added to "Key Concepts" table in index.md

### UI Components Documentation

**Already documented in:** `docs/docs/modules/ui/display.md`, `interactive.md`

- [x] StatSmall - already documented with props
- [x] Image - already documented with props
- [x] Tabs - already documented with props
- [x] Tab - already documented with props
- [x] Table sorting props - already documented
- [x] Progress size prop - already documented

### Import List

**File updated:** `docs/docs/modules/ui/index.md`

- [x] Added StatSmall, LineChart, SegmentedProgress, SegmentedProgressSegment, Image
- [x] Added Tabs, Tab

---

## Summary

| Priority | Count | Description |
|----------|-------|-------------|
| 🟢 Low | 3 | Architecture, API reference, redundant examples |
| 🔵 Style | 1 | Unify documentation style |
| 🔵 Verify | 1 | Cross-references |

**Total remaining: ~5 tasks**
