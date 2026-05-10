#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CLI Entry Point - 命令行入口
Main command-line interface for GitConflictPilot.
"""

import argparse
import sys
import time
from pathlib import Path
from typing import List, Optional

from .detector import ConflictDetector, ConflictFile
from .resolver import ConflictResolver, ResolutionStrategy, ResolutionResult
from .analyzer import ConflictAnalyzer, AnalysisReport
from .backup import BackupManager
from .history import HistoryManager
from .tui import TUIInterface, print_banner


def create_parser() -> argparse.ArgumentParser:
    """创建命令行参数解析器"""
    parser = argparse.ArgumentParser(
        prog="gitconflictpilot",
        description="🔧 GitConflictPilot - 轻量级终端Git冲突智能解决引擎",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  gitconflictpilot detect                    # 检测所有冲突
  gitconflictpilot resolve --strategy smart  # 智能解决所有冲突
  gitconflictpilot analyze                   # 分析冲突详情
  gitconflictpilot history                   # 查看解决历史
  gitconflictpilot backup list               # 列出备份
  gitconflictpilot stats                     # 显示统计信息
        """
    )
    
    parser.add_argument(
        "-v", "--version",
        action="version",
        version="%(prog)s 1.0.0"
    )
    
    parser.add_argument(
        "--no-color",
        action="store_true",
        help="禁用彩色输出"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="详细输出模式"
    )
    
    parser.add_argument(
        "-p", "--path",
        default=".",
        help="Git仓库路径 (默认: 当前目录)"
    )
    
    # 子命令
    subparsers = parser.add_subparsers(dest="command", help="可用命令")
    
    # detect 子命令
    detect_parser = subparsers.add_parser(
        "detect",
        help="检测Git冲突"
    )
    detect_parser.add_argument(
        "-f", "--file",
        help="检测指定文件"
    )
    detect_parser.add_argument(
        "--json",
        action="store_true",
        help="以JSON格式输出"
    )
    
    # resolve 子命令
    resolve_parser = subparsers.add_parser(
        "resolve",
        help="解决Git冲突"
    )
    resolve_parser.add_argument(
        "-f", "--file",
        help="解决指定文件的冲突"
    )
    resolve_parser.add_argument(
        "-s", "--strategy",
        choices=["ours", "theirs", "union", "smart", "manual"],
        default="smart",
        help="解决策略 (默认: smart)"
    )
    resolve_parser.add_argument(
        "--no-backup",
        action="store_true",
        help="不创建备份"
    )
    resolve_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="模拟运行，不实际修改文件"
    )
    
    # analyze 子命令
    analyze_parser = subparsers.add_parser(
        "analyze",
        help="分析冲突详情"
    )
    analyze_parser.add_argument(
        "-f", "--file",
        help="分析指定文件"
    )
    analyze_parser.add_argument(
        "--report",
        action="store_true",
        help="生成详细报告"
    )
    
    # history 子命令
    history_parser = subparsers.add_parser(
        "history",
        help="查看解决历史"
    )
    history_parser.add_argument(
        "-f", "--file",
        help="查看指定文件的历史"
    )
    history_parser.add_argument(
        "-l", "--limit",
        type=int,
        default=20,
        help="显示数量限制 (默认: 20)"
    )
    history_parser.add_argument(
        "--clear",
        action="store_true",
        help="清除历史记录"
    )
    history_parser.add_argument(
        "--export",
        help="导出历史记录到文件"
    )
    
    # backup 子命令
    backup_parser = subparsers.add_parser(
        "backup",
        help="管理备份文件"
    )
    backup_parser.add_argument(
        "action",
        choices=["list", "restore", "delete", "cleanup"],
        help="备份操作"
    )
    backup_parser.add_argument(
        "--id",
        help="备份ID"
    )
    backup_parser.add_argument(
        "--max-age",
        type=int,
        default=30,
        help="最大保留天数 (默认: 30)"
    )
    
    # stats 子命令
    stats_parser = subparsers.add_parser(
        "stats",
        help="显示统计信息"
    )
    stats_parser.add_argument(
        "--json",
        action="store_true",
        help="以JSON格式输出"
    )
    
    return parser


def cmd_detect(args, tui: TUIInterface) -> int:
    """执行detect命令"""
    detector = ConflictDetector(args.path)
    
    if args.file:
        conflicts = detector.detect_file(args.file)
        if conflicts:
            conflicts = [conflicts]
        else:
            conflicts = []
    else:
        conflicts = detector.detect_all()
    
    if args.json:
        import json
        data = []
        for cf in conflicts:
            if cf:
                data.append({
                    "path": cf.path,
                    "conflicts": cf.total_conflicts,
                    "severity": cf.severity.value,
                    "is_binary": cf.is_binary,
                    "error": cf.error_message
                })
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        tui.print_header("🔍 冲突检测", f"路径: {Path(args.path).resolve()}")
        tui.print_conflict_list([cf for cf in conflicts if cf])
    
    return 0 if conflicts else 1


def cmd_resolve(args, tui: TUIInterface) -> int:
    """执行resolve命令"""
    detector = ConflictDetector(args.path)
    resolver = ConflictResolver(args.path)
    history = HistoryManager(args.path)
    
    # 检测冲突
    if args.file:
        conflict_file = detector.detect_file(args.file)
        conflicts = [conflict_file] if conflict_file else []
    else:
        conflicts = detector.detect_all()
    
    if not conflicts:
        print(tui._colorize("✅ 没有发现冲突", TUIInterface._get_color("GREEN")))
        return 0
    
    # 转换策略
    strategy_map = {
        "ours": ResolutionStrategy.OURS,
        "theirs": ResolutionStrategy.THEIRS,
        "union": ResolutionStrategy.UNION,
        "smart": ResolutionStrategy.SMART,
        "manual": ResolutionStrategy.MANUAL,
    }
    strategy = strategy_map.get(args.strategy, ResolutionStrategy.SMART)
    
    if args.dry_run:
        print(tui._colorize("🔍 模拟运行模式 - 不会修改文件", TUIInterface._get_color("YELLOW")))
        for cf in conflicts:
            print(f"  将解决: {cf.path} ({cf.total_conflicts} 个冲突)")
        return 0
    
    # 解决冲突
    results: List[ResolutionResult] = []
    
    for cf in conflicts:
        start_time = time.time()
        
        result = resolver.resolve_file(
            cf,
            strategy=strategy,
            create_backup=not args.no_backup
        )
        
        duration_ms = int((time.time() - start_time) * 1000)
        
        # 记录历史
        history.add_record(
            file_path=cf.path,
            strategy=strategy.value,
            hunks_resolved=result.hunks_resolved,
            hunks_total=result.hunks_total,
            success=result.success,
            backup_id=result.backup_path,
            duration_ms=duration_ms
        )
        
        results.append(result)
        
        if args.verbose:
            tui.print_resolution_result(result)
    
    # 打印摘要
    tui.print_summary(results)
    
    return 0 if all(r.success for r in results) else 1


def cmd_analyze(args, tui: TUIInterface) -> int:
    """执行analyze命令"""
    detector = ConflictDetector(args.path)
    analyzer = ConflictAnalyzer(args.path)
    
    # 检测冲突
    if args.file:
        conflict_file = detector.detect_file(args.file)
        conflicts = [conflict_file] if conflict_file else []
    else:
        conflicts = detector.detect_all()
    
    if not conflicts:
        print(tui._colorize("✅ 没有发现冲突", TUIInterface._get_color("GREEN")))
        return 0
    
    # 生成报告
    report = analyzer.analyze_all(conflicts)
    
    if args.report:
        print(analyzer.generate_summary(report))
    else:
        tui.print_analysis_report(report)
    
    return 0


def cmd_history(args, tui: TUIInterface) -> int:
    """执行history命令"""
    history = HistoryManager(args.path)
    
    if args.clear:
        cleared = history.clear_history()
        print(tui._colorize(f"已清除 {cleared} 条历史记录", TUIInterface._get_color("GREEN")))
        return 0
    
    if args.export:
        success = history.export_history(args.export, "markdown")
        if success:
            print(tui._colorize(f"已导出到: {args.export}", TUIInterface._get_color("GREEN")))
            return 0
        else:
            print(tui._colorize("导出失败", TUIInterface._get_color("RED")))
            return 1
    
    records = history.get_history(file_path=args.file, limit=args.limit)
    
    if not records:
        print(tui._colorize("没有历史记录", TUIInterface._get_color("YELLOW")))
        return 0
    
    tui.print_header("📜 解决历史", f"共 {len(records)} 条记录")
    
    for record in records:
        icon = "✅" if record.success else "❌"
        print(f"  {icon} {record.file_path}")
        print(f"     策略: {record.strategy} | 冲突: {record.hunks_resolved}/{record.hunks_total}")
        print(f"     时间: {record.timestamp}")
        print()
    
    return 0


def cmd_backup(args, tui: TUIInterface) -> int:
    """执行backup命令"""
    backup_mgr = BackupManager(args.path)
    
    if args.action == "list":
        backups = backup_mgr.list_backups()
        
        if not backups:
            print(tui._colorize("没有备份文件", TUIInterface._get_color("YELLOW")))
            return 0
        
        tui.print_header("📦 备份列表")
        
        for backup in backups:
            print(f"  📄 {backup.original_path}")
            print(f"     ID: {backup.id}")
            print(f"     时间: {backup.timestamp}")
            print(f"     大小: {backup.file_size} bytes")
            print()
        
        return 0
    
    elif args.action == "restore":
        if not args.id:
            print(tui._colorize("请指定备份ID (--id)", TUIInterface._get_color("RED")))
            return 1
        
        success = backup_mgr.restore_backup(args.id)
        if success:
            print(tui._colorize(f"已恢复备份: {args.id}", TUIInterface._get_color("GREEN")))
            return 0
        else:
            print(tui._colorize("恢复失败", TUIInterface._get_color("RED")))
            return 1
    
    elif args.action == "delete":
        if not args.id:
            print(tui._colorize("请指定备份ID (--id)", TUIInterface._get_color("RED")))
            return 1
        
        success = backup_mgr.delete_backup(args.id)
        if success:
            print(tui._colorize(f"已删除备份: {args.id}", TUIInterface._get_color("GREEN")))
            return 0
        else:
            print(tui._colorize("删除失败", TUIInterface._get_color("RED")))
            return 1
    
    elif args.action == "cleanup":
        cleaned = backup_mgr.cleanup_old_backups(max_age_days=args.max_age)
        print(tui._colorize(f"已清理 {cleaned} 个旧备份", TUIInterface._get_color("GREEN")))
        return 0
    
    return 0


def cmd_stats(args, tui: TUIInterface) -> int:
    """执行stats命令"""
    history = HistoryManager(args.path)
    backup_mgr = BackupManager(args.path)
    detector = ConflictDetector(args.path)
    
    history_stats = history.get_stats()
    backup_stats = backup_mgr.get_backup_stats()
    conflict_stats = detector.get_statistics()
    
    if args.json:
        import json
        data = {
            "history": history_stats,
            "backup": backup_stats,
            "conflicts": conflict_stats
        }
        print(json.dumps(data, indent=2, ensure_ascii=False))
    else:
        tui.print_header("📊 统计信息")
        
        print("  📜 解决历史:")
        print(f"     总解决次数: {history_stats['total_resolutions']}")
        print(f"     成功率: {history_stats['success_rate']}%")
        print(f"     已解决冲突: {history_stats['total_conflicts_resolved']}")
        print(f"     最常用策略: {history_stats['most_used_strategy']}")
        print()
        
        print("  📦 备份信息:")
        print(f"     备份总数: {backup_stats['total_backups']}")
        print(f"     占用空间: {backup_stats['total_size_mb']} MB")
        print()
        
        print("  ⚠️ 当前冲突:")
        print(f"     冲突文件: {conflict_stats['total_files']}")
        print(f"     冲突总数: {conflict_stats['total_conflicts']}")
        print()
    
    return 0


def main(args: Optional[List[str]] = None) -> int:
    """主入口函数"""
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # 初始化TUI
    tui = TUIInterface(use_color=not parsed_args.no_color)
    
    # 没有子命令时显示帮助
    if not parsed_args.command:
        print_banner()
        tui.print_help()
        return 0
    
    # 路由到对应命令
    command_handlers = {
        "detect": cmd_detect,
        "resolve": cmd_resolve,
        "analyze": cmd_analyze,
        "history": cmd_history,
        "backup": cmd_backup,
        "stats": cmd_stats,
    }
    
    handler = command_handlers.get(parsed_args.command)
    if handler:
        return handler(parsed_args, tui)
    else:
        parser.print_help()
        return 1


if __name__ == "__main__":
    sys.exit(main())
