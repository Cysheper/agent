from src.tool import tool
import requests
import os

@tool
def get_balance() -> str:
    """
## get_balance() , 获取LLM账户余额

### 参数； 无

### 返回值
类型：str
    """
    response = requests.get(
        "https://api.deepseek.com/user/balance",
        headers={"Authorization": f"Bearer {os.environ['DEEPSEEK_API_KEY']}"},
        timeout=60,
    )
    response.raise_for_status()

    return str(response.json())

if __name__ == "__main__":
    get_balance()