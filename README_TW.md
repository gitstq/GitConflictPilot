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
  <b>輕量級終端Git衝突智能解決引擎</b><br>
  <sub>零依賴 · 智能分析 · 多策略解決 · 安全回滾</sub>
</p>

---

## 🎉 專案介紹

**GitConflictPilot** 是一款專為開發者設計的**輕量級終端Git衝突智能解決工具**。它能夠自動檢測、分析並解決Git合併衝突，大幅提升開發效率。

### 💡 靈感來源

在日常開發中，Git衝突是最令人頭痛的問題之一。每次合併程式碼時遇到衝突，都需要手動編輯檔案、仔細比較差異、擔心改錯程式碼。**GitConflictPilot** 應運而生，旨在讓衝突解決變得**簡單、安全、高效**。

### 🌟 自研差異化亮點

| 特性 | GitConflictPilot | 傳統方式 |
|------|-----------------|---------|
| **零依賴** | ✅ 純Python實現，無需安裝任何第三方函式庫 | ❌ 需要配置複雜環境 |
| **智能分析** | ✅ AI驅動的衝突原因分析與解決建議 | ❌ 需要人工判斷 |
| **多策略解決** | ✅ 5種解決策略，靈活應對各種場景 | ❌ 只能手動編輯 |
| **安全回滾** | ✅ 自動備份，一鍵恢復 | ❌ 無法撤銷 |
| **歷史追蹤** | ✅ 完整的解決歷史記錄 | ❌ 無記錄可查 |

---

## ✨ 核心特性

### 🔍 智能衝突檢測
- **自動掃描**：一鍵檢測倉庫中所有衝突檔案
- **深度解析**：精確識別衝突標記，提取衝突區塊資訊
- **嚴重程度評估**：自動評估衝突嚴重程度（低/中/高/關鍵）
- **二進位檔案識別**：智能識別無法自動解決的二進位檔案衝突

### 🤖 AI驅動分析
- **衝突類型識別**：自動識別導入衝突、函式簽名衝突、配置變更等
- **原因分析**：智能推斷衝突產生的可能原因
- **解決建議**：針對每種衝突提供專業的解決建議
- **風險評估**：計算風險分數，幫助優先處理關鍵衝突

### 🔄 多策略解決
| 策略 | 說明 | 適用場景 |
|------|------|---------|
| `ours` | 使用我們的版本 | 確認本地修改正確 |
| `theirs` | 使用他們的版本 | 接受遠端分支修改 |
| `union` | 合併兩個版本 | 需要保留雙方修改 |
| `smart` | 智能選擇最佳版本 | **推薦預設策略** |
| `manual` | 手動解決 | 複雜衝突需人工判斷 |

### 🔒 安全保障
- **自動備份**：解決衝突前自動建立備份
- **校驗和驗證**：SHA256校驗確保備份完整性
- **一鍵恢復**：支援從任意備份快速恢復
- **歷史追蹤**：完整的操作歷史記錄

### 📊 視覺化報告
- **衝突統計**：檔案數、衝突數、嚴重程度分布
- **解決摘要**：成功率、耗時、策略分布
- **風險評分**：0-100分量化衝突風險
- **時間估算**：預估解決所需時間

---

## 🚀 快速開始

### 📋 環境要求
- **Python**: 3.8 或更高版本
- **Git**: 任意版本
- **作業系統**: Windows / macOS / Linux

### 📦 安裝

```bash
# 方式1: 從PyPI安裝 (推薦)
pip install gitconflictpilot

# 方式2: 從原始碼安裝
git clone https://github.com/gitstq/GitConflictPilot.git
cd GitConflictPilot
pip install -e .
```

### 🎯 基本使用

```bash
# 檢測衝突
gitconflictpilot detect

# 智能解決所有衝突
gitconflictpilot resolve --strategy smart

# 分析衝突詳情
gitconflictpilot analyze

# 查看解決歷史
gitconflictpilot history

# 管理備份
gitconflictpilot backup list
```

---

## 📖 詳細使用指南

### 🔍 檢測衝突

```bash
# 檢測當前倉庫所有衝突
gitconflictpilot detect

# 檢測指定檔案
gitconflictpilot detect -f path/to/file.py

# JSON格式輸出
gitconflictpilot detect --json
```

### 🔄 解決衝突

```bash
# 智能解決所有衝突 (推薦)
gitconflictpilot resolve --strategy smart

# 使用特定策略
gitconflictpilot resolve --strategy ours      # 使用我們的版本
gitconflictpilot resolve --strategy theirs    # 使用他們的版本
gitconflictpilot resolve --strategy union     # 合併兩個版本

# 解決指定檔案
gitconflictpilot resolve -f path/to/file.py

# 模擬運行 (不實際修改檔案)
gitconflictpilot resolve --dry-run

# 不建立備份 (不推薦)
gitconflictpilot resolve --no-backup
```

### 📊 分析衝突

```bash
# 分析所有衝突
gitconflictpilot analyze

# 生成詳細報告
gitconflictpilot analyze --report

# 分析指定檔案
gitconflictpilot analyze -f path/to/file.py
```

### 📜 歷史記錄

```bash
# 查看解決歷史
gitconflictpilot history

# 查看指定檔案的歷史
gitconflictpilot history -f path/to/file.py

# 限制顯示數量
gitconflictpilot history -l 50

# 匯出歷史記錄
gitconflictpilot history --export history.md

# 清除歷史記錄
gitconflictpilot history --clear
```

### 📦 備份管理

```bash
# 列出所有備份
gitconflictpilot backup list

# 恢復備份
gitconflictpilot backup restore --id <backup_id>

# 刪除備份
gitconflictpilot backup delete --id <backup_id>

# 清理舊備份 (超過30天)
gitconflictpilot backup cleanup --max-age 30
```

### 📊 統計資訊

```bash
# 顯示統計資訊
gitconflictpilot stats

# JSON格式輸出
gitconflictpilot stats --json
```

---

## 💡 設計思路與迭代規劃

### 🏗️ 架構設計

```
GitConflictPilot
├── detector/      # 衝突檢測模組
│   ├── 檔案掃描
│   ├── 標記解析
│   └── 嚴重程度評估
├── analyzer/      # 智能分析模組
│   ├── 衝突類型識別
│   ├── 原因推斷
│   └── 風險評估
├── resolver/      # 衝突解決模組
│   ├── 多策略引擎
│   ├── 智能選擇
│   └── 安全備份
├── backup/        # 備份管理模組
│   ├── 自動備份
│   ├── 校驗驗證
│   └── 恢復機制
├── history/       # 歷史追蹤模組
│   ├── 操作記錄
│   ├── 統計分析
│   └── 匯出功能
└── tui/           # 終端介面模組
    ├── 彩色輸出
    ├── 表格渲染
    └── 進度展示
```

### 🔮 後續迭代規劃

- [ ] **v1.1**: 添加互動式衝突解決模式
- [ ] **v1.2**: 支援更多衝突類型（重命名、刪除）
- [ ] **v1.3**: 整合LLM進行更智能的衝突分析
- [ ] **v1.4**: 支援自訂解決規則
- [ ] **v1.5**: 添加Web UI介面

---

## 📦 打包與部署指南

### 開發環境搭建

```bash
# 複製倉庫
git clone https://github.com/gitstq/GitConflictPilot.git
cd GitConflictPilot

# 建立虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/macOS
# venv\Scripts\activate   # Windows

# 安裝開發依賴
pip install -e ".[dev]"
```

### 執行測試

```bash
# 執行單元測試
python -m pytest tests/

# 執行覆蓋率測試
python -m pytest --cov=gitconflictpilot tests/
```

### 建置發布

```bash
# 建置wheel套件
python -m build

# 上傳到PyPI
python -m twine upload dist/*
```

---

## 🤝 貢獻指南

我們歡迎所有形式的貢獻！

### 如何貢獻

1. **Fork** 本倉庫
2. **建立** 特性分支 (`git checkout -b feature/AmazingFeature`)
3. **提交** 變更 (`git commit -m 'feat: Add some AmazingFeature'`)
4. **推送** 到分支 (`git push origin feature/AmazingFeature`)
5. **提交** Pull Request

### 提交規範

遵循 [Conventional Commits](https://www.conventionalcommits.org/) 規範：

- `feat:` 新功能
- `fix:` 修復bug
- `docs:` 文檔更新
- `refactor:` 程式碼重構
- `test:` 測試相關
- `chore:` 建置/工具相關

---

## 📄 開源協議说明

本專案採用 **MIT License** 開源協議。

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
  <sub>如果這個專案對你有幫助，請給一個 ⭐️ Star 支持一下！</sub>
</p>
