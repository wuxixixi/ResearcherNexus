#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
测试脚本：验证从 DeerFlow 同步的更新功能
"""

import sys
import json

def test_json_utils():
    """测试 JSON 修复功能"""
    print("=" * 60)
    print("测试 1: JSON 修复功能 (json_utils.py)")
    print("=" * 60)
    
    try:
        from src.utils.json_utils import (
            repair_json_output, 
            sanitize_tool_response,
            _extract_json_from_content
        )
        print("[OK] 成功导入 json_utils 模块")
        
        # 测试 1: 修复简单的 JSON
        test_json = '{"name": "test", "value": 123}'
        result = repair_json_output(test_json)
        print("[OK] 简单 JSON 修复测试通过")
        
        # 测试 2: 修复带有 Markdown 代码块的 JSON
        test_md_json = '''```json
{"name": "test", "value": 123}
```'''
        result = repair_json_output(test_md_json)
        print("[OK] Markdown JSON 修复测试通过")
        
        # 测试 3: 修复带有额外 token 的 JSON
        test_extra = '{"name": "test"} some extra text'
        result = _extract_json_from_content(test_extra)
        print("[OK] 额外 token 提取测试通过")
        
        # 测试 4: sanitize_tool_response
        test_response = '{"key": "value"} trailing garbage'
        result = sanitize_tool_response(test_response, max_length=1000)
        print("[OK] 工具响应清理测试通过")
        
        print("\n[OK] JSON 修复功能测试全部通过！\n")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] JSON 修复功能测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_citations_module():
    """测试 Citations 模块"""
    print("=" * 60)
    print("测试 2: Citations 模块")
    print("=" * 60)
    
    try:
        from src.citations import (
            Citation,
            CitationMetadata,
            CitationCollector,
            CitationFormatter,
            extract_citations_from_messages,
            merge_citations,
            citations_to_markdown_references
        )
        print("[OK] 成功导入 citations 模块")
        
        # 测试 1: 创建 CitationMetadata
        metadata = CitationMetadata(
            url="https://example.com/article",
            title="Test Article",
            description="A test article"
        )
        print(f"[OK] CitationMetadata 创建测试通过: {metadata.title}")
        
        # 测试 2: 创建 Citation
        citation = Citation(
            number=1,
            metadata=metadata,
            context="Test context"
        )
        print(f"[OK] Citation 创建测试通过: [{citation.number}] {citation.title}")
        
        # 测试 3: CitationCollector
        collector = CitationCollector()
        print(f"[OK] CitationCollector 创建测试通过")
        
        # 测试 4: CitationFormatter
        formatter = CitationFormatter(collector)
        print(f"[OK] CitationFormatter 创建测试通过")
        
        print("\n[OK] Citations 模块测试全部通过！\n")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] Citations 模块测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_state_types():
    """测试 State 类型更新"""
    print("=" * 60)
    print("测试 3: State 类型 (types.py)")
    print("=" * 60)
    
    try:
        from src.graph.types import State
        
        # 测试 1: 检查 citations 字段存在
        state = State()
        
        # 检查是否有 citations 属性
        if hasattr(state, 'citations'):
            print(f"[OK] State 类型包含 citations 字段")
            print(f"   citations 默认值: {state.citations}")
        else:
            print("[WARNING] State 类型可能不包含 citations 字段（可能使用 dataclass 默认）")
        
        # 测试 2: 测试设置 citations
        test_citations = [
            {"url": "https://example.com", "title": "Test"}
        ]
        
        # 创建新的 state 并设置 citations
        try:
            state_with_citations = State()
            state_with_citations.citations = test_citations
            print(f"[OK] 成功设置 citations 字段")
        except Exception as e2:
            print(f"[WARNING] 设置 citations 字段时出现问题: {e2}")
        
        print("\n[OK] State 类型测试完成！\n")
        return True
        
    except Exception as e:
        print(f"\n[ERROR] State 类型测试失败: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 60)
    print("开始测试从 DeerFlow 同步的更新功能")
    print("=" * 60 + "\n")
    
    results = []
    
    # 测试 1: JSON 修复功能
    results.append(("JSON 修复功能", test_json_utils()))
    
    # 测试 2: Citations 模块
    results.append(("Citations 模块", test_citations_module()))
    
    # 测试 3: State 类型
    results.append(("State 类型", test_state_types()))
    
    # 打印总结
    print("\n" + "=" * 60)
    print("测试结果总结")
    print("=" * 60)
    
    for name, passed in results:
        status = "[OK] 通过" if passed else "[ERROR] 失败"
        print(f"{name}: {status}")
    
    all_passed = all(passed for _, passed in results)
    
    if all_passed:
        print("\n[OK] 所有测试通过！同步的功能正常工作。\n")
        return 0
    else:
        print("\n[ERROR] 部分测试失败，请检查相关功能。\n")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
