"""
代码审查检查清单

用于后续修改时，检查是否引入字符截断、内容丢失等问题

运行方法：
  python tests/code_review_checklist.py
  python tests/code_review_checklist.py --check scripts/generate_slides.py
  python tests/code_review_checklist.py --monitor  # 持续监控改动
"""

import sys
import re
import argparse
from pathlib import Path
from typing import List, Tuple

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))


class CodeReviewChecklist:
    """代码审查检查清单"""

    # 要检查的关键模式
    DANGEROUS_PATTERNS = [
        {
            'pattern': r'\[:(\d+)\](?!\.)(?!\+)',
            'description': '字符串截断操作 [:N]',
            'reason': '可能导致内容丢失（如 caption[:200]）',
            'fix': '应无条件保留完整内容',
            'severity': 'CRITICAL',
            'examples': ['text[:200]', 'content[:100]'],
        },
        {
            'pattern': r'all_items\[0\]',
            'description': '只取列表首项',
            'reason': '导致其他项全部丢失',
            'fix': '应处理所有项目',
            'severity': 'CRITICAL',
            'examples': ['all_items[0]'],
        },
        {
            'pattern': r'all_items\[\s*:\s*\d+\s*\]',
            'description': '列表切片限制',
            'reason': '可能截断内容',
            'fix': '根据业务逻辑判断是否真需要切片',
            'severity': 'HIGH',
            'examples': ['all_items[:5]', 'items[:10]'],
        },
        {
            'pattern': r"\.join\([^)]*\)\[:\d+\]",
            'description': 'join 后立即截断',
            'reason': '结合字符串和截断，极易丢失内容',
            'fix': '移除截断，或在 join 前处理',
            'severity': 'CRITICAL',
            'examples': ["' '.join(items)[:200]"],
        },
        {
            'pattern': r'caption_parts\s*=\s*\[[^\]]*\]\[:\d+\]',
            'description': 'caption_parts 列表被截断',
            'reason': '截断前的内容会全部丢失',
            'fix': '应完整保留所有 caption_parts',
            'severity': 'CRITICAL',
            'examples': ['caption_parts[:1]', 'parts[:5]'],
        },
        {
            'pattern': r'if\s+body_texts\s*:\s*entry\[\s*["\']caption["\']\s*\]\s*=\s*body_texts\[0\]',
            'description': 'body_texts 只取第一项',
            'reason': '其他 body_text 会丢失',
            'fix': '应包含所有 body_text',
            'severity': 'HIGH',
            'examples': ['entry["caption"] = body_texts[0]'],
        },
        {
            'pattern': r'smartart_texts?\s*=\s*\[\]|smartart\s*=\s*None',
            'description': '忽略或清空 SmartArt',
            'reason': 'SmartArt 内容会丢失',
            'fix': '应保留 SmartArt 内容',
            'severity': 'MEDIUM',
            'examples': ['smartart_texts = []'],
        },
        {
            'pattern': r'entry\[[\'\"]items[\'\"\]\s*=\s*\[\]',
            'description': '清空 items 列表',
            'reason': '所有列表项会丢失',
            'fix': '应赋予有效的 items',
            'severity': 'CRITICAL',
            'examples': ['entry["items"] = []'],
        },
        {
            'pattern': r'continue(?!\s*#)',
            'description': 'continue 语句跳过 slide 处理',
            'reason': 'Slide 会被跳过/丢失',
            'fix': '应处理每个 slide，必要时只跳过内容',
            'severity': 'HIGH',
            'examples': ['if condition: continue'],
        },
        {
            'pattern': r'break(?!\s*#)',
            'description': 'break 语句提前退出循环',
            'reason': '后续 slides 会被遗漏',
            'fix': '避免在 slide 循环中使用 break',
            'severity': 'HIGH',
            'examples': ['if condition: break'],
        },
        {
            'pattern': r'return\s+\[\](?!\s*#)',
            'description': '返回空列表',
            'reason': '所有 slides 数据会丢失',
            'fix': '应返回完整的处理结果',
            'severity': 'CRITICAL',
            'examples': ['return []'],
        },
        {
            'pattern': r"\.get\(['\"]items['\"]\s*,\s*\[\]\s*\)\[:(\d+)\]",
            'description': '获取 items 后立即切片',
            'reason': '截断内容',
            'fix': '移除切片操作',
            'severity': 'HIGH',
            'examples': ['entry.get("items", [])[:5]'],
        },
    ]

    # 正确模式（应该存在）
    REQUIRED_PATTERNS = [
        {
            'pattern': r'all_items\s*=\s*body_texts\s*\+\s*table_lines\s*\+\s*smartart_texts',
            'description': '合并所有内容来源',
            'reason': '确保各类型内容都被考虑',
        },
        {
            'pattern': r"entry\[[\'\"]items[\'\"\]\s*=\s*all_items",
            'description': '完整保留 all_items',
            'reason': '确保所有内容都被输出',
        },
        {
            'pattern': r'caption_parts\.extend\(body_texts\)',
            'description': '扩展 caption_parts',
            'reason': '确保 body_texts 被包含',
        },
        {
            'pattern': r'caption_parts\.extend\(smartart_texts\)',
            'description': '扩展 SmartArt 内容',
            'reason': '确保 SmartArt 被包含',
        },
        {
            'pattern': r"[\'\"]\\n[\'\"]\.join\(",
            'description': '使用换行符连接',
            'reason': '提高可读性，避免空格拼接导致的歧义',
        },
    ]

    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.results = {
            'issues': [],
            'warnings': [],
            'suggestions': [],
            'passed': True,
        }

    def check_file(self, filepath: str) -> dict:
        """检查单个文件"""
        print(f"\n🔍 检查文件: {filepath}")
        print(f"{'=' * 70}")

        path = Path(filepath)
        if not path.exists():
            print(f"❌ 文件不存在: {filepath}")
            return {'passed': False, 'issues': ['文件不存在']}

        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()

        results = {
            'passed': True,
            'file': filepath,
            'issues': [],
            'warnings': [],
            'suggestions': [],
        }

        # 检查危险模式
        print("\n🚨 检查危险模式...")
        for pattern_def in self.DANGEROUS_PATTERNS:
            pattern = pattern_def['pattern']
            severity = pattern_def['severity']
            
            matches = re.finditer(pattern, content)
            for match in matches:
                line_num = content[:match.start()].count('\n') + 1
                
                issue = {
                    'type': 'DANGEROUS_PATTERN',
                    'severity': severity,
                    'line': line_num,
                    'pattern': pattern_def['description'],
                    'reason': pattern_def['reason'],
                    'fix': pattern_def['fix'],
                    'matched': match.group(0),
                }

                results['issues'].append(issue)
                results['passed'] = False

                icon = '🔴' if severity == 'CRITICAL' else '🟡'
                print(f"  {icon} L{line_num}: {pattern_def['description']}")
                print(f"     匹配: {match.group(0)[:50]}")
                print(f"     原因: {pattern_def['reason']}")
                print(f"     建议: {pattern_def['fix']}\n")

        # 检查必需模式
        print("✅ 检查必需模式...")
        missing_patterns = []
        for pattern_def in self.REQUIRED_PATTERNS:
            pattern = pattern_def['pattern']
            if not re.search(pattern, content):
                missing_patterns.append(pattern_def)

        if missing_patterns:
            print(f"  ⚠️  缺少 {len(missing_patterns)} 个必需模式:")
            for p in missing_patterns:
                print(f"     - {p['description']}")
                print(f"       原因: {p['reason']}\n")
                results['warnings'].append({
                    'type': 'MISSING_PATTERN',
                    'pattern': p['description'],
                    'reason': p['reason'],
                })
        else:
            print(f"  ✓ 所有必需模式都存在")

        return results

    def generate_report(self):
        """生成审查报告"""
        print(f"\n\n📋 代码审查总结")
        print(f"{'=' * 70}")

        if self.results['passed']:
            print("✅ 审查通过！")
        else:
            print("❌ 发现问题！")

        print(f"\n统计:")
        print(f"  - 关键问题: {len([i for i in self.results['issues'] if i.get('severity') == 'CRITICAL'])}")
        print(f"  - 高风险: {len([i for i in self.results['issues'] if i.get('severity') == 'HIGH'])}")
        print(f"  - 警告: {len(self.results['warnings'])}")

    def save_html_report(self, output_path: str = None) -> str:
        """保存 HTML 报告"""
        if not output_path:
            output_path = 'code_review_report.html'

        html = self._generate_html()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"\n📄 HTML 报告已保存: {output_path}")
        return output_path

    def _generate_html(self) -> str:
        """生成 HTML 报告"""
        issues_html = ''
        if self.results['issues']:
            issues_html = '<ul class="issues">'
            for issue in self.results['issues']:
                severity_class = 'critical' if issue['severity'] == 'CRITICAL' else 'high' if issue['severity'] == 'HIGH' else 'medium'
                icon = '🔴' if issue['severity'] == 'CRITICAL' else '🟡' if issue['severity'] == 'HIGH' else '🔵'
                
                issues_html += f"""
                <li class="issue {severity_class}">
                    <div class="issue-header">
                        {icon} {issue['severity']} - {issue['pattern']}
                    </div>
                    <div class="issue-detail">
                        <p><strong>位置:</strong> 第 {issue['line']} 行</p>
                        <p><strong>匹配:</strong> <code>{issue['matched'][:100]}</code></p>
                        <p><strong>原因:</strong> {issue['reason']}</p>
                        <p><strong>建议:</strong> {issue['fix']}</p>
                    </div>
                </li>
                """
            issues_html += '</ul>'
        else:
            issues_html = '<p class="success">✅ 未检测到问题</p>'

        return f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <title>代码审查报告</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            max-width: 1000px;
            margin: 0 auto;
            padding: 20px;
            background: #f5f7fa;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 8px;
            margin-bottom: 20px;
        }}
        .header h1 {{
            margin: 0;
        }}
        .issues {{
            list-style: none;
            padding: 0;
        }}
        .issue {{
            background: white;
            margin-bottom: 15px;
            border-radius: 8px;
            overflow: hidden;
            border-left: 4px solid #f44336;
        }}
        .issue.high {{
            border-left-color: #ff9800;
        }}
        .issue.medium {{
            border-left-color: #2196f3;
        }}
        .issue-header {{
            padding: 15px;
            background: #f9f9f9;
            font-weight: bold;
        }}
        .issue-detail {{
            padding: 15px;
        }}
        .issue-detail p {{
            margin: 8px 0;
            font-size: 14px;
        }}
        code {{
            background: #f0f0f0;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
        }}
        .success {{
            background: #4caf50;
            color: white;
            padding: 20px;
            border-radius: 8px;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🔍 代码审查报告</h1>
        <p>PPTX 转 HTML 内容完整性代码审查</p>
    </div>
    {issues_html}
</body>
</html>
"""


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='代码审查检查清单 — 验证 PPTX 转换代码',
    )

    parser.add_argument('--check', help='检查指定文件')
    parser.add_argument('--verbose', '-v', action='store_true', help='详细输出')
    parser.add_argument('--html', help='生成 HTML 报告')

    args = parser.parse_args()

    checker = CodeReviewChecklist(verbose=args.verbose)

    # 如果指定了文件，检查该文件；否则显示检查清单
    if args.check:
        result = checker.check_file(args.check)
        checker.results = result
        checker.generate_report()
        
        if args.html:
            checker.save_html_report(args.html)
    else:
        # 显示检查清单
        print("📋 代码审查检查清单")
        print("=" * 70)
        print("\n🚨 危险模式 (应避免):\n")

        for i, pattern_def in enumerate(CodeReviewChecklist.DANGEROUS_PATTERNS, 1):
            severity_icon = '🔴' if pattern_def['severity'] == 'CRITICAL' else '🟡' if pattern_def['severity'] == 'HIGH' else '🔵'
            print(f"{i}. {severity_icon} {pattern_def['description']}")
            print(f"   原因: {pattern_def['reason']}")
            print(f"   建议: {pattern_def['fix']}")
            print(f"   例子: {', '.join(pattern_def['examples'])}\n")

        print("\n✅ 必需模式 (应包含):\n")
        for i, pattern_def in enumerate(CodeReviewChecklist.REQUIRED_PATTERNS, 1):
            print(f"{i}. {pattern_def['description']}")
            print(f"   原因: {pattern_def['reason']}\n")

        print("\n" + "=" * 70)
        print("用法:")
        print("  python code_review_checklist.py --check scripts/generate_slides.py")
        print("  python code_review_checklist.py --check scripts/generate_slides.py --html report.html")


if __name__ == '__main__':
    main()
