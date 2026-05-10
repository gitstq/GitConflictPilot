#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitConflictPilot - Lightweight Terminal Git Conflict Intelligent Resolution Engine
轻量级终端Git冲突智能解决引擎

A zero-dependency CLI tool for intelligent Git conflict detection, analysis, and resolution.
"""

__version__ = "1.0.0"
__author__ = "GitConflictPilot Team"
__license__ = "MIT"

from gitconflictpilot.cli import main
from gitconflictpilot.detector import ConflictDetector
from gitconflictpilot.resolver import ConflictResolver
from gitconflictpilot.analyzer import ConflictAnalyzer
from gitconflictpilot.backup import BackupManager
from gitconflictpilot.history import HistoryManager

__all__ = [
    "main",
    "ConflictDetector",
    "ConflictResolver",
    "ConflictAnalyzer",
    "BackupManager",
    "HistoryManager",
]
