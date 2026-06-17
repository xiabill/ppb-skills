#!/usr/bin/env python3
"""
PPB Draw — AI 图片生成与带图对话（PPB 开发）
鉴权: Authorization: Bearer sk-xxxxx
"""

import argparse
import base64
import json
import os
import sys
import urllib.request
import urllib.error
from pathlib import Path

BASE_URL = "https://www.right.codes/draw"


def get_api_key(api_key_arg: str | None = None) -> str:
    """获取 API Key，优先使用参数，其次环境变量"""
    key = api_key_arg or os.environ.get("RIGHTCODE_API_KEY")
    if not key:
        print("\u274c 未找到 API Key。请通过以下方式之一提供：", file=sys.stderr)
        print("   1. 设置环境变量: export RIGHTCODE_API_KEY=sk-xxxxx", file=sys.stderr)
        print("   2. 使用 --api-key 参数", file=sys.stderr)
        sys.exit(1)
    if not key.startswith("sk-"):
        print("\u26a0\ufe0f  API Key 格式可能不正确，应以 'sk-' 开头", file=sys.stderr)
    return key


def make_request(endpoint: str, payload: dict, api_key: str, timeout: int = 120) -> dict:
    """发送 POST 请求到 API"""
    url = f"{BASE_URL}/{endpoint.lstrip('/')}"
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8") if e.fp else ""
        print(f"\u274c HTTP {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"\u274c 请求失败: {e.reason}", file=sys.stderr)
        sys.exit(1)


def encode_image_to_base64(file_path: str) -> str:
    """将本地图片编码为 base64 data URL"""
    path = Path(file_path)
    if not path.exists():
        print(f"\u26a0\ufe0f  文件不存在: {file_path}", file=sys.stderr)
        return None
    mime_map = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".gif": "image/gif",
        ".webp": "image/webp",
        ".bmp": "image/bmp",
    }
    mime = mime_map.get(path.suffix.lower(), "image/png")
    img_bytes = path.read_bytes()
    b64 = base64.b64encode(img_bytes).decode("utf-8")
    return f"data:{mime};base64,{b64}"


def resolve_ref_images(ref_images: list[str]) -> list[str]:
    """将参考图路径列表解析为 API 需要的格式（URL 或 base64 data URL）"""
    result = []
    for img in ref_images:
        if img.startswith(("http://", "https://", "data:")):
            result.append(img)
        else:
            encoded = encode_image_to_base64(img)
            if encoded:
                result.append(encoded)
    return result


# 画质预设：标准尺寸
QUALITY_SIZES = {
    "standard": None,       # 使用 --size 指定的尺寸或默认 1024x1024
    "hd": "2048x2048",      # 2K 高清
    "4k": "4096x4096",      # 4K 超清 (VIP)
}


def cmd_generate(args):
    """图片生成子命令（文生图 / 图生图）"""
    api_key = get_api_key(args.api_key)

    # 处理画质/4K 参数
    quality = args.quality or "standard"
    if getattr(args, "flag_4k", False):
        quality = "4k"

    # 确定模型：4K 模式下可指定专属模型
    model = args.model
    if quality == "4k" and args.model_4k:
        model = args.model_4k
    elif quality == "hd" and args.model_hd:
        model = args.model_hd

    # 确定尺寸：画质预设可覆盖默认尺寸，但显式 --size 优先
    user_explicit_size = args.size != "1024x1024"  # 判断用户是否显式改了 size
    size = args.size
    if quality != "standard" and not user_explicit_size:
        size = QUALITY_SIZES.get(quality, args.size) or args.size

    payload = {
        "model": model,
        "prompt": args.prompt,
    }

    if size:
        payload["size"] = size
    if args.response_format:
        payload["response_format"] = args.response_format

    # 处理参考图（图生图）
    ref_images = []
    if args.ref_image:
        ref_images.append(args.ref_image)
    if args.ref_images:
        ref_images.extend(args.ref_images)

    if ref_images:
        payload["image"] = resolve_ref_images(ref_images)

    quality_label = {"standard": "", "hd": " [2K HD]", "4k": " [4K VIP]"}.get(quality, "")
    mode = "\u56fe\u751f\u56fe" if ref_images else "\u6587\u751f\u56fe"
    print(f"\U0001f3a8 \u6b63\u5728\u751f\u6210\u56fe\u7247 ({mode}){quality_label}...")
    print(f"   Model: {model}")
    print(f"   Prompt: {args.prompt}")
    if size:
        print(f"   Size: {size}")
    if quality == "4k":
        print(f"   \u26a1 VIP 4K \u6a21\u5f0f\uff08\u8f83\u9ad8\u8017\u65f6\uff0c\u8bf7\u8010\u5fc3\u7b49\u5f85\uff09")
    if ref_images:
        print(f"   Reference images: {len(ref_images)}")

    result = make_request("v1/images/generations", payload, api_key,
                          timeout=300 if quality == "4k" else 120)

    # 输出 usage 信息
    usage = result.get("usage", {})
    if usage:
        print(f"\n\U0001f4ca Token: input={usage.get('input_tokens', '?')}, "
              f"output={usage.get('output_tokens', '?')}, "
              f"total={usage.get('total_tokens', '?')}")

    # 保存图片
    data_items = result.get("data", [])
    for i, item in enumerate(data_items):
        img_data = None
        img_url = None

        if "b64_json" in item and item["b64_json"]:
            img_data = base64.b64decode(item["b64_json"])
        elif "url" in item and item["url"]:
            img_url = item["url"]
            try:
                req = urllib.request.Request(img_url)
                with urllib.request.urlopen(req, timeout=60) as resp:
                    img_data = resp.read()
            except Exception as e:
                print(f"\u26a0\ufe0f  \u4e0b\u8f7d\u56fe\u7247\u5931\u8d25: {img_url} ({e})", file=sys.stderr)
                continue

        if img_data:
            output_path = args.output
            if len(data_items) > 1:
                stem = Path(output_path).stem
                suffix = Path(output_path).suffix or ".png"
                output_path = f"{stem}_{i+1}{suffix}"

            Path(output_path).write_bytes(img_data)
            print(f"\u2705 \u5df2\u4fdd\u5b58: {output_path}")
        elif img_url:
            print(f"\U0001f517 \u56fe\u7247 URL: {img_url}")
        else:
            print(f"\u26a0\ufe0f  \u7b2c {i+1} \u5f20\u56fe\u7247\u65e0\u53ef\u7528\u6570\u636e")

    print(f"\n---")
    print(f"\u751f\u6210\u5b8c\u6210 \u2014 {len(data_items)} \u5f20\u56fe\u7247")
    for i, item in enumerate(data_items):
        if "url" in item and item["url"]:
            print(f"- [{i+1}]({item['url']})")


def cmd_chat(args):
    """带图对话子命令（纯文本 / 多模态）"""
    api_key = get_api_key(args.api_key)

    # 构建消息内容
    has_images = bool(args.image or args.images)

    if has_images:
        # 多模态消息
        content = [
            {"type": "text", "text": args.prompt}
        ]
        # 处理图片
        image_paths = []
        if args.image:
            image_paths.append(args.image)
        if args.images:
            image_paths.extend(args.images)

        for img_path in image_paths:
            path = Path(img_path)
            if path.exists():
                encoded = encode_image_to_base64(img_path)
                if encoded:
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": encoded},
                    })
            elif img_path.startswith(("http://", "https://")):
                content.append({
                    "type": "image_url",
                    "image_url": {"url": img_path},
                })
            else:
                print(f"\u26a0\ufe0f  \u8df3\u8fc7\u4e0d\u5b58\u5728\u6587\u4ef6: {img_path}", file=sys.stderr)
    else:
        # 纯文本消息
        content = args.prompt

    payload = {
        "model": args.model,
        "stream": args.stream,
        "messages": [{"role": "user", "content": content}],
    }

    mode = "\u5e26\u56fe" if has_images else "\u7eaf\u6587\u672c"
    stream_label = " (\u6d41\u5f0f)" if args.stream else ""
    print(f"\U0001f4ac \u6b63\u5728\u5206\u6790 ({mode}){stream_label}...")
    print(f"   Model: {args.model}")
    print(f"   Prompt: {args.prompt}")

    result = make_request("v1/chat/completions", payload, api_key)

    # 输出回复
    choices = result.get("choices", [])
    if choices:
        reply = choices[0].get("message", {}).get("content", "")
        finish_reason = choices[0].get("finish_reason", "")
        print(f"\n{'='*60}")
        print(reply)
        print(f"{'='*60}")
        if finish_reason == "length":
            print(f"\n\u26a0\ufe0f  \u8f93\u51fa\u88ab\u622a\u65ad (finish_reason=length)\uff0c\u53ef\u80fd\u9700\u8981\u589e\u5927 token \u9650\u5236")

    # Token 统计
    usage = result.get("usage", {})
    if usage:
        print(f"\n\U0001f4ca Token: prompt={usage.get('prompt_tokens', '?')}, "
              f"completion={usage.get('completion_tokens', '?')}, "
              f"total={usage.get('total_tokens', '?')}")


def main():
    parser = argparse.ArgumentParser(
        description="PPB Draw — AI 图片生成与带图对话（PPB 开发）",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
\u793a\u4f8b:
  # \u6587\u751f\u56fe (\u6807\u51c6)
  %(prog)s generate --prompt "\u4e00\u53ea\u5728\u592a\u7a7a\u6f2b\u6b65\u7684\u732b" --size 1024x1024 --output cat.png

  # 2K \u9ad8\u6e05\u8f93\u51fa
  %(prog)s generate --prompt "\u4e00\u5e45\u98ce\u666f\u753b" --quality hd --output landscape.png

  # VIP 4K \u8d85\u6e05\u8f93\u51fa
  %(prog)s generate --prompt "\u4e00\u5e45\u98ce\u666f\u753b" --4k --output landscape_4k.png

  # 4K + \u6307\u5b9a VIP \u4e13\u5c5e\u6a21\u578b
  %(prog)s generate --prompt "\u4e00\u5e45\u98ce\u666f\u753b" --4k --model-4k gemini-3-pro-image-preview --output landscape_4k.png

  # \u56fe\u751f\u56fe (\u53c2\u8003\u56fe)
  %(prog)s generate --prompt "\u8f6c\u4e3a\u6c34\u5f69\u753b\u98ce\u683c" --ref-image photo.jpg --output art.png

  # \u5e26\u56fe\u5bf9\u8bdd
  %(prog)s chat --image photo.jpg --prompt "\u63cf\u8ff0\u8fd9\u5f20\u56fe\u7247\u7684\u5185\u5bb9"

  # \u7eaf\u6587\u672c\u5bf9\u8bdd
  %(prog)s chat --prompt "\u4f60\u597d\uff0c\u4ecb\u7ecd\u4e00\u4e0b\u4f60\u81ea\u5df1"

  # \u6307\u5b9a API Key
  %(prog)s generate --api-key sk-xxxxx --prompt "Sunset" --output sunset.png
        """,
    )
    parser.add_argument(
        "--api-key",
        default=None,
        help="API Key（也可通过环境变量 RIGHTCODE_API_KEY 设置）",
    )

    subparsers = parser.add_subparsers(dest="command", help="\u5b50\u547d\u4ee4")

    # === generate 子命令 ===
    gen_parser = subparsers.add_parser("generate", help="\u751f\u6210\u56fe\u7247 (\u6587\u751f\u56fe / \u56fe\u751f\u56fe)")
    gen_parser.add_argument("--prompt", "-p", required=True, help="\u56fe\u7247\u63cf\u8ff0\uff08\u82f1\u6587/\u4e2d\u6587\u5747\u53ef\uff0c\u5efa\u8bae\u8be6\u7ec6\u63cf\u8ff0\uff09")
    gen_parser.add_argument("--model", "-m", default="gpt-image-2", help="\u6a21\u578b\u540d\u79f0\uff08\u9ed8\u8ba4: gpt-image-2\uff0c\u5176\u4ed6\u5982 gpt-image-1\u3001dall-e-3 \u7b49\uff09")
    gen_parser.add_argument("--model-hd", default=None, help="HD \u6a21\u5f0f\u4e13\u5c5e\u6a21\u578b\uff08\u4f8b\u5982 gpt-image-2-hd\uff0c\u53ef\u5728\u540e\u53f0\u67e5\u770b\uff09")
    gen_parser.add_argument("--model-4k", default=None, help="4K VIP \u6a21\u5f0f\u4e13\u5c5e\u6a21\u578b\uff08\u4f8b\u5982 gemini-3-pro-image-preview\uff0c\u53ef\u5728\u540e\u53f0\u67e5\u770b\uff09")
    gen_parser.add_argument("--size", "-s", default="1024x1024", help="\u56fe\u7247\u5c3a\u5bf8\uff0c\u683c\u5f0f \u5bbdx\u9ad8\uff08\u9ed8\u8ba4: 1024x1024\uff09")
    gen_parser.add_argument("--quality", "-q", choices=["standard", "hd", "4k"], default="standard", help="\u753b\u8d28\u9884\u8bbe: standard(1024) / hd(2K 2048) / 4k(4K 4096 VIP)")
    gen_parser.add_argument("--4k", dest="flag_4k", action="store_true", default=False, help="\u5feb\u6377\u5f00\u5173\uff0c\u542f\u7528 VIP 4K \u8d85\u6e05\u8f93\u51fa\uff08\u7b49\u540c --quality 4k\uff09")
    gen_parser.add_argument("--ref-image", default=None, help="\u53c2\u8003\u56fe\u8def\u5f84\u6216 URL\uff08\u7528\u4e8e\u56fe\u751f\u56fe/\u98ce\u683c\u5f15\u5bfc\uff09")
    gen_parser.add_argument("--ref-images", nargs="*", default=[], help="\u591a\u5f20\u53c2\u8003\u56fe\u8def\u5f84")
    gen_parser.add_argument("--response-format", default="url", choices=["url", "b64_json"], help="\u54cd\u5e94\u683c\u5f0f\uff08\u9ed8\u8ba4: url\uff09")
    gen_parser.add_argument("--output", "-o", default="output.png", help="\u8f93\u51fa\u6587\u4ef6\u8def\u5f84\uff08\u9ed8\u8ba4: output.png\uff09")
    gen_parser.add_argument("--api-key", default=None, help="API Key\uff08\u4e5f\u53ef\u901a\u8fc7\u73af\u5883\u53d8\u91cf RIGHTCODE_API_KEY \u8bbe\u7f6e\uff09")

    # === chat 子命令 ===
    chat_parser = subparsers.add_parser("chat", help="\u5e26\u56fe\u5bf9\u8bdd (\u7eaf\u6587\u672c / \u591a\u6a21\u6001)")
    chat_parser.add_argument("--prompt", "-p", required=True, help="\u63d0\u95ee\u5185\u5bb9")
    chat_parser.add_argument("--image", "-i", default=None, help="\u56fe\u7247\u6587\u4ef6\u8def\u5f84\u6216 URL")
    chat_parser.add_argument("--images", nargs="*", default=[], help="\u591a\u5f20\u56fe\u7247\u6587\u4ef6\u8def\u5f84")
    chat_parser.add_argument("--model", "-m", default="gemini-3.1-pro", help="\u6a21\u578b\u540d\u79f0\uff08\u9ed8\u8ba4: gemini-3.1-pro\uff09")
    chat_parser.add_argument("--stream", action="store_true", default=False, help="\u542f\u7528 SSE \u6d41\u5f0f\u8f93\u51fa")
    chat_parser.add_argument("--api-key", default=None, help="API Key\uff08\u4e5f\u53ef\u901a\u8fc7\u73af\u5883\u53d8\u91cf RIGHTCODE_API_KEY \u8bbe\u7f6e\uff09")

    args = parser.parse_args()

    if args.command == "generate":
        cmd_generate(args)
    elif args.command == "chat":
        cmd_chat(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
