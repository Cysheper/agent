
class Tool:
    tools = []
    tools_prompt: str = ""

    @classmethod
    def register(cls, tool_function):
        cls.tools.append((tool_function.__name__, tool_function))
        cls.tools_prompt += tool_function.__doc__


def tool(tool_function):
    Tool.register(tool_function)
    return tool_function