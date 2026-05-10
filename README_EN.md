<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python Version">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="License">
  <img src="https://img.shields.io/badge/Zero%20Dependencies-✓-brightgreen.svg" alt="Zero Dependencies">
  <img src="https://img.shields.io/badge/Platform-Cross%20Platform-lightgrey.svg" alt="Platform">
</p>

<p align="center">
  <a href="README.md">简体中文</a> | <a href="README_EN.md">English</a> | <a href="README_TW.md">繁體中文</a>
</p>

<h1 align="center">🔧 GitConflictPilot</h1>

<p align="center">
  <b>Lightweight Terminal Git Conflict Intelligent Resolution Engine</b><br>
  <sub>Zero Dependencies · Smart Analysis · Multi-Strategy Resolution · Safe Rollback</sub>
</p>

---

## 🎉 Introduction

**GitConflictPilot** is a **lightweight terminal-based intelligent Git conflict resolution tool** designed for developers. It automatically detects, analyzes, and resolves Git merge conflicts, significantly boosting development efficiency.

### 💡 Inspiration

In daily development, Git conflicts are one of the most frustrating problems. Every time you encounter a conflict during code merging, you need to manually edit files, carefully compare differences, and worry about making mistakes. **GitConflictPilot** was created to make conflict resolution **simple, safe, and efficient**.

### 🌟 Key Differentiators

| Feature | GitConflictPilot | Traditional Methods |
|---------|------------------|---------------------|
| **Zero Dependencies** | ✅ Pure Python, no third-party libraries needed | ❌ Complex environment setup |
| **Smart Analysis** | ✅ AI-powered conflict cause analysis & suggestions | ❌ Manual judgment required |
| **Multi-Strategy** | ✅ 5 resolution strategies for various scenarios | ❌ Manual editing only |
| **Safe Rollback** | ✅ Automatic backup, one-click restore | ❌ Cannot undo |
| **History Tracking** | ✅ Complete resolution history records | ❌ No records available |

---

## ✨ Core Features

### 🔍 Smart Conflict Detection
- **Auto Scan**: One-click detection of all conflict files in repository
- **Deep Parsing**: Precise identification of conflict markers and extraction of conflict hunks
- **Severity Assessment**: Automatic evaluation of conflict severity (Low/Medium/High/Critical)
- **Binary File Detection**: Smart identification of binary file conflicts that cannot be auto-resolved

### 🤖 AI-Powered Analysis
- **Conflict Type Recognition**: Auto-identify import conflicts, function signature conflicts, config changes, etc.
- **Cause Analysis**: Intelligent inference of possible conflict causes
- **Resolution Suggestions**: Professional resolution recommendations for each conflict type
- **Risk Assessment**: Calculate risk scores to help prioritize critical conflicts

### 🔄 Multi-Strategy Resolution
| Strategy | Description | Use Case |
|----------|-------------|----------|
| `ours` | Use our version | Confirm local changes are correct |
| `theirs` | Use their version | Accept remote branch changes |
| `union` | Merge both versions | Need to keep both modifications |
| `smart` | Intelligently select best version | **Recommended default strategy** |
| `manual` | Manual resolution | Complex conflicts need human judgment |

### 🔒 Safety Guarantees
- **Auto Backup**: Automatically create backups before resolving conflicts
- **Checksum Verification**: SHA256 checksum ensures backup integrity
- **One-Click Restore**: Support quick restore from any backup
- **History Tracking**: Complete operation history records

### 📊 Visual Reports
- **Conflict Statistics**: File count, conflict count, severity distribution
- **Resolution Summary**: Success rate, duration, strategy distribution
- **Risk Score**: 0-100 score quantifying conflict risk
- **Time Estimation**: Estimated time needed for resolution

---

## 🚀 Quick Start

### 📋 Requirements
- **Python**: 3.8 or higher
- **Git**: Any version
- **OS**: Windows / macOS / Linux

### 📦 Installation

```bash
# Method 1: Install from PyPI (Recommended)
pip install gitconflictpilot

# Method 2: Install from source
git clone https://github.com/gitstq/GitConflictPilot.git
cd GitConflictPilot
pip install -e .
```

### 🎯 Basic Usage

```bash
# Detect conflicts
gitconflictpilot detect

# Smart resolve all conflicts
gitconflictpilot resolve --strategy smart

# Analyze conflict details
gitconflictpilot analyze

# View resolution history
gitconflictpilot history

# Manage backups
gitconflictpilot backup list
```

---

## 📖 Detailed Usage Guide

### 🔍 Detect Conflicts

```bash
# Detect all conflicts in current repository
gitconflictpilot detect

# Detect specific file
gitconflictpilot detect -f path/to/file.py

# JSON format output
gitconflictpilot detect --json
```

### 🔄 Resolve Conflicts

```bash
# Smart resolve all conflicts (Recommended)
gitconflictpilot resolve --strategy smart

# Use specific strategy
gitconflictpilot resolve --strategy ours      # Use our version
gitconflictpilot resolve --strategy theirs    # Use their version
gitconflictpilot resolve --strategy union     # Merge both versions

# Resolve specific file
gitconflictpilot resolve -f path/to/file.py

# Dry run (don't actually modify files)
gitconflictpilot resolve --dry-run

# Skip backup creation (Not recommended)
gitconflictpilot resolve --no-backup
```

### 📊 Analyze Conflicts

```bash
# Analyze all conflicts
gitconflictpilot analyze

# Generate detailed report
gitconflictpilot analyze --report

# Analyze specific file
gitconflictpilot analyze -f path/to/file.py
```

### 📜 History Records

```bash
# View resolution history
gitconflictpilot history

# View history for specific file
gitconflictpilot history -f path/to/file.py

# Limit display count
gitconflictpilot history -l 50

# Export history records
gitconflictpilot history --export history.md

# Clear history records
gitconflictpilot history --clear
```

### 📦 Backup Management

```bash
# List all backups
gitconflictpilot backup list

# Restore backup
gitconflictpilot backup restore --id <backup_id>

# Delete backup
gitconflictpilot backup delete --id <backup_id>

# Cleanup old backups (older than 30 days)
gitconflictpilot backup cleanup --max-age 30
```

### 📊 Statistics

```bash
# Show statistics
gitconflictpilot stats

# JSON format output
gitconflictpilot stats --json
```

---

## 💡 Design Philosophy & Roadmap

### 🏗️ Architecture

```
GitConflictPilot
├── detector/      # Conflict Detection Module
│   ├── File Scanning
│   ├── Marker Parsing
│   └── Severity Assessment
├── analyzer/      # Smart Analysis Module
│   ├── Conflict Type Recognition
│   ├── Cause Inference
│   └── Risk Assessment
├── resolver/      # Conflict Resolution Module
│   ├── Multi-Strategy Engine
│   ├── Smart Selection
│   └── Safe Backup
├── backup/        # Backup Management Module
│   ├── Auto Backup
│   ├── Checksum Verification
│   └── Restore Mechanism
├── history/       # History Tracking Module
│   ├── Operation Records
│   ├── Statistical Analysis
│   └── Export Function
└── tui/           # Terminal Interface Module
    ├── Color Output
    ├── Table Rendering
    └── Progress Display
```

### 🔮 Roadmap

- [ ] **v1.1**: Add interactive conflict resolution mode
- [ ] **v1.2**: Support more conflict types (rename, delete)
- [ ] **v1.3**: Integrate LLM for smarter conflict analysis
- [ ] **v1.4**: Support custom resolution rules
- [ ] **v1.5**: Add Web UI interface

---

## 📦 Build & Deployment

### Development Setup

```bash
# Clone repository
git clone https://github.com/gitstq/GitConflictPilot.git
cd GitConflictPilot

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# Install development dependencies
pip install -e ".[dev]"
```

### Run Tests

```bash
# Run unit tests
python -m pytest tests/

# Run coverage tests
python -m pytest --cov=gitconflictpilot tests/
```

### Build & Publish

```bash
# Build wheel package
python -m build

# Upload to PyPI
python -m twine upload dist/*
```

---

## 🤝 Contributing

We welcome all forms of contributions!

### How to Contribute

1. **Fork** this repository
2. **Create** feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Submit** Pull Request

### Commit Convention

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` New feature
- `fix:` Bug fix
- `docs:` Documentation update
- `refactor:` Code refactoring
- `test:` Test related
- `chore:` Build/tool related

---

## 📄 License

This project is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2024 GitConflictPilot Team

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

<p align="center">
  <sub>If this project helps you, please give it a ⭐️ Star!</sub>
</p>
