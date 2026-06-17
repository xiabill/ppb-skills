---
name: pdf-edit-ppb
description: 通用 PDF/DOCX 内容更新与公章处理。自动搜索替换字段（保持排版、字体一致）+ AI 生成公章盖印到文档。Trigger phrases: 保单修改, 替换字段, PDF编辑, 盖章, 加公章, 文档修改, 批单, pdf edit, stamp, seal。
version: 3.0.0
author: Hermes Agent + OpenClaw
license: MIT
metadata:
  hermes:
    tags: [PDF, 保单, 文档修改, 自动搜索替换, PyMuPDF, 版式保持, 字体一致, 公章, 盖章, stamp]
---

# 通用 PDF 内容更新与公章处理

本技能由两个独立模块组成：

- **模块 A（内容更新）**：处理 PDF/DOCX 中的任意小范围内容更新——替换字段、修改文本、保持字体排版
- **模块 B（公章处理）**：自动分析文档各方关系、生成对应公章、定位签章位、随机化盖印、输出高清扫描件 PDF

两个模块可独立使用，也可组合使用（如先改内容再加章）。

---

# 模块 A：内容更新

用于处理**用户自有或明确授权处理的本地 PDF 保单/批改单/附件**中的任意小范围内容更新需求。支持：

- 投保人 / 被保险人 / 飞手 / 操作员 / 驾驶员信息
- 保单号、地址、用途、联系方式、证件号、日期、金额等指定字段
- 用户明确指出的任意原文 -> 新文 替换
- 自动搜索、自动定位、自动生成新 PDF
- 尽量保持原文件中的字体、字号、颜色、位置和排版风格一致

> 仅用于用户拥有或明确授权处理的文件。不要把输出表述为保险公司重新签发的官方原件；如用户需要正式法律效力文件，应建议其联系承保方出具正式批单或更正件。

## 适用触发词

当用户说类似：
- "这份保单帮我改一下内容"
- "把保单上的某些资料替换掉"
- "自动搜索并替换这些字段"
- "帮我把保单里的信息更新一下，生成新的 PDF"
- "尽量保证字体和排版一致"

都应触发模块 A。

## 自动触发规则（基于上传文件识别）

当用户上传文件时，应先自动识别文件类型与用途。

如果满足以下任一信号，应优先判断为保单/保险相关文件，并自动触发本技能：
- 文件名包含：保单、保险单、电子保单、批单、保险、policy、endorsement
- PDF 正文包含：投保人、被保险人、保险人、保单号、保险期间、保险费、特别约定、承保公司、批单
- 页面标题或显著区域包含：保险单、电子保险单、Insurance Policy、批单
- 文档整体结构呈现典型保单版式：字段表格 + 条款 + 保单号 + 保险公司信息

### 上传文件后的默认流程
1. 先识别文件类型（PDF / 图片 / Word / 其他）
2. 提取文件名与正文前几页的关键信息
3. 判断是否属于保单/批单/保险附件
   - 如果是保单，直接加载搜索替换流程
   - 默认支持批量替换多个字段
   - 如果不是保单，再根据文件类型走其他常规文档流程

## 用户需求目标（核心要求）

此模块默认满足以下 3 点：

### 1. 自动搜索与替换
当用户指定要修改保单上的某些资料时：自动搜索 → 定位 → 替换。

### 2. 自动生成文件
替换完成后：另存为新文件 → 保留原文件 → 默认直接发送给用户。

### 3. 字体一致性
尽量保证字体风格、字号、粗细、位置、对齐方式接近原文。

## 输入形式

### 形式 A：直接给原文和新文
### 形式 B：给字段名和值
### 形式 C：一次给多组替换
### 形式 D：批量替换列表（推荐）

```python
replacements = [
  {"field": "投保人", "old": "张三", "new": "李四"},
  {"field": "被保人", "old": "张三", "new": "李四"},
  {"field": "联系电话", "new": "13800138000"},
]
```

## 优先策略
1. 精确原文替换优先
2. 字段定位替换次之
3. 多轮确认仅在必要时使用

## 标准工作流

### 第 1 步：读取并初步识别文档
用 PyMuPDF 获取页数、判断是否可搜索文本。

### 第 1.5 步：自动识别保单所用字体（默认必做）
读取目标字段附近 span 的 font/size/flags/color，汇总字体名，检查本机字体匹配情况，向用户汇报字体预检结果。

### 第 2 步：标准化替换任务
### 第 3 步：全局搜索命中
### 第 4 步：提取原始样式（bbox/size/font/flags/color）
### 第 5 步：决定替换方式

#### 方案 A：直接文本覆盖（英文/数字/简单短文本）
#### 方案 B：透明文字图覆盖（默认首选，中文保单更稳）
1. 红框擦除旧内容
2. Pillow 生成透明 PNG 文字图
3. `insert_image()` 精确覆盖回 PDF

## 自动搜索与替换规则
1. 优先精确匹配
2. 支持一对多替换
3. 避免误伤公共文本
4. 按上下文过滤

## 字体一致性策略
1. 优先继承原 span 参数
2. 字体映射（macOS：Songti.ttc / STHeiti / Arial Bold / Arial Unicode）
3. 中文优先走 PNG 覆盖，不依赖 insert_text
4. 分段处理混排字段（中文+数字分别渲染）
5. 小 bbox 中文字段不要死守原字号，预计算宽度后自动缩放
6. 视觉 QA 发现字号偏大时：先缩小字号 → 分段处理 → 收窄覆盖区 → 再次 QA

## 视觉 QA 流程
1. 渲染目标页为 PNG
2. 整页检查字段更新、完整性、位置、排版
3. **高倍局部裁剪 QA**（8x~12x）：每个字段单独裁剪，检查下半部截断、末字裁掉、旧字残影
4. QA 结论必须可说明、可复核

## 回退策略
保留原文件、当前可用版、试验版。若新版本更差则回退。

## 批量替换规则
1. 标准化为统一任务列表
2. 先搜索后统一替换
3. 同页先独立字段，同行优先整体替换
4. 每批做总体验收

## 推荐执行顺序
1. 读取 PDF
2. 标准化任务列表
3. 全局搜索
4. 收集命中信息
5. 检查冲突
6. 提取样式
7. 执行替换
8. 生成 PDF
9. 渲染预览
10. vision QA
11. 回退机制
12. 交付

## 常见坑
- 不要只改封面
- 不要盲目全局替换
- 不要只靠文本搜索做验收
- 不要覆盖唯一可用版本
- 中文优先 PNG 覆盖

## 验收标准
每个字段已处理、新 PDF 正常可用、视觉上已更新、字体排版接近原文。

---

# 模块 B：公章处理

用于在理赔书、保单、合同、协议等文档上自动加盖中国公章。

## 适用触发词

当用户说类似：
- "帮我在文件上加章"
- "这份文件需要盖章"
- "盖公章"
- "生成公章盖上去"
- "文档盖章"

都应触发模块 B。

## 场景
- 保险理赔书、保单、合同、协议等文档
- 支持一文档多公司公章
- 支持任意数量签章位置
- **自动分析文档各方角色关系，匹配正确公章**

## 依赖

```bash
sudo apt-get install -y poppler-utils
pip install Pillow numpy scipy weasyprint python-docx pdfplumber
```

## 依赖技能

本模块公章生成依赖 **draw-ppb** skill（位于 `skills/draw-ppb/`），通过 `https://www.right.codes/draw/v1/images/generations` 接口生成公章图片。

### Right Code Draw API 配置

- **Endpoint**: `https://www.right.codes/draw/v1/images/generations`
- **Auth**: `Authorization: Bearer <RIGHTCODE_API_KEY>`
- **Key 获取方式**: 环境变量 `RIGHTCODE_API_KEY` 或用户手动提供
- **默认模型**: `gpt-image-2`
- **输出尺寸**: `1024x1024`

详细用法见 `skills/draw-ppb/SKILL.md`。

## 完整工作流

```
输入文档 (DOCX/PDF/HTML)
    ↓
[1. 文档关系分析] ←── 关键：自动提取各方角色和公司名
    ↓
[2. 公章生成] ← 调用 draw-ppb API 为每个角色生成公章
    ↓
[3. 公章标准化] ← 等径对齐 + 透明化
    ↓
[4. 文档渲染] ← 转为 300DPI 图
    ↓
[5. 签章定位] ← 自动检测签章文字位置
    ↓
[6. 角色→位置映射] ← 谁该盖在哪里
    ↓
[7. 随机化盖印] ← 真实感处理（旋转、偏移、墨色变化）
    ↓
[8. 输出 PDF]
```

---

### Step 1：文档关系分析 🧠

这是整个流程的大脑。在生成公章前，必须完整解析文档，理解各方的**角色和关系**。

#### 提取全文文本

```python
# DOCX
import docx
doc = docx.Document("input.docx")
full_text = "\n".join([p.text for p in doc.paragraphs])
for table in doc.tables:
    for row in table.rows:
        for cell in row.cells:
            full_text += "\n" + cell.text

# PDF
import pdfplumber
with pdfplumber.open("input.pdf") as pdf:
    full_text = "\n".join([p.extract_text() or "" for p in pdf.pages])
```

#### 角色提取

```python
import re
def extract_parties(full_text):
    parties = {}
    patterns = [
        (r"(?<=被保险人[：:])\s*([^\s]{2,30}?(?:有限公司|股份公司|集团|厂|社))", "被保险人"),
        (r"(?<=受益人[：:])\s*([^\s]{2,30}?(?:有限公司|股份公司|集团|厂|社))", "受益人"),
        (r"(?<=投保人[：:])\s*([^\s]{2,30}?(?:有限公司|股份公司|集团|厂|社))", "投保人"),
        (r"(?<=甲方[：:])\s*([^\s]{2,30}?(?:有限公司|股份公司|集团|厂|社))", "甲方"),
        (r"(?<=乙方[：:])\s*([^\s]{2,30}?(?:有限公司|股份公司|集团|厂|社))", "乙方"),
        (r"(?<=开户户名[：:])\s*([^\s]{2,30}?(?:有限公司|股份公司|集团|厂|社))", "受益人账户"),
    ]
    for pattern, role in patterns:
        match = re.search(pattern, full_text)
        if match:
            parties[role] = match.group(1).strip()
    if "受益人" not in parties and "受益人账户" in parties:
        parties["受益人"] = parties["受益人账户"]
    return parties
```

#### 签章点 → 角色映射

```python
def map_sign_positions_to_parties(sign_texts, parties):
    mapping = []
    for label in sign_texts:
        if "被保险人" in label and "受益" not in label:
            company = parties.get("被保险人") or parties.get("投保人")
        elif "受益人" in label:
            company = parties.get("受益人")
        elif "甲方" in label:
            company = parties.get("甲方")
        elif "乙方" in label:
            company = parties.get("乙方")
        elif "投保人" in label:
            company = parties.get("投保人")
        else:
            company = parties.get("被保险人")
        mapping.append((label, company))
    return mapping
```

#### 常见文档类型角色关系

| 文档类型 | 常见签章点 | 角色关系 |
|----------|-----------|----------|
| 理赔书 | 被保险人（代表）签章 ×2 + 被保险人签章确认 + 受益人签章确认 | 被保险人=出险方，受益人=收款方 |
| 保单 | 投保人签章 + 被保险人签章 | 投保人=买保险的人，被保险人=被保障的人 |
| 合同 | 甲方签章 + 乙方签章 | 任意两家公司 |
| 协议 | 甲方签章 + 乙方签章 + 丙方签章 | 三方协议 |
| 声明书 | 声明人签章 | 单一公司 |

#### 完整分析函数

```python
def analyze_document_relationships(full_text):
    parties = extract_parties(full_text)
    sign_labels = []
    for keyword in ["被保险人（代表）签章", "被保险人签章确认",
                     "受益人签章确认", "投保人签章", "甲方签章", "乙方签章",
                     "签章确认", "签章"]:
        if keyword in full_text:
            count = full_text.count(keyword)
            sign_labels.extend([keyword] * count if count > 1 else [keyword])
    seen = set()
    unique_labels = []
    for label in sign_labels:
        if label not in seen or label.count("）") > 1:
            unique_labels.append(label)
            seen.add(label)
    seal_assignments = map_sign_positions_to_parties(unique_labels, parties)
    return {
        "parties": parties,
        "sign_labels": unique_labels,
        "assignments": seal_assignments,
        "unique_companies": list(set(c for _, c in seal_assignments if c))
    }
```

---

### Step 2：公章生成（通过 draw-ppb API）

**每个公司分别调用一次 API，不要用一个 prompt 生成全文档。**

调用 `https://www.right.codes/draw/v1/images/generations` 接口，使用 `gpt-image-2` 模型生成公章图。

```python
import os
import json
import urllib.request

def generate_seal(company_name):
    """通过 Right Code Draw API 生成单个公司公章，返回下载的图片路径。"""
    api_key = os.environ.get("RIGHTCODE_API_KEY")
    if not api_key:
        raise ValueError("未设置 RIGHTCODE_API_KEY 环境变量")

    prompt = (f"Chinese official company seal stamp, macro photography. "
              f"Circular red stamp on white paper. "
              f"Outer ring text curved around circle reads: {company_name}. "
              f"Inner center has a five-pointed star. "
              f"Clear bold Chinese characters using standard seal font. "
              f"Deep vermillion red ink. The stamp impression is slightly "
              f"imperfect at edges. High detail, sharp text. "
              f"1024x1024. Clean white background.")

    payload = {
        "model": "gpt-image-2",
        "prompt": prompt,
        "size": "1024x1024",
        "response_format": "url"
    }

    req = urllib.request.Request(
        "https://www.right.codes/draw/v1/images/generations",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))

    image_url = result["data"][0]["url"]

    # 下载并保存图片
    import requests
    resp = requests.get(image_url, timeout=60)
    out_path = f"/tmp/seal_{company_name}.png"
    with open(out_path, "wb") as f:
        f.write(resp.content)
    return out_path
```

**如果不想直接用 urllib**，也可使用 `skills/draw-ppb/scripts/draw.py` CLI 工具：

```bash
export RIGHTCODE_API_KEY="sk-xxxxx"
python3 skills/draw-ppb/scripts/draw.py generate \
  --prompt "Chinese official company seal stamp..." \
  --size 1024x1024 \
  --output /tmp/seal_公司名.png
```

---

### Step 3：公章标准化处理

将 API 生成的白底红章转为 RGBA 带透明的标准图，并确保所有公章外径一致。

```python
from scipy.ndimage import binary_erosion, binary_dilation, gaussian_filter
from PIL import Image
import numpy as np

TARGET_DIAMETER_PX = 380

def seal_to_rgba(path, target_px=TARGET_DIAMETER_PX):
    raw = Image.open(path).convert('RGB')
    r, g, b = [np.array(c, dtype=np.float32) for c in raw.split()]
    mask = ((r - np.maximum(g, b)) > 30) & (r > 80) & ((r+g+b)/3 > 40)
    mask = binary_dilation(binary_erosion(mask, iterations=3), iterations=5)
    rows, cols = np.where(mask.any(axis=1))[0], np.where(mask.any(axis=0))[0]
    orig_diam = max(cols[-1]-cols[0], rows[-1]-rows[0]) if len(rows) > 0 else raw.size[0]
    new_sz = int(raw.size[0] * target_px / orig_diam)
    img = raw.resize((new_sz, new_sz), Image.LANCZOS)
    r, g, b = [np.array(c, dtype=np.float32) for c in img.split()]
    mask = ((r - np.maximum(g, b)) > 30) & (r > 80) & ((r+g+b)/3 > 40)
    mask = binary_dilation(binary_erosion(mask, iterations=2), iterations=3)
    alpha = np.clip(gaussian_filter(mask.astype(np.float32), sigma=0.8) * 255, 0, 255).astype(np.uint8)
    rgba = np.zeros((new_sz, new_sz, 4), dtype=np.uint8)
    rgba[:,:,0] = np.clip(r * 1.1, 0, 255).astype(np.uint8)
    rgba[:,:,1] = np.clip(g * 0.5, 0, 255).astype(np.uint8)
    rgba[:,:,2] = np.clip(b * 0.5, 0, 255).astype(np.uint8)
    rgba[:,:,3] = alpha
    return Image.fromarray(rgba, 'RGBA')
```

---

### Step 4：文档渲染为 300DPI 图像

```python
from weasyprint import HTML
HTML(string=html_content).write_pdf("/tmp/doc.pdf")
import subprocess
subprocess.run(["pdftoppm", "-png", "-r", "300", "-singlefile", "/tmp/doc.pdf", "/tmp/doc_page"])
doc = Image.open("/tmp/doc_page.png")
```

---

### Step 5：自动定位签章位置

```python
def find_sign_positions(doc_img, dpi=300):
    np_gray = np.array(doc_img.convert('L'))
    positions = []
    keywords = ["被保险人（代表）签章", "被保险人签章确认",
                "受益人签章确认", "投保人签章", "甲方签章", "乙方签章"]
    for keyword_prefix in keywords:
        for y in range(0, np_gray.shape[0]):
            row = np_gray[y, 200:600]
            if (row < 150).sum() > 20:
                dark_pixels = np.where(row < 150)[0]
                if len(dark_pixels) > 0:
                    gaps = np.diff(dark_pixels)
                    big_gaps = np.where(gaps > 15)[0]
                    if len(big_gaps) >= 1:
                        blank_center_x = (dark_pixels[big_gaps[0]] + dark_pixels[big_gaps[0]+1]) // 2 + 200
                        positions.append((blank_center_x, y, keyword_prefix))
                    break
    return positions
```

---

### Step 6：角色→位置自动映射

```python
def auto_assign_seals(relationships, positions):
    label_to_company = {}
    for label, company in relationships["assignments"]:
        label_to_company[label] = company
    result = []
    for x, y, text_label in positions:
        for assigned_label, company in relationships["assignments"]:
            if assigned_label in text_label:
                result.append({"x": x, "y": y, "company": company, "label": text_label})
                break
    return result
```

---

### Step 7：盖印（随机化合成）

```python
import random

def apply_stamps(doc, seal_positions, seals_map,
                 rotation_range=20, offset_x_range=50, offset_y_range=40,
                 opacity_range=(0.75, 1.0)):
    random.seed(42)
    for i, pos in enumerate(seal_positions):
        cx, cy = pos["x"], pos["y"]
        seal = seals_map[pos["company"]]
        seed = [7, 13, 19, 31, 47][i % 5]
        random.seed(seed)
        np.random.seed(seed)
        angle = random.uniform(-rotation_range, rotation_range)
        seal_r = seal.rotate(angle, expand=False, fillcolor=(0,0,0,0), resample=Image.BICUBIC)
        snp = np.array(seal_r).astype(np.float32)
        snp[:,:,3] *= random.uniform(*opacity_range)
        h, w = snp.shape[:2]
        gx = np.linspace(random.uniform(0.85, 1.0), random.uniform(0.85, 1.0), w)
        gy = np.linspace(random.uniform(0.85, 1.0), random.uniform(0.85, 1.0), h)
        snp[:,:,3] = (snp[:,:,3].astype(np.float32) * np.outer(gy, gx)).clip(0,255).astype(np.uint8)
        snp[:,:,0] = np.clip(snp[:,:,0] * random.uniform(0.9, 1.1), 100, 255)
        seal_r = Image.fromarray(snp.astype(np.uint8), 'RGBA')
        sz = seal_r.size[0]
        ox, oy = random.randint(-offset_x_range, offset_x_range), random.randint(-offset_y_range, offset_y_range)
        px, py = cx - sz//2 + ox, cy - sz//2 + oy
        doc.paste(seal_r, (px, py), seal_r)
    return doc
```

---

### Step 8：输出 PDF

```python
doc.convert('RGB').save(output_path, "PDF", resolution=300)
```

---

### 一键自动化流程

```python
def auto_stamp_document(input_path, output_path):
    # 1. 提取全文
    if input_path.endswith('.docx'):
        doc_obj = docx.Document(input_path)
        full_text = "\n".join([p.text for p in doc_obj.paragraphs] +
                             [cell.text for t in doc_obj.tables for r in t.rows for c in r.cells])
    elif input_path.endswith('.pdf'):
        with pdfplumber.open(input_path) as pdf:
            full_text = "\n".join([p.extract_text() or "" for p in pdf.pages])
    else:
        full_text = open(input_path, encoding='utf-8').read()
    # 2. 分析关系
    rel = analyze_document_relationships(full_text)
    print(f"检测到各方: {rel['parties']}")
    print(f"签章分配: {rel['assignments']}")
    # 3. 生成公章（通过 draw-ppb API）
    seal_images = {}
    for company in rel["unique_companies"]:
        if not os.path.exists(f"/tmp/seal_{company}.png"):
            seal_path = generate_seal(company)
        else:
            seal_path = f"/tmp/seal_{company}.png"
        seal_images[company] = seal_to_rgba(seal_path)
    # 4. 渲染文档
    doc_img = render_document(input_path)
    # 5. 定位
    positions = find_sign_positions(doc_img)
    # 6. 映射
    assignments = auto_assign_seals(rel, positions)
    # 7. 盖印
    doc_img = apply_stamps(doc_img, assignments, seal_images)
    # 8. 输出
    doc_img.save(output_path, "PDF", resolution=300)
    print(f"✅ 完成: {output_path}")
```

## 模块 B 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 公章文字模糊 | API 输出压缩 | 使用更高画质模型或参数 |
| 公章大小不一致 | 不同图外径不同 | `seal_to_rgba()` 自动等比例缩放 |
| 背景噪点 | alpha 提取门槛太低 | 先腐蚀后膨胀 + sigma≤0.8 |
| 章盖错位置 | 没分析文档角色关系 | 先做文档关系分析 |
| 章的公司不对 | 没读账户信息区域 | 从开户户名反推受益人 |
| 盖得太整齐 | 无随机化 | rotation±20°+offset±50px+ink variance |
| 像贴上去的 | alpha 边缘太锐利 | sigma=0.8 轻羽化 |
| API Key 缺失 | 未设置环境变量 | 设置 RIGHTCODE_API_KEY=sk-xxxxx |

## 配置示例

```python
config = {
    "document_path": "理赔书.docx",
    "output_path": "output.pdf",
    "dpi": 300,
    "target_stamp_diameter_px": 380,
    "auto_analyze": True,
    "stamp_randomness": {
        "rotation_degrees": 20,
        "offset_x_px": 50,
        "offset_y_px": 40,
        "opacity_range": (0.75, 1.0),
        "ink_gradient": (0.85, 1.0),
        "color_variation": 0.1,
    },
}
```

---

# 组合使用场景

两个模块可组合使用：

1. **先改内容，再加章**：先用模块 A 修改保单/合同上的字段信息，再用模块 B 加盖公章
2. **只加章不改内容**：直接走模块 B
3. **只改内容不加章**：直接走模块 A

判断依据：如果用户同时提到修改内容和盖章，优先先执行内容修改，再在新生成的 PDF 上盖章。
