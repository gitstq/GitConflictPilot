#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conflict Resolver - Git冲突智能解决模块
Provides multiple strategies for resolving Git conflicts.
"""

import os
import re
import shutil
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import List, Optional, Callable, Dict, Any, Tuple

from .detector import ConflictFile, ConflictHunk, ConflictSeverity


class ResolutionStrategy(Enum):
    """冲突解决策略"""
    OURS = "ours"                    # 使用我们的版本
    THEIRS = "theirs"                # 使用他们的版本
    UNION = "union"                  # 合并两个版本
    MANUAL = "manual"                # 手动解决
    SMART = "smart"                  # 智能选择
    INTERACTIVE = "interactive"      # 交互式选择


@dataclass
class ResolutionResult:
    """解决结果"""
    success: bool
    file_path: str
    strategy: ResolutionStrategy
    hunks_resolved: int
    hunks_total: int
    message: str
    backup_path: Optional[str] = None
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


class ConflictResolver:
    """Git冲突解决器"""
    
    def __init__(self, repo_path: str = ".", backup_dir: str = ".gitconflictpilot/backups"):
        """
        初始化冲突解决器
        
        Args:
            repo_path: Git仓库路径
            backup_dir: 备份目录路径
        """
        self.repo_path = Path(repo_path).resolve()
        self.backup_dir = self.repo_path / backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        # 解决策略映射
        self._strategies: Dict[ResolutionStrategy, Callable] = {
            ResolutionStrategy.OURS: self._resolve_ours,
            ResolutionStrategy.THEIRS: self._resolve_theirs,
            ResolutionStrategy.UNION: self._resolve_union,
            ResolutionStrategy.SMART: self._resolve_smart,
        }
    
    def resolve_file(
        self,
        conflict_file: ConflictFile,
        strategy: ResolutionStrategy = ResolutionStrategy.SMART,
        create_backup: bool = True
    ) -> ResolutionResult:
        """
        解决单个文件的冲突
        
        Args:
            conflict_file: 冲突文件信息
            strategy: 解决策略
            create_backup: 是否创建备份
            
        Returns:
            解决结果
        """
        file_path = self.repo_path / conflict_file.path
        
        # 检查文件是否存在
        if not file_path.exists():
            return ResolutionResult(
                success=False,
                file_path=conflict_file.path,
                strategy=strategy,
                hunks_resolved=0,
                hunks_total=conflict_file.total_conflicts,
                message=f"文件不存在: {conflict_file.path}"
            )
        
        # 二进制文件无法自动解决
        if conflict_file.is_binary:
            return ResolutionResult(
                success=False,
                file_path=conflict_file.path,
                strategy=strategy,
                hunks_resolved=0,
                hunks_total=1,
                message="二进制文件冲突无法自动解决，请手动处理"
            )
        
        # 创建备份
        backup_path = None
        if create_backup:
            backup_path = self._create_backup(file_path)
        
        try:
            # 读取文件内容
            with open(file_path, 'r', encoding=conflict_file.encoding) as f:
                content = f.read()
            
            # 应用解决策略
            resolve_func = self._strategies.get(strategy, self._resolve_smart)
            resolved_content, hunks_resolved = resolve_func(content, conflict_file.hunks)
            
            # 写入解决后的内容
            with open(file_path, 'w', encoding=conflict_file.encoding) as f:
                f.write(resolved_content)
            
            return ResolutionResult(
                success=True,
                file_path=conflict_file.path,
                strategy=strategy,
                hunks_resolved=hunks_resolved,
                hunks_total=conflict_file.total_conflicts,
                message=f"成功解决 {hunks_resolved}/{conflict_file.total_conflicts} 个冲突",
                backup_path=backup_path
            )
            
        except Exception as e:
            return ResolutionResult(
                success=False,
                file_path=conflict_file.path,
                strategy=strategy,
                hunks_resolved=0,
                hunks_total=conflict_file.total_conflicts,
                message=f"解决冲突时发生错误: {str(e)}",
                backup_path=backup_path
            )
    
    def resolve_all(
        self,
        conflict_files: List[ConflictFile],
        strategy: ResolutionStrategy = ResolutionStrategy.SMART,
        create_backup: bool = True
    ) -> List[ResolutionResult]:
        """
        批量解决所有冲突文件
        
        Args:
            conflict_files: 冲突文件列表
            strategy: 解决策略
            create_backup: 是否创建备份
            
        Returns:
            解决结果列表
        """
        results = []
        for cf in conflict_files:
            result = self.resolve_file(cf, strategy, create_backup)
            results.append(result)
        return results
    
    def _create_backup(self, file_path: Path) -> str:
        """创建文件备份"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_name = f"{file_path.name}.{timestamp}.bak"
        backup_path = self.backup_dir / backup_name
        
        shutil.copy2(file_path, backup_path)
        return str(backup_path)
    
    def restore_backup(self, backup_path: str, original_path: str) -> bool:
        """
        从备份恢复文件
        
        Args:
            backup_path: 备份文件路径
            original_path: 原始文件路径
            
        Returns:
            是否恢复成功
        """
        try:
            backup = Path(backup_path)
            original = self.repo_path / original_path
            
            if not backup.exists():
                return False
            
            shutil.copy2(backup, original)
            return True
            
        except Exception:
            return False
    
    def _resolve_ours(self, content: str, hunks: List[ConflictHunk]) -> Tuple[str, int]:
        """使用我们的版本"""
        resolved = content
        resolved_count = 0
        
        for hunk in reversed(hunks):  # 从后往前替换，避免行号偏移
            lines = resolved.splitlines(keepends=True)
            
            # 构建解决后的内容
            start_idx = hunk.start_line - 1
            end_idx = hunk.end_line
            
            # 替换冲突块为我们的内容
            new_lines = lines[:start_idx] + [hunk.ours_content] + lines[end_idx:]
            resolved = ''.join(new_lines)
            resolved_count += 1
        
        return resolved, resolved_count
    
    def _resolve_theirs(self, content: str, hunks: List[ConflictHunk]) -> Tuple[str, int]:
        """使用他们的版本"""
        resolved = content
        resolved_count = 0
        
        for hunk in reversed(hunks):
            lines = resolved.splitlines(keepends=True)
            
            start_idx = hunk.start_line - 1
            end_idx = hunk.end_line
            
            # 替换冲突块为他们的内容
            new_lines = lines[:start_idx] + [hunk.theirs_content] + lines[end_idx:]
            resolved = ''.join(new_lines)
            resolved_count += 1
        
        return resolved, resolved_count
    
    def _resolve_union(self, content: str, hunks: List[ConflictHunk]) -> Tuple[str, int]:
        """合并两个版本"""
        resolved = content
        resolved_count = 0
        
        for hunk in reversed(hunks):
            lines = resolved.splitlines(keepends=True)
            
            start_idx = hunk.start_line - 1
            end_idx = hunk.end_line
            
            # 合并内容（先我们的，再他们的）
            merged_content = hunk.ours_content
            if hunk.theirs_content.strip():
                # 避免重复内容
                if hunk.theirs_content.strip() not in hunk.ours_content:
                    merged_content += hunk.theirs_content
            
            new_lines = lines[:start_idx] + [merged_content] + lines[end_idx:]
            resolved = ''.join(new_lines)
            resolved_count += 1
        
        return resolved, resolved_count
    
    def _resolve_smart(self, content: str, hunks: List[ConflictHunk]) -> Tuple[str, int]:
        """智能选择最佳版本"""
        resolved = content
        resolved_count = 0
        
        for hunk in reversed(hunks):
            lines = resolved.splitlines(keepends=True)
            
            start_idx = hunk.start_line - 1
            end_idx = hunk.end_line
            
            # 智能决策逻辑
            chosen_content = self._choose_best_version(hunk)
            
            new_lines = lines[:start_idx] + [chosen_content] + lines[end_idx:]
            resolved = ''.join(new_lines)
            resolved_count += 1
        
        return resolved, resolved_count
    
    def _choose_best_version(self, hunk: ConflictHunk) -> str:
        """
        智能选择最佳版本
        
        决策规则：
        1. 如果一方为空，选择非空版本
        2. 如果一方只有注释变化，选择有代码变化的版本
        3. 如果一方包含更多代码行，选择更多行的版本
        4. 默认选择我们的版本
        """
        ours = hunk.ours_content.strip()
        theirs = hunk.theirs_content.strip()
        
        # 规则1：一方为空
        if not ours and theirs:
            return hunk.theirs_content
        if ours and not theirs:
            return hunk.ours_content
        
        # 规则2：检查是否只有注释变化
        ours_code = self._remove_comments(ours)
        theirs_code = self._remove_comments(theirs)
        
        if ours_code == theirs_code:
            # 只有注释变化，选择更多注释的版本
            if len(theirs) > len(ours):
                return hunk.theirs_content
        
        # 规则3：选择代码行更多的版本
        ours_lines = len([l for l in ours.splitlines() if l.strip()])
        theirs_lines = len([l for l in theirs.splitlines() if l.strip()])
        
        if theirs_lines > ours_lines * 1.5:
            return hunk.theirs_content
        
        # 默认选择我们的版本
        return hunk.ours_content
    
    def _remove_comments(self, code: str) -> str:
        """移除代码中的注释"""
        # 移除单行注释
        code = re.sub(r'#.*$', '', code, flags=re.MULTILINE)
        code = re.sub(r'//.*$', '', code, flags=re.MULTILINE)
        
        # 移除多行注释
        code = re.sub(r'/\*.*?\*/', '', code, flags=re.DOTALL)
        
        return code.strip()
    
    def get_resolution_suggestions(self, hunk: ConflictHunk) -> Dict[str, Any]:
        """
        获取冲突块的解决建议
        
        Args:
            hunk: 冲突块
            
        Returns:
            建议信息字典
        """
        ours = hunk.ours_content.strip()
        theirs = hunk.theirs_content.strip()
        
        suggestions = {
            'ours_lines': hunk.ours_lines,
            'theirs_lines': hunk.theirs_lines,
            'similarity': self._calculate_similarity(ours, theirs),
            'recommended_strategy': ResolutionStrategy.SMART.value,
            'reason': ''
        }
        
        # 分析并给出建议
        if not ours:
            suggestions['recommended_strategy'] = ResolutionStrategy.THEIRS.value
            suggestions['reason'] = '我们的版本为空，建议使用他们的版本'
        elif not theirs:
            suggestions['recommended_strategy'] = ResolutionStrategy.OURS.value
            suggestions['reason'] = '他们的版本为空，建议使用我们的版本'
        elif suggestions['similarity'] > 0.9:
            suggestions['recommended_strategy'] = ResolutionStrategy.OURS.value
            suggestions['reason'] = '两个版本高度相似，建议使用我们的版本'
        elif hunk.ours_lines == 0 and hunk.theirs_lines > 0:
            suggestions['recommended_strategy'] = ResolutionStrategy.THEIRS.value
            suggestions['reason'] = '我们的版本没有实质内容，建议使用他们的版本'
        else:
            suggestions['reason'] = '建议使用智能策略自动选择最佳版本'
        
        return suggestions
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算两个文本的相似度"""
        if not text1 and not text2:
            return 1.0
        if not text1 or not text2:
            return 0.0
        
        # 简单的相似度计算：基于共同字符
        set1 = set(text1.split())
        set2 = set(text2.split())
        
        intersection = len(set1 & set2)
        union = len(set1 | set2)
        
        return intersection / union if union > 0 else 0.0
