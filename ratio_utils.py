import torch
import numpy as np
from PIL import Image

def tensor2pil(image):
    """将tensor转换为PIL图像列表"""
    if len(image.shape) == 4:
        # 批次维度存在
        return [Image.fromarray(np.clip(255. * img.cpu().numpy(), 0, 255).astype(np.uint8)) for img in image]
    else:
        # 单张图片
        return [Image.fromarray(np.clip(255. * image.cpu().numpy(), 0, 255).astype(np.uint8))]

def pil2tensor(images):
    """将PIL图像列表转换为tensor"""
    if isinstance(images, list):
        tensors = [torch.from_numpy(np.array(img).astype(np.float32) / 255.0) for img in images]
        return torch.stack(tensors, dim=0)
    else:
        return torch.from_numpy(np.array(images).astype(np.float32) / 255.0).unsqueeze(0)

class TransparentImageNode:
    """将输入图像居中放置在等比例的白色背景上"""
    
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "resolution": (["1K", "2K", "4K"], {"default": "2K"}),
            }
        }
    
    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("output_image",)
    FUNCTION = "generate_centered_image"
    CATEGORY = "Banana Node"
    
    def generate_centered_image(self, image, resolution):
        # 将tensor转换为PIL图像
        pil_images = tensor2pil(image)
        result_images = []
        
        # 定义分辨率映射
        resolution_map = {"1K": 1024, "2K": 2048, "4K": 4096}
        target_size = resolution_map[resolution]
        
        for pil_img in pil_images:
            orig_width, orig_height = pil_img.size
            aspect_ratio = orig_width / orig_height
            
            # 根据宽高比确定画布尺寸，长边为目标像素
            if aspect_ratio > 1:  # 宽图
                canvas_width = target_size
                canvas_height = int(target_size / aspect_ratio)
            else:  # 高图或正方形
                canvas_height = target_size
                canvas_width = int(target_size * aspect_ratio)
            
            # 创建白色背景
            canvas = Image.new('RGB', (canvas_width, canvas_height), 'white')
            
            # 计算缩放比例（保持宽高比）
            scale = min(1.0, min(canvas_width / orig_width, canvas_height / orig_height))
            new_width = max(1, int(orig_width * scale))
            new_height = max(1, int(orig_height * scale))
            
            # 缩放并居中放置
            resized_img = pil_img.resize((new_width, new_height), Image.Resampling.LANCZOS)
            x_offset = (canvas_width - new_width) // 2
            y_offset = (canvas_height - new_height) // 2
            canvas.paste(resized_img, (x_offset, y_offset))
            
            result_images.append(canvas)
        
        return (pil2tensor(result_images),)