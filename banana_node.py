import os
import json
import torch
import numpy as np
from PIL import Image
from io import BytesIO
import logging
import base64
import time
import requests
import re

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
                "model": (["gemini-2.5-flash-image","gemini-3-pro-image-preview"],{"default": "gemini-3-pro-image-preview"}),
                "prompt": ("STRING", {"multiline": True, "default": "Combine the features of all input images into a single new image."}),
                "aspect_ratio": (["Automatic", "1:1", "2:3", "3:2", "3:4", "4:3", "4:5", "5:4", "9:16", "16:9", "21:9"], {"default": "Automatic"}),
                "resolution": (["1K", "2K", "4K"], {"default": "1K"}),
            },
            "optional": {
                "api_key": ("STRING", {"multiline": False, "default": ""}),
                "base_url": ("STRING", {"multiline": False, "default": ""}),
                "image1": ("IMAGE",),
                "image2": ("IMAGE",),
                "image3": ("IMAGE",),
                "image4": ("IMAGE",),
                "image5": ("IMAGE",),
                "image6": ("IMAGE",),
                "image7": ("IMAGE",),
                "image8": ("IMAGE",),
                "image9": ("IMAGE",),
                "image10": ("IMAGE",),
                "image11": ("IMAGE",),
                "image12": ("IMAGE",),
                "image13": ("IMAGE",),
                "image14": ("IMAGE",),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "STRING")
    RETURN_NAMES = ("image", "revised_prompt", "image_url")
    FUNCTION = "generate"
    CATEGORY = "Banana"

    def generate(self, model: str, prompt: str, aspect_ratio: str, resolution: str, api_key: str = "", base_url: str = "",
                 image1: torch.Tensor = None, image2: torch.Tensor = None, image3: torch.Tensor = None, image4: torch.Tensor = None,
                 image5: torch.Tensor = None, image6: torch.Tensor = None, image7: torch.Tensor = None, image8: torch.Tensor = None,
                 image9: torch.Tensor = None, image10: torch.Tensor = None, image11: torch.Tensor = None, image12: torch.Tensor = None,
                 image13: torch.Tensor = None, image14: torch.Tensor = None):
        # --- vvvvvvvvvvvv 主要修改区域 vvvvvvvvvvvv ---
        # 1. 在函数开始时获取 logger 实例
        logging.basicConfig(level=logging.INFO, format='%(asctime)s - BananaNode - %(levelname)s - %(message)s', force=True)
        logger = logging.getLogger(__name__)
        # --- ^^^^^^^^^^^^ 主要修改区域 ^^^^^^^^^^^^ ---
        
        # 优先使用输入的 api_key，如果没有则使用配置文件中的
        api_key = api_key.strip() if api_key else self.config.get("api_key")
        if not api_key:
            raise ValueError("Google AI API Key 未在节点输入或 'config.json' 中设置。")
            
        # 根据分辨率设置超时时间
        timeout = 120 # 默认 1K/2K 为 2分钟
        if resolution == "4K":
            timeout = 360 # 4K 为 6分钟
        logger.info(f"设置超时时间为: {timeout} 秒 (分辨率: {resolution})")

        # 聚合所有图片输入（多端口 + 批次），顺序：image1 → image14
        aggregated_pil_images = []
        try:
            images_list = [image1, image2, image3, image4, image5, image6, image7, image8, image9, image10, image11, image12, image13, image14]
            for img_tensor in images_list:
                if img_tensor is not None:
                    aggregated_pil_images.extend(tensor2pil(img_tensor))
        except Exception as e:
            raise ValueError(f"错误：图片输入解析失败 - {e}")

        # if not aggregated_pil_images:
        #     raise ValueError("错误：需要至少提供一张图片（image1~image4）。")

        try:
            # 处理代理与自定义端点（与 Gemini_Pro_Node 类似），优先使用节点输入的 base_url
            endpoint = (base_url or self.config.get('base_url', '') or '').strip()
            if endpoint.endswith('/'):
                endpoint = endpoint[:-1]

            proxy = (self.config.get('proxy', '') or '').strip()
            if proxy:
                if not (proxy.startswith('http://') or proxy.startswith('https://')):
                    proxy = f"http://{proxy}"
                os.environ['http_proxy'] = proxy
                os.environ['https_proxy'] = proxy
                os.environ['HTTP_PROXY'] = proxy
                os.environ['HTTPS_PROXY'] = proxy
                os.environ['ALL_PROXY'] = proxy
                logger.info(f"使用代理: {proxy}")
            else:
                for proxy_var in ['http_proxy', 'https_proxy', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY']:
                    if proxy_var in os.environ:
                        del os.environ[proxy_var]
                logger.info("不使用代理")

            # 与 Gemini_Pro_Node 保持一致：通过环境变量暴露端点给潜在的子流程
            if endpoint:
                os.environ['GENAI_API_ENDPOINT'] = endpoint
            else:
                if 'GENAI_API_ENDPOINT' in os.environ:
                    del os.environ['GENAI_API_ENDPOINT']

            # ========== 改为地址调用（REST）而非 SDK ==========
            # 组装基础地址（为空则使用官方默认）
            base = endpoint if endpoint else "https://generativelanguage.googleapis.com"
            if base.endswith('/'):
                base = base[:-1]

            # 路径需要 models/<model>:generateContent
            model_path = model if isinstance(model, str) and model.startswith('models/') else f"models/{model}"
            url = f"{base}/v1beta/{model_path}:generateContent"

            # 记录输入统计
            batch_size = len(aggregated_pil_images)
            logger.info(f"检测到 {batch_size} 张图片输入，将作为单次任务发送（REST 地址调用）。")

            # 构建 parts：对齐 Tutu.py，先添加每张图片的标识文本再添加图片（PNG base64）
            parts = []
            # 先放入图片标识+图片
            for idx, img in enumerate(aggregated_pil_images, start=1):
                try:
                    # 添加图片标识文本，便于模型在后续引用（如“图片1”、“图片2”）
                    parts.append({"text": f"[这是图片{idx}]"})
                    buf = BytesIO()
                    img.save(buf, format='PNG')
                    b64 = base64.b64encode(buf.getvalue()).decode('utf-8')
                    parts.append({
                        "inlineData": {
                            "mimeType": "image/png",
                            "data": b64
                        }
                    })
                except Exception as _e:
                    logger.warning(f"编码输入图片失败（已跳过一张）: {_e}")
            # 再放入用户文本指令
            if prompt:
                parts.append({"text": prompt})

            # 构建 generationConfig
            generation_config = {
                "temperature": 0.4,
                "maxOutputTokens": 8192,
                "candidateCount": 1
            }
            
            # 构建 imageConfig
            image_config = {}
            if aspect_ratio != "Automatic":
                image_config["aspectRatio"] = aspect_ratio
            
            # 只有 gemini-3-pro-image-preview 支持 imageSize (resolution)
            image_config["imageSize"] = resolution
            
            if image_config:
                generation_config["imageConfig"] = image_config

            payload = {
                "contents": [
                    {
                        "role": "user",
                        "parts": parts
                    }
                ],
                "generationConfig": generation_config
            }

            # 使用查询参数携带 API Key（官方 REST 支持 key=...）
            params = {"key": api_key}

            # requests 代理（也支持环境变量自动读取）
            req_proxies = None
            if (self.config.get('proxy', '') or '').strip():
                req_proxies = {"http": proxy, "https": proxy}

            response_data = None
            last_error = "未知错误"
            max_retries = 2
            for attempt in range(max_retries):
                try:
                    logger.info(f"[Banana|REST] 尝试第 {attempt + 1}/{max_retries} 次 API 调用...")
                    start_time = time.time()
                    r = requests.post(url, json=payload, params=params, timeout=timeout, proxies=req_proxies, headers={"Content-Type": "application/json"})
                    end_time = time.time()
                    if r.status_code == 200:
                        response_data = r.json()
                        logger.info(f"[Banana|REST] API 调用成功，耗时: {end_time - start_time:.2f} 秒")
                        break
                    else:
                        last_error = f"HTTP {r.status_code}: {r.text[:300]}"
                        logger.warning(f"[Banana|REST] 返回非 200 状态码: {last_error}")
                        if attempt < max_retries - 1:
                            time.sleep(1)
                except Exception as e:
                    last_error = str(e)
                    logger.warning(f"[Banana|REST] 第 {attempt + 1} 次尝试失败: {last_error}")
                    if attempt < max_retries - 1:
                        logger.info("[Banana|REST] 网络连接超时或错误，1秒后重试...")
                        time.sleep(1)

            if response_data is None:
                raise ValueError(f"错误：API 未返回任何内容。最后一次错误: {last_error}")

            # 默认回传：如果未生成图片，则透传第一张输入图片，保证端口类型正确
            fallback_tensor = pil2tensor([aggregated_pil_images[0]]) if aggregated_pil_images else torch.zeros((1, 1, 1, 3), dtype=torch.float32)
            output_tensor = fallback_tensor
            image_url_output = "N/A"

            # 提取所有返回的图片（包括 inlineData 以及 文本中的 data:image/...;base64,...）
            generated_pils = []
            first_image_url = None
            try:
                candidates = []
                if isinstance(response_data, dict):
                    candidates = response_data.get('candidates') or []
                for cand in candidates:
                    content = cand.get('content') if isinstance(cand, dict) else None
                    parts_list = []
                    if isinstance(content, dict):
                        parts_list = content.get('parts') or []
                    elif isinstance(content, list):
                        parts_list = content
                    for part in parts_list or []:
                        if not isinstance(part, dict):
                            continue
                        # 1) inlineData 图片
                        inline_data = part.get('inlineData') or part.get('inline_data')
                        if isinstance(inline_data, dict):
                            data = inline_data.get('data')
                            mime = inline_data.get('mimeType') or inline_data.get('mime_type') or 'image/png'
                            if data:
                                try:
                                    img_bytes = data if isinstance(data, bytes) else base64.b64decode(data)
                                    pil = Image.open(BytesIO(img_bytes)).convert('RGB')
                                    generated_pils.append(pil)
                                    if first_image_url is None:
                                        # 还原成 data URL 用于第三个输出口
                                        b64_out = base64.b64encode(img_bytes).decode('utf-8')
                                        first_image_url = f"data:{mime};base64,{b64_out}"
                                except Exception:
                                    pass
                        # 2) 文本中的 data:image/...;base64,...
                        txt = part.get('text')
                        if isinstance(txt, str) and ('data:image/' in txt):
                            try:
                                # 支持多个 data URL
                                matches = re.findall(r'data:image/[^;]+;base64,[A-Za-z0-9+/=]+', txt)
                                for url in matches:
                                    try:
                                        _, b64data = url.split(',', 1)
                                        img_bytes = base64.b64decode(b64data)
                                        pil = Image.open(BytesIO(img_bytes)).convert('RGB')
                                        generated_pils.append(pil)
                                        if first_image_url is None:
                                            first_image_url = url
                                    except Exception:
                                        continue
                            except Exception:
                                pass
            except Exception as e:
                logger.warning(f"提取图片失败: {str(e)}")

            if generated_pils:
                logger.info(f"✅ API 请求成功，提取到 {len(generated_pils)} 张返回的图片。")
                output_tensor = pil2tensor(generated_pils)
                image_url_output = first_image_url or "N/A"
            else:
                logger.warning("API 响应中未找到生成的图片数据，将透传输入图片作为输出。")
            
            # 提取模型返回文本作为 revised_prompt（若存在）
            try:
                texts = []
                if isinstance(response_data, dict):
                    for cand in (response_data.get('candidates') or []):
                        content = cand.get('content') if isinstance(cand, dict) else None
                        parts_list = content.get('parts') if isinstance(content, dict) else []
                        for p in parts_list or []:
                            if isinstance(p, dict):
                                t = p.get('text')
                                if t:
                                    texts.append(t)
                revised_prompt_output = (" ".join(texts)).strip() if texts else "N/A"
            except Exception:
                revised_prompt_output = "N/A"
            
            return (output_tensor, revised_prompt_output, image_url_output)

        except Exception as e:
            # 确保 logger 在异常处理中也可用
            logger.error(f"❌ 发生错误: {e}")
            raise
