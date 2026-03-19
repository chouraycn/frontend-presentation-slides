"""
单元测试：_normalise_pptx() 函数数据完整性验证

作用：
1. 验证 _normalise_pptx() 不会丢失内容
2. 测试各种 PPTX 布局类型
3. 检查字符串截断问题
4. 确保 SmartArt 和表格内容完整保留

关键修复点（2025-03-19）：
- 移除 200 字截断限制（L2076 中的 [:200]）
- 保留所有 body_texts + smartart_texts
- 使用换行符而非空格分隔

运行方法：
  python -m pytest tests/test_normalise_pptx.py -v
"""

import sys
import json
import unittest
from pathlib import Path

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'scripts'))

from generate_slides import _normalise_pptx


class TestNormalisePptxDataIntegrity(unittest.TestCase):
    """验证 _normalise_pptx() 数据完整性的核心测试"""

    def test_no_content_loss_in_bullets(self):
        """
        关键测试：验证 bullets 类型的列表项完全保留
        
        场景：109 个列表项的幻灯片不应丢失任何项
        这是之前发生的 bug：只显示 1 个，其他 108 个丢失
        """
        raw_slides = [
            {
                'number': 1,
                'layout': 'content-list',
                'title': 'Test Bullets',
                'body_paragraphs': [
                    {'text': f'Item {i}'} 
                    for i in range(1, 110)  # 109 items
                ],
                'tables': [],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        
        self.assertEqual(len(result), 1, "应该返回 1 个 slide")
        self.assertEqual(result[0]['type'], 'bullets', "类型应为 bullets")
        
        items = result[0].get('items', [])
        self.assertEqual(len(items), 109, 
            f"应有 109 个列表项，实际 {len(items)} 个（丢失 {109 - len(items)} 个！）")
        
        # 验证首尾项目
        self.assertIn('Item 1', items[0], "首项缺失")
        self.assertIn('Item 109', items[-1], "末项缺失")


    def test_no_truncation_in_table_caption(self):
        """
        关键测试：验证表格 caption 不被截断
        
        场景：表格下有 200+ 字的说明文本
        修复前：只保留前 200 字（[:200] 截断）
        修复后：完整保留所有文本
        """
        caption_text = 'A' * 250  # 250 字超过原来的 200 字限制
        
        raw_slides = [
            {
                'number': 1,
                'layout': 'table',
                'title': 'Table with Caption',
                'body_paragraphs': [
                    {'text': caption_text}
                ],
                'tables': [
                    {
                        'headers': ['Col1', 'Col2'],
                        'rows': [['A', 'B'], ['C', 'D']]
                    }
                ],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['type'], 'table')
        
        caption = result[0].get('caption', '')
        self.assertEqual(len(caption), 250, 
            f"caption 应为 250 字，实际 {len(caption)} 字（被截断了 {250 - len(caption)} 字！）")
        self.assertEqual(caption, caption_text, 
            "caption 内容应完全保留，不应截断")


    def test_smartart_not_lost(self):
        """
        关键测试：SmartArt 内容不应丢失
        
        场景：表格 + SmartArt 内容
        修复前：SmartArt 不被包含在 caption 中
        修复后：SmartArt 完整包含
        """
        smartart_items = [f'SmartArt Item {i}' for i in range(1, 6)]
        body_text = 'Body text content'
        
        raw_slides = [
            {
                'number': 1,
                'layout': 'table',
                'title': 'Table with SmartArt',
                'body_paragraphs': [
                    {'text': body_text}
                ],
                'tables': [
                    {
                        'headers': ['A', 'B'],
                        'rows': [['1', '2']]
                    }
                ],
                'smartart': smartart_items,
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        
        self.assertEqual(len(result), 1)
        caption = result[0].get('caption', '')
        
        # 验证所有 SmartArt 项都在 caption 中
        for item in smartart_items:
            self.assertIn(item, caption, 
                f"SmartArt 项 '{item}' 应在 caption 中")
        
        # 验证 body_text 也在
        self.assertIn(body_text, caption,
            f"Body text '{body_text}' 应在 caption 中")


    def test_table_structure_preserved(self):
        """
        验证表格结构（headers, rows）完整保留
        """
        headers = ['Product', 'Q1', 'Q2', 'Q3']
        rows = [
            ['Sales', '1000', '1200', '1500'],
            ['Profit', '200', '250', '300'],
            ['Margin', '20%', '21%', '20%']
        ]
        
        raw_slides = [
            {
                'number': 1,
                'layout': 'table',
                'title': 'Quarterly Results',
                'body_paragraphs': [],
                'tables': [
                    {
                        'headers': headers,
                        'rows': rows
                    }
                ],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        
        self.assertEqual(result[0]['type'], 'table')
        self.assertEqual(result[0]['headers'], headers)
        self.assertEqual(result[0]['rows'], rows)


    def test_caption_uses_newline_not_space(self):
        """
        验证 caption 中的多个内容项用换行符分隔，而非空格
        
        这对可读性和 HTML 渲染很重要
        """
        body_texts_input = ['Line 1', 'Line 2', 'Line 3']
        smartart_input = ['SmartArt 1', 'SmartArt 2']
        
        raw_slides = [
            {
                'number': 1,
                'layout': 'table',
                'title': 'Multi-line Caption',
                'body_paragraphs': [
                    {'text': text} for text in body_texts_input
                ],
                'tables': [
                    {'headers': ['H'], 'rows': [['R']]}
                ],
                'smartart': smartart_input,
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        caption = result[0].get('caption', '')
        
        # 验证使用换行符分隔
        self.assertIn('\n', caption, 
            "caption 应使用换行符分隔多个内容")
        
        # 验证所有项都在
        all_expected = body_texts_input + smartart_input
        for item in all_expected:
            self.assertIn(item, caption,
                f"'{item}' 应在 caption 中")


    def test_no_slide_skipping(self):
        """
        关键测试：所有 slide 都应被处理，不应有任何遗漏
        
        这是 _normalise_pptx 的核心不变量：
        输入 N 个 slide → 输出 N 个 entry（无一例外）
        """
        raw_slides = [
            {
                'number': 1,
                'layout': 'title',
                'title': 'Title',
                'body_paragraphs': [{'text': 'Subtitle'}],
                'tables': [],
                'smartart': [],
                'images': [],
                'notes': '',
            },
            {
                'number': 2,
                'layout': 'content-list',
                'title': 'Content',
                'body_paragraphs': [{'text': 'Item 1'}, {'text': 'Item 2'}],
                'tables': [],
                'smartart': [],
                'images': [],
                'notes': '',
            },
            {
                'number': 3,
                'layout': 'content',
                'title': 'Blank',
                'body_paragraphs': [],
                'tables': [],
                'smartart': [],
                'images': [],
                'notes': '',
            },
        ]

        result = _normalise_pptx(raw_slides)
        
        self.assertEqual(len(result), 3, 
            "输入 3 个 slide 应返回 3 个 entry，不能有遗漏或合并")


    def test_empty_text_handling(self):
        """
        验证空文本处理：不应添加空项
        """
        raw_slides = [
            {
                'number': 1,
                'layout': 'content-list',
                'title': 'Content',
                'body_paragraphs': [
                    {'text': ''},           # 空
                    {'text': '   '},        # 空白
                    {'text': 'Valid'},      # 有效
                    {'text': '\n'},         # 空
                ],
                'tables': [],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        items = result[0].get('items', [])
        
        # 应只有 1 个有效项
        self.assertEqual(len(items), 1,
            "空文本应被过滤掉")
        self.assertEqual(items[0], 'Valid')


    def test_type_promotion_to_stats(self):
        """
        验证数字内容自动升级为 stats 类型
        """
        raw_slides = [
            {
                'number': 2,  # 不是第一个，所以不强制为 title
                'layout': 'content-list',
                'title': 'Stats',
                'body_paragraphs': [
                    {'text': '500K Revenue'},
                    {'text': '25% Growth'},
                    {'text': '10M Users'},
                ],
                'tables': [],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        
        self.assertEqual(result[0]['type'], 'stats',
            "包含数字的 content-list 应升级为 stats 类型")
        
        stats = result[0].get('stats', [])
        self.assertEqual(len(stats), 3)


    def test_image_always_included(self):
        """
        验证主图像在所有 slide 类型中都被保留
        （之前的 bug：只在 image 类型中保留）
        """
        image_url = 'path/to/image.png'
        
        raw_slides = [
            {
                'number': 1,
                'layout': 'image-text',
                'title': 'With Image',
                'body_paragraphs': [{'text': 'Some text'}],
                'tables': [],
                'smartart': [],
                'images': [image_url],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        
        self.assertIn('image', result[0],
            "图像应被保留在 entry 中")
        self.assertEqual(result[0]['image'], image_url)


class TestNormalisePptxRegressions(unittest.TestCase):
    """回归测试：确保之前修复的 bug 不会再出现"""

    def test_regression_bug_200char_truncation(self):
        """
        回归测试：200 字截断 bug
        
        BUG ID: PPTX_CONTENT_LOSS_2025_03_19
        描述：表格下的 caption 被硬截断到 200 字
        修复：改用 '\n'.join() 且不截断
        
        验证：
        - 确保 caption 不会被截断
        - 确保即使超过 200 字也完整保留
        """
        long_caption = 'Long text ' * 30  # 300+ 字
        
        raw_slides = [
            {
                'number': 1,
                'layout': 'table',
                'title': 'Regression Test',
                'body_paragraphs': [{'text': long_caption}],
                'tables': [{'headers': ['A'], 'rows': [['B']]}],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        caption = result[0].get('caption', '')
        
        # 验证没有被截断到 200 字
        self.assertGreater(len(caption), 200,
            "Caption 不应被截断到 200 字！")
        self.assertIn(long_caption, caption,
            "Long caption 应完整保留")


    def test_regression_109_items_loss(self):
        """
        回归测试：109 个列表项只显示 1 个
        
        BUG ID: PPTX_CONTENT_LOSS_2025_03_19_SLIDE6
        描述：真实 PPT 的 Slide 6 有 109 个项目，但只显示 1 个
        根因：某处代码只取了 all_items[0] 或做了不当的 join/split
        修复：确保 all_items 完整传递
        """
        items = [f'Item {i}' for i in range(1, 110)]
        
        raw_slides = [
            {
                'number': 1,
                'layout': 'content-list',
                'title': 'Many Items',
                'body_paragraphs': [{'text': item} for item in items],
                'tables': [],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        result_items = result[0].get('items', [])
        
        self.assertEqual(len(result_items), 109,
            f"应有 109 个项，实际 {len(result_items)} 个（丢失 {109-len(result_items)} 个！）")


class TestNormalisePptxEdgeCases(unittest.TestCase):
    """边界情况测试"""

    def test_multiple_tables_uses_first(self):
        """
        验证多个表格时使用第一个，其他表格转为 caption
        """
        raw_slides = [
            {
                'number': 1,
                'layout': 'table',
                'title': 'Multiple Tables',
                'body_paragraphs': [],
                'tables': [
                    {'headers': ['A1', 'B1'], 'rows': [['R1', 'S1']]},
                    {'headers': ['A2', 'B2'], 'rows': [['R2', 'S2']]},
                ],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        
        # 应使用第一个表格
        self.assertEqual(result[0]['headers'], ['A1', 'B1'])
        self.assertEqual(result[0]['rows'][0], ['R1', 'S1'])


    def test_table_without_headers(self):
        """
        验证无 headers 的表格处理
        """
        raw_slides = [
            {
                'number': 1,
                'layout': 'table',
                'title': 'No Headers',
                'body_paragraphs': [],
                'tables': [
                    {'headers': [], 'rows': [['A', 'B'], ['C', 'D']]},
                ],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        
        self.assertEqual(result[0]['headers'], [])
        self.assertEqual(len(result[0]['rows']), 2)


    def test_mixed_content_types(self):
        """
        验证混合内容处理：body_texts + table_lines + smartart
        
        UPDATE (2025-03-19): With improved mixed content handling,
        slides with tables are now correctly prioritized to 'table' type.
        So this test now verifies table type is preserved with all content in caption.
        """
        raw_slides = [
            {
                'number': 1,
                'layout': 'content-list',
                'title': 'Mixed',
                'body_paragraphs': [{'text': 'Body 1'}, {'text': 'Body 2'}],
                'tables': [
                    {'headers': ['H1'], 'rows': [['R1'], ['R2']]}
                ],
                'smartart': ['SA1', 'SA2'],
                'images': [],
                'notes': '',
            }
        ]

        result = _normalise_pptx(raw_slides)
        entry = result[0]
        
        # With improved logic, should be table type (not bullets)
        self.assertEqual(entry['type'], 'table',
            "Mixed table+text+smartart should use table type")
        
        # Should preserve all content in caption
        caption = entry.get('caption', '')
        self.assertIn('Body 1', caption, "Body text should be in caption")
        self.assertIn('Body 2', caption, "Body text should be in caption")
        self.assertIn('SA1', caption, "SmartArt should be in caption")
        self.assertIn('SA2', caption, "SmartArt should be in caption")


    def test_image_with_many_body_paragraphs(self):
        """
        🔥 CRITICAL FIX: Image slides with large amounts of body text
        
        Previously: 138 body_paragraphs → only 2 saved as caption (99.3% loss)
        Now: All body_paragraphs should be preserved in caption field
        
        This was the root cause of Slides 3, 5, 8 problems in 001.pptx
        """
        raw_slides = [
            {
                'number': 1,
                'layout': 'image-text',
                'title': 'Image with Many Items',
                'body_paragraphs': [
                    {'text': f'Item {i}'} 
                    for i in range(1, 139)  # 138 items
                ],
                'tables': [],
                'smartart': [],
                'images': ['image1.jpg'],
                'notes': '',
            }
        ]
        
        result = _normalise_pptx(raw_slides)
        entry = result[0]
        
        # Should be image type
        self.assertEqual(entry['type'], 'image')
        
        # Caption should contain ALL 138 items, not just 2
        caption = entry.get('caption', '')
        self.assertIn('Item 1', caption, "First item should be in caption")
        self.assertIn('Item 138', caption, "Last item should be in caption")
        
        # Count items in caption (separated by newlines)
        caption_lines = [l.strip() for l in caption.split('\n') if l.strip()]
        self.assertGreaterEqual(len(caption_lines), 100,
            f"Expected 100+ lines, got {len(caption_lines)} (significant loss detected!)")

    def test_table_mixed_with_text_preserves_type(self):
        """
        FIX: Table type should be preserved even when mixed with text
        
        Previously: 2 tables + 3 text items → bullets type (table lost)
        Now: Should detect table priority and keep table type
        
        This was the root cause of Slide 4 problem in 001.pptx
        """
        raw_slides = [
            {
                'number': 1,
                'layout': 'content-list',
                'title': 'Mixed Table and Text',
                'body_paragraphs': [
                    {'text': 'Intro text'},
                    {'text': 'Middle text'},
                    {'text': 'Conclusion text'},
                ],
                'tables': [
                    {
                        'headers': ['Header 1', 'Header 2'],
                        'rows': [['Row1Col1', 'Row1Col2'], ['Row2Col1', 'Row2Col2']]
                    },
                    {
                        'headers': ['Header A', 'Header B'],
                        'rows': [['RowACol1', 'RowACol2']]
                    }
                ],
                'smartart': [],
                'images': [],
                'notes': '',
            }
        ]
        
        result = _normalise_pptx(raw_slides)
        entry = result[0]
        
        # Should detect table priority and use table type
        self.assertEqual(entry['type'], 'table',
            "Mixed table+text should use table type, not bullets")
        
        # Should preserve table structure
        self.assertIn('headers', entry)
        self.assertEqual(entry['headers'], ['Header 1', 'Header 2'])
        
        # Should preserve all body text in caption
        caption = entry.get('caption', '')
        self.assertIn('Intro text', caption, "First text item should be in caption")
        self.assertIn('Conclusion text', caption, "Last text item should be in caption")

    def test_image_with_smartart_and_text(self):
        """
        Complex mixed content: Image + body text + SmartArt
        
        All content should be preserved in caption without truncation
        """
        raw_slides = [
            {
                'number': 1,
                'layout': 'image-text',
                'title': 'Complex Mixed Slide',
                'body_paragraphs': [
                    {'text': f'Body Item {i}'} 
                    for i in range(1, 11)  # 10 body items
                ],
                'tables': [],
                'smartart': [f'SmartArt {i}' for i in range(1, 6)],  # 5 smartart items
                'images': ['image.jpg'],
                'notes': '',
            }
        ]
        
        result = _normalise_pptx(raw_slides)
        entry = result[0]
        
        self.assertEqual(entry['type'], 'image')
        caption = entry.get('caption', '')
        
        # All body items should be present
        self.assertIn('Body Item 1', caption)
        self.assertIn('Body Item 10', caption)
        
        # All smartart items should be present
        self.assertIn('SmartArt 1', caption)
        self.assertIn('SmartArt 5', caption)
        
        # No truncation at 120 chars
        self.assertGreater(len(caption), 120,
            f"Caption was truncated (only {len(caption)} chars), should preserve all content")


if __name__ == '__main__':
    # 运行测试
    unittest.main(verbosity=2)
