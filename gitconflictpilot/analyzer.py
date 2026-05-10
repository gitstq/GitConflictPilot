#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conflict Analyzer - Git冲突智能分析模块
Provides AI-powered analysis and insights for Git conflicts.
"""

import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any

from .detector import ConflictFile, ConflictHunk, ConflictSeverity, ConflictType


@dataclass
class AnalysisReport:
    """冲突分析报告"""
    repo_path: str
    total_files: int
    total_conflicts: int
    severity_breakdown: Dict[str, int]
    type_breakdown: Dict[str, int]
    risk_score: float  # 0-100
    recommendations: List[str]
    estimated_resolution_time: int  # 分钟
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()


@dataclass
class ConflictInsight:
    """单个冲突的洞察"""
    file_path: str
    hunk_index: int
    conflict_type: str
    severity: str
    possible_causes: List[str]
    resolution_hints: List[str]
    code_context: str
    suggested_strategy: str


class ConflictAnalyzer:
    """Git冲突分析器"""
    
    # 常见冲突模式及其原因
    CONFLICT_PATTERNS = {
        'import_conflict': {
            'pattern': r'^(import|from)\s+',
            'causes': ['导入语句冲突', '依赖版本不一致', '模块重命名'],
            'hints': ['检查依赖版本', '确认导入顺序', '考虑使用绝对导入']
        },
        'function_signature': {
            'pattern': r'def\s+\w+\s*\([^)]*\)',
            'causes': ['函数签名变更', '参数修改', '返回类型变更'],
            'hints': ['检查函数调用处', '确认参数兼容性', '更新调用代码']
        },
        'class_definition': {
            'pattern': r'class\s+\w+',
            'causes': ['类定义变更', '继承关系修改', '方法签名变更'],
            'hints': ['检查子类兼容性', '确认接口一致性', '更新相关代码']
        },
        'config_change': {
            'pattern': r'("?\w+"?\s*[:=]\s*[^,\n]+)',
            'causes': ['配置项变更', '环境变量修改', '默认值调整'],
            'hints': ['检查配置兼容性', '确认环境依赖', '更新文档']
        },
        'whitespace': {
            'pattern': r'^\s*$',
            'causes': ['空白字符差异', '格式化工具差异', '编辑器配置不同'],
            'hints': ['统一代码格式化配置', '使用.editorconfig', '运行格式化工具']
        }
    }
    
    def __init__(self, repo_path: str = "."):
        """
        初始化冲突分析器
        
        Args:
            repo_path: Git仓库路径
        """
        self.repo_path = Path(repo_path).resolve()
    
    def analyze_all(self, conflict_files: List[ConflictFile]) -> AnalysisReport:
        """
        分析所有冲突文件，生成综合报告
        
        Args:
            conflict_files: 冲突文件列表
            
        Returns:
            分析报告
        """
        if not conflict_files:
            return AnalysisReport(
                repo_path=str(self.repo_path),
                total_files=0,
                total_conflicts=0,
                severity_breakdown={'low': 0, 'medium': 0, 'high': 0, 'critical': 0},
                type_breakdown={'content': 0, 'binary': 0, 'rename': 0, 'delete': 0},
                risk_score=0,
                recommendations=['没有发现冲突，代码库状态良好'],
                estimated_resolution_time=0
            )
        
        # 统计分析
        severity_breakdown = {'low': 0, 'medium': 0, 'high': 0, 'critical': 0}
        type_breakdown = {'content': 0, 'binary': 0, 'rename': 0, 'delete': 0}
        total_conflicts = 0
        
        for cf in conflict_files:
            severity_breakdown[cf.severity.value] += 1
            type_breakdown[cf.conflict_type.value] += 1
            total_conflicts += cf.total_conflicts
        
        # 计算风险分数
        risk_score = self._calculate_risk_score(
            len(conflict_files),
            total_conflicts,
            severity_breakdown
        )
        
        # 生成建议
        recommendations = self._generate_recommendations(
            conflict_files,
            severity_breakdown,
            type_breakdown
        )
        
        # 估算解决时间
        estimated_time = self._estimate_resolution_time(
            total_conflicts,
            severity_breakdown
        )
        
        return AnalysisReport(
            repo_path=str(self.repo_path),
            total_files=len(conflict_files),
            total_conflicts=total_conflicts,
            severity_breakdown=severity_breakdown,
            type_breakdown=type_breakdown,
            risk_score=risk_score,
            recommendations=recommendations,
            estimated_resolution_time=estimated_time
        )
    
    def analyze_hunk(self, conflict_file: ConflictFile, hunk_index: int) -> ConflictInsight:
        """
        分析单个冲突块
        
        Args:
            conflict_file: 冲突文件
            hunk_index: 冲突块索引
            
        Returns:
            冲突洞察
        """
        if hunk_index >= len(conflict_file.hunks):
            raise IndexError(f"冲突块索引 {hunk_index} 超出范围")
        
        hunk = conflict_file.hunks[hunk_index]
        
        # 识别冲突模式
        conflict_type = self._identify_conflict_type(hunk)
        
        # 生成可能原因
        possible_causes = self._identify_causes(hunk, conflict_type)
        
        # 生成解决提示
        resolution_hints = self._generate_hints(hunk, conflict_type)
        
        # 提取代码上下文
        code_context = self._extract_context(hunk)
        
        # 建议解决策略
        suggested_strategy = self._suggest_strategy(hunk, conflict_type)
        
        return ConflictInsight(
            file_path=conflict_file.path,
            hunk_index=hunk_index,
            conflict_type=conflict_type,
            severity=conflict_file.severity.value,
            possible_causes=possible_causes,
            resolution_hints=resolution_hints,
            code_context=code_context,
            suggested_strategy=suggested_strategy
        )
    
    def _calculate_risk_score(
        self,
        total_files: int,
        total_conflicts: int,
        severity_breakdown: Dict[str, int]
    ) -> float:
        """计算风险分数（0-100）"""
        # 基础分数基于冲突数量
        base_score = min(total_conflicts * 2, 40)
        
        # 严重程度加权
        severity_weights = {
            'low': 1,
            'medium': 3,
            'high': 5,
            'critical': 10
        }
        
        severity_score = sum(
            severity_breakdown.get(s, 0) * w
            for s, w in severity_weights.items()
        )
        severity_score = min(severity_score * 2, 40)
        
        # 文件数量影响
        file_score = min(total_files * 2, 20)
        
        return min(base_score + severity_score + file_score, 100)
    
    def _generate_recommendations(
        self,
        conflict_files: List[ConflictFile],
        severity_breakdown: Dict[str, int],
        type_breakdown: Dict[str, int]
    ) -> List[str]:
        """生成解决建议"""
        recommendations = []
        
        # 基于严重程度
        if severity_breakdown.get('critical', 0) > 0:
            recommendations.append(
                f"⚠️ 发现 {severity_breakdown['critical']} 个关键冲突，建议优先处理"
            )
        
        if severity_breakdown.get('high', 0) > 0:
            recommendations.append(
                f"🔴 发现 {severity_breakdown['high']} 个高严重度冲突，需要仔细审查"
            )
        
        # 基于冲突类型
        if type_breakdown.get('binary', 0) > 0:
            recommendations.append(
                "📦 存在二进制文件冲突，需要手动选择正确版本"
            )
        
        if type_breakdown.get('rename', 0) > 0:
            recommendations.append(
                "📝 存在重命名冲突，请确认文件命名约定"
            )
        
        # 基于文件类型分析
        file_types = self._analyze_file_types(conflict_files)
        if 'config' in file_types:
            recommendations.append(
                "⚙️ 配置文件存在冲突，请确认环境配置一致性"
            )
        
        if 'test' in file_types:
            recommendations.append(
                "🧪 测试文件存在冲突，解决后请运行测试验证"
            )
        
        # 通用建议
        if not recommendations:
            recommendations.append(
                "✅ 冲突情况可控，建议按文件逐一解决"
            )
        
        recommendations.append(
            "💡 建议使用 'gitconflictpilot resolve --strategy smart' 自动解决简单冲突"
        )
        
        return recommendations
    
    def _estimate_resolution_time(
        self,
        total_conflicts: int,
        severity_breakdown: Dict[str, int]
    ) -> int:
        """估算解决时间（分钟）"""
        # 基础时间：每个冲突2分钟
        base_time = total_conflicts * 2
        
        # 严重程度加成
        severity_time = (
            severity_breakdown.get('low', 0) * 1 +
            severity_breakdown.get('medium', 0) * 3 +
            severity_breakdown.get('high', 0) * 5 +
            severity_breakdown.get('critical', 0) * 10
        )
        
        return base_time + severity_time
    
    def _identify_conflict_type(self, hunk: ConflictHunk) -> str:
        """识别冲突类型"""
        ours = hunk.ours_content
        theirs = hunk.theirs_content
        
        for type_name, pattern_info in self.CONFLICT_PATTERNS.items():
            pattern = pattern_info['pattern']
            if re.search(pattern, ours, re.MULTILINE) or re.search(pattern, theirs, re.MULTILINE):
                return type_name
        
        return 'unknown'
    
    def _identify_causes(self, hunk: ConflictHunk, conflict_type: str) -> List[str]:
        """识别可能的原因"""
        if conflict_type in self.CONFLICT_PATTERNS:
            return self.CONFLICT_PATTERNS[conflict_type]['causes']
        
        # 默认原因分析
        causes = []
        
        if not hunk.ours_content.strip():
            causes.append('我们的版本被删除')
        elif not hunk.theirs_content.strip():
            causes.append('他们的版本被删除')
        else:
            causes.append('双方同时修改了相同代码')
            causes.append('分支合并时间过长导致代码差异')
        
        return causes
    
    def _generate_hints(self, hunk: ConflictHunk, conflict_type: str) -> List[str]:
        """生成解决提示"""
        if conflict_type in self.CONFLICT_PATTERNS:
            hints = self.CONFLICT_PATTERNS[conflict_type]['hints'].copy()
        else:
            hints = []
        
        # 添加通用提示
        hints.append('仔细比较两个版本的差异')
        hints.append('确保解决后代码逻辑正确')
        
        return hints
    
    def _extract_context(self, hunk: ConflictHunk) -> str:
        """提取代码上下文"""
        ours_lines = hunk.ours_content.strip().split('\n')
        theirs_lines = hunk.theirs_content.strip().split('\n')
        
        # 取前5行作为上下文
        ours_preview = '\n'.join(ours_lines[:5])
        theirs_preview = '\n'.join(theirs_lines[:5])
        
        return f"我们的版本:\n{ours_preview}\n\n他们的版本:\n{theirs_preview}"
    
    def _suggest_strategy(self, hunk: ConflictHunk, conflict_type: str) -> str:
        """建议解决策略"""
        # 基于冲突类型建议策略
        strategy_map = {
            'import_conflict': 'union',
            'function_signature': 'manual',
            'class_definition': 'manual',
            'config_change': 'smart',
            'whitespace': 'ours'
        }
        
        return strategy_map.get(conflict_type, 'smart')
    
    def _analyze_file_types(self, conflict_files: List[ConflictFile]) -> List[str]:
        """分析冲突文件类型"""
        types = []
        
        for cf in conflict_files:
            path = cf.path.lower()
            
            if any(ext in path for ext in ['.json', '.yaml', '.yml', '.toml', '.ini', '.env']):
                types.append('config')
            if 'test' in path or 'spec' in path:
                types.append('test')
            if any(ext in path for ext in ['.md', '.rst', '.txt']):
                types.append('docs')
        
        return list(set(types))
    
    def generate_summary(self, report: AnalysisReport) -> str:
        """
        生成人类可读的分析摘要
        
        Args:
            report: 分析报告
            
        Returns:
            摘要文本
        """
        lines = [
            "=" * 60,
            "📊 Git冲突分析报告",
            "=" * 60,
            "",
            f"📁 仓库路径: {report.repo_path}",
            f"📄 冲突文件数: {report.total_files}",
            f"⚠️ 冲突总数: {report.total_conflicts}",
            f"🎯 风险分数: {report.risk_score:.1f}/100",
            f"⏱️ 预计解决时间: {report.estimated_resolution_time} 分钟",
            "",
            "📈 严重程度分布:",
        ]
        
        severity_emoji = {
            'low': '🟢',
            'medium': '🟡', 
            'high': '🟠',
            'critical': '🔴'
        }
        
        for severity, count in report.severity_breakdown.items():
            emoji = severity_emoji.get(severity, '⚪')
            lines.append(f"  {emoji} {severity}: {count}")
        
        lines.extend([
            "",
            "💡 建议:",
        ])
        
        for i, rec in enumerate(report.recommendations, 1):
            lines.append(f"  {i}. {rec}")
        
        lines.extend([
            "",
            "=" * 60,
        ])
        
        return '\n'.join(lines)
