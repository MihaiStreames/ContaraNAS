# Feature Notes & UI Redesign

## Simple Module Ideas

### CPU Modules

- **CPU Usage Percentage** - Single rounded progress bar showing current CPU usage
- **CPU Name Display** - Simple text display of CPU model/name
- **CPU Usage History** - Line chart showing recent CPU usage over time
- **CPU Temperature per Core** - Bar chart with one bar per core showing temperatures
- **CPU Usage per Core** - Bar chart showing usage percentage per core

### Network Modules

- **NAS Address Display** - Shows IP address and port
- **Interface Monitor** - Per-interface monitoring showing:
  - In/out traffic graph (dual-line chart)
  - Live in/out rates (kbps/Mbps/Gbps)
  - Link state indicator (up/down)

### Memory Module

- **Memory Pie Chart** - RAM breakdown showing:
  - Used
  - Free
  - Cached
  - Services (?) *(depends on DTO - needs verification)*

### System Info Module

- **Basic System Info Card** - Displays:
  - CPU name
  - Motherboard name
  - OS
  - Memory size
  - Disk size(s)
  - GPU (if any - includes iGPUs)

### Storage Module

- **Single Disk Monitor** - Minimal display showing:
  - Disk name
  - Mount point
  - Type
  - Usage (numbers only)

  *Note: Uncertain about final design for this one*

---

## Component Gaps

- **Circular/Radial Progress** - Need a ring/gauge component for CPU usage percentage (linear Progress won't work)
- **Dual-line chart** - LineChart only supports single series; needed for network in/out traffic
- **Pie/Donut chart** - Only have SegmentedProgress (linear); could be acceptable substitute for Memory breakdown

---

## UI Redesign Proposals

### Navigation

- **Sidebar (Left)** - Primary navigation for:
  - Dashboard
  - Marketplace
  - Settings (?)
- **Sidebar Style**:
  - Not collapsible (always visible)
  - Tab items have icons on the right side
- **Status**: ✅ Implemented - Sidebar.svelte added to Dashboard

### Header Changes

- **Notifications Button** - Store and access all notifications from header
- **Logs/Errors Button** - Opens interface to view:
  - .log files from cache (formatted nicely)
  - Errors (if any - usually none)
- **Connection Status** - Replace badge with filled circle indicator:
  - Green = connected
  - Red = disconnected
  - Positioned right of "ContaraNAS" title, vertically centered
  - Hover shows: "Connected to [ip:port]!"
- **Unpair** - Move to Settings (replaced by app shutdown button in header)
- **Shutdown Button** - New button to close the application
  - Uses Tauri API (`getCurrentWindow().close()`) - no backend action needed
- **Status**: ✅ Implemented - Header split into Header.svelte with:
  - Connection indicator (circle)
  - Icon buttons (Bell, FileText, Power)
  - Shutdown wired to Tauri window close

### Dashboard Configuration

- **Module Management** - Allow users to:
  - Add/remove modules from dashboard
  - Position modules anywhere on dashboard
  - See list of available (installed) modules
  - Drag & drop interface for module placement
  - Minified/collapsed view for available modules (design TBD)
  - Link to marketplace: "Want more? Look in the marketplace"

- **Module Disabling** - Moving a module outside dashboard area disables it automatically

- **Drag & Drop Implementation Notes**:
  - Disable text selection during drag (`user-select: none`)
  - Disable default browser context menu (right-click)
  - Layout persistence: store locally (Tauri `store` plugin) or sync to backend
  - Consider splitting Dashboard component - currently handles too much

- **Dashboard Refactoring** - Current Dashboard.svelte is doing too much:
  - WebSocket connection
  - State management
  - Module rendering
  - Modal handling
  - Action dispatching
  - Should be split into smaller, focused components
- **Status**: ✅ Implemented - Dashboard split into:
  - Header.svelte (header bar)
  - Sidebar.svelte (navigation)
  - DashboardContent.svelte (module grid)
  - Dashboard.svelte (orchestrator)

### Module Badges

- **Removed** - Tile badges (like "Live", "Ready") were redundant given the enable/disable UI
- **Status**: ✅ Removed from backend Tile component and all module views

### Settings Organization

- **Current** - Only has unpair functionality
- **Future** - Needs planning for:
  - General settings
  - Module settings
  - Network settings
  - Display preferences
  - etc.
  
  *Note: Organization structure needs to be thought through*
