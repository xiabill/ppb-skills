# ppb-skills

WorkBuddy AI 技能包集合，涵盖绘图、文档处理、自动化等场景。

## 已安装 Skills

### right-code-draw — Right Code 绘图 API

基于 [Right Code](https://www.right.codes/draw) 的 AI 图片生成与带图对话技能。

**能力：**
- 🎨 文生图 / 图生图（支持参考图风格引导）
- 📐 三档画质：standard (1024) / HD (2K) / 4K VIP (4096)
- 💬 带图对话（多模态图片理解）
- 🔄 SSE 流式输出

**快速使用：**
```bash
# 安装
cp -r right-code-draw ~/.workbuddy/skills/

# 设置 API Key
export RIGHTCODE_API_KEY="sk-xxxxx"

# 文生图
python3 scripts/draw.py generate --prompt "一只可爱的小猪" --output pig.png

# VIP 4K 超清
python3 scripts/draw.py generate --prompt "一幅壮丽的山水" --4k --output landscape.png

# 带图对话
python3 scripts/draw.py chat --image photo.jpg --prompt "描述这张图片"
```

### pdf-policy-field-update — PDF 保单内容更新与公章处理

保单/合同 PDF 字段自动搜索替换 + AI 公章生成盖印。

**模块 A — 内容更新：**
- 🔍 自动搜索 PDF/DOCX 保单字段并替换
- 🎨 保持原字体、字号、颜色、位置、排版一致
- 📋 支持批量替换、一对一/一对多映射
- ✅ 视觉 QA 流程（高倍局部裁剪复核）

**模块 B — 公章处理：**
- 🧠 自动分析文档角色关系（投保人/被保险人/受益人/甲乙方）
- 🖼️ 通过 right-code-draw API 为每个公司生成专属公章
- 📍 自动定位签章位置 + 角色→位置映射
- 🎲 随机化盖印（旋转 ±20°、偏移、墨色变化、羽化边缘）

**快速使用：**
```bash
# 安装
cp -r pdf-policy-field-update ~/.workbuddy/skills/

# 保单字段更新
"帮我把这份保单上的投保人改成张三，联系电话改成13800138000"
# → 自动搜索→替换→保持排版→生成新PDF

# 文档盖章
"帮我在这份理赔书上盖章"
# → 自动分析关系→生成公章→定位→盖印→输出PDF
```

## 目录结构

```
ppb-skills/
├── right-code-draw/
│   ├── SKILL.md
│   ├── scripts/draw.py
│   └── references/api.md
└── pdf-policy-field-update/
    └── SKILL.md          # 模块 A（内容更新）+ 模块 B（公章处理）
```
