#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
History Manager - Git冲突解决历史管理模块
Tracks and manages conflict resolution history.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict, field


@dataclass
class ResolutionHistory:
    """解决历史记录"""
    id: str
    timestamp: str
    file_path: str
    strategy: str
    hunks_resolved: int
    hunks_total: int
    success: bool
    backup_id: Optional[str] = None
    duration_ms: int = 0
    error_message: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)


class HistoryManager:
    """历史记录管理器"""
    
    def __init__(self, repo_path: str = ".", history_dir: str = ".gitconflictpilot/history"):
        """
        初始化历史管理器
        
        Args:
            repo_path: Git仓库路径
            history_dir: 历史记录目录
        """
        self.repo_path = Path(repo_path).resolve()
        self.history_dir = self.repo_path / history_dir
        self.history_dir.mkdir(parents=True, exist_ok=True)
        
        self.history_file = self.history_dir / "resolution_history.json"
        self._history: List[ResolutionHistory] = []
        self._load_history()
    
    def _load_history(self):
        """加载历史记录"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._history = [
                        ResolutionHistory(**item) for item in data
                    ]
            except (json.JSONDecodeError, KeyError):
                self._history = []
    
    def _save_history(self):
        """保存历史记录"""
        data = [asdict(h) for h in self._history]
        with open(self.history_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_record(
        self,
        file_path: str,
        strategy: str,
        hunks_resolved: int,
        hunks_total: int,
        success: bool,
        backup_id: Optional[str] = None,
        duration_ms: int = 0,
        error_message: str = "",
        metadata: Optional[Dict] = None
    ) -> ResolutionHistory:
        """
        添加解决历史记录
        
        Args:
            file_path: 文件路径
            strategy: 解决策略
            hunks_resolved: 已解决冲突数
            hunks_total: 总冲突数
            success: 是否成功
            backup_id: 备份ID
            duration_ms: 耗时（毫秒）
            error_message: 错误信息
            metadata: 额外元数据
            
        Returns:
            历史记录
        """
        timestamp = datetime.now().isoformat()
        record_id = f"{timestamp.replace(':', '-').replace('.', '-')}"
        
        record = ResolutionHistory(
            id=record_id,
            timestamp=timestamp,
            file_path=file_path,
            strategy=strategy,
            hunks_resolved=hunks_resolved,
            hunks_total=hunks_total,
            success=success,
            backup_id=backup_id,
            duration_ms=duration_ms,
            error_message=error_message,
            metadata=metadata or {}
        )
        
        self._history.append(record)
        self._save_history()
        
        return record
    
    def get_history(
        self,
        file_path: Optional[str] = None,
        limit: int = 100
    ) -> List[ResolutionHistory]:
        """
        获取历史记录
        
        Args:
            file_path: 可选，筛选特定文件
            limit: 返回数量限制
            
        Returns:
            历史记录列表
        """
        if file_path:
            records = [
                h for h in self._history
                if h.file_path == file_path
            ]
        else:
            records = self._history.copy()
        
        # 按时间倒序
        records.sort(key=lambda h: h.timestamp, reverse=True)
        
        return records[:limit]
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        if not self._history:
            return {
                'total_resolutions': 0,
                'successful_resolutions': 0,
                'failed_resolutions': 0,
                'success_rate': 0,
                'total_conflicts_resolved': 0,
                'average_duration_ms': 0,
                'most_used_strategy': None
            }
        
        successful = sum(1 for h in self._history if h.success)
        failed = len(self._history) - successful
        total_conflicts = sum(h.hunks_resolved for h in self._history)
        avg_duration = sum(h.duration_ms for h in self._history) / len(self._history)
        
        # 统计策略使用频率
        strategy_counts: Dict[str, int] = {}
        for h in self._history:
            strategy_counts[h.strategy] = strategy_counts.get(h.strategy, 0) + 1
        
        most_used = max(strategy_counts.items(), key=lambda x: x[1])[0] if strategy_counts else None
        
        return {
            'total_resolutions': len(self._history),
            'successful_resolutions': successful,
            'failed_resolutions': failed,
            'success_rate': round(successful / len(self._history) * 100, 1) if self._history else 0,
            'total_conflicts_resolved': total_conflicts,
            'average_duration_ms': round(avg_duration, 2),
            'most_used_strategy': most_used,
            'strategy_distribution': strategy_counts
        }
    
    def clear_history(self, before: Optional[str] = None) -> int:
        """
        清除历史记录
        
        Args:
            before: 可选，清除此时间之前的记录
            
        Returns:
            清除的记录数
        """
        if before:
            original_count = len(self._history)
            self._history = [
                h for h in self._history
                if h.timestamp >= before
            ]
            cleared = original_count - len(self._history)
        else:
            cleared = len(self._history)
            self._history = []
        
        self._save_history()
        return cleared
    
    def export_history(self, output_path: str, format: str = "json") -> bool:
        """
        导出历史记录
        
        Args:
            output_path: 输出文件路径
            format: 导出格式 (json, csv, markdown)
            
        Returns:
            是否导出成功
        """
        try:
            output = Path(output_path)
            
            if format == "json":
                data = [asdict(h) for h in self._history]
                with open(output, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
                    
            elif format == "csv":
                import csv
                with open(output, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.DictWriter(f, fieldnames=[
                        'id', 'timestamp', 'file_path', 'strategy',
                        'hunks_resolved', 'hunks_total', 'success',
                        'backup_id', 'duration_ms', 'error_message'
                    ])
                    writer.writeheader()
                    for h in self._history:
                        writer.writerow(asdict(h))
                        
            elif format == "markdown":
                lines = [
                    "# Git冲突解决历史",
                    "",
                    f"**导出时间**: {datetime.now().isoformat()}",
                    "",
                    "## 记录列表",
                    ""
                ]
                
                for h in self._history:
                    status = "✅" if h.success else "❌"
                    lines.extend([
                        f"### {status} {h.file_path}",
                        f"- **时间**: {h.timestamp}",
                        f"- **策略**: {h.strategy}",
                        f"- **解决进度**: {h.hunks_resolved}/{h.hunks_total}",
                        f"- **耗时**: {h.duration_ms}ms",
                        ""
                    ])
                
                with open(output, 'w', encoding='utf-8') as f:
                    f.write('\n'.join(lines))
            
            return True
            
        except Exception as e:
            print(f"导出失败: {e}")
            return False
