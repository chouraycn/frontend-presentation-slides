#!/usr/bin/env python3
"""
测试运行脚本 — 执行所有单元测试、回归测试和代码审查

用法：
  python run_tests.py                    # 运行所有测试
  python run_tests.py --unit            # 仅单元测试
  python run_tests.py --regression FILE # 回归测试
  python run_tests.py --review FILE     # 代码审查
"""

import sys
import argparse
import subprocess
from pathlib import Path

# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent
TESTS_DIR = Path(__file__).parent
SCRIPTS_DIR = PROJECT_ROOT / 'scripts'


def run_unit_tests() -> bool:
    """运行单元测试"""
    print("\n" + "=" * 70)
    print("🧪 运行单元测试")
    print("=" * 70)

    result = subprocess.run(
        [sys.executable, '-m', 'pytest', str(TESTS_DIR / 'test_normalise_pptx.py'), '-v'],
        cwd=PROJECT_ROOT
    )

    return result.returncode == 0


def run_regression_test(pptx_file: str = None) -> bool:
    """运行回归测试"""
    print("\n" + "=" * 70)
    print("🔄 运行回归测试")
    print("=" * 70)

    if not pptx_file:
        print("❌ 错误: 需要指定 PPTX 文件")
        print("用法: python run_tests.py --regression <pptx_file>")
        return False

    # 生成报告路径
    pptx_path = Path(pptx_file)
    json_report = pptx_path.with_suffix('.integrity.json')
    html_report = pptx_path.with_suffix('.integrity.html')

    result = subprocess.run(
        [sys.executable, str(TESTS_DIR / 'regression_test_pptx.py'),
         pptx_file, '--json', str(json_report), '--html', str(html_report)],
        cwd=PROJECT_ROOT
    )

    return result.returncode == 0


def run_code_review(filepath: str = None) -> bool:
    """运行代码审查"""
    print("\n" + "=" * 70)
    print("👀 运行代码审查")
    print("=" * 70)

    if filepath:
        result = subprocess.run(
            [sys.executable, str(TESTS_DIR / 'code_review_checklist.py'),
             '--check', filepath, '--html', filepath.replace('.py', '.review.html')],
            cwd=PROJECT_ROOT
        )
    else:
        # 检查 generate_slides.py
        result = subprocess.run(
            [sys.executable, str(TESTS_DIR / 'code_review_checklist.py'),
             '--check', str(SCRIPTS_DIR / 'generate_slides.py'),
             '--html', str(PROJECT_ROOT / 'code_review_report.html')],
            cwd=PROJECT_ROOT
        )

    return result.returncode == 0


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='PPTX 转换代码完整性测试套件',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  # 运行所有测试
  python run_tests.py

  # 仅运行单元测试
  python run_tests.py --unit

  # 回归测试
  python run_tests.py --regression /path/to/file.pptx

  # 代码审查
  python run_tests.py --review

  # 代码审查特定文件
  python run_tests.py --review scripts/generate_slides.py
        '''
    )

    parser.add_argument('--unit', action='store_true', help='运行单元测试')
    parser.add_argument('--regression', metavar='FILE', help='运行回归测试（指定 PPTX 文件）')
    parser.add_argument('--review', nargs='?', const='generate_slides.py', metavar='FILE', help='运行代码审查')

    args = parser.parse_args()

    results = {
        'unit': None,
        'regression': None,
        'review': None,
    }

    # 确定要运行的测试
    if args.unit:
        results['unit'] = run_unit_tests()
    elif args.regression:
        results['regression'] = run_regression_test(args.regression)
    elif args.review is not None:
        filepath = args.review
        if not filepath.startswith('/'):
            filepath = str(SCRIPTS_DIR / filepath)
        results['review'] = run_code_review(filepath)
    else:
        # 默认：运行所有测试
        print("🚀 运行完整测试套件...\n")

        results['unit'] = run_unit_tests()
        results['review'] = run_code_review()

    # 输出总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70)

    passed_count = sum(1 for v in results.values() if v is True)
    total_count = sum(1 for v in results.values() if v is not None)

    if results['unit'] is not None:
        status = '✅ PASS' if results['unit'] else '❌ FAIL'
        print(f"单元测试: {status}")

    if results['regression'] is not None:
        status = '✅ PASS' if results['regression'] else '❌ FAIL'
        print(f"回归测试: {status}")

    if results['review'] is not None:
        status = '✅ PASS' if results['review'] else '❌ FAIL'
        print(f"代码审查: {status}")

    print(f"\n总体: {passed_count}/{total_count} 通过")

    if passed_count == total_count:
        print("\n✅ 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n❌ {total_count - passed_count} 个测试失败")
        sys.exit(1)


if __name__ == '__main__':
    main()
