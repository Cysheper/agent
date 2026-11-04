from pydantic import * # type: ignore
import os
import requests
import time
import threading
from src.module import *

class QQ():
    def __init__(
            self,
            QQ_API_BASE: str,
            TOKEN: str
        ) -> None:
        self.base: str=QQ_API_BASE
        self.token: str=TOKEN
        self.qq_number: int=self.getSelfQQNumber()

    def getSelfQQNumber(self) -> int:
        url = f"{self.base}/get_login_info"
        response = requests.get(url, headers={"Authorization": self.token})
        data = response.json().get("data", {})
        return data.get("user_id")

    def getQQUserName(self, number: int) -> str:
        url = f"{self.base}/get_stranger_info"
        payload = {
            "user_id": number
        }
        response = requests.get(url, params=payload, headers={"Authorization": self.token})
        # print(response.json())
        data = response.json().get("data", {})
        return data.get("nickname", "未知用户")
    
    def postMessage(self, group_id: int, message: str, at: str | None=None) -> Status:
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "text",
                    "data": {
                        "text": message
                    }
                }
            ]
        }
        if at is not None:
            payload["message"].append(
                {
                    "type": "at",
                    "data": {
                        "qq": at
                    }
                }
            )
        try:
            info = requests.post(f"{self.base}/send_group_msg", 
                                 json=payload, 
                                 headers={"Authorization": self.token}).json()

            if info["status"] == "ok":
                return Status(code="ok", message="[Accepted] Post Message Success")
            else:
                return Status(code="error", message="[Error] Post Message Failed")
        except Exception as e:
            return Status(code="error", message="[Error] Network Error")

    
    def postImg(self, group_id: int, img: str, willdel: bool = False) -> Status:
        payload = {
            "group_id": group_id,
            "message": [
                {
                    "type": "image",
                    "data": {
                        "summary": "[图片]",
                        "file": img
                    }
                }
            ]
        }
        try:
            info = requests.post(f"{self.base}/send_group_msg", 
                                 json=payload, headers={"Authorization": self.token}, 
                                 timeout=10).json()
            if info["status"] == "ok":
                if willdel:
                    message_id = info["data"]["message_id"]
                    delImage = threading.Thread(target=self.delMessage, args=(message_id,))
                    delImage.start()
                return Status(code="ok", message="[Accepted] Post Image Success")
            else:
                return Status(code="error", message="[Error] Post Image Failed")
        except Exception as e:
            return Status(code="error", message=str(e))
        
        
    def delMessage(self, message_id) -> Status:
        time.sleep(60)
        try:
            data = {
                "message_id": message_id
            }
            response = requests.post(f"{self.base}/delete_msg", 
                                     data=data,
                                     headers={"Authorization": self.token}
                                     ).json()
            if response["status"] == "ok":
                return Status(code="ok", message="[Info] 图片已撤回")
            else:
                return Status(code="error", message="[Error] 图片撤回失败")

        except Exception as e:
            return Status(code="error", message=str(e))