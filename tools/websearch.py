from src.tool import tool
import os
import requests


@tool
def web_search(query: str, count: int = 3) -> str:
    """
## web_search(query: str, count: int = 3), 网页搜索

### 参数：
- query: 
    类型: str
    示例："query": "deepseek最新模型是什么？"
- count:
    类型: int
    示例："count": 5
    默认值: 3

### 返回值
类型： str
    """
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/tools/search",
            headers={"Authorization": f"Bearer {os.getenv("DEEPSEEK_API_KEY")}"},
            json={
                "query": query,
                "count": count,
                "need_content": False,
            },
            timeout=60,
        )
        response.raise_for_status()

        data, count = "", 1
        for result in response.json()["results"]:
            data += f"结果{str(count)}：标题：{result["title"]}\n"
            data += f"网址：{result["url"]}\n"
            data += f"发布时间：{result["date"]}\n"
            data += f"长摘要: \n{result["summary"]} \n\n"
            count += 1
        return data
    except Exception as e:
        return f"[Error]: {str(e)}"

@tool
def web_fetch(url: str):
    """
## web_fetch(url: str), 网页抓取

### 参数：
- url:
    类型：str
    示例："url": "https://example.com"

### 返回值
类型： str
    """
    try:
        response = requests.post(
            "https://api.deepseek.com/v1/tools/fetch",
            headers={"Authorization": f"Bearer {os.environ['DEEPSEEK_API_KEY']}"},
            json={"url": url},
            timeout=60,
        )
        response.raise_for_status()
        page = response.json()
        data = f"# url: {url}\n# 标题：{page["title"]}\n# 正文：\n{page["content"]}\n"
        return data

    except Exception as e:
        return f"[Error]: {str(e)}"

if __name__ == "__main__":
    print(web_search("明日方舟新干员塔露拉是最强近卫吗", 2))
    print(web_fetch("https://api-docs.deepseek.com/zh-cn/"))
