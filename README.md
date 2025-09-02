# ComfyUI-Banana-Node

一个用于ComfyUI的自定义节点，使用Google的Gemini 2.5 Flash Image Preview API生成图像。

## 功能特性

- 使用Google Gemini 2.5 Flash Image Preview模型
- 支持多张输入图像
- 可自定义提示词
- 支持多种输出尺寸比例
- 完整的错误处理和日志记录

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

1. 在ComfyUI中找到 "Banana" 分类下的 "Banana Gemini Gen" 节点
2. 连接输入图像
3. 设置提示词（描述你想要生成的图像）
4. 选择输出尺寸比例
5. 运行工作流

## 输入参数

- **model**: 模型选择（目前支持 gemini-2.5-flash-image-preview）
- **prompt**: 文本提示词，描述你想要生成的图像
- **size**: 输出图像尺寸比例
- **input_image**: 输入图像（必需）

## 输出

- **image**: 生成的图像
- **revised_prompt**: 修订后的提示词（当前为N/A）
- **image_url**: 图像URL（当前为N/A）

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

### v1.0.0
- 初始版本
- 支持Gemini 2.5 Flash Image Preview API
- 基本的图像生成功能