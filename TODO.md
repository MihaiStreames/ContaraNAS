# Declarative UI System - Implementation Plan

> **Estimated time:** 4-6 weeks  
> **Status:** In Progress (Phase 1 Complete)  
> **Goal:** Module authors write Python only, UI renders automatically with consistent design

---

## Overview

Replace the current `get_tile_data() -> dict` pattern with a typed, declarative UI system where:

1. Modules define state as Pydantic models
2. Modules define UI as component trees
3. Framework handles rendering, updates, and actions
4. Frontend renders from JSON with a consistent design system

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

**Goal:** Define all UI primitives as Pydantic models.

### 2.1 Base component

- [ ] Create `Component(BaseModel)` base class
- [ ] Implement `to_dict()` serialization
- [ ] Handle children serialization (recursive)
- [ ] Handle callable serialization (actions)

### 2.2 Layout components

- [ ] `Card` - title, subtitle, icon, children
- [ ] `Stack` - direction, gap, align, justify, children
- [ ] `Grid` - columns, gap, children
- [ ] `Divider` - optional label
- [ ] `Spacer` - size

### 2.3 Data display components

- [ ] `Text` - content, variant, color
- [ ] `Heading` - content, level
- [ ] `Stat` - label, value, unit, icon, color, trend
- [ ] `Progress` - value, max, label, color
- [ ] `Badge` - text, variant
- [ ] `Table` - columns, data, empty_message
- [ ] `TableColumn` - key, label, width, align
- [ ] `List` - items, divided
- [ ] `ListItem` - title, subtitle, icon, trailing, on_click
- [ ] `Image` - src, alt, width, height, fit
- [ ] `Icon` - name, size, color
- [ ] `Empty` - icon, title, description, action

### 2.4 Interactive components

- [ ] `Button` - label, on_click, variant, size, icon, disabled, loading
- [ ] `IconButton` - icon, on_click, variant, size, tooltip
- [ ] `Input` - name, label, value, type, placeholder, on_change
- [ ] `Select` - name, label, options, value, on_change
- [ ] `SelectOption` - value, label
- [ ] `Toggle` - name, label, checked, on_change
- [ ] `Checkbox` - name, label, checked, on_change
- [ ] `Form` - on_submit, children

### 2.5 Modal components

- [ ] `Modal` - id, title, size, children, footer, closable

### 2.6 Feedback components

- [ ] `Alert` - message, variant, title
- [ ] `Spinner` - size, label

### 2.7 Exports

- [ ] Create `ContaraNAS/core/ui/__init__.py` with all exports

**Deliverable:** Can import and instantiate all components.

---

## Phase 3: Action System

**Goal:** Module methods can be called from frontend via actions.

### 3.1 Action decorator

- [ ] Create `@action` decorator
- [ ] Register decorated methods
- [ ] Handle async actions
- [ ] Auto-commit state after action completes

### 3.2 Action results

- [ ] `OpenModal(modal_id)` - signal to open a modal
- [ ] `CloseModal(modal_id)` - signal to close a modal  
- [ ] `Notify(message, variant)` - show notification
- [ ] `Refresh()` - force UI refresh
- [ ] Support returning multiple results as list

### 3.3 ActionDispatcher

- [ ] Create `ActionDispatcher` class
- [ ] Route action calls to correct module/method
- [ ] Handle action payloads (form data, etc.)
- [ ] Process action results
- [ ] Error handling

### 3.4 Action serialization

- [ ] Generate action IDs for callables
- [ ] Serialize action references in component props
- [ ] Map action IDs back to methods on invoke

**Deliverable:** Can call module methods from frontend, get structured results.

---

## Phase 4: Module Integration

**Goal:** Modules define UI through get_tile() and get_modals().

### 4.1 Module base class updates

- [ ] Add `get_tile(self) -> Component | None` method
- [ ] Add `get_modals(self) -> list[Modal]` method
- [ ] Add `render_tile()` - serializes tile to dict
- [ ] Add `render_modals()` - serializes modals to dicts
- [ ] Add `render_ui()` - returns complete UI state

### 4.2 Backwards compatibility

- [ ] Keep `get_tile_data()` working
- [ ] If `get_tile()` returns None, fall back to `get_tile_data()`
- [ ] Log deprecation warnings

### 4.3 UI rendering pipeline

- [ ] On `commit()`, trigger UI re-render
- [ ] Call `get_tile()` and `get_modals()`
- [ ] Serialize component tree
- [ ] Compare with previous (optional optimization)
- [ ] Emit update event

**Deliverable:** Modules can define UI, serializes to JSON.

---

## Phase 5: API Layer

**Goal:** Frontend can fetch UI and invoke actions.

### 5.1 UI endpoints

- [ ] `GET /api/modules/{name}/ui` - full UI (tile + modals)
- [ ] `GET /api/modules/{name}/tile` - just tile
- [ ] `GET /api/modules/{name}/modals` - just modals

### 5.2 Action endpoint

- [ ] `POST /api/modules/{name}/action/{action_name}`
- [ ] Accept JSON payload for action arguments
- [ ] Return action results (success, open_modal, notify, etc.)
- [ ] Error responses

### 5.3 Initial state endpoint

- [ ] `GET /api/state` - full app state on connect
- [ ] All modules' UI in one response
- [ ] App-level state (active modal, etc.)

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

### 8.2 Component designs

- [x] Card - sketch/design
- [x] Stat - sketch/design
- [x] Button variants - sketch/design
- [x] Table - sketch/design
- [x] Modal - sketch/design
- [x] Form inputs - sketch/design
- [x] Progress - sketch/design
- [x] Badge - sketch/design

### 8.3 Design documentation

- [x] Document design decisions
- [x] Create reference for component usage

**Deliverable:** Know exactly what each component looks like.

---

## Phase 9: Frontend Components

**Goal:** Svelte components that render from JSON.

### 9.1 Setup

- [ ] Create `frontend/src/lib/ui/` directory structure
- [ ] Import generated types
- [ ] Set up component registry pattern

### 9.2 Layout components

- [ ] `Card.svelte`
- [ ] `Stack.svelte`
- [ ] `Grid.svelte`
- [ ] `Divider.svelte`
- [ ] `Spacer.svelte`

### 9.3 Data display components

- [ ] `Text.svelte`
- [ ] `Heading.svelte`
- [ ] `Stat.svelte`
- [ ] `Progress.svelte`
- [ ] `Badge.svelte`
- [ ] `Table.svelte`
- [ ] `List.svelte`
- [ ] `ListItem.svelte`
- [ ] `Image.svelte`
- [ ] `Icon.svelte`
- [ ] `Empty.svelte`

### 9.4 Interactive components

- [ ] `Button.svelte`
- [ ] `IconButton.svelte`
- [ ] `Input.svelte`
- [ ] `Select.svelte`
- [ ] `Toggle.svelte`
- [ ] `Checkbox.svelte`
- [ ] `Form.svelte`

### 9.5 Modal system

- [ ] `Modal.svelte`
- [ ] Modal state management (open/close)
- [ ] Backdrop and focus trap

### 9.6 Feedback components

- [ ] `Alert.svelte`
- [ ] `Spinner.svelte`
- [ ] Notification system

### 9.7 Component registry

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

### 11.2 Other modules

- [ ] List all modules to migrate
- [ ] Migrate one by one
- [ ] Remove legacy code paths when all migrated

**Deliverable:** All modules use new system.

---

## Phase 12: Documentation

**Goal:** Community can build modules.

### 12.1 Module development guide

- [ ] Defining state
- [ ] Available components
- [ ] Building tiles
- [ ] Building modals
- [ ] Actions and interactions
- [ ] Forms and user input
- [ ] Best practices

### 12.2 Component reference

- [ ] Document each component
- [ ] Props, examples, do's and don'ts

### 12.3 Example module

- [ ] Create minimal example module
- [ ] Create more complex example module
- [ ] Template repository or cookiecutter

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
