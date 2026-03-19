"""
集成回归测试：对真实 PPTX 文件进行完整性检查

作用：
1. 验证真实 PPTX 文件转换后的内容完整性
2. 检测内容丢失、截断等问题
3. 对比提取前后的内容量
4. 生成详细的完整性报告

运行方法：
  python tests/regression_test_pptx.py <pptx_file> [--verbose] [--html]
  
示例：
  # 基本检查
  python tests/regression_test_pptx.py /path/to/file.pptx
  
  # 详细输出 + HTML 报告
  python tests/regression_test_pptx.py /path/to/file.pptx --verbose --html
"""

import sys
import json
import argparse
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from extract_pptx import extract_pptx
from generate_slides import _normalise_pptx


class PPTXIntegrityChecker:
    """PPTX 内容完整性检查器"""

    def __init__(self, pptx_file: str, verbose: bool = False):
        self.pptx_file = Path(pptx_file)
        self.verbose = verbose
        self.results = {
            'file': str(self.pptx_file),
            'timestamp': datetime.now().isoformat(),
            'passed': True,
            'issues': [],
            'metrics': {},
            'slides': [],
        }

    def run_checks(self) -> dict:
        """运行所有完整性检查"""
        print(f"🔍 检查 PPTX 文件: {self.pptx_file}")
        print(f"{'=' * 60}\n")

        # Step 1: 提取 PPTX
        print("📥 Step 1: 提取 PPTX 内容...")
        extracted = self._extract_pptx()
        if extracted is None:
            return self.results

        # Step 2: 规范化转换
        print("🔄 Step 2: 规范化 → outline 格式...")
        normalized = self._normalize_pptx(extracted)

        # Step 3: 完整性检查
        print("✓ Step 3: 检查完整性...")
        self._check_completeness(extracted, normalized)

        # Step 4: 生成报告
        print("📊 Step 4: 生成报告...\n")
        self._generate_report(extracted, normalized)

        return self.results

    def _extract_pptx(self) -> list:
        """提取 PPTX，返回 slides 列表"""
        try:
            # 创建临时输出目录
            import tempfile
            temp_dir = tempfile.mkdtemp(prefix='pptx_test_')
            
            # 调用 extract_pptx，返回的是 slides 列表
            slides = extract_pptx(str(self.pptx_file), temp_dir)
            
            if not slides:
                self._add_issue('ERROR', '无法提取 PPTX 文件')
                return None

            slides_count = len(slides)
            print(f"  ✓ 成功提取 {slides_count} 个 slide")
            
            self.results['metrics']['input_slides'] = slides_count
            return slides

        except Exception as e:
            self._add_issue('ERROR', f'提取失败: {str(e)}')
            return None

    def _normalize_pptx(self, slides: list) -> list:
        """规范化转换"""
        try:
            # slides 已经是列表，直接传给 _normalise_pptx
            normalized = _normalise_pptx(slides)
            
            print(f"  ✓ 转换 {len(normalized)} 个 outline entry")
            
            self.results['metrics']['output_slides'] = len(normalized)
            return normalized

        except Exception as e:
            self._add_issue('ERROR', f'规范化失败: {str(e)}')
            return []

    def _check_completeness(self, slides: list, normalized: list):
        """完整性检查"""
        
        # 检查 1: 同数量
        input_count = len(slides)
        output_count = len(normalized)
        
        if input_count != output_count:
            self._add_issue('ERROR', 
                f'Slide 数量不匹配: 输入 {input_count}, 输出 {output_count} '
                f'(丢失 {input_count - output_count} 个!)')
            return

        print(f"  ✓ Slide 数量匹配: {input_count} = {output_count}")

        # 检查 2: 内容完整性
        for i, (raw, out) in enumerate(zip(slides, normalized)):
            slide_result = {
                'index': i + 1,
                'issues': [],
            }

            # 检查文本内容
            self._check_text_content(raw, out, slide_result)

            # 检查表格
            self._check_table_content(raw, out, slide_result)

            # 检查图像
            self._check_image_content(raw, out, slide_result)

            # 检查 SmartArt
            self._check_smartart_content(raw, out, slide_result)

            if slide_result['issues']:
                self.results['issues'].append(slide_result)
                self.results['passed'] = False

            self.results['slides'].append(slide_result)

    def _check_text_content(self, raw: dict, out: dict, slide_result: dict):
        """检查文本内容完整性"""
        # 获取原始 body_paragraphs 的数量
        raw_texts = raw.get('body_paragraphs', [])
        raw_count = len([
            p['text'] if isinstance(p, dict) else str(p)
            for p in raw_texts
            if (p.get('text') if isinstance(p, dict) else str(p)).strip()
        ])

        # 根据输出类型获取文本内容数量
        out_count = 0
        out_type = out.get('type')
        
        if out_type == 'bullets':
            # bullets 类型使用 items 列表
            out_items = out.get('items', [])
            out_count = len([item for item in out_items if str(item).strip()])
        elif out_type == 'text':
            # text 类型使用 body 字符串
            body = out.get('body', '')
            out_count = 1 if body.strip() else 0
        elif out_type in ('table', 'image'):
            # IMPROVED: table/image 类型可能使用 caption
            # caption 现在包含所有内容，用换行符分隔
            caption = out.get('caption', '')
            if caption.strip():
                # Count lines in caption (each line is a preserved item)
                caption_lines = [l.strip() for l in caption.split('\n') if l.strip()]
                out_count = len(caption_lines)
            else:
                out_count = 0
        else:
            # 其他类型检查 body 或 items
            body = out.get('body', '')
            items = out.get('items', [])
            out_count = len([item for item in items if str(item).strip()]) if items else (1 if body.strip() else 0)

        # 检查是否有内容丢失
        if raw_count > 0 and out_count == 0:
            slide_result['issues'].append({
                'type': 'ERROR',
                'severity': 'CRITICAL',
                'message': f'文本丢失: 输入 {raw_count} 项，输出 0 项 (100% 丢失!)',
            })
        elif raw_count > out_count and out_count > 0:
            loss_pct = (raw_count - out_count) / raw_count * 100
            slide_result['issues'].append({
                'type': 'WARNING',
                'severity': 'HIGH',
                'message': f'文本部分丢失: 输入 {raw_count} 项，输出 {out_count} 项 ({loss_pct:.1f}% 丢失)',
            })

    def _check_table_content(self, raw: dict, out: dict, slide_result: dict):
        """检查表格完整性"""
        raw_tables = raw.get('tables', [])
        
        if not raw_tables:
            return

        # 检查表格是否被保留
        if out.get('type') != 'table':
            slide_result['issues'].append({
                'type': 'WARNING',
                'severity': 'MEDIUM',
                'message': f'表格类型未保留: 输入类型 table，输出类型 {out.get("type")}',
            })
            return

        # 检查表头
        raw_headers = raw_tables[0].get('headers', [])
        out_headers = out.get('headers', [])
        
        if len(raw_headers) != len(out_headers):
            slide_result['issues'].append({
                'type': 'ERROR',
                'severity': 'HIGH',
                'message': f'表头丢失: 输入 {len(raw_headers)} 列，输出 {len(out_headers)} 列',
            })

        # 检查行数
        raw_rows = raw_tables[0].get('rows', [])
        out_rows = out.get('rows', [])
        
        if len(raw_rows) != len(out_rows):
            slide_result['issues'].append({
                'type': 'ERROR',
                'severity': 'HIGH',
                'message': f'表行丢失: 输入 {len(raw_rows)} 行，输出 {len(out_rows)} 行',
            })

        # 检查 caption（表格下的说明文本）
        caption = out.get('caption', '')
        if caption:
            # 验证 caption 不被截断到 200 字
            if len(caption) > 200:
                # 这是正常的（修复后）
                pass
            else:
                # 检查是否有被截断的迹象
                raw_body = raw.get('body_paragraphs', [])
                raw_text_len = sum(
                    len(p['text'] if isinstance(p, dict) else str(p))
                    for p in raw_body
                )
                if raw_text_len > len(caption):
                    slide_result['issues'].append({
                        'type': 'WARNING',
                        'severity': 'MEDIUM',
                        'message': f'Caption 可能被截断: 输入 {raw_text_len} 字，输出 {len(caption)} 字',
                    })

    def _check_image_content(self, raw: dict, out: dict, slide_result: dict):
        """检查图像完整性"""
        raw_images = raw.get('images', [])
        out_image = out.get('image')

        if raw_images and not out_image:
            slide_result['issues'].append({
                'type': 'WARNING',
                'severity': 'MEDIUM',
                'message': '图像丢失: 输入有图像，输出无图像',
            })

    def _check_smartart_content(self, raw: dict, out: dict, slide_result: dict):
        """检查 SmartArt 完整性"""
        raw_smartart = raw.get('smartart', [])
        raw_count = len([s for s in raw_smartart if str(s).strip()])

        if not raw_count:
            return

        # 检查 SmartArt 是否被保留
        caption = out.get('caption', '')
        items = out.get('items', [])

        found_count = 0
        for smartart_item in raw_smartart:
            item_str = str(smartart_item).strip()
            if item_str and (item_str in caption or item_str in items):
                found_count += 1

        if found_count < raw_count:
            loss_pct = (raw_count - found_count) / raw_count * 100
            slide_result['issues'].append({
                'type': 'WARNING',
                'severity': 'MEDIUM',
                'message': f'SmartArt 部分丢失: 输入 {raw_count} 项，输出 {found_count} 项 ({loss_pct:.1f}% 丢失)',
            })

    def _add_issue(self, issue_type: str, message: str):
        """添加问题记录"""
        self.results['issues'].append({
            'type': issue_type,
            'message': message,
        })
        if issue_type == 'ERROR':
            self.results['passed'] = False

    def _generate_report(self, slides: list, normalized: list):
        """生成检查报告"""
        
        # 汇总统计
        total_issues = len(self.results['issues'])
        
        print(f"📋 完整性检查报告")
        print(f"{'=' * 60}")
        print(f"文件: {self.pptx_file.name}")
        print(f"检查时间: {self.results['timestamp']}")
        print(f"结果: {'✅ PASS' if self.results['passed'] else '❌ FAIL'}")
        print(f"\n📊 指标:")
        print(f"  - 输入 slides: {self.results['metrics'].get('input_slides', 0)}")
        print(f"  - 输出 slides: {self.results['metrics'].get('output_slides', 0)}")
        print(f"  - 检测到的问题: {total_issues}")

        if self.results['issues']:
            print(f"\n⚠️  问题详情:")
            for i, issue in enumerate(self.results['issues'][:20], 1):  # 显示前 20 个
                if 'index' in issue:
                    print(f"\n  Slide {issue['index']}:")
                    for problem in issue['issues']:
                        severity = problem.get('severity', 'UNKNOWN')
                        icon = '🔴' if severity == 'CRITICAL' else '🟡' if severity == 'HIGH' else '🔵'
                        print(f"    {icon} [{problem['type']}] {problem['message']}")
                else:
                    print(f"  🔴 {issue['type']}: {issue['message']}")

            if len(self.results['issues']) > 20:
                print(f"\n  ... 还有 {len(self.results['issues']) - 20} 个问题")

        print(f"\n{'=' * 60}\n")

    def save_json_report(self, output_path: str = None) -> str:
        """保存 JSON 报告"""
        if not output_path:
            output_path = self.pptx_file.with_suffix('.integrity.json')

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.results, f, ensure_ascii=False, indent=2)

        print(f"📄 JSON 报告已保存: {output_path}")
        return str(output_path)

    def save_html_report(self, output_path: str = None) -> str:
        """保存 HTML 报告"""
        if not output_path:
            output_path = self.pptx_file.with_suffix('.integrity.html')

        html = self._generate_html_report()

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html)

        print(f"🌐 HTML 报告已保存: {output_path}")
        return str(output_path)

    def _generate_html_report(self) -> str:
        """生成 HTML 报告"""
        passed_class = 'passed' if self.results['passed'] else 'failed'
        passed_text = '✅ PASS' if self.results['passed'] else '❌ FAIL'

        html = f"""
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>PPTX 完整性检查报告</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
            background: #f5f7fa;
            padding: 20px;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            border-radius: 8px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
        }}
        .header h1 {{
            font-size: 24px;
            margin-bottom: 10px;
        }}
        .status {{
            display: inline-block;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            font-size: 14px;
            margin-top: 10px;
        }}
        .status.passed {{
            background: rgba(76, 175, 80, 0.2);
            color: #4caf50;
        }}
        .status.failed {{
            background: rgba(244, 67, 54, 0.2);
            color: #f44336;
        }}
        .content {{
            padding: 30px;
        }}
        .section {{
            margin-bottom: 30px;
        }}
        .section h2 {{
            font-size: 18px;
            margin-bottom: 15px;
            color: #333;
            border-bottom: 2px solid #667eea;
            padding-bottom: 10px;
        }}
        .metrics {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin-bottom: 20px;
        }}
        .metric {{
            padding: 15px;
            background: #f9f9f9;
            border-left: 4px solid #667eea;
            border-radius: 4px;
        }}
        .metric-label {{
            font-size: 12px;
            color: #666;
            text-transform: uppercase;
            margin-bottom: 8px;
        }}
        .metric-value {{
            font-size: 24px;
            font-weight: bold;
            color: #333;
        }}
        .issues {{
            list-style: none;
        }}
        .issue {{
            padding: 15px;
            margin-bottom: 10px;
            border-left: 4px solid #f44336;
            background: #fff5f5;
            border-radius: 4px;
        }}
        .issue.warning {{
            border-left-color: #ff9800;
            background: #fff8f3;
        }}
        .issue.info {{
            border-left-color: #2196f3;
            background: #f3f9ff;
        }}
        .issue-type {{
            font-weight: bold;
            color: #666;
            font-size: 12px;
            text-transform: uppercase;
            margin-bottom: 5px;
        }}
        .issue-message {{
            color: #333;
        }}
        .slide-issues {{
            margin-bottom: 20px;
            padding: 15px;
            background: #f9f9f9;
            border-radius: 4px;
        }}
        .slide-title {{
            font-weight: bold;
            color: #667eea;
            margin-bottom: 10px;
        }}
        .footer {{
            background: #f5f7fa;
            padding: 20px 30px;
            font-size: 12px;
            color: #999;
            border-top: 1px solid #eee;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔍 PPTX 完整性检查报告</h1>
            <div class="status {passed_class}">
                {passed_text}
            </div>
        </div>

        <div class="content">
            <!-- 文件信息 -->
            <div class="section">
                <h2>📄 文件信息</h2>
                <div class="metric">
                    <div class="metric-label">文件路径</div>
                    <div class="metric-value" style="font-size: 14px; word-break: break-all;">{self.results['file']}</div>
                </div>
                <div class="metric" style="margin-top: 10px;">
                    <div class="metric-label">检查时间</div>
                    <div class="metric-value" style="font-size: 14px;">{self.results['timestamp']}</div>
                </div>
            </div>

            <!-- 检查指标 -->
            <div class="section">
                <h2>📊 检查指标</h2>
                <div class="metrics">
                    <div class="metric">
                        <div class="metric-label">输入 Slides</div>
                        <div class="metric-value">{self.results['metrics'].get('input_slides', 0)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">输出 Slides</div>
                        <div class="metric-value">{self.results['metrics'].get('output_slides', 0)}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">检测到的问题</div>
                        <div class="metric-value">{len(self.results['issues'])}</div>
                    </div>
                </div>
            </div>

            <!-- 问题详情 -->
            <div class="section">
                <h2>⚠️  问题详情</h2>
                {self._generate_issues_html()}
            </div>
        </div>

        <div class="footer">
            <p>报告由 PPTX 完整性检查工具生成</p>
        </div>
    </div>
</body>
</html>
"""
        return html

    def _generate_issues_html(self) -> str:
        """生成问题 HTML"""
        if not self.results['issues']:
            return '<p style="color: #4caf50; font-weight: bold;">✅ 未检测到任何问题！</p>'

        html = '<ul class="issues">'
        for issue in self.results['issues'][:30]:
            if 'index' in issue:
                html += f'<li><div class="slide-issues"><div class="slide-title">Slide {issue["index"]}</div>'
                for problem in issue['issues']:
                    severity_class = 'warning' if problem.get('severity') in ['HIGH', 'MEDIUM'] else 'info'
                    html += f'''<div class="issue {severity_class}">
                        <div class="issue-type">{problem['type']}</div>
                        <div class="issue-message">{problem['message']}</div>
                    </div>'''
                html += '</div></li>'
            else:
                html += f'''<li class="issue warning">
                    <div class="issue-type">{issue['type']}</div>
                    <div class="issue-message">{issue['message']}</div>
                </li>'''
        html += '</ul>'
        return html


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='PPTX 内容完整性检查工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例：
  # 基本检查
  python regression_test_pptx.py file.pptx

  # 详细输出 + HTML 报告
  python regression_test_pptx.py file.pptx --verbose --html

  # 保存到自定义路径
  python regression_test_pptx.py file.pptx --json report.json --html report.html
        '''
    )

    parser.add_argument('pptx_file', help='PPTX 文件路径')
    parser.add_argument('-v', '--verbose', action='store_true', help='详细输出')
    parser.add_argument('--json', help='JSON 报告输出路径')
    parser.add_argument('--html', action='store_true', help='生成 HTML 报告')
    parser.add_argument('--html-path', help='HTML 报告输出路径')

    args = parser.parse_args()

    # 验证文件存在
    if not Path(args.pptx_file).exists():
        print(f"❌ 错误: 文件不存在 - {args.pptx_file}")
        sys.exit(1)

    # 创建检查器并运行
    checker = PPTXIntegrityChecker(args.pptx_file, verbose=args.verbose)
    results = checker.run_checks()

    # 保存报告
    if args.json:
        checker.save_json_report(args.json)

    if args.html:
        checker.save_html_report(args.html_path)

    # 返回状态码
    sys.exit(0 if results['passed'] else 1)


if __name__ == '__main__':
    main()
