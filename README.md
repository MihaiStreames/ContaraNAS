# ContaraNAS

A modular desktop application for monitoring and managing NAS systems at home.

## Features

- 🎮 **Steam Library Monitor**: Track game installations, library sizes, and drive usage across multiple Steam libraries
- 💻 **System Monitor**: Real-time CPU, memory, and disk monitoring with interactive graphs and per-core CPU visualization
- 🔄 **Automatic Tracking**: Detect changes in Steam installations and system resources automatically
- 🖥️ **Native Desktop GUI**: Clean, responsive interface built with NiceGUI

## Quick Start

### Installation

```bash
# Clone the repository
git clone https://github.com/MihaiStreames/ContaraNAS
cd ContaraNAS

# Install dependencies
uv sync

# Run the application
uv run -m ContaraNAS.main
```

### Requirements

- Python 3.9+
- Steam installed (for Steam module)
- `dmidecode` installed (for hardware monitoring)

## Architecture

ContaraNAS uses a modular plugin-based architecture where new monitoring modules can be easily added through Python entry points.
