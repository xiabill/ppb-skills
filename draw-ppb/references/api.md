# PPB Draw API Reference

> Base URL: `https://www.right.codes/draw`
> Auth: `Authorization: Bearer sk-xxxxx`

---

## 1. 图片生成 — `/v1/images/generations`

根据文字描述生成图片，支持传入参考图进行图生图/风格引导。

**如果只想拿一张图的直链，这个接口最省事。**

### 请求

```
POST /v1/images/generations
Content-Type: application/json
Authorization: Bearer sk-xxxxx
```

### 请求参数

| 参数 | 类型 | 必填 | 默认值 | 说明 |
|------|------|------|--------|------|
| `model` | string | 是 | — | 图片生成模型名称。已知可用：`gpt-image-2`、`gpt-image-1`、`dall-e-3` 等 |
| `prompt` | string | 是 | — | 图片描述文本，英文/中文均可，建议详细描述以获得更好效果 |
| `image` | array | 否 | — | 参考图列表，每个元素为 base64 data URL 或 HTTP(S) URL。用于图生图：以参考图为蓝本生成新图 |
| `size` | string | 否 | — | 输出尺寸，格式 `宽x高`。常用：`1024x1024`（标准）、`2048x2048`（2K HD）、`4096x4096`（4K VIP）。直接填像素值 |
| `response_format` | string | 否 | — | 响应返回格式，示例值 `url`。可能支持 `b64_json` |

### 使用场景

#### 文生图（Text-to-Image）

只提供 `prompt`，由模型从零生成图片。支持标准、高清、4K 三种画质：

**标准（1024×1024）：**
```json
{
  "model": "gpt-image-2",
  "prompt": "生成一张边牧与古牧正在抖音直播间直播带货截图",
  "size": "1024x1024",
  "response_format": "url"
}
```

**4K 超清（4096×4096）— VIP：**
```json
{
  "model": "gpt-image-2",
  "prompt": "生成一张边牧与古牧正在抖音直播间直播带货截图",
  "size": "4096x4096",
  "response_format": "url"
}
```

> ⚡ 4K 模式 output tokens 约 25000（标准 1024 约 6250），token 消耗约为标准模式的 4 倍，预留充足额度。

#### 图生图 / 参考图（Image-to-Image）

提供 `image` 数组传入参考图，模型以参考图为蓝本，根据 `prompt` 进行风格转换或内容调整。

```json
{
  "model": "gpt-image-2",
  "prompt": "将这张照片转为吉卜力动漫风格",
  "image": ["https://example.com/my-photo.jpg"],
  "size": "1024x1024",
  "response_format": "url"
}
```

参考图的 `image` 数组中每个元素支持两种格式：
- **URL**：`"https://example.com/photo.jpg"`
- **Base64 Data URL**：`"data:image/png;base64,iVBORw0KGgo..."`

### Curl 示例

```bash
# 文生图
curl -X POST https://www.right.codes/draw/v1/images/generations \
  -H "Authorization: Bearer $RIGHTCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "一只在太空站里漂浮的柴犬，窗外是地球",
    "size": "1024x1024",
    "response_format": "url"
  }'

# 图生图（本地文件先转 base64）
curl -X POST https://www.right.codes/draw/v1/images/generations \
  -H "Authorization: Bearer $RIGHTCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-image-2",
    "prompt": "转为水彩画风格",
    "image": ["data:image/jpeg;base64,'$(base64 -i photo.jpg)'"],
    "size": "1024x1024",
    "response_format": "url"
  }'
```

### 响应格式

#### 成功 (200)

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

**响应字段：**

| 字段 | 类型 | 说明 |
|------|------|------|
| `created` | integer | 生成时间的 Unix 时间戳 |
| `data` | array | 生成的图片数据数组，每项包含 `url` 或 `b64_json` |
| `data[].url` | string | 生成的图片直链 URL（`response_format=url` 时） |
| `data[].b64_json` | string | Base64 编码的图片数据（`response_format=b64_json` 时） |
| `usage` | object | Token 使用量统计 |
| `usage.total_tokens` | integer | 总消耗 Token 数 |
| `usage.input_tokens` | integer | 输入消耗 Token 数（prompt + 参考图） |
| `usage.output_tokens` | integer | 输出消耗 Token 数（生成的图片） |

#### 错误响应

```json
{
  "error": {
    "message": "错误描述信息",
    "type": "error_type",
    "code": "error_code"
  }
}
```

### 常见错误码

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 请求参数错误（如 model 不支持、prompt 为空） |
| 401 | API Key 无效或缺失 |
| 402 | 账户额度不足 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

---

## 2. 带图对话 — `/v1/chat/completions`

兼容 OpenAI Chat Completions 格式，支持纯文本对话和带图提问（多模态）。

### 请求

```
POST /v1/chat/completions
Content-Type: application/json
Authorization: Bearer sk-xxxxx
```

### 请求参数

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `model` | string | 是 | 模型名称。已知可用：`gemini-3.1-pro`、`gpt-4o`、`gemini-2.5-pro` 等 |
| `stream` | boolean | 是 | `true` 启用 SSE 流式输出；`false` 返回完整 JSON 响应 |
| `messages` | array | 是 | 对话消息数组，每项包含 `role` 和 `content` 字段 |

### 消息格式详解

#### 纯文本消息

`content` 直接为字符串。

```json
{
  "role": "user",
  "content": "你好，请介绍一下自己"
}
```

#### 多模态消息（文字 + 图片）

`content` 为数组，混合 `text` 和 `image_url` 类型。

```json
{
  "role": "user",
  "content": [
    {
      "type": "text",
      "text": "这张图片内容是什么"
    },
    {
      "type": "image_url",
      "image_url": {
        "url": "https://example.com/photo.jpg"
      }
    }
  ]
}
```

**图片 (`image_url`) 支持两种格式：**

1. **URL**：`"url": "https://example.com/photo.jpg"`
2. **Base64 Data URL**：`"url": "data:image/png;base64,iVBORw0KGgoAAAA..."`
   - 支持 MIME 类型：`image/png`、`image/jpeg`、`image/gif`、`image/webp`

**支持的系统角色：**
- `system` — 系统级指令（设置 AI 的行为和上下文）
- `user` — 用户消息
- `assistant` — AI 的历史回复（用于多轮对话）

#### 多轮对话示例

```json
{
  "model": "gemini-3.1-pro",
  "stream": false,
  "messages": [
    {"role": "system", "content": "你是一个专业的图片分析师，用中文回答。"},
    {"role": "user", "content": "这张图片里有什么动物？"},
    {
      "role": "user",
      "content": [
        {"type": "text", "text": "就在这张图里"},
        {
          "type": "image_url",
          "image_url": {"url": "https://example.com/animals.jpg"}
        }
      ]
    }
  ]
}
```

### Curl 示例

```bash
# 纯文本对话
curl -X POST https://www.right.codes/draw/v1/chat/completions \
  -H "Authorization: Bearer $RIGHTCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro",
    "stream": false,
    "messages": [{"role": "user", "content": "你好"}]
  }'

# 带图提问（URL 图片）
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

# 流式输出
curl -X POST https://www.right.codes/draw/v1/chat/completions \
  -H "Authorization: Bearer $RIGHTCODE_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gemini-3.1-pro",
    "stream": true,
    "messages": [{"role": "user", "content": "讲一个关于龙的故事"}]
  }'
```

### 响应格式

#### 非流式响应 (`stream: false`)

```json
{
  "id": "1-2ede12b5-77cc-48f9-b1d0-7ae35ee8d444",
  "object": "",
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

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | string | 本次请求唯一 ID |
| `object` | string | 对象类型，通常为空字符串 |
| `created` | integer | 创建时间 Unix 时间戳 |
| `model` | string | 实际使用的模型名称 |
| `choices[].index` | integer | 选项索引 |
| `choices[].message.role` | string | 固定为 `assistant` |
| `choices[].message.content` | string | AI 回复的正文内容 |
| `choices[].finish_reason` | string | `stop`（正常结束）或 `length`（因 token 限制截断） |
| `usage.prompt_tokens` | integer | 提示词消耗 Token 数 |
| `usage.completion_tokens` | integer | 回复消耗 Token 数 |
| `usage.total_tokens` | integer | 总消耗 Token 数 |
| `system_fingerprint` | string | 系统指纹，通常为空 |

#### 流式响应 (`stream: true`) — SSE

服务端按 Server-Sent Events (SSE) 分片返回，每片格式为：

```
data: <JSON>\n\n
```

**单片的 JSON 格式：**

```json
{
  "id": "chatcmpl-xxx",
  "object": "chat.completion.chunk",
  "created": 1777897048,
  "model": "gemini-3.1-pro",
  "choices": [
    {
      "index": 0,
      "delta": {
        "content": "你好！",
        "role": "assistant"
      },
      "finish_reason": null
    }
  ],
  "usage": null,
  "content_filter_results": {}
}
```

**流式字段说明：**

- `choices[].delta.content` — 当前片段的文本内容（非流式的 `message.content` 对应字段）
- `choices[].finish_reason` — 最后一个 chunk 为 `"stop"`，之前均为 `null`
- `usage` — 最后一个 chunk 附带完整的 Token 统计
- `content_filter_results` — 内容安全过滤结果

**客户端处理逻辑：**

1. 逐行读取 SSE 数据
2. 解析每行的 `data:` 后的 JSON
3. 拼接 `delta.content` 得到完整回复
4. 最后一个 chunk 的 `finish_reason` 非 `null` 时停止读取

### 常见错误码

| HTTP 状态码 | 说明 |
|-------------|------|
| 400 | 请求参数错误（如 model 不支持、stream 未传） |
| 401 | API Key 无效或缺失 |
| 402 | 账户额度不足 |
| 429 | 请求频率超限 |
| 500 | 服务器内部错误 |

---

## 3. 通用信息

### 接口速查

| 接口 | 方法 | 路径 | 用途 |
|------|------|------|------|
| 图片生成 | POST | `/v1/images/generations` | 文生图 / 图生图，支持 2K/4K |
| 带图对话 | POST | `/v1/chat/completions` | 纯文本 / 多模态对话 |

### 画质预设速查

| 预设 | 尺寸 | 命令参数 | 预期 output tokens | 适用场景 |
|------|------|----------|-------------------|----------|
| standard | 1024×1024 | 默认 | ~6,250 | 快速预览、社交媒体 |
| hd | 2048×2048 | `--quality hd` | ~12,500 | 高清展示、海报 |
| 4k | 4096×4096 | `--quality 4k` 或 `--4k` | ~25,000 | 印刷、大幅输出（VIP） |

### 鉴权

所有接口统一使用 Bearer Token：

```
Authorization: Bearer sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### 模型管理

- 模型列表在后台动态管理
- 可按需选择可用的端点查看模型名称
- 文档不静态列出模型，以实际后台显示为准

### 速率限制

以后台实际限制为准。如遇 429，建议：
- 降低请求频率
- 使用指数退避重试（1s → 2s → 4s → 8s ...）
- 联系后台提升配额

### 超时建议

- 图片生成（标准/HD）：120s
- 图片生成（4K）：300s（生成 4096×4096 图片耗时较长）
- 带图对话：60s（非流式）或保持连接（流式）

### 注意事项

- `stream` 在 chat completions 中为**必填参数**，不传会报错
- 图片生成接口的 `image` 数组用于传入参考图，不是多图生成
- 每次请求只生成一张图片（从实际响应 `data` 数组通常只有一项可知）
- Base64 编码的图片数据较大时，建议使用 URL 方式传图以减小请求体积
