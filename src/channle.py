from .module import Message, Channle
import json

class Output:
    def __init__(self):
        pass

    def out(self, message: Message):
        match message.output:
            case Channle.Console:
                print(f"> {message.content}")
            case Channle.WebUI:
                data = json.dumps(message)
                yield f"data: {data}\n\n"
            case Channle.QQ:
                data = "[MessageChannle]: QQ\n[UserName]"