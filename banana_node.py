import os
import json
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import logging

# NEW: Import the required Google GenAI library
import google.generativeai as genai

# --- 日志配置 ---
# 我们将 logger 的获取放到类的方法中，以确保作用域正确
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - BananaNode - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)


# --- Helper functions for Image Conversion ---
# (tensor2pil 和 pil2tensor 函数保持不变)
def tensor2pil(image: torch.Tensor) -> list[Image.Image]:
    """Converts a torch tensor to a list of PIL Images."""
    batch_count = image.shape[0]
    images = []
    for i in range(batch_count):
        img_tensor = image[i]
        img_np = (img_tensor.cpu().numpy().squeeze() * 255).astype(np.uint8)
        if len(img_np.shape) == 3 and img_np.shape[2] == 3: # HWC
            images.append(Image.fromarray(img_np, 'RGB'))
        elif len(img_np.shape) == 2: # HW (grayscale)
            images.append(Image.fromarray(img_np, 'L'))
        else: # Fallback for other formats
            images.append(Image.fromarray(img_np))
    return images

def pil2tensor(images: list[Image.Image]) -> torch.Tensor:
    """Converts a list of PIL Images to a torch tensor."""
    tensors = []
    for img in images:
        img_np = np.array(img).astype(np.float32) / 255.0
        if len(img_np.shape) == 2: # Grayscale to RGB
            img_np = np.stack([img_np]*3, axis=-1)
        tensors.append(torch.from_numpy(img_np))
    return torch.stack(tensors)


class BananaNode:
    # __init__, load_config, INPUT_TYPES 等保持不变
    def __init__(self):
        self.config = self.load_config()

    def load_config(self):
        """加载配置文件"""
        try:
            config_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'config.json')
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            api_key = config.get('api_key', '')
            if api_key.lower().startswith('bearer '):
                api_key = api_key[7:].strip()
            config['api_key'] = api_key
            return config
        except FileNotFoundError:
            raise FileNotFoundError("错误：'config.json' 文件未找到。请将 'config.json.example' 重命名为 'config.json' 并填入您的 Google AI API Key。")
        except json.JSONDecodeError:
            raise ValueError("错误：'config.json' 文件格式不正确。请检查其内容是否为有效的 JSON。")
        except Exception as e:
            # 在这里我们还不能使用 logger，所以用 print
            print(f"[Banana Node] 加载配置时出错: {e}")
            return {}

    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "model": (["gemini-2.5-flash-image-preview"],),
                "prompt": ("STRING", {"multiline": True, "default": "Combine the features of all input images into a single new image."}),
                "size": (["和输入图一样", "1x1", "16x9", "9x16", "4x3", "3x4", "3x2", "2x3", "21x9", "9x21"],),
            },
            "optional": {
                "input_image": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "revised_prompt", "image_url")
    FUNCTION = "generate"
    CATEGORY = "Banana"

    def generate(self, model: str, prompt: str, size: str, input_image: torch.Tensor = None):
        # --- vvvvvvvvvvvv 主要修改区域 vvvvvvvvvvvv ---
        # 1. 在函数开始时获取 logger 实例
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - BananaNode - %(levelname)s - %(message)s', force=True)
        logger = logging.getLogger(__name__)
        # --- ^^^^^^^^^^^^ 主要修改区域 ^^^^^^^^^^^^ ---
        
        api_key = self.config.get("api_key")
        if not api_key:
            raise ValueError("Google AI API Key 未在 'config.json' 中设置。")

        if input_image is None:
            raise ValueError("错误：此节点需要一个 'input_image' 输入才能运行。")

        try:
            genai.configure(api_key=api_key)
            generative_model = genai.GenerativeModel(model)

            input_pil_images = tensor2pil(input_image)
            batch_size = len(input_pil_images)
            logger.info(f"检测到 {batch_size} 张图片输入，将作为单次任务发送。")
            
            contents = []
            for img in input_pil_images:
                contents.append(img)
            contents.append(prompt)
            
            logger.info(f"正在向 Gemini API ({model}) 发送包含 {batch_size} 张图片和1条文本的请求...")
            
            response = generative_model.generate_content(contents)

            image_parts = [
                part.inline_data.data
                for part in response.candidates[0].content.parts
                if part.inline_data
            ]

            if not image_parts:
                raise Exception("API 响应中未找到生成的图片数据。")
            
            logger.info("✅ API 请求成功，正在处理返回的图片...")
            
            generated_pil_image = Image.open(BytesIO(image_parts[0])).convert("RGB")
            output_tensor = pil2tensor([generated_pil_image])
            
            revised_prompt_output = "N/A"
            image_url_output = "N/A"
            
            return (output_tensor, revised_prompt_output, image_url_output)

        except Exception as e:
            # 确保 logger 在异常处理中也可用
            logger.error(f"❌ 发生错误: {e}")
            raise
