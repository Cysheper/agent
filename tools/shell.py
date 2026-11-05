from src.tool import tool
import subprocess

# @tool
# def weather(city: str) -> str:
#     """
# ## weather(city: str), 获取城市天气

# ### 参数：
# - city:
#     类型: str
#     示例："city": "Tokyo"

# ### 返回值
# 类型： str

#     """
#     return f"The weather of {city} is sunny."

@tool
def shell(cmd: list[str]) -> dict:
    """
## `shell`工具

### 参数：
类型: list[str]
示例
"cmd": ["ls", "-l", ...] 

### 返回值
类型： str

### **注意**
Shell工具是你的主要工具，请灵活使用。你可以使用shell编写python脚本并执行，也可以编写很多自己制作的工具。
    """

    result = subprocess.run(cmd, capture_output=True, text=True)
    data = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
    return data


