#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TUI Interface - 终端用户界面模块
Provides beautiful terminal interface for GitConflictPilot.
"""

import sys
from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from enum import Enum

from .detector import ConflictFile, ConflictSeverity
from .resolver import ResolutionStrategy, ResolutionResult
from .analyzer import AnalysisReport


class Color(Enum):
    """终端颜色"""
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"
    WHITE = "\033[97m"
    
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"


@dataclass
class TableColumn:
    """表格列定义"""
    header: str
    width: int
    align: str = "left"


class TUIInterface:
    """终端用户界面"""
    
    # 严重程度对应的颜色和图标
    SEVERITY_STYLE = {
        ConflictSeverity.LOW: (Color.GREEN, "🟢"),
        ConflictSeverity.MEDIUM: (Color.YELLOW, "🟡"),
        ConflictSeverity.HIGH: (Color.RED, "🟠"),
        ConflictSeverity.CRITICAL: (Color.BG_RED, "🔴"),
    }
    
    def __init__(self, use_color: bool = True):
        """
        初始化TUI界面
        
        Args:
            use_color: 是否使用颜色
        """
        self.use_color = use_color and self._supports_color()
    
    def _supports_color(self) -> bool:
        """检查终端是否支持颜色"""
        return (
            hasattr(sys.stdout, 'isatty') and
            sys.stdout.isatty() and
            sys.platform != 'win32'
        )
    
    def _colorize(self, text: str, color) -> str:
        """添加颜色"""
        if not self.use_color:
            return text
        if isinstance(color, Color):
            color_code = color.value
        else:
            # 支持颜色列表
            color_code = "".join(c.value for c in color)
        return f"{color_code}{text}{Color.RESET.value}"
    
    def print_header(self, title: str, subtitle: str = ""):
        """打印标题头"""
        width = 60
        lines = [
            self._colorize("═" * width, Color.CYAN),
            self._colorize(f"  {title}", [Color.BOLD, Color.WHITE]),
        ]
        
        if subtitle:
            lines.append(self._colorize(f"  {subtitle}", Color.DIM))
        
        lines.append(self._colorize("═" * width, Color.CYAN))
        lines.append("")
        
        print("\n".join(lines))
    
    def print_conflict_list(self, conflicts: List[ConflictFile]):
        """打印冲突文件列表"""
        if not conflicts:
            print(self._colorize("✅ 没有发现冲突文件", Color.GREEN))
            return
        
        # 表头
        columns = [
            TableColumn("状态", 8),
            TableColumn("文件路径", 40),
            TableColumn("冲突数", 8),
            TableColumn("严重程度", 12),
        ]
        
        self._print_table_header(columns)
        
        # 数据行
        for cf in conflicts:
            color, icon = self.SEVERITY_STYLE.get(cf.severity, (Color.WHITE, "⚪"))
            
            row = [
                icon,
                self._truncate(cf.path, columns[1].width),
                str(cf.total_conflicts),
                cf.severity.value,
            ]
            
            self._print_table_row(row, columns, color if cf.severity in [ConflictSeverity.HIGH, ConflictSeverity.CRITICAL] else None)
        
        self._print_table_separator(columns)
        
        # 统计
        total_conflicts = sum(cf.total_conflicts for cf in conflicts)
        print(f"\n{self._colorize('📊 统计:', Color.BOLD)} {len(conflicts)} 个文件, {total_conflicts} 个冲突")
    
    def print_analysis_report(self, report: AnalysisReport):
        """打印分析报告"""
        self.print_header("📊 冲突分析报告", f"仓库: {report.repo_path}")
        
        # 基本信息
        info_lines = [
            f"📄 冲突文件数: {self._colorize(str(report.total_files), Color.CYAN)}",
            f"⚠️ 冲突总数: {self._colorize(str(report.total_conflicts), Color.YELLOW)}",
            f"🎯 风险分数: {self._format_risk_score(report.risk_score)}",
            f"⏱️ 预计解决时间: {self._colorize(f'{report.estimated_resolution_time} 分钟', Color.BLUE)}",
        ]
        
        for line in info_lines:
            print(f"  {line}")
        
        print()
        
        # 严重程度分布
        print(self._colorize("  📈 严重程度分布:", Color.BOLD))
        severity_emoji = {
            'low': '🟢',
            'medium': '🟡',
            'high': '🟠',
            'critical': '🔴'
        }
        
        for severity, count in report.severity_breakdown.items():
            emoji = severity_emoji.get(severity, '⚪')
            bar = self._progress_bar(count, report.total_files, 20)
            print(f"    {emoji} {severity:8s}: {bar} {count}")
        
        print()
        
        # 建议
        print(self._colorize("  💡 解决建议:", Color.BOLD))
        for i, rec in enumerate(report.recommendations, 1):
            print(f"    {i}. {rec}")
        
        print()
    
    def print_resolution_result(self, result: ResolutionResult):
        """打印解决结果"""
        if result.success:
            icon = self._colorize("✅", Color.GREEN)
            status = self._colorize("成功", Color.GREEN)
        else:
            icon = self._colorize("❌", Color.RED)
            status = self._colorize("失败", Color.RED)
        
        lines = [
            f"{icon} {result.file_path}",
            f"   策略: {result.strategy.value}",
            f"   进度: {result.hunks_resolved}/{result.hunks_total}",
            f"   状态: {status}",
            f"   消息: {result.message}",
        ]
        
        if result.backup_path:
            lines.append(f"   备份: {result.backup_path}")
        
        print("\n".join(lines))
    
    def print_summary(self, results: List[ResolutionResult]):
        """打印批量解决摘要"""
        success = sum(1 for r in results if r.success)
        failed = len(results) - success
        
        print()
        print(self._colorize("═" * 60, Color.CYAN))
        print(self._colorize("  📋 解决摘要", Color.BOLD))
        print(self._colorize("═" * 60, Color.CYAN))
        
        print(f"\n  ✅ 成功: {self._colorize(str(success), Color.GREEN)}")
        print(f"  ❌ 失败: {self._colorize(str(failed), Color.RED)}")
        print(f"  📊 成功率: {self._colorize(f'{success/len(results)*100:.1f}%', Color.CYAN)}")
        print()
    
    def print_help(self):
        """打印帮助信息"""
        help_text = """
╔════════════════════════════════════════════════════════════╗
║          🔧 GitConflictPilot - 命令帮助                     ║
╠════════════════════════════════════════════════════════════╣
║                                                            ║
║  detect        检测Git冲突                                 ║
║  resolve       解决Git冲突                                 ║
║  analyze       分析冲突详情                                ║
║  history       查看解决历史                                ║
║  backup        管理备份文件                                ║
║  stats         显示统计信息                                ║
║                                                            ║
║  --strategy    指定解决策略                                ║
║                (ours/theirs/union/smart/manual)            ║
║  --no-backup   不创建备份                                  ║
║  --verbose     详细输出                                    ║
║  --help        显示帮助                                    ║
║                                                            ║
╚════════════════════════════════════════════════════════════╝
"""
        print(help_text)
    
    def _print_table_header(self, columns: List[TableColumn]):
        """打印表头"""
        headers = []
        for col in columns:
            header = self._colorize(col.header.ljust(col.width), Color.BOLD)
            headers.append(header[:col.width])
        
        print("  " + " │ ".join(headers))
        print("  " + "─┼─".join("─" * c.width for c in columns))
    
    def _print_table_row(self, values: List[str], columns: List[TableColumn], color: Optional[Color] = None):
        """打印表格行"""
        cells = []
        for i, (val, col) in enumerate(zip(values, columns)):
            cell = val[:col.width].ljust(col.width)
            if color:
                cell = self._colorize(cell, color)
            cells.append(cell)
        
        print("  " + " │ ".join(cells))
    
    def _print_table_separator(self, columns: List[TableColumn]):
        """打印表格分隔线"""
        print("  " + "─┴─".join("─" * c.width for c in columns))
    
    def _truncate(self, text: str, max_len: int) -> str:
        """截断文本"""
        if len(text) <= max_len:
            return text
        return "..." + text[-(max_len - 3):]
    
    def _format_risk_score(self, score: float) -> str:
        """格式化风险分数"""
        if score < 30:
            color = Color.GREEN
            level = "低风险"
        elif score < 60:
            color = Color.YELLOW
            level = "中等风险"
        elif score < 80:
            color = Color.RED
            level = "高风险"
        else:
            color = Color.BG_RED
            level = "极高风险"
        
        return f"{self._colorize(f'{score:.1f}', color)} ({level})"
    
    def _progress_bar(self, value: int, total: int, width: int) -> str:
        """生成进度条"""
        if total == 0:
            filled = 0
        else:
            filled = int(width * value / total)
        
        bar = "█" * filled + "░" * (width - filled)
        return self._colorize(bar, Color.CYAN)


def print_banner():
    """打印程序横幅"""
    banner = """
    ╔═══════════════════════════════════════════════════════════╗
    ║                                                           ║
    ║   🔧 GitConflictPilot - Git冲突智能解决引擎               ║
    ║                                                           ║
    ║   轻量级 · 零依赖 · 智能分析 · 多策略解决                 ║
    ║                                                           ║
    ╚═══════════════════════════════════════════════════════════╝
    """
    print(banner)
