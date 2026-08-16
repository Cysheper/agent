from src.tool import tool
import subprocess

@tool
def weather(city: str) -> str:
    """
    ## weather(city), 获取城市天气

    ### 参数：
    **类型**：字符串
    **示例**：
    "args": "Tokyo"

    ### 返回对应city的天气

    """
    return f"The weather of {city} is sunny."

@tool
def shell(cmd: list[str]) -> dict:
    """
    ## `shell`工具

    ### 参数：
    **类型**：列表
    **示例**
    "args": ["ls", "-l", ...] 

    ### 返回：
    shell执行后的结果
    """

    result = subprocess.run(cmd, capture_output=True, text=True)
    data = {
        "stdout": result.stdout,
        "stderr": result.stderr,
        "returncode": result.returncode
    }
    return data


