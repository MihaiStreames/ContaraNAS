# Documentation TODO List

---

## Module Developer Docs

> Arch Wiki style + your voice. Practical, reference-oriented, scannable.

### Style Pass

**Files to update:** All docs in `docs/docs/`

**What to cut (bad verbosity):**

- "This page explains how to..." / "The following section covers..."
- Empty intro sentences that don't add information
- Redundant explanations of things already shown in code

**What to keep (good content):**

- Short intro sentences explaining purpose
- "When to use" / "Why" guidance where it helps
- Patterns and examples sections
- Notes on common mistakes or important behaviors
- The explanatory context (e.g., how auto-commit timing works, when to use ActionRef)

**Style:**

- [x] Apply to all docs
- [x] Keep structure clean with tables and code examples
- [x] Ensure consistent formatting

**Main index.md:**

- [x] Point module developers to the Modules section
- [x] Point curious readers to the Internals section (once created) — added as HTML comment

### Cleanup

- [x] ~~Remove redundant TaskModule example~~ — Reviewed: no actual duplication found. Examples in `actions.md` (action results) and `modal.md` (modal definitions) serve distinct purposes with appropriate cross-references already in place.

### Verification

- [x] All "See Also" links work
- [x] All internal doc links are valid
- [x] Navigation structure in mkdocs.yml matches actual files

---

## Internals / Architecture (Blog-style)

> Narrative, explanatory, interesting reads for the curious. Not required for module authors.

**Location:** `docs/docs/internals/` (NEW)

- [ ] **Render Pipeline** - Module → State → commit() → WebSocket → Frontend
- [ ] **Server-Driven UI** - The concept and why it works this way
- [ ] **Type Generation** - Python → OpenAPI → TypeScript pipeline
- [ ] **WebSocket Protocol** - Message types (`module_ui`, `app_state`, `full_state`)
- [ ] **REST API** - Endpoints overview (modules, actions, state)
- [ ] **Authentication** - Pairing flow

---

## Core Contributor Docs

> The code is the documentation. Self-selecting audience.

- [ ] `CONTRIBUTING.md` - Setup instructions, conventions, how to run locally

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

| Scope | Tasks | Notes |
|-------|-------|-------|
| Module Docs | 0 | ✅ Complete |
| Internals | 6 | Blog-style articles (low priority) |
| Contributor | 1 | CONTRIBUTING.md |
