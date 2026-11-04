from src.tool import tool


from memory.memory import Memory

memory = Memory()

@tool
def memory_get(content: list[str]):
    """
## memory_get(content: list[str]), 获取与content相关的记忆

### 参数：
- content
    类型： list[str]
    示例："content": ["最喜欢的水果"]

### 返回值
类型：list[str, double] 第一个参数是记忆，第二个参数是相关度
    """
    return memory.get(" ".join(content))

@tool
def memory_add(content: list[str]):
    """
## memory_add(content: str), 添加相关记忆

### 参数：
- content
    类型：list[str]
    示例："content": ["用户最喜欢吃西瓜"]

    """
    return memory.add("".join(content))