#!/usr/bin/env python3

from src.graph.nodes import _get_intelligent_tool_recommendations

# 测试推荐
recommendations = _get_intelligent_tool_recommendations(
    "数据存储和知识图谱构建",
    "存储研究发现，建立实体关系，创建知识图谱", 
    "researcher"
)

print("智能推荐结果:")
for category, details in recommendations.items():
    print(f"  {category}: {details}")

print("\n检查filesystem推荐:")
print(f"  是否包含filesystem: {'filesystem' in recommendations}")

# 检查关键词匹配
content = "数据存储和知识图谱构建 存储研究发现，建立实体关系，创建知识图谱".lower()
filesystem_keywords = [
    "file", "document", "read", "write", "csv", "json", "pdf", "text", "local",
    "folder", "directory", "path", "upload", "download",
    "文件", "文档", "读取", "写入", "本地", "目录", "路径", "上传", "下载",
    "文本", "资料", "材料"
]

print(f"\n内容: {content}")
print("filesystem关键词匹配:")
for keyword in filesystem_keywords:
    if keyword in content:
        print(f"  ✅ {keyword}")

# 检查工具匹配
test_tools = {
    "memory-server": ["create_entities", "create_relations", "add_observations"],
    "arxiv-paper-mcp": ["search_papers", "get_paper_details"], 
    "filesystem": ["read_file", "write_file"]
}

print("\n工具匹配检查:")
for server_name, tools in test_tools.items():
    print(f"\n{server_name}:")
    for tool_name in tools:
        tool_name_lower = tool_name.lower()
        
        # Memory tools
        if "memory" in recommendations and any(keyword in tool_name_lower for keyword in 
               ["memory", "entities", "relations", "observations", "store", "save", "create", "add"]):
            print(f"  ✅ {tool_name} -> memory")
        
        # Search tools  
        elif "search" in recommendations and any(keyword in tool_name_lower for keyword in 
               ["search", "find", "query", "retrieve", "browse", "papers", "paper"]):
            print(f"  ✅ {tool_name} -> search")
        
        # Filesystem tools
        elif "filesystem" in recommendations and any(keyword in tool_name_lower for keyword in 
               ["file", "read", "write", "directory", "path"]):
            print(f"  ✅ {tool_name} -> filesystem")
        
        else:
            print(f"  ❌ {tool_name} -> 无匹配") 