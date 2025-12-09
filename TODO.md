# Declarative UI System - Implementation Plan

> **Estimated time:** 4-6 weeks  
> **Status:** In Progress (Phase 5 Complete)  
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

- [ ] `module_ui` - full UI update for a module
- [ ] `app_state` - app-level state (active modal, notifications)
- [ ] Document message format

### 6.2 Update triggers

- [ ] On `commit()`, push `module_ui` message
- [ ] On action result, push relevant updates
- [ ] On module enable/disable, push UI or removal

### 6.3 Connection handling

- [ ] On new connection, send full state
- [ ] Handle reconnection (resend full state)

**Deliverable:** State changes push to frontend automatically.

---

## Phase 7: Type Generation

**Goal:** TypeScript types auto-generated from Python.

### 7.1 Generation script

- [ ] Create `scripts/generate_ui_types.py`
- [ ] Read all Component subclasses
- [ ] Convert Pydantic fields to TypeScript types
- [ ] Handle Literal types (unions)
- [ ] Handle nested types
- [ ] Handle list/dict types
- [ ] Handle optional types

### 7.2 Output

- [ ] Generate `frontend/src/lib/ui/types.generated.ts`
- [ ] Export all component prop interfaces
- [ ] Export `ComponentNode` union type
- [ ] Export action-related types

### 7.3 Build integration

- [ ] Add npm script to run generation
- [ ] Run on `npm run dev` and `npm run build`
- [ ] Git-ignore or commit generated file (decide)

**Deliverable:** TypeScript types match Python, auto-updated.

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

- [ ] Create `frontend/src/lib/ui/` directory structure
- [ ] Import generated types
- [ ] Set up component registry pattern

### 9.2 Layout components

- [ ] `Stack.svelte` (flex container, direction, gap, align, justify)
- [ ] `Grid.svelte` (CSS grid, columns, gap)

### 9.3 Card components

- [ ] `Card.svelte` (icon, title, content, footer)
- [ ] `Tile.svelte` (module tile: icon, title, badge, stats, content, actions)
- [ ] `Stat.svelte` (inline stat for tiles: label, value)
- [ ] `StatCard.svelte` (standalone stat: label, value, icon, color, trend)

### 9.4 Data display components

- [ ] `Text.svelte` (body, secondary, muted, code variants)
- [ ] `Progress.svelte` (value, max, label, sublabel, color)
- [ ] `Badge.svelte` (default, primary, success, warning, error, info)
- [ ] `Table.svelte` (columns, data, empty_message)

### 9.5 Interactive components

- [ ] `Button.svelte` (primary, secondary, ghost, danger + sizes + icon + loading)
- [ ] `Input.svelte` (text, password, email, number)
- [ ] `Select.svelte` (options, value)
- [ ] `Toggle.svelte` (switch)
- [ ] `Checkbox.svelte`

### 9.6 Modal system

- [ ] `Modal.svelte` (id, title, children, footer, closable)
- [ ] Modal state management (open/close)
- [ ] Backdrop and focus trap

### 9.7 Feedback components

- [ ] `Alert.svelte` (info, success, warning, error + optional title)
- [ ] `Spinner.svelte` (sm, md, lg + optional label)
- [ ] Notification toast system

### 9.8 Component registry

- [ ] Create `registry.ts` mapping type names to components
- [ ] Handle unknown component types gracefully

**Deliverable:** All Svelte components built and styled.

---

## Phase 10: Frontend Renderer

**Goal:** Render component trees from JSON.

### 10.1 ComponentRenderer

- [ ] Create `ComponentRenderer.svelte`
- [ ] Look up component from registry by type
- [ ] Pass props to component
- [ ] Recursively render children
- [ ] Handle action props (convert to handlers)

### 10.2 Action handling

- [ ] Create `actions.ts` utility
- [ ] Convert action references to click handlers
- [ ] POST to action endpoint on trigger
- [ ] Handle action results (open modal, notify, etc.)

### 10.3 UI store

- [ ] Create store for module UIs
- [ ] Handle incoming WebSocket updates
- [ ] Provide UI state to components

### 10.4 Integration

- [ ] Update dashboard to use ComponentRenderer for tiles
- [ ] Render modals from module definitions
- [ ] Handle module enable/disable

**Deliverable:** End-to-end rendering works.

---

## Phase 11: Migration

**Goal:** Convert existing modules to new system.

### 11.1 Steam module

- [ ] Define `SteamState(ModuleState)`
- [ ] Move state from controller instance vars to state class
- [ ] Implement `get_tile()`
- [ ] Implement `get_modals()` (games list, libraries)
- [ ] Convert actions (refresh, etc.)
- [ ] Remove old `get_tile_data()`
- [ ] Test thoroughly

### 11.2 System Monitor module

- [ ] Define `SysMonitorState(ModuleState)`
- [ ] Move state from controller instance vars to state class
- [ ] Implement `get_tile()`
- [ ] Implement `get_modals()` (system details, processes, etc.)
- [ ] Convert actions (refresh, etc.)
- [ ] Remove old `get_tile_data()`
- [ ] Test thoroughly

### 11.3 Cleanup

- [ ] Remove legacy code paths when all migrated
- [ ] Remove EventBus (replaced by commit/WebSocket updates)

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
