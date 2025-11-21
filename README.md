# ComfyUI-Banana-Node

一个用于ComfyUI的自定义节点，使用Google的Gemini 2.5 Flash Image 与 Gemini 3 Pro Image Preview API生成图像。

## 功能特性

- 使用Google Gemini 2.5 Flash Image Preview模型
- 支持多张输入图像
- 可自定义提示词
- 支持多种输出尺寸比例
- 完整的错误处理和日志记录
- **新增**：图像比例调整节点 - 支持裁剪、填充、拉伸等多种调整方式
- **新增**：分辨率缩放节点 - 支持1K、2K、4K、8K等多种分辨率缩放

## 安装

1. 将此仓库克隆到你的ComfyUI自定义节点目录：
```bash
cd ComfyUI/custom_nodes
git clone https://github.com/your-username/ComfyUI-Banana-Node.git
```

2. 安装依赖：
```bash
cd ComfyUI-Banana-Node
pip install google-generativeai pillow numpy torch
```

3. 配置API密钥：
   - 复制 `config.json.example` 为 `config.json`
   - 在 `config.json` 中填入你的Google AI API密钥
   - 获取API密钥：访问 [Google AI Studio](https://aistudio.google.com/app/apikey)
   - 需绑定一张visa或者master 信用卡即可获得300美元的免费额度
   - 绑定方法：访问 [Google AI Studio](https://aistudio.google.com/app/apikey)，点击"绑定信用卡"，输入信用卡信息即可绑定。

```json
{
    "api_key": "your_google_ai_api_key_here"
}
```

4. 重启ComfyUI

## 使用方法

### Banana Gemini Gen 节点
1. 在ComfyUI中找到 "Banana" 分类下的 "Banana Gemini Gen" 节点
2. 连接输入图像
3. 设置提示词（描述你想要生成的图像）
4. 选择输出尺寸比例
5. 运行工作流

### Banana Ratio Adjuster 节点
1. 在ComfyUI中找到 "Banana Node/Ratio" 分类下的 "Banana Ratio Adjuster" 节点
2. 连接输入图像
3. 选择目标比例（1:1、4:3、16:9等常见比例或自定义比例）
4. 选择调整方法：
   - **crop**: 裁剪图像以匹配目标比例
   - **pad**: 填充图像以匹配目标比例
   - **stretch**: 拉伸图像以匹配目标比例
5. 如选择填充模式，可设置填充颜色
6. 运行工作流

### Banana Resolution Scaler 节点
1. 在ComfyUI中找到 "Banana Node/Ratio" 分类下的 "Banana Resolution Scaler" 节点
2. 连接输入图像
3. 选择目标分辨率（1K、2K、4K、8K或自定义）
4. 选择是否保持宽高比
5. 运行工作流

## 输入参数

### Banana Gemini Gen 节点
- **model**: 模型选择（目前支持 gemini-2.5-flash-image 与 gemini-3-pro-image-preview）
- **prompt**: 文本提示词，描述你想要生成的图像
- **size**: 输出图像尺寸比例
- **input_image**: 输入图像（必需）

### Banana Ratio Adjuster 节点
- **image**: 输入图像
- **target_ratio**: 目标比例（1:1、4:3、16:9等或自定义）
- **resize_method**: 调整方法（crop、pad、stretch）
- **custom_width**: 自定义宽度比例（当选择自定义比例时）
- **custom_height**: 自定义高度比例（当选择自定义比例时）
- **pad_color_r/g/b**: 填充颜色的RGB值（当选择pad方法时）

### Banana Resolution Scaler 节点
- **image**: 输入图像
- **target_resolution**: 目标分辨率（1K、2K、4K、8K、自定义）
- **maintain_ratio**: 是否保持宽高比
- **custom_size**: 自定义尺寸（当选择自定义分辨率时）

## 输出

### Banana Gemini Gen 节点
- **image**: 生成的图像
- **revised_prompt**: 修订后的提示词（当前为N/A）
- **image_url**: 图像URL（当前为N/A）

### Banana Ratio Adjuster 节点
- **image**: 调整后的图像
- **width**: 输出图像宽度
- **height**: 输出图像高度
- **ratio**: 最终宽高比

### Banana Resolution Scaler 节点
- **image**: 缩放后的图像
- **width**: 输出图像宽度
- **height**: 输出图像高度

## 注意事项

- 需要有效的Google AI API密钥
- 确保网络连接正常
- API调用可能产生费用，请查看Google AI的定价政策

## 故障排除

1. **"config.json文件未找到"错误**：
   - 确保已将 `config.json.example` 复制为 `config.json`
   - 检查文件是否在正确的目录中

2. **API密钥错误**：
   - 验证API密钥是否正确
   - 确保API密钥有足够的权限和配额

3. **依赖包错误**：
   - 确保已安装所有必需的Python包
   - 尝试重新安装依赖包

## 许可证

MIT License

## 贡献

欢迎提交问题和拉取请求！

## 更新日志

### v1.1.0
- 新增图像比例调整节点（Banana Ratio Adjuster）
- 新增分辨率缩放节点（Banana Resolution Scaler）
- 支持多种图像比例调整方式（裁剪、填充、拉伸）
- 支持1K、2K、4K、8K等多种分辨率缩放
- 完善的比例计算和图像处理工具类

### v1.0.0
- 初始版本
- 支持Gemini 2.5 Flash Image Preview API
- 基本的图像生成功能