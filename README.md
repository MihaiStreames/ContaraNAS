<a id="readme-top"></a>

<!-- PROJECT SHIELDS -->
<div align="center">

![GitHub License](https://img.shields.io/github/license/MihaiStreames/ContaraNAS)
![GitHub contributors](https://img.shields.io/github/contributors/MihaiStreames/ContaraNAS)
![GitHub Issues](https://img.shields.io/github/issues/MihaiStreames/ContaraNAS)
![GitHub Stars](https://img.shields.io/github/stars/MihaiStreames/ContaraNAS)

</div>

<!-- PROJECT LOGO -->
<br />
<div align="center">
  <a href="https://github.com/MihaiStreames/ContaraNAS">
    <h1>ContaraNAS</h1>
  </a>

  <h3 align="center">Modular NAS Management Desktop Application</h3>

  <p align="center">
    Monitor and manage your home NAS systems with a modern, extensible interface
    <br />
    <a href="https://contaranas.xyz/"><strong>Explore the docs »</strong></a>
    <br />
    <br />
    <a href="https://github.com/MihaiStreames/ContaraNAS/issues/new">Report Bug</a>
    ·
    <a href="https://github.com/MihaiStreames/ContaraNAS/issues/new">Request Feature</a>
  </p>
</div>

<!-- TABLE OF CONTENTS -->
<details>
  <summary>Table of Contents</summary>
  <ol>
    <li>
      <a href="#about-the-project">About The Project</a>
      <ul>
        <li><a href="#features">Features</a></li>
        <li><a href="#built-with">Built With</a></li>
      </ul>
    </li>
    <li>
      <a href="#getting-started">Getting Started</a>
      <ul>
        <li><a href="#prerequisites">Prerequisites</a></li>
        <li><a href="#installation">Installation</a></li>
      </ul>
    </li>
    <li><a href="#module-development">Module Development</a></li>
    <li><a href="#license">License</a></li>
  </ol>
</details>

<!-- ABOUT THE PROJECT -->
## About The Project

**ContaraNAS** is a modular desktop application designed for monitoring and managing NAS systems at home.

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Features

* **Steam Library Monitor** - Track game installations and library sizes across your NAS
* **System Monitor** - Real-time CPU, memory, and disk usage monitoring
* **Real-time Updates** - WebSocket-based live data streaming for instant feedback
* **Modular Architecture** - Enable or disable features based on your needs
* **Extensible Design** - Build custom modules using the developer API
* **Community Marketplace** - Share and discover community-built modules *(coming soon)*

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Built With

**Frontend:**

* [Tauri](https://tauri.app/) - Desktop application framework
* [SvelteKit](https://kit.svelte.dev/) - Web framework
* [TypeScript](https://www.typescriptlang.org/) - Type-safe JavaScript

**Backend:**

* [Python 3.13+](https://www.python.org/)
* [WebSocket](https://websockets.readthedocs.io/) - Real-time communication
* Custom module system with typed state management

**Documentation:**

* [MkDocs](https://www.mkdocs.org/) - Documentation site generator

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- GETTING STARTED -->
## Getting Started

Get ContaraNAS up and running on your local machine.

### Prerequisites

#### Linux

1. **Python 3.13+**

   Verify your version:

   ```bash
   python --version  # Should be 3.13 or higher
   ```

   If you need Python 3.13+, install via your package manager or [python.org](https://www.python.org/downloads/)

2. **uv (Python package manager)**

   Arch Linux:

   ```bash
   sudo pacman -S uv
   ```

   Debian/Ubuntu and other distributions:

   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Node.js 18+ and pnpm**

   Arch Linux:

   ```bash
   sudo pacman -S nodejs npm
   npm install -g pnpm
   ```

   Debian/Ubuntu:

   ```bash
   # Install Node.js 20.x
   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
   sudo apt-get install -y nodejs

   # Install pnpm
   npm install -g pnpm
   ```

   Other distributions (via package manager or [nodejs.org](https://nodejs.org/)):

   ```bash
   # After installing Node.js:
   npm install -g pnpm
   ```

4. **Rust (for Tauri)**

   All distributions:

   ```bash
   curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
   source $HOME/.cargo/env  # Or restart your terminal
   ```

#### Windows

1. **Python 3.13+**

   Download and install from [python.org](https://www.python.org/downloads/)

2. **uv (Python package manager)**

   PowerShell:

   ```powershell
   powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

3. **Node.js 18+ and pnpm**

   Download Node.js from [nodejs.org](https://nodejs.org/), then:

   ```powershell
   npm install -g pnpm
   ```

4. **Rust (for Tauri)**

   Download and install from [rustup.rs](https://rustup.rs/)

<p align="right">(<a href="#readme-top">back to top</a>)</p>

### Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/MihaiStreames/ContaraNAS.git
   cd ContaraNAS
   ```

2. **Set up the backend**

   ```bash
   cd backend
   uv sync
   ```

3. **Set up the frontend**

   ```bash
   cd frontend
   pnpm install
   ```

4. **Run the application**

   In one terminal (backend):

   ```bash
   cd backend
   uv run -m ContaraNAS
   ```

   In another terminal (frontend):

   ```bash
   cd frontend
   pnpm tauri dev
   ```

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- MODULE DEVELOPMENT -->
## Module Development

ContaraNAS features a powerful module system that allows you to extend functionality. Full documentation is available at [contaranas.xyz](https://contaranas.xyz/modules/).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

<!-- LICENSE -->
## License

> [!IMPORTANT]
> ContaraNAS is licensed under the **GNU General Public License v3.0**.
>
> This means:
>
> * ✅ You can use, modify, and distribute this software
> * ✅ You can use it for commercial purposes
> * ⚠️ You must disclose the source code of any modifications
> * ⚠️ You must license derivative works under GPL-3.0
> * ⚠️ You must include copyright and license notices
>
> See [LICENSE](LICENSE) for complete terms, or read the [official GPL-3.0 documentation](https://www.gnu.org/licenses/gpl-3.0.en.html).

<p align="right">(<a href="#readme-top">back to top</a>)</p>

---

<div align="center">
  <p>Made with ❤️</p>
  <p>
    <a href="https://github.com/MihaiStreames/ContaraNAS">GitHub</a>
    ·
    <a href="https://contaranas.xyz">Documentation</a>
    ·
    <a href="https://github.com/MihaiStreames/ContaraNAS/issues">Issues</a>
  </p>
</div>
