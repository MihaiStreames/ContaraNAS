# Declarative UI System - Implementation Plan

> **Estimated time:** 1 week remaining
> **Status:** In Progress (Phase 11 Complete)
> **Goal:** Module authors write Python only, UI renders automatically with consistent design

---

## Overview

Replace the current `get_tile_data() -> dict` pattern with a typed, declarative UI system where:

1. Modules define state as Pydantic models
2. Modules define UI as component trees
3. Framework handles rendering, updates, and actions
4. Frontend renders from JSON with a consistent design system

**Inspiration:** Simplified version
of [Airbnb's server-driven UI](https://medium.com/airbnb-engineering/a-deep-dive-into-airbnbs-server-driven-ui-system-842244c5f5) -
backend defines UI structure, frontend renders it.

---

## Phase 1: State Foundation

**Goal:** Modules can define typed state that persists and tracks changes.

### 1.1 ModuleState base class

- [x] Create `ModuleState(BaseModel)` base class
- [x] Add dirty tracking (know when state changed)
- [x] Add serialization for persistence
- [x] Add `commit()` method to signal "push update"

### 1.2 StateManager

- [x] Existing `StateManager` class handles enabled module persistence
- [x] Typed state is in-memory only (not persisted to disk)

### 1.3 Module base class updates

- [x] Add optional `State` inner class support
- [x] Add `typed_state` property that returns typed state
- [x] Create state instance on module instantiation
- [x] Commit callback emits events for frontend

### 1.4 Tests

- [x] Test state creation
- [x] Test dirty tracking
- [x] Test serialization/deserialization
- [x] Test module lifecycle with state
- [x] Test commit emits events

**Deliverable:** Can define `class State(ModuleState)` in a module and it works.

---

## Phase 2: UI Components

**Goal:** Define UI primitives as Pydantic models (matching DesignPlayground.svelte).

### 2.1 Base component

- [x] Create `Component(BaseModel)` base class
- [x] Implement `to_dict()` serialization
- [x] Handle children serialization (recursive)
- [x] Handle callable serialization (actions)

### 2.2 Layout components

- [x] `Stack` - direction, gap, align, justify, children (CSS flexbox)
- [x] `Grid` - columns, gap, children (CSS grid)

### 2.3 Card components

- [x] `Card` - icon, title, children, footer
- [x] `Tile` - module tile variant (icon, title, badge, stats, actions)
- [x] `Stat` - inline stat for tiles (label, value)

### 2.4 Data display components

- [x] `Text` - content, variant (body, secondary, muted, code)
- [x] `StatCard` - standalone stat card (label, value, icon, color, trend)
- [x] `Progress` - value, max, label, color
- [x] `Badge` - text, variant (default, primary, success, warning, error, info)
- [x] `Table` - columns, data, empty_message
- [x] `TableColumn` - key, label, width, align

### 2.5 Interactive components

- [x] `Button` - label, on_click, variant, size, icon, disabled, loading
- [x] `Input` - name, label, value, type, placeholder, disabled
- [x] `Select` - name, label, options, value, disabled
- [x] `SelectOption` - value, label
- [x] `Toggle` - name, label, checked, disabled
- [x] `Checkbox` - name, label, checked, disabled

### 2.6 Modal component

- [x] `Modal` - id, title, children, footer, closable

### 2.7 Feedback components

- [x] `Alert` - message, variant (info, success, warning, error), title
- [x] `Spinner` - size, label

### 2.8 Exports

- [x] Create `ContaraNAS/core/ui/__init__.py` with all exports
- [x] Tests for all components (22 tests)

**Deliverable:** Can import and instantiate all components.

---

## Phase 3: Action System

**Goal:** Module methods can be called from frontend via actions.

### 3.1 Action decorator

- [x] Create `@action` decorator
- [x] Register decorated methods
- [x] Handle async actions
- [x] Auto-commit state after action completes

### 3.2 Action results

- [x] `OpenModal(modal_id)` - signal to open a modal
- [x] `CloseModal(modal_id)` - signal to close a modal
- [x] `Notify(message, variant)` - show notification
- [x] `Refresh()` - force UI refresh
- [x] Support returning multiple results as list

### 3.3 ActionDispatcher

- [x] Create `ActionDispatcher` class
- [x] Route action calls to correct module/method
- [x] Handle action payloads (form data, etc.)
- [x] Process action results
- [x] Error handling

### 3.4 Action serialization

- [x] Generate action IDs for callables
- [x] Serialize action references in component props
- [x] Map action IDs back to methods on invoke

### 3.5 Tests

- [x] Test `@action` decorator registration
- [x] Test action dispatching to correct method
- [x] Test action results (OpenModal, Notify, etc.)
- [x] Test async actions
- [x] Test error handling

**Deliverable:** Can call module methods from frontend, get structured results.

---

## Phase 4: Module Integration

**Goal:** Modules define UI through get_tile() and get_modals().

### 4.1 Module base class updates

- [x] Add `get_tile(self) -> Tile` method (sync - just builds UI from state)
- [x] Add `get_modals(self) -> list[Modal]` method (sync - just builds UI from state)
- [x] Add `render_tile()` - serializes tile to dict
- [x] Add `render_modals()` - serializes modals to dicts
- [x] Add `render_ui()` - returns complete UI state

**Note:** `get_tile()` and `get_modals()` are synchronous because they only construct UI objects from existing state. No
I/O is needed - state is already loaded via `start_monitoring()` or updated via actions.

### 4.2 Backwards compatibility

- [x] Keep `get_tile_data()` working (deprecated, emits warning)
- [x] If `get_tile()` raises NotImplementedError, fall back to `get_tile_data()`
- [x] Log deprecation warnings

### 4.3 UI rendering pipeline

- [x] On `commit()`, trigger UI re-render
- [x] Call `get_tile()` and `get_modals()`
- [x] Serialize component tree
- [ ] Compare with previous (optional optimization)
- [x] Emit update event

### 4.4 Tests

- [x] Test `get_tile()` returns Component
- [x] Test `render_ui()` serialization
- [x] Test backwards compatibility with `get_tile_data()`

**Deliverable:** Modules can define UI, serializes to JSON.

---

## Phase 5: API Layer

**Goal:** Frontend can fetch UI and invoke actions.

### 5.1 UI endpoints

- [x] `GET /api/modules/{name}/ui` - full UI (tile + modals)
- [x] `GET /api/modules/{name}/tile` - just tile
- [x] `GET /api/modules/{name}/modals` - just modals

### 5.2 Action endpoint

- [x] `POST /api/modules/{name}/action/{action_name}`
- [x] Accept JSON payload for action arguments
- [x] Return action results (success, open_modal, notify, etc.)
- [x] Error responses

### 5.3 Initial state endpoint

- [x] `GET /api/state` - full app state on connect
- [x] All modules' UI in one response
- [x] App-level state (active modal, etc.)

**Deliverable:** Can curl the API and get UI JSON back.

---

## Phase 6: WebSocket Integration

**Goal:** UI updates push to frontend in real-time.

### 6.1 New message types

- [x] `module_ui` - full UI update for a module
- [x] `app_state` - app-level state (active modal, notifications)
- [x] `full_state` - complete app state on connect

### 6.2 Update triggers

- [x] On `commit()`, push `module_ui` message
- [x] On module enable/disable, push UI update
- [ ] On action result, push relevant updates (handled by commit())

### 6.3 Connection handling

- [x] On new connection, send full state
- [x] Handle reconnection (resend full state)

### 6.4 EventBus decoupling

- [x] StreamManager uses direct callbacks instead of EventBus
- [x] Modules call `_on_state_commit()` which triggers callback
- [x] ModuleManager wires up callback to StreamManager

**Deliverable:** State changes push to frontend automatically.

---

## Phase 7: Type Generation

**Goal:** TypeScript types auto-generated from Python via OpenAPI.

### 7.1 OpenAPI Schema Generation

- [x] Create `backend/ContaraNAS/api/schemas/` with typed Pydantic models
- [x] Create `scripts/generate_api_types.py` to export OpenAPI JSON
- [x] Schemas mirror UI components for JSON serialization
- [x] Handle discriminated unions with `type` field
- [x] Handle nested component types
- [x] Handle all field types (Literal, Optional, list, dict, tuple)

### 7.2 TypeScript Generation

- [x] Install `openapi-typescript` for type generation
- [x] Generate `frontend/src/lib/api/types.generated.ts` from OpenAPI
- [x] Generate `frontend/src/lib/api/index.ts` with convenient aliases
- [x] Export `ComponentSchema` union type
- [x] Export all response types
- [x] Export `isComponentType` type guard

### 7.3 Build integration

- [x] Create `scripts/generate-types.sh` that runs all steps
- [x] Add `pnpm run generate` to call the shell script
- [x] TypeScript compilation check verifies generated types

**Deliverable:** TypeScript types match Python, auto-updated via `pnpm run generate`.

---

## Phase 8: Design System

**Goal:** Define visual language before building components.

### 8.1 Design tokens

- [x] Colors (background, surface, text, accent, status colors)
- [x] Typography (font family, sizes, weights)
- [x] Spacing scale (xs, sm, md, lg, xl)
- [x] Border radius
- [x] Shadows

### 8.2 Component designs (see DesignPlayground.svelte)

- [x] Card (with header, content, footer)
- [x] Module Tile (icon, title, badge, stats, actions)
- [x] Stat / StatCard (value + label, with optional icon/trend)
- [x] Button (primary, secondary, ghost, danger + sizes + loading)
- [x] Table (with header, rows, badges)
- [x] Modal (header, body, footer, close button)
- [x] Form inputs (Input, Select, Toggle, Checkbox)
- [x] Progress bar (with labels)
- [x] Badge (default, primary, success, warning, error, info)
- [x] Alert (info, success, warning, error)

### 8.3 Design documentation

- [x] Document design decisions
- [x] Create reference for component usage

**Deliverable:** Know exactly what each component looks like.

---

## Phase 9: Frontend Components

**Goal:** Svelte components that render from JSON (matching DesignPlayground.svelte).

### 9.1 Setup

- [x] Create `frontend/src/lib/ui/` directory structure
- [x] Import generated types
- [x] Set up component registry pattern
- [x] Extract shared CSS to `components.css`
- [x] Create `+layout.svelte` for global CSS imports

### 9.2 Layout components

- [x] `Stack.svelte` (flex container, direction, gap, align, justify)
- [x] `Grid.svelte` (CSS grid, columns, gap)

### 9.3 Card components

- [x] `Card.svelte` (icon, title, content, footer)
- [x] `Tile.svelte` (module tile: icon, title, badge, stats, content, actions)
- [x] `Stat.svelte` (inline stat for tiles: label, value)
- [x] `StatCard.svelte` (standalone stat: label, value, icon, color, trend)

### 9.4 Data display components

- [x] `Text.svelte` (body, secondary, muted, code variants)
- [x] `Progress.svelte` (value, max, label, sublabel, color)
- [x] `Badge.svelte` (default, primary, success, warning, error, info)
- [x] `Table.svelte` (columns, data, empty_message)

### 9.5 Interactive components

- [x] `Button.svelte` (primary, secondary, ghost, danger + sizes + icon + loading)
- [x] `Input.svelte` (text, password, email, number)
- [x] `Select.svelte` (options, value)
- [x] `Toggle.svelte` (switch)
- [x] `Checkbox.svelte`

### 9.6 Modal system

- [x] `Modal.svelte` (id, title, children, footer, closable)
- [x] Modal state management (open/close)
- [x] Backdrop and ESC key handling

### 9.7 Feedback components

- [x] `Alert.svelte` (info, success, warning, error + optional title)
- [x] `Spinner.svelte` (sm, md, lg + optional label)
- [ ] Notification toast system (deferred to Phase 10)

### 9.8 Component registry

- [x] Create `registry.ts` mapping type names to components
- [x] Create `ComponentRenderer.svelte` for dynamic rendering
- [x] Create `Icon.svelte` for dynamic icon loading
- [x] Handle unknown component types gracefully

### 9.9 Refactoring

- [x] Refactor `DesignPlayground.svelte` to use imported components
- [x] Verify build succeeds

**Deliverable:** All Svelte components built and styled.

---

## Phase 10: Frontend Renderer

**Goal:** Render component trees from JSON.

### 10.1 ComponentRenderer

- [x] Create `ComponentRenderer.svelte`
- [x] Look up component from registry by type
- [x] Pass props to component
- [x] Recursively render children
- [x] Handle action props (convert to handlers)

### 10.2 Action handling

- [x] Create `actions.ts` utility
- [x] Convert action references to click handlers
- [x] POST to action endpoint on trigger
- [x] Handle action results (open modal, notify, etc.)

### 10.3 UI store

- [x] Create store for module UIs (`ui.svelte.ts`)
- [x] Create auth store (`auth.svelte.ts`)
- [x] Handle incoming WebSocket updates
- [x] Provide UI state to components

### 10.4 Integration

- [x] Create pairing screen for initial authentication
- [x] Update dashboard to use ComponentRenderer for tiles
- [x] Render modals from module definitions
- [x] Handle module enable/disable
- [x] Create WebSocket service for real-time updates
- [x] Create API client for REST endpoints

**Deliverable:** End-to-end rendering works.

---

## Phase 11: Migration

**Goal:** Convert existing modules to new system.

### 11.0 Legacy code removal (done in Phase 6)

- [x] Remove `get_tile_data()` from Module base
- [x] Remove `update_state()` from Module base
- [x] Remove `self.state` dict from Module base
- [x] Update tests to use callback pattern instead of EventBus

### 11.1 Steam module

- [x] Define `SteamState(ModuleState)`
- [x] Move state from controller instance vars to state class
- [x] Implement `get_tile()`
- [x] Implement `get_modals()` (games list, libraries)
- [x] Convert actions (refresh, etc.)
- [x] Delete SteamController (logic moved to module)
- [x] Create views package for UI separation

### 11.2 System Monitor module

- [x] Define `SysMonitorState(ModuleState)`
- [x] Move state from controller instance vars to state class
- [x] Implement `get_tile()`
- [x] Implement `get_modals()` (system details, processes, etc.)
- [x] Convert actions (refresh, etc.)
- [x] Delete SysMonitorController (logic moved to module)
- [x] Create views package for UI separation

### 11.3 Cleanup

- [x] Remove EventBus (not used by modules)
- [x] All 57 tests passing
- [x] Frontend build successful

**Deliverable:** All modules use new system.

---

## Phase 12: Documentation

**Goal:** Community can build modules.

### 12.1 Module development guide

- [x] Defining state
- [x] Available components
- [x] Building tiles
- [x] Building modals
- [x] Actions and interactions
- [x] Forms and user input
- [x] Best practices

### 12.2 Component reference

- [x] Document each component
- [x] Props, examples, do's and don'ts

### 12.3 Example module / template

- [x] Create minimal example module (in docs)
- [x] Create more complex example module (TaskModule in actions.md)
- [ ] Template repository or cookiecutter (optional, for later)

**Deliverable:** Docs ready for community.

---

## Phase 13: Polish

**Goal:** Production ready.

### 13.1 Error handling

- [ ] Handle `get_tile()` exceptions gracefully
- [ ] Handle action exceptions
- [ ] Show error states in UI

### 13.2 Performance

- [ ] Profile rendering
- [ ] Optimize if needed (lazy loading, virtualization for tables)

### 13.3 Testing

- [ ] Unit tests for components
- [ ] Integration tests for full flow
- [ ] Visual regression tests (optional)

### 13.4 Cleanup

- [ ] Remove all legacy code paths
- [ ] Remove backwards compatibility shims
- [ ] Final review

**Deliverable:** Stable, tested, documented system.

---

## Dependencies / Blockers

- Phase 2-4 can be done in parallel
- Phase 5-6 depend on Phase 4
- Phase 8 should happen before Phase 9 (design before build)
- Phase 9-10 depend on Phase 7 (types)
- Phase 11 depends on Phase 10
