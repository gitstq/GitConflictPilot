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
  <b>轻量级终端Git冲突智能解决引擎</b><br>
  <sub>Zero Dependencies · 智能分析 · 多策略解决 · 安全回滚</sub>
</p>

---

## 🎉 项目介绍

**GitConflictPilot** 是一款专为开发者设计的**轻量级终端Git冲突智能解决工具**。它能够自动检测、分析并解决Git合并冲突，大大提升开发效率。

### 💡 灵感来源

在日常开发中，Git冲突是最令人头疼的问题之一。每次合并代码时遇到冲突，都需要手动编辑文件、仔细比较差异、担心改错代码。**GitConflictPilot** 应运而生，旨在让冲突解决变得**简单、安全、高效**。

### 🌟 自研差异化亮点

| 特性 | GitConflictPilot | 传统方式 |
|------|-----------------|---------|
| **零依赖** | ✅ 纯Python实现，无需安装任何第三方库 | ❌ 需要配置复杂环境 |
| **智能分析** | ✅ AI驱动的冲突原因分析与解决建议 | ❌ 需要人工判断 |
| **多策略解决** | ✅ 5种解决策略，灵活应对各种场景 | ❌ 只能手动编辑 |
| **安全回滚** | ✅ 自动备份，一键恢复 | ❌ 无法撤销 |
| **历史追踪** | ✅ 完整的解决历史记录 | ❌ 无记录可查 |

---

## ✨ 核心特性

### 🔍 智能冲突检测
- **自动扫描**：一键检测仓库中所有冲突文件
- **深度解析**：精确识别冲突标记，提取冲突块信息
- **严重程度评估**：自动评估冲突严重程度（低/中/高/关键）
- **二进制文件识别**：智能识别无法自动解决的二进制文件冲突

### 🤖 AI驱动分析
- **冲突类型识别**：自动识别导入冲突、函数签名冲突、配置变更等
- **原因分析**：智能推断冲突产生的可能原因
- **解决建议**：针对每种冲突提供专业的解决建议
- **风险评估**：计算风险分数，帮助优先处理关键冲突

### 🔄 多策略解决
| 策略 | 说明 | 适用场景 |
|------|------|---------|
| `ours` | 使用我们的版本 | 确认本地修改正确 |
| `theirs` | 使用他们的版本 | 接受远程分支修改 |
| `union` | 合并两个版本 | 需要保留双方修改 |
| `smart` | 智能选择最佳版本 | **推荐默认策略** |
| `manual` | 手动解决 | 复杂冲突需人工判断 |

### 🔒 安全保障
- **自动备份**：解决冲突前自动创建备份
- **校验和验证**：SHA256校验确保备份完整性
- **一键恢复**：支持从任意备份快速恢复
- **历史追踪**：完整的操作历史记录

### 📊 可视化报告
- **冲突统计**：文件数、冲突数、严重程度分布
- **解决摘要**：成功率、耗时、策略分布
- **风险评分**：0-100分量化冲突风险
- **时间估算**：预估解决所需时间

---

## 🚀 快速开始

### 📋 环境要求
- **Python**: 3.8 或更高版本
- **Git**: 任意版本
- **操作系统**: Windows / macOS / Linux

### 📦 安装

```bash
# 方式1: 从PyPI安装 (推荐)
pip install gitconflictpilot

# 方式2: 从源码安装
git clone https://github.com/gitstq/GitConflictPilot.git
cd GitConflictPilot
pip install -e .
```

### 🎯 基本使用

```bash
# 检测冲突
gitconflictpilot detect

# 智能解决所有冲突
gitconflictpilot resolve --strategy smart

# 分析冲突详情
gitconflictpilot analyze

# 查看解决历史
gitconflictpilot history

# 管理备份
gitconflictpilot backup list
```

---

## 📖 详细使用指南

### 🔍 检测冲突

```bash
# 检测当前仓库所有冲突
gitconflictpilot detect

# 检测指定文件
gitconflictpilot detect -f path/to/file.py

# JSON格式输出
gitconflictpilot detect --json
```

**输出示例**：
```
════════════════════════════════════════════════════════════
  🔍 冲突检测
════════════════════════════════════════════════════════════

  状态 │ 文件路径                              │ 冲突数 │ 严重程度
  ─────┼───────────────────────────────────────┼────────┼──────────
  🟡   │ src/main.py                           │   3    │ medium
  🟠   │ config/settings.json                  │   1    │ high
  🟢   │ README.md                             │   1    │ low

📊 统计: 3 个文件, 5 个冲突
```

### 🔄 解决冲突

```bash
# 智能解决所有冲突 (推荐)
gitconflictpilot resolve --strategy smart

# 使用特定策略
gitconflictpilot resolve --strategy ours      # 使用我们的版本
gitconflictpilot resolve --strategy theirs    # 使用他们的版本
gitconflictpilot resolve --strategy union     # 合并两个版本

# 解决指定文件
gitconflictpilot resolve -f path/to/file.py

# 模拟运行 (不实际修改文件)
gitconflictpilot resolve --dry-run

# 不创建备份 (不推荐)
gitconflictpilot resolve --no-backup
```

### 📊 分析冲突

```bash
# 分析所有冲突
gitconflictpilot analyze

# 生成详细报告
gitconflictpilot analyze --report

# 分析指定文件
gitconflictpilot analyze -f path/to/file.py
```

**分析报告示例**：
```
════════════════════════════════════════════════════════════
  📊 冲突分析报告
════════════════════════════════════════════════════════════

  📄 冲突文件数: 3
  ⚠️ 冲突总数: 5
  🎯 风险分数: 42.5 (中等风险)
  ⏱️ 预计解决时间: 15 分钟

  📈 严重程度分布:
    🟢 low     : ████████░░░░░░░░░░░░ 1
    🟡 medium  : ████████████████░░░░ 2
    🟠 high    : ████░░░░░░░░░░░░░░░░ 1
    🔴 critical: ░░░░░░░░░░░░░░░░░░░░ 0

  💡 解决建议:
    1. ⚠️ 发现 1 个高严重度冲突，需要仔细审查
    2. ⚙️ 配置文件存在冲突，请确认环境配置一致性
    3. 💡 建议使用 'gitconflictpilot resolve --strategy smart' 自动解决简单冲突
```

### 📜 历史记录

```bash
# 查看解决历史
gitconflictpilot history

# 查看指定文件的历史
gitconflictpilot history -f path/to/file.py

# 限制显示数量
gitconflictpilot history -l 50

# 导出历史记录
gitconflictpilot history --export history.md

# 清除历史记录
gitconflictpilot history --clear
```

### 📦 备份管理

```bash
# 列出所有备份
gitconflictpilot backup list

# 恢复备份
gitconflictpilot backup restore --id <backup_id>

# 删除备份
gitconflictpilot backup delete --id <backup_id>

# 清理旧备份 (超过30天)
gitconflictpilot backup cleanup --max-age 30
```

### 📊 统计信息

```bash
# 显示统计信息
gitconflictpilot stats

# JSON格式输出
gitconflictpilot stats --json
```

---

## 💡 设计思路与迭代规划

### 🏗️ 架构设计

```
GitConflictPilot
├── detector/      # 冲突检测模块
│   ├── 文件扫描
│   ├── 标记解析
│   └── 严重程度评估
├── analyzer/      # 智能分析模块
│   ├── 冲突类型识别
│   ├── 原因推断
│   └── 风险评估
├── resolver/      # 冲突解决模块
│   ├── 多策略引擎
│   ├── 智能选择
│   └── 安全备份
├── backup/        # 备份管理模块
│   ├── 自动备份
│   ├── 校验验证
│   └── 恢复机制
├── history/       # 历史追踪模块
│   ├── 操作记录
│   ├── 统计分析
│   └── 导出功能
└── tui/           # 终端界面模块
    ├── 彩色输出
    ├── 表格渲染
    └── 进度展示
```

### 🔮 后续迭代规划

- [ ] **v1.1**: 添加交互式冲突解决模式
- [ ] **v1.2**: 支持更多冲突类型（重命名、删除）
- [ ] **v1.3**: 集成LLM进行更智能的冲突分析
- [ ] **v1.4**: 支持自定义解决规则
- [ ] **v1.5**: 添加Web UI界面

---

## 📦 打包与部署指南

### 开发环境搭建

```bash
# 克隆仓库
git clone https://github.com/gitstq/GitConflictPilot.git
cd GitConflictPilot

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安装开发依赖
pip install -e ".[dev]"
```

### 运行测试

```bash
# 运行单元测试
python -m pytest tests/

# 运行覆盖率测试
python -m pytest --cov=gitconflictpilot tests/
```

### 构建发布

```bash
# 构建wheel包
python -m build

# 上传到PyPI
python -m twine upload dist/*
```

---

## 🤝 贡献指南

我们欢迎所有形式的贡献！

### 如何贡献

1. **Fork** 本仓库
2. **创建** 特性分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 更改 (`git commit -m 'feat: Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **提交** Pull Request

### 提交规范

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 规范：

- `feat:` 新功能
- `fix:` 修复bug
- `docs:` 文档更新
- `refactor:` 代码重构
- `test:` 测试相关
- `chore:` 构建/工具相关

---

## 📄 开源协议说明

本项目采用 **MIT License** 开源协议。

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
  <sub>如果这个项目对你有帮助，请给一个 ⭐️ Star 支持一下！</sub>
</p>
