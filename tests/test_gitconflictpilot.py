#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for GitConflictPilot
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from gitconflictpilot.detector import ConflictDetector, ConflictHunk
from gitconflictpilot.resolver import ConflictResolver, ResolutionStrategy
from gitconflictpilot.analyzer import ConflictAnalyzer
from gitconflictpilot.backup import BackupManager
from gitconflictpilot.history import HistoryManager


class TestConflictDetector(unittest.TestCase):
    """测试冲突检测器"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.detector = ConflictDetector(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_parse_conflict_markers(self):
        """测试解析冲突标记"""
        conflict_content = """line 1
<<<<<<< HEAD
our content
=======
their content
>>>>>>> branch
line 2
"""
        hunks = self.detector._parse_conflicts(conflict_content)
        
        self.assertEqual(len(hunks), 1)
        self.assertEqual(hunks[0].start_line, 2)
        self.assertEqual(hunks[0].ours_content, "our content\n")
        self.assertEqual(hunks[0].theirs_content, "their content\n")
    
    def test_multiple_conflicts(self):
        """测试多个冲突块"""
        conflict_content = """<<<<<<< HEAD
ours1
=======
theirs1
>>>>>>> branch
middle
<<<<<<< HEAD
ours2
=======
theirs2
>>>>>>> branch
"""
        hunks = self.detector._parse_conflicts(conflict_content)
        
        self.assertEqual(len(hunks), 2)
    
    def test_no_conflict(self):
        """测试无冲突文件"""
        normal_content = "line 1\nline 2\nline 3\n"
        hunks = self.detector._parse_conflicts(normal_content)
        
        self.assertEqual(len(hunks), 0)


class TestConflictResolver(unittest.TestCase):
    """测试冲突解决器"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.resolver = ConflictResolver(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_resolve_ours(self):
        """测试使用我们的版本"""
        content = """line 1
<<<<<<< HEAD
our content
=======
their content
>>>>>>> branch
line 2
"""
        hunk = ConflictHunk(
            start_line=2,
            separator_line=4,
            end_line=6,
            ours_content="our content\n",
            theirs_content="their content\n"
        )
        
        resolved, count = self.resolver._resolve_ours(content, [hunk])
        
        self.assertEqual(count, 1)
        self.assertIn("our content", resolved)
        self.assertNotIn("their content", resolved)
    
    def test_resolve_theirs(self):
        """测试使用他们的版本"""
        content = """line 1
<<<<<<< HEAD
our content
=======
their content
>>>>>>> branch
line 2
"""
        hunk = ConflictHunk(
            start_line=2,
            separator_line=4,
            end_line=6,
            ours_content="our content\n",
            theirs_content="their content\n"
        )
        
        resolved, count = self.resolver._resolve_theirs(content, [hunk])
        
        self.assertEqual(count, 1)
        self.assertIn("their content", resolved)
        self.assertNotIn("our content", resolved)
    
    def test_calculate_similarity(self):
        """测试相似度计算"""
        sim1 = self.resolver._calculate_similarity("hello world", "hello world")
        self.assertEqual(sim1, 1.0)
        
        sim2 = self.resolver._calculate_similarity("hello", "world")
        self.assertEqual(sim2, 0.0)
        
        sim3 = self.resolver._calculate_similarity("hello world", "hello there")
        self.assertGreater(sim3, 0)


class TestConflictAnalyzer(unittest.TestCase):
    """测试冲突分析器"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.analyzer = ConflictAnalyzer(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_identify_conflict_type(self):
        """测试冲突类型识别"""
        hunk = ConflictHunk(
            start_line=1,
            separator_line=3,
            end_line=5,
            ours_content="import os\n",
            theirs_content="import sys\n"
        )
        
        conflict_type = self.analyzer._identify_conflict_type(hunk)
        self.assertEqual(conflict_type, "import_conflict")
    
    def test_calculate_risk_score(self):
        """测试风险分数计算"""
        # 低风险
        score1 = self.analyzer._calculate_risk_score(1, 1, {'low': 1, 'medium': 0, 'high': 0, 'critical': 0})
        self.assertLess(score1, 30)
        
        # 高风险
        score2 = self.analyzer._calculate_risk_score(10, 50, {'low': 0, 'medium': 5, 'high': 3, 'critical': 2})
        self.assertGreater(score2, 50)


class TestBackupManager(unittest.TestCase):
    """测试备份管理器"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.backup_mgr = BackupManager(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_and_restore_backup(self):
        """测试创建和恢复备份"""
        # 创建测试文件
        test_file = Path(self.temp_dir) / "test.txt"
        test_file.write_text("original content")
        
        # 创建备份
        record = self.backup_mgr.create_backup("test.txt", conflict_count=1)
        
        self.assertIsNotNone(record)
        self.assertEqual(record.original_path, "test.txt")
        
        # 修改文件
        test_file.write_text("modified content")
        
        # 恢复备份
        success = self.backup_mgr.restore_backup(record.id)
        self.assertTrue(success)
        
        # 验证恢复
        self.assertEqual(test_file.read_text(), "original content")


class TestHistoryManager(unittest.TestCase):
    """测试历史管理器"""
    
    def setUp(self):
        """设置测试环境"""
        self.temp_dir = tempfile.mkdtemp()
        self.history = HistoryManager(self.temp_dir)
    
    def tearDown(self):
        """清理测试环境"""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_add_and_get_history(self):
        """测试添加和获取历史"""
        record = self.history.add_record(
            file_path="test.txt",
            strategy="smart",
            hunks_resolved=2,
            hunks_total=2,
            success=True
        )
        
        self.assertIsNotNone(record.id)
        
        records = self.history.get_history()
        self.assertEqual(len(records), 1)
    
    def test_get_stats(self):
        """测试获取统计"""
        self.history.add_record("file1.txt", "smart", 1, 1, True)
        self.history.add_record("file2.txt", "ours", 1, 1, False)
        
        stats = self.history.get_stats()
        
        self.assertEqual(stats['total_resolutions'], 2)
        self.assertEqual(stats['successful_resolutions'], 1)
        self.assertEqual(stats['success_rate'], 50.0)


if __name__ == "__main__":
    unittest.main()
