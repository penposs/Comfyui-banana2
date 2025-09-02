"""
@author: Gemini
@title: Banana Node
@nickname: Banana Node
@description: A node to generate images using the Apicore.ai gemini-2.5-flash-image-preview API.
"""

# 从 banana_node.py 文件中导入主类
from .banana_node import BananaNode

# 节点类名到 Python 类的映射
NODE_CLASS_MAPPINGS = {
    "BananaNode": BananaNode
}

# 节点在 ComfyUI 菜单中的显示名称
NODE_DISPLAY_NAME_MAPPINGS = {
    "BananaNode": "Banana Gemini Gen"
}

# 导出映射，以便 ComfyUI 加载
__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS']

print("✅ [Banana Node] Custom Node Loaded")