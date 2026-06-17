---
name: draw-ppb
description: "Right Code 绘图 API skill。当用户需要生成图片、创建图像、AI绘画、文生图、图生图、参考图生成、4K超清输出、或进行带图提问的对话时使用。覆盖 /v1/images/generations（图片生成，支持参考图和4K）和 /v1/chat/completions（带图对话，支持多模态）两个接口。Trigger phrases: 生成图片, 画图, 文生图, AI绘画, 创建图像, 生成一张图, 画一张, 以图生图, 参考图, 带图提问, 4K, 超清, 高清, 4k, hd, vip, make an image, generate image, draw, create picture, text to image, image to image, img2img, image generation, DALL-E, stable diffusion, 图片处理, 图像处理, 图片生成, 图片理解."
agent_created: true
---

# Right Code Draw

统一入口 `https://www.right.codes/draw`，兼容 OpenAI 格式的图片生成与带图对话能力。

官方文档：
- 总览：https://docs.right.codes/docs/rc_extension/draw/
- 图片生成：https://docs.right.codes/docs/rc_extension/draw/images-generations.html
- 带图对话：https://docs.right.codes/docs/rc_extension/draw/chat-completions.html
- 模型列表（后台）：https://docs.right.codes/docs/rc_quick_start/models.html

## 前置条件

### API Key

需要有效的 Right Code API Key（格式 `sk-xxxxx`）。查找优先级：

1. 环境变量 `RIGHTCODE_API_KEY`
2. 用户在对话中明确提供
3. 使用脚本时通过 `--api-key` 参数传入

如果 Key 不存在，先询问用户提供 Key 再继续。

### 鉴权方式

所有请求统一使用 Header：

```
Authorization: Bearer <API_KEY>
```

### 模型选择

模型列表在 Right Code 后台动态管理（进入后台 → 模型列表），不在文档中静态列出。常见模型：
- 图片生成：`gpt-image-2`、`gpt-image-1`、`dall-e-3` 等（以后台实际显示为准）
- 带图对话：`gemini-3.1-pro`、`gpt-4o`、`gemini-2.5-pro` 等（以后台实际显示为准）

如果用户不指定模型，默认使用 `gpt-image-2`（生成）和 `gemini-3.1-pro`（对话）。

### 画质预设（Quality Presets）

图片生成支持三档画质预设，通过 `--quality` 或 `--4k` 快捷开关选择：

| 预设 | 尺寸 | 命令 | 说明 |
|------|------|------|------|
| `standard` | 1024×1024（默认） | 默认，无需指定 | 标准画质，速度最快 |
| `hd` | 2048×2048 | `--quality hd` | 2K 高清 |
| `4k` | 4096×4096 | `--quality 4k` 或 `--4k` | 4K 超清（VIP），耗时较长 |

**4K 注意事项：**
- 4K 模式 token 消耗显著增加（输出约 25000 token），预留充足额度
- 可在后台查看是否有专用 4K 模型（如 `gemini-3-pro-image-preview`），通过 `--model-4k` 指定
- 如果 4K 模型不可用，使用 `--model` 指定支持 4K 输出的模型即可
- 超时自动设为 300s

---

## Core Capabilities

### 1. 图片生成 — `/v1/images/generations`

根据文字描述生成图片，支持传入参考图进行风格/内容引导（图生图）。

**如果只想拿一张图的直链，这个接口最省事。**

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 图片生成模型名称，如 `gpt-image-2` |
| `prompt` | string | 是 | 提示词，描述要生成的图片内容 |
| `image` | array | 否 | 参考图列表，每个元素为 base64 或 URL 字符串，用于图生图/风格引导 |
| `size` | string | 否 | 输出尺寸，格式 `宽x高`（如 `1024x1024`），直接填像素值 |
| `response_format` | string | 否 | 响应格式，通常为 `url` |

#### Curl 示例（文生图）

```bash
curl -X POST https://www.right.codes/draw/v1/images/generations \
  -H "Authorization: Bearer $RIGHTCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "一只边牧与古牧正在抖音直播间直播带货",
    "size": "1024x1024",
    "response_format": "url"
  }'
```

#### Curl 示例（图生图 / 参考图）

```bash
curl -X POST https://www.right.codes/draw/v1/images/generations \
  -H "Authorization: Bearer $RIGHTCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "将这张照片转为动漫风格",
    "image": ["https://example.com/my-photo.jpg"],
    "size": "1024x1024",
    "response_format": "url"
  }'
```

#### 响应格式

```json
{
  "created": 1777689832,
  "data": [
    {
      "url": "https://file4.aitohumanize.com/file/dfa13fe60e7649e88f46037b968b54a3.png"
    }
  ],
  "usage": {
    "total_tokens": 6267,
    "input_tokens": 17,
    "output_tokens": 6250
  }
}
```

#### 脚本调用

```bash
# 文生图（标准画质）
python3 scripts/draw.py generate \
  --prompt "一只在太空漫步的猫" \
  --size 1024x1024 \
  --output space_cat.png

# 高清 2K
python3 scripts/draw.py generate \
  --prompt "一幅壮丽的山水风景" \
  --quality hd \
  --output landscape.png

# VIP 4K 超清（快捷开关）
python3 scripts/draw.py generate \
  --prompt "一幅壮丽的山水风景" \
  --4k \
  --output landscape_4k.png

# 4K + 指定 VIP 模型
python3 scripts/draw.py generate \
  --prompt "一幅壮丽的山水风景" \
  --quality 4k \
  --model-4k gemini-3-pro-image-preview \
  --output landscape_4k.png

# 图生图（参考图）
python3 scripts/draw.py generate \
  --prompt "转为水彩画风格" \
  --ref-image my-photo.jpg \
  --size 1024x1024 \
  --output watercolor.png
```

### 2. 带图对话 — `/v1/chat/completions`

兼容 OpenAI Chat Completions 格式，支持纯文本对话和带图提问（多模态）。支持流式与非流式两种模式。

#### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 支持多模态的模型名称，如 `gemini-3.1-pro` |
| `stream` | boolean | 是 | `true` 启用 SSE 流式输出，`false` 返回完整 JSON |
| `messages` | array | 是 | 对话消息数组，content 支持纯文本或多模态（文本+图片）格式 |

#### 消息格式

**纯文本：** content 直接传入字符串。

**多模态（图片 + 文本）：** content 使用数组格式，`text` 类型为文本内容，`image_url` 类型为图片（支持 URL 或 base64）。

```json
{
  "role": "user",
  "content": [
    {"type": "text", "text": "这张图片内容是什么"},
    {
      "type": "image_url",
      "image_url": {"url": "https://xxxxxxx.png"}
    }
  ]
}
```

#### Curl 示例（纯文本）

```bash
curl -X POST https://www.right.codes/draw/v1/chat/completions \
  -H "Authorization: Bearer $RIGHTCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro",
    "stream": false,
    "messages": [{"role": "user", "content": "你好"}]
  }'
```

#### Curl 示例（带图提问）

```bash
curl -X POST https://www.right.codes/draw/v1/chat/completions \
  -H "Authorization: Bearer $RIGHTCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro",
    "stream": false,
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "这张图片内容是什么"},
          {
            "type": "image_url",
            "image_url": {"url": "https://example.com/photo.jpg"}
          }
        ]
      }
    ]
  }'
```

#### 响应格式（`stream: false`）

```json
{
  "id": "1-2ede12b5-77cc-48f9-b1d0-7ae35ee8d444",
  "created": 1777897048,
  "model": "gemini-3.1-pro",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "你好！请问有什么我可以帮您的吗？"
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 2,
    "completion_tokens": 261,
    "total_tokens": 263
  },
  "system_fingerprint": ""
}
```

**关键字段：**
- `choices[0].message.content` — 助手回复内容
- `choices[0].finish_reason` — `stop`（正常结束）或 `length`（超长截断）
- `usage.prompt_tokens` / `usage.completion_tokens` / `usage.total_tokens` — Token 消耗

#### 响应格式（`stream: true` — SSE 流式）

服务端按 SSE 分片返回，正文在 `choices[0].delta.content` 中，最后一个 chunk 附带 `usage` 和 `finish_reason`。

```
data: {"choices":[{"delta":{"content":"你好！"}}],...}

data: {"choices":[{"delta":{"content":"请问有什么我可以帮你的吗？"}],"finish_reason":"stop"},...}
```

#### 脚本调用

```bash
# 纯文本对话
python3 scripts/draw.py chat --prompt "你好，介绍一下自己"

# 带图对话（本地文件）
python3 scripts/draw.py chat \
  --image /path/to/photo.jpg \
  --prompt "描述这张图片的内容"

# 带图对话（URL）
python3 scripts/draw.py chat \
  --image "https://example.com/photo.jpg" \
  --prompt "这张图里有什么"

# 流式输出
python3 scripts/draw.py chat \
  --image photo.jpg \
  --prompt "描述这张图片" \
  --stream
```

---

## 工作流程

### 图片生成流程

1. 确认用户需求：描述内容、是否需要参考图、尺寸偏好
2. 确保 API Key 可用（检查环境变量或询问用户）
3. 调用 `scripts/draw.py generate` 或直接 curl
4. 下载并保存图片，返回给用户

### 图生图流程

1. 让用户提供参考图（本地路径或 URL）
2. 确认用户期望的变换效果（风格转换、内容修改等）
3. 将参考图以 base64 或 URL 形式放入 `image` 数组
4. 调用接口，返回处理后的图片

### 带图对话流程

1. 确认用户要分析的图片路径或 URL
2. 确认用户的问题
3. 调用 `scripts/draw.py chat` 或直接 curl
4. 将分析结果直接返回给用户

---

## 资源

### scripts/draw.py

Python CLI 工具，封装两个接口的调用。支持：

- `generate` 子命令 — 文生图 / 图生图（`--ref-image` 传入参考图）
- `--quality` 画质预设 — `standard`（默认 1024）/ `hd`（2K 2048）/ `4k`（4K 4096）
- `--4k` 快捷开关 — 等效 `--quality 4k`
- `--model-hd` / `--model-4k` — 高清/4K 模式专属模型（可选，不指定则沿用 `--model`）
- `chat` 子命令 — 纯文本 / 带图对话（`--stream` 启用流式输出）
- 自动从环境变量 `RIGHTCODE_API_KEY` 读取 Key
- `--api-key` 参数手动指定
- 图片自动保存到指定路径

### references/api.md

完整 API 参考文档，含参数说明、响应格式、SSE 流式处理、消息格式等。

## 注意事项

- 图片生成 prompt 建议使用详细描述，英文/中文均可
- 图生图时参考图支持 URL 和 base64 两种格式
- 生成图片可能需要数秒到数十秒，超时设为 120s
- `stream` 参数在 chat completions 中为**必填**，非流式填 `false`
- 支持的模型列表以 Right Code 后台实际显示为准，会动态更新
- API Key 额度限制请参考 Right Code 后台
