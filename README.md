# Codes Workspace

Personal multi-project workspace organized by project type.

## Structure

```
codes/
├── bots/           # Automated bots and trading agents
├── apps/           # Applications (mobile, desktop, mods)
├── websites/       # Static and GitHub Pages sites
├── scripts/        # Standalone scripts, notebooks, scratch files
├── plugins/        # Claude Code plugins and tools
├── data/           # Data files and assets
└── test/           # Miscellaneous test files
```

---

## bots/

| Project | Description | Stack |
|---------|-------------|-------|
| `polymarket-bot-by_openclaw/` | BTC prediction market trading bot | Python, Conda |

**Run:**
```bash
cd bots/polymarket-bot-by_openclaw
conda activate polymarket-bot
python main.py   # DRY_RUN=true by default
```

---

## apps/

| Project | Description | Stack |
|---------|-------------|-------|
| `nail-coach-flutter/` | Nail-trim reminder app | Flutter / Dart |
| `AI_agent/` | Multi-AI agent playground | Python |
| `GeminiTranslator/` | Minecraft NeoForge translation mod | Java 24 / Gradle |
| `JavaDemo/` | Java 24 Maven demo | Java / Maven |

**Run:**
```bash
# Flutter app
cd apps/nail-coach-flutter && flutter pub get && flutter run

# Minecraft mod
cd apps/GeminiTranslator && ./gradlew build

# Java demo
cd apps/JavaDemo && mvn compile && mvn exec:java
```

---

## websites/

| Project | Description | Stack |
|---------|-------------|-------|
| `chemwebsite/` | Static chemistry website | HTML |
| `chem.github.io/` | Chemistry GitHub Pages site | HTML |
| `nthu-chemistry/` | NTHU chemistry dept site | HTML |
| `website/` | Personal static site | HTML |

**Run:** Open `index.html` in browser.

---

## scripts/

| Project | Description | Stack |
|---------|-------------|-------|
| `matlab/` | MATLAB lecture & homework scripts | MATLAB |
| `scratch/` | Scratch files: Python, C++, Jupyter, shell | Mixed |
| `vim/` | C++ snake game (Vim workspace) | C++ |

**Run:**
```bash
# C++ files
g++ scripts/scratch/1.cpp -o out && ./out

# Shell utility
bash scripts/scratch/video_operator.sh
```

---

## plugins/

| Project | Description | Stack |
|---------|-------------|-------|
| `everything-claude-code/` | Claude Code plugin collection | Node.js / Python |
| `clearcontext/` | ClearContext Claude plugin | — |

**Run:**
```bash
cd plugins/everything-claude-code
node tests/run-all.js
```

---

## data/

| Directory | Description |
|-----------|-------------|
| `chem_datas/` | Chemistry lecture data, PDFs, and assets |

---

## test/

Miscellaneous test files (JS server, HTML pages).

| File | Description |
|------|-------------|
| `finance_server.js` | Node.js finance data server |
| `finance_today.html` | Finance HTML page |
| `snake.html` | Browser snake game |
# MENDEL-Multi-agent-Element-level-Negotiation-for-Dynamic-Energy-Landscapes
