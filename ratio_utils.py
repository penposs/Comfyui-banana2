import torch
import numpy as np
from PIL import Image, ImageDraw
import os
import math

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
        pil_images = tensor2pil(image)
        result_images = []
        
        resolution_map = {"1K": 1024, "2K": 2048, "4K": 4096}
        target_size = resolution_map[resolution]
        
        for pil_img in pil_images:
            orig_width, orig_height = pil_img.size
            aspect_ratio = orig_width / max(1, orig_height)
            
            # 1. 根据原图宽高比和目标分辨率，计算出一个“目标”画布尺寸
            if aspect_ratio > 1:
                proportional_canvas_width = int(round(target_size))
                proportional_canvas_height = max(1, int(round(target_size / aspect_ratio)))
            else:
                proportional_canvas_height = int(round(target_size))
                proportional_canvas_width = max(1, int(round(target_size * aspect_ratio)))
            
            # 2. 最终画布尺寸必须能容纳下原始图片，所以取计算尺寸和原始尺寸中的最大值
            canvas_width = max(proportional_canvas_width, orig_width)
            canvas_height = max(proportional_canvas_height, orig_height)
            
            # 3. 创建白色背景画布
            canvas = Image.new('RGB', (canvas_width, canvas_height), 'black')
            
            # 4. 计算偏移量，将原图居中
            x_offset = (canvas_width - orig_width) // 2
            y_offset = (canvas_height - orig_height) // 2
            
            # 5. 直接粘贴原始图片，不进行任何缩放
            canvas.paste(pil_img, (x_offset, y_offset))

            # --- 全新逻辑：在四角绘制箭头 ---
            # 只有在存在白边的情况下才绘制
            if x_offset > 0 or y_offset > 0:
                draw = ImageDraw.Draw(canvas)
                
                # --- 核心修改：增大箭头粗细 ---
                arrow_color = "black"
                # 根据画布较小边的尺寸动态调整箭头粗细 (除数更小=更粗, 最小宽度更大)
                arrow_width = max(4, int(min(canvas_width, canvas_height) / 256))

                # 定义原图的四个角点
                img_tl = (x_offset, y_offset)
                img_tr = (x_offset + orig_width, y_offset)
                img_bl = (x_offset, y_offset + orig_height)
                img_br = (x_offset + orig_width, y_offset + orig_height)
                
                # 定义画布的四个角点 (使用-1确保在画布内)
                canvas_tl = (0, 0)
                canvas_tr = (canvas_width - 1, 0)
                canvas_bl = (0, canvas_height - 1)
                canvas_br = (canvas_width - 1, canvas_height - 1)
                
                # 绘制四个箭头
                _draw_arrow(draw, img_tl, canvas_tl, fill=arrow_color, width=arrow_width)
                _draw_arrow(draw, img_tr, canvas_tr, fill=arrow_color, width=arrow_width)
                _draw_arrow(draw, img_bl, canvas_bl, fill=arrow_color, width=arrow_width)
                _draw_arrow(draw, img_br, canvas_br, fill=arrow_color, width=arrow_width)
            
            result_images.append(canvas)
        
        return (pil2tensor(result_images),)


def _draw_arrow(draw, start, end, fill, width):
    """在给定的画布(draw)上，从start点到end点绘制一个带箭头的线。"""
    
    # 将箭头柄缩短至80%，以确保箭头头部总能完整显示
    shaft_end_x = start[0] + 0.8 * (end[0] - start[0])
    shaft_end_y = start[1] + 0.8 * (end[1] - start[1])
    shaft_end = (shaft_end_x, shaft_end_y)
    
    # 绘制缩短后的主线段
    draw.line([start, shaft_end], fill=fill, width=width)

    # --- 核心修改：增大箭头头部尺寸 ---
    # 箭头头部两条线的长度，与主线宽度成比例 (乘数更大=更长, 最小长度更大)
    arrowhead_len = max(30, width * 8)
    arrowhead_angle = math.pi / 6

    # 箭头的指向角度保持不变 (永远指向原始的终点'end')
    angle = math.atan2(end[1] - start[1], end[0] - start[0])

    # 计算箭头头部两条线的终点坐标 (相对于shaft_end)
    p1_x = shaft_end[0] - arrowhead_len * math.cos(angle - arrowhead_angle)
    p1_y = shaft_end[1] - arrowhead_len * math.sin(angle - arrowhead_angle)

    p2_x = shaft_end[0] - arrowhead_len * math.cos(angle + arrowhead_angle)
    p2_y = shaft_end[1] - arrowhead_len * math.sin(angle + arrowhead_angle)

    # 从shaft_end处绘制箭头头部的两条线
    draw.line([shaft_end, (p1_x, p1_y)], fill=fill, width=width)
    draw.line([shaft_end, (p2_x, p2_y)], fill=fill, width=width)