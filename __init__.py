# 从 banana_node.py 文件中导入 BananaNode
from .banana_node import BananaNode
# 从 ratio_utils.py 文件中导入透明图节点
from .ratio_utils import TransparentImageNode

# 节点类名到 Python 类的映射
NODE_CLASS_MAPPINGS = {
    "BananaNode": BananaNode,
    "TransparentImageNode": TransparentImageNode
}

# 节点在 ComfyUI 菜单中的显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "BananaNode": "Banana Gemini Gen",
    "TransparentImageNode": "Banana Transparent Generator"
}