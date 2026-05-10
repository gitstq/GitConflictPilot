#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Backup Manager - Git冲突备份管理模块
Manages backups of conflicted files for safe recovery.
"""

import json
import os
import shutil
import hashlib
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from dataclasses import dataclass, asdict


@dataclass
class BackupRecord:
    """备份记录"""
    id: str
    original_path: str
    backup_path: str
    timestamp: str
    file_size: int
    checksum: str
    conflict_count: int
    resolution_strategy: str = ""
    notes: str = ""


class BackupManager:
    """备份管理器"""
    
    def __init__(self, repo_path: str = ".", backup_dir: str = ".gitconflictpilot/backups"):
        """
        初始化备份管理器
        
        Args:
            repo_path: Git仓库路径
            backup_dir: 备份目录路径
        """
        self.repo_path = Path(repo_path).resolve()
        self.backup_dir = self.repo_path / backup_dir
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.index_file = self.backup_dir / "backup_index.json"
        self._index: Dict[str, BackupRecord] = {}
        self._load_index()
    
    def _load_index(self):
        """加载备份索引"""
        if self.index_file.exists():
            try:
                with open(self.index_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self._index = {
                        k: BackupRecord(**v) for k, v in data.items()
                    }
            except (json.JSONDecodeError, KeyError):
                self._index = {}
    
    def _save_index(self):
        """保存备份索引"""
        data = {k: asdict(v) for k, v in self._index.items()}
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def create_backup(
        self,
        file_path: str,
        conflict_count: int = 0,
        resolution_strategy: str = "",
        notes: str = ""
    ) -> Optional[BackupRecord]:
        """
        创建文件备份
        
        Args:
            file_path: 要备份的文件路径
            conflict_count: 冲突数量
            resolution_strategy: 解决策略
            notes: 备注信息
            
        Returns:
            备份记录，失败返回None
        """
        source = self.repo_path / file_path
        
        if not source.exists():
            return None
        
        # 生成备份ID
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_id = f"{source.stem}_{timestamp}_{hashlib.md5(str(source).encode()).hexdigest()[:8]}"
        
        # 创建备份文件
        backup_name = f"{backup_id}{source.suffix}"
        backup_path = self.backup_dir / backup_name
        
        try:
            shutil.copy2(source, backup_path)
            
            # 计算校验和
            checksum = self._calculate_checksum(backup_path)
            
            # 创建备份记录
            record = BackupRecord(
                id=backup_id,
                original_path=file_path,
                backup_path=str(backup_path),
                timestamp=timestamp,
                file_size=backup_path.stat().st_size,
                checksum=checksum,
                conflict_count=conflict_count,
                resolution_strategy=resolution_strategy,
                notes=notes
            )
            
            self._index[backup_id] = record
            self._save_index()
            
            return record
            
        except Exception as e:
            print(f"创建备份失败: {e}")
            return None
    
    def restore_backup(self, backup_id: str) -> bool:
        """
        从备份恢复文件
        
        Args:
            backup_id: 备份ID
            
        Returns:
            是否恢复成功
        """
        if backup_id not in self._index:
            return False
        
        record = self._index[backup_id]
        backup_path = Path(record.backup_path)
        original_path = self.repo_path / record.original_path
        
        if not backup_path.exists():
            return False
        
        try:
            # 验证校验和
            if self._calculate_checksum(backup_path) != record.checksum:
                print("警告: 备份文件校验和不匹配")
            
            # 恢复文件
            shutil.copy2(backup_path, original_path)
            return True
            
        except Exception as e:
            print(f"恢复备份失败: {e}")
            return False
    
    def list_backups(self, file_path: Optional[str] = None) -> List[BackupRecord]:
        """
        列出备份记录
        
        Args:
            file_path: 可选，筛选特定文件的备份
            
        Returns:
            备份记录列表
        """
        if file_path:
            return [
                r for r in self._index.values()
                if r.original_path == file_path
            ]
        
        return list(self._index.values())
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        删除备份
        
        Args:
            backup_id: 备份ID
            
        Returns:
            是否删除成功
        """
        if backup_id not in self._index:
            return False
        
        record = self._index[backup_id]
        backup_path = Path(record.backup_path)
        
        try:
            if backup_path.exists():
                backup_path.unlink()
            
            del self._index[backup_id]
            self._save_index()
            
            return True
            
        except Exception:
            return False
    
    def cleanup_old_backups(self, max_age_days: int = 30, max_count: int = 100) -> int:
        """
        清理旧备份
        
        Args:
            max_age_days: 最大保留天数
            max_count: 最大保留数量
            
        Returns:
            清理的备份数量
        """
        deleted = 0
        now = datetime.now()
        
        # 按时间排序
        records = sorted(
            self._index.values(),
            key=lambda r: r.timestamp,
            reverse=True
        )
        
        for i, record in enumerate(records):
            # 检查数量限制
            if i >= max_count:
                if self.delete_backup(record.id):
                    deleted += 1
                continue
            
            # 检查时间限制
            try:
                backup_time = datetime.strptime(record.timestamp, "%Y%m%d_%H%M%S")
                age_days = (now - backup_time).days
                
                if age_days > max_age_days:
                    if self.delete_backup(record.id):
                        deleted += 1
                        
            except ValueError:
                continue
        
        return deleted
    
    def get_backup_stats(self) -> Dict[str, Any]:
        """获取备份统计信息"""
        total_size = sum(r.file_size for r in self._index.values())
        
        return {
            'total_backups': len(self._index),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'backup_dir': str(self.backup_dir),
            'oldest_backup': min(
                (r.timestamp for r in self._index.values()),
                default=None
            ),
            'newest_backup': max(
                (r.timestamp for r in self._index.values()),
                default=None
            )
        }
    
    def _calculate_checksum(self, file_path: Path) -> str:
        """计算文件校验和"""
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            for chunk in iter(lambda: f.read(8192), b''):
                sha256.update(chunk)
        
        return sha256.hexdigest()[:16]
