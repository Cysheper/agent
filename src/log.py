
import logging

# 创建Logger
logger = logging.getLogger("Agent")
logger.setLevel(logging.DEBUG)

# 创建文件handler
file_handler = logging.FileHandler("app.log", encoding='UTF-8')
file_handler.setLevel(logging.DEBUG)

# 创建formatter
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(filename)s - %(lineno)d - %(funcName)s - %(message)s")
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)

