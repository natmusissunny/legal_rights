#!/usr/bin/env python3
"""
开源发布准备脚本
自动清理隐私信息、临时文件，准备开源发布
"""
import os
import re
import shutil
from pathlib import Path
from typing import List, Tuple


class OpensourcePreparer:
    """开源准备工具"""

    # 需要删除的临时文件
    TEMP_FILES = [
        "HOTFIX_v1.0.1.md",
        "URGENT_FIX_v1.0.2.md",
        "DOWNLOAD_SUCCESS.md",
        "NEXT_STEPS.md",
        "PROJECT_COMPLETION.md",
        "OPENSOURCE_PREPARE.md",
    ]

    # 需要清理路径的文件扩展名
    CLEAN_EXTENSIONS = [".py", ".md", ".txt", ".sh"]

    # 隐私路径模式
    PRIVACY_PATTERNS = [
        # cd 命令特殊处理
        (r'cd /Users/nat\.mei/data/Claude-Project/legal_rights', 'cd legal_rights'),
        (r'cd /Users/nat\.mei/data/Claude-Project', 'cd /path/to/workspace'),
        # 普通路径
        (r'/Users/nat\.mei/data/Claude-Project/legal_rights', './legal_rights'),
        (r'/Users/nat\.mei/data/Claude-Project', '/path/to/workspace'),
        (r'/Users/nat\.mei', '~'),
    ]

    def __init__(self, project_root: Path, dry_run: bool = True):
        """
        初始化

        Args:
            project_root: 项目根目录
            dry_run: 是否为预演模式（不实际修改文件）
        """
        self.project_root = project_root
        self.dry_run = dry_run
        self.changes: List[str] = []

    def clean_temp_files(self):
        """删除临时文件"""
        print("\n" + "="*80)
        print("🗑️  清理临时文件")
        print("="*80)

        for filename in self.TEMP_FILES:
            filepath = self.project_root / filename
            if filepath.exists():
                if self.dry_run:
                    print(f"[预演] 将删除: {filename}")
                    self.changes.append(f"删除文件: {filename}")
                else:
                    filepath.unlink()
                    print(f"✅ 已删除: {filename}")
                    self.changes.append(f"删除文件: {filename}")
            else:
                print(f"⏭️  跳过（不存在）: {filename}")

    def clean_pycache(self):
        """清理Python缓存"""
        print("\n" + "="*80)
        print("🧹 清理Python缓存")
        print("="*80)

        # 删除 __pycache__ 目录
        pycache_dirs = list(self.project_root.rglob("__pycache__"))
        for pycache_dir in pycache_dirs:
            if self.dry_run:
                print(f"[预演] 将删除: {pycache_dir.relative_to(self.project_root)}")
                self.changes.append(f"删除目录: {pycache_dir.relative_to(self.project_root)}")
            else:
                shutil.rmtree(pycache_dir)
                print(f"✅ 已删除: {pycache_dir.relative_to(self.project_root)}")
                self.changes.append(f"删除目录: {pycache_dir.relative_to(self.project_root)}")

        # 删除 .pyc 文件
        pyc_files = list(self.project_root.rglob("*.pyc"))
        for pyc_file in pyc_files:
            if self.dry_run:
                print(f"[预演] 将删除: {pyc_file.relative_to(self.project_root)}")
            else:
                pyc_file.unlink()
                print(f"✅ 已删除: {pyc_file.relative_to(self.project_root)}")

    def find_privacy_paths(self) -> List[Tuple[Path, List[int]]]:
        """
        查找包含隐私路径的文件

        Returns:
            [(文件路径, [行号列表]), ...]
        """
        print("\n" + "="*80)
        print("🔍 扫描隐私路径")
        print("="*80)

        results = []

        # 搜索所有需要清理的文件
        for ext in self.CLEAN_EXTENSIONS:
            for filepath in self.project_root.rglob(f"*{ext}"):
                # 跳过 data/ 目录
                if "data/" in str(filepath):
                    continue

                try:
                    content = filepath.read_text(encoding='utf-8')

                    # 检查是否包含隐私路径
                    found_lines = []
                    for line_num, line in enumerate(content.split('\n'), 1):
                        for pattern, _ in self.PRIVACY_PATTERNS:
                            if re.search(pattern, line):
                                found_lines.append(line_num)
                                break

                    if found_lines:
                        results.append((filepath, found_lines))
                        rel_path = filepath.relative_to(self.project_root)
                        print(f"⚠️  {rel_path}: {len(found_lines)} 处")

                except Exception as e:
                    print(f"❌ 读取失败 {filepath}: {e}")

        print(f"\n📊 共发现 {len(results)} 个文件包含隐私路径")
        return results

    def clean_privacy_paths(self, files: List[Tuple[Path, List[int]]]):
        """
        清理隐私路径

        Args:
            files: 包含隐私路径的文件列表
        """
        print("\n" + "="*80)
        print("🔒 清理隐私路径")
        print("="*80)

        for filepath, line_numbers in files:
            try:
                content = filepath.read_text(encoding='utf-8')
                original_content = content

                # 应用所有替换规则
                for pattern, replacement in self.PRIVACY_PATTERNS:
                    content = re.sub(pattern, replacement, content)

                # 检查是否有修改
                if content != original_content:
                    rel_path = filepath.relative_to(self.project_root)

                    if self.dry_run:
                        print(f"[预演] 将修改: {rel_path}")
                        self.changes.append(f"修改文件: {rel_path}")
                    else:
                        filepath.write_text(content, encoding='utf-8')
                        print(f"✅ 已修改: {rel_path}")
                        self.changes.append(f"修改文件: {rel_path}")

            except Exception as e:
                print(f"❌ 处理失败 {filepath}: {e}")

    def check_sensitive_info(self):
        """检查敏感信息（API密钥等）"""
        print("\n" + "="*80)
        print("🔐 检查敏感信息")
        print("="*80)

        sensitive_patterns = [
            (r'sk-ant-api03-[a-zA-Z0-9_-]+', 'Claude API密钥'),
            (r'sk-[a-zA-Z0-9]{48,}', 'OpenAI API密钥'),
            (r'Bearer [a-zA-Z0-9_-]+', 'Bearer Token'),
            (r'password\s*=\s*["\'][^"\']+["\']', '密码'),
        ]

        found_sensitive = []

        for ext in self.CLEAN_EXTENSIONS:
            for filepath in self.project_root.rglob(f"*{ext}"):
                # 跳过 .env.example
                if filepath.name == ".env.example":
                    continue

                # 跳过 data/ 目录
                if "data/" in str(filepath):
                    continue

                try:
                    content = filepath.read_text(encoding='utf-8')

                    for pattern, desc in sensitive_patterns:
                        if re.search(pattern, content, re.IGNORECASE):
                            rel_path = filepath.relative_to(self.project_root)
                            found_sensitive.append((rel_path, desc))
                            print(f"⚠️  {rel_path}: 可能包含 {desc}")

                except Exception:
                    pass

        if not found_sensitive:
            print("✅ 未发现敏感信息")
        else:
            print(f"\n⚠️  发现 {len(found_sensitive)} 处可能的敏感信息")
            print("请手动检查并确认")

        return found_sensitive

    def generate_summary(self):
        """生成清理摘要"""
        print("\n" + "="*80)
        print("📊 清理摘要")
        print("="*80)

        if self.dry_run:
            print("\n⚠️  这是预演模式，未实际修改文件")
            print("运行 python scripts/prepare_opensource.py --execute 执行实际清理")
        else:
            print("\n✅ 清理完成！")

        print(f"\n共执行 {len(self.changes)} 项操作：")
        for i, change in enumerate(self.changes, 1):
            print(f"  {i}. {change}")

        print("\n" + "="*80)
        print("📝 下一步操作")
        print("="*80)
        print("""
1. 手动检查修改结果：
   git diff

2. 创建标准文档：
   - README.md (重写)
   - LICENSE (选择MIT)
   - CONTRIBUTING.md
   - CHANGELOG.md

3. 测试功能：
   python -m pytest tests/

4. 提交到Git：
   git add .
   git commit -m "Prepare for open source release"

5. 创建GitHub仓库并推送
        """)


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(
        description="准备开源发布",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 预演模式（不实际修改）
  python scripts/prepare_opensource.py

  # 执行清理
  python scripts/prepare_opensource.py --execute

  # 仅扫描隐私路径
  python scripts/prepare_opensource.py --scan-only
        """
    )

    parser.add_argument('--execute', action='store_true',
                       help='执行实际清理（默认为预演模式）')
    parser.add_argument('--scan-only', action='store_true',
                       help='仅扫描，不执行清理')

    args = parser.parse_args()

    # 确定项目根目录
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    print("="*80)
    print("🚀 开源发布准备工具")
    print("="*80)
    print(f"\n项目根目录: {project_root}")
    print(f"模式: {'执行' if args.execute else '预演'}")

    # 创建清理器
    preparer = OpensourcePreparer(project_root, dry_run=not args.execute)

    # 扫描隐私路径
    privacy_files = preparer.find_privacy_paths()

    if args.scan_only:
        print("\n✅ 扫描完成")
        return

    # 清理临时文件
    preparer.clean_temp_files()

    # 清理Python缓存
    preparer.clean_pycache()

    # 清理隐私路径
    if privacy_files:
        preparer.clean_privacy_paths(privacy_files)

    # 检查敏感信息
    preparer.check_sensitive_info()

    # 生成摘要
    preparer.generate_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ 用户取消")
    except Exception as e:
        print(f"\n\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
