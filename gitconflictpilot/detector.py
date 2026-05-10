#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conflict Detector - Git冲突智能检测模块
Detects and parses Git conflict markers in files.
"""

import os
import re
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import List, Optional, Tuple, Dict


class ConflictType(Enum):
    """冲突类型枚举"""
    CONTENT = "content"  # 内容冲突
    RENAME = "rename"    # 重命名冲突
    DELETE = "delete"    # 删除冲突
    BINARY = "binary"    # 二进制文件冲突


class ConflictSeverity(Enum):
    """冲突严重程度"""
    LOW = "low"          # 简单冲突，可自动解决
    MEDIUM = "medium"    # 中等冲突，需要人工确认
    HIGH = "high"        # 复杂冲突，必须人工解决
    CRITICAL = "critical"  # 关键冲突，可能导致数据丢失


@dataclass
class ConflictHunk:
    """单个冲突块"""
    start_line: int
    separator_line: int
    end_line: int
    ours_content: str
    theirs_content: str
    base_content: Optional[str] = None
    
    @property
    def line_count(self) -> int:
        """冲突块总行数"""
        return self.end_line - self.start_line + 1
    
    @property
    def ours_lines(self) -> int:
        """我们的内容行数"""
        return len(self.ours_content.splitlines())
    
    @property
    def theirs_lines(self) -> int:
        """他们的内容行数"""
        return len(self.theirs_content.splitlines())


@dataclass
class ConflictFile:
    """冲突文件信息"""
    path: str
    hunks: List[ConflictHunk] = field(default_factory=list)
    conflict_type: ConflictType = ConflictType.CONTENT
    severity: ConflictSeverity = ConflictSeverity.MEDIUM
    is_binary: bool = False
    encoding: str = "utf-8"
    error_message: Optional[str] = None
    
    @property
    def total_conflicts(self) -> int:
        """总冲突数"""
        return len(self.hunks)
    
    @property
    def total_lines(self) -> int:
        """冲突涉及的总行数"""
        return sum(h.line_count for h in self.hunks)


class ConflictDetector:
    """Git冲突检测器"""
    
    # Git冲突标记正则表达式
    CONFLICT_START = re.compile(r'^<{7} (.+)$')
    CONFLICT_SEPARATOR = re.compile(r'^={7}$')
    CONFLICT_END = re.compile(r'^>{7} (.+)$')
    
    # 支持的文件编码
    ENCODINGS = ['utf-8', 'utf-8-sig', 'gbk', 'gb2312', 'latin-1']
    
    def __init__(self, repo_path: str = "."):
        """
        初始化冲突检测器
        
        Args:
            repo_path: Git仓库路径
        """
        self.repo_path = Path(repo_path).resolve()
        self._detected_files: Dict[str, ConflictFile] = {}
    
    def detect_all(self) -> List[ConflictFile]:
        """
        检测仓库中所有冲突文件
        
        Returns:
            冲突文件列表
        """
        self._detected_files.clear()
        
        # 获取Git状态中的冲突文件
        conflict_paths = self._get_conflict_paths()
        
        for path in conflict_paths:
            conflict_file = self.detect_file(path)
            if conflict_file:
                self._detected_files[path] = conflict_file
        
        return list(self._detected_files.values())
    
    def detect_file(self, file_path: str) -> Optional[ConflictFile]:
        """
        检测单个文件的冲突
        
        Args:
            file_path: 文件路径
            
        Returns:
            冲突文件信息，无冲突返回None
        """
        full_path = self.repo_path / file_path
        
        if not full_path.exists():
            return ConflictFile(
                path=file_path,
                error_message=f"文件不存在: {file_path}"
            )
        
        # 检查是否为二进制文件
        if self._is_binary_file(full_path):
            return ConflictFile(
                path=file_path,
                conflict_type=ConflictType.BINARY,
                is_binary=True,
                severity=ConflictSeverity.HIGH
            )
        
        # 读取文件内容
        content, encoding = self._read_file_with_encoding(full_path)
        if content is None:
            return ConflictFile(
                path=file_path,
                error_message=f"无法读取文件: {file_path}"
            )
        
        # 解析冲突块
        hunks = self._parse_conflicts(content)
        
        if not hunks:
            return None
        
        # 确定冲突严重程度
        severity = self._calculate_severity(hunks)
        
        return ConflictFile(
            path=file_path,
            hunks=hunks,
            conflict_type=ConflictType.CONTENT,
            severity=severity,
            encoding=encoding
        )
    
    def _get_conflict_paths(self) -> List[str]:
        """获取Git状态中的冲突文件路径"""
        import subprocess
        
        try:
            result = subprocess.run(
                ['git', 'diff', '--name-only', '--diff-filter=U'],
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                paths = result.stdout.strip().split('\n')
                return [p for p in paths if p]
            
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        # 备用方案：递归搜索包含冲突标记的文件
        return self._search_conflict_files()
    
    def _search_conflict_files(self) -> List[str]:
        """递归搜索包含冲突标记的文件"""
        conflict_files = []
        
        for root, dirs, files in os.walk(self.repo_path):
            # 跳过.git目录
            if '.git' in root:
                continue
            
            # 跳过常见的非代码目录
            dirs[:] = [d for d in dirs if d not in {
                'node_modules', '__pycache__', '.venv', 'venv',
                'build', 'dist', '.idea', '.vscode'
            }]
            
            for file in files:
                file_path = Path(root) / file
                try:
                    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if '<<<<<<<' in content and '>>>>>>>' in content:
                            rel_path = str(file_path.relative_to(self.repo_path))
                            conflict_files.append(rel_path)
                except (IOError, PermissionError):
                    continue
        
        return conflict_files
    
    def _is_binary_file(self, file_path: Path) -> bool:
        """检查是否为二进制文件"""
        try:
            with open(file_path, 'rb') as f:
                chunk = f.read(8192)
                return b'\x00' in chunk
        except (IOError, PermissionError):
            return True
    
    def _read_file_with_encoding(self, file_path: Path) -> Tuple[Optional[str], str]:
        """尝试多种编码读取文件"""
        for encoding in self.ENCODINGS:
            try:
                with open(file_path, 'r', encoding=encoding) as f:
                    return f.read(), encoding
            except UnicodeDecodeError:
                continue
        
        return None, 'utf-8'
    
    def _parse_conflicts(self, content: str) -> List[ConflictHunk]:
        """解析文件中的冲突块"""
        hunks = []
        lines = content.splitlines(keepends=True)
        
        i = 0
        while i < len(lines):
            line = lines[i].rstrip('\n\r')
            
            # 检查冲突开始标记
            start_match = self.CONFLICT_START.match(line)
            if start_match:
                start_line = i + 1
                ours_branch = start_match.group(1)
                ours_content = []
                theirs_content = []
                separator_line = None
                
                i += 1
                
                # 读取我们的内容
                while i < len(lines):
                    line = lines[i].rstrip('\n\r')
                    sep_match = self.CONFLICT_SEPARATOR.match(line)
                    if sep_match:
                        separator_line = i + 1
                        break
                    ours_content.append(lines[i])
                    i += 1
                
                i += 1
                
                # 读取他们的内容
                while i < len(lines):
                    line = lines[i].rstrip('\n\r')
                    end_match = self.CONFLICT_END.match(line)
                    if end_match:
                        end_line = i + 1
                        theirs_branch = end_match.group(1)
                        break
                    theirs_content.append(lines[i])
                    i += 1
                
                hunk = ConflictHunk(
                    start_line=start_line,
                    separator_line=separator_line or start_line,
                    end_line=end_line,
                    ours_content=''.join(ours_content),
                    theirs_content=''.join(theirs_content)
                )
                hunks.append(hunk)
            
            i += 1
        
        return hunks
    
    def _calculate_severity(self, hunks: List[ConflictHunk]) -> ConflictSeverity:
        """计算冲突严重程度"""
        if not hunks:
            return ConflictSeverity.LOW
        
        # 根据冲突数量和大小判断
        total_lines = sum(h.line_count for h in hunks)
        
        if len(hunks) == 1 and total_lines < 10:
            return ConflictSeverity.LOW
        elif len(hunks) <= 3 and total_lines < 50:
            return ConflictSeverity.MEDIUM
        elif len(hunks) <= 10 and total_lines < 200:
            return ConflictSeverity.HIGH
        else:
            return ConflictSeverity.CRITICAL
    
    def get_statistics(self) -> Dict:
        """获取冲突统计信息"""
        if not self._detected_files:
            self.detect_all()
        
        total_files = len(self._detected_files)
        total_hunks = sum(f.total_conflicts for f in self._detected_files.values())
        total_lines = sum(f.total_lines for f in self._detected_files.values())
        
        severity_counts = {
            'low': 0, 'medium': 0, 'high': 0, 'critical': 0
        }
        
        for cf in self._detected_files.values():
            severity_counts[cf.severity.value] += 1
        
        return {
            'total_files': total_files,
            'total_conflicts': total_hunks,
            'total_lines': total_lines,
            'severity_distribution': severity_counts,
            'binary_files': sum(1 for f in self._detected_files.values() if f.is_binary)
        }
