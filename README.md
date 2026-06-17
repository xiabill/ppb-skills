# ppb-skills

WorkBuddy AI 技能包集合，涵盖绘图、文档处理、自动化等场景。

## Skills

### draw-ppb — AI 绘图

基于 [Right Code](https://www.right.codes/draw) 的图片生成与带图对话技能。

**能力：**
- 🎨 文生图 / 图生图（支持参考图风格引导）
- 📐 三档画质：standard (1024) / HD (2K) / 4K VIP (4096)
- 💬 带图对话（多模态图片理解）
- 🔄 SSE 流式输出

**安装与使用：**
```bash
cp -r draw-ppb ~/.workbuddy/skills/
export RIGHTCODE_API_KEY="sk-xxxxx"

# 文生图
python3 ~/.workbuddy/skills/draw-ppb/scripts/draw.py generate --prompt "一只可爱的小猪" --output pig.png

# 4K 超清
python3 ~/.workbuddy/skills/draw-ppb/scripts/draw.py generate --prompt "山水" --4k --output landscape.png
```

### pdf-edit-ppb — PDF 编辑与盖章

PDF/DOCX 保单字段自动替换 + AI 公章生成盖印。

**模块 A — 内容更新：**
- 🔍 自动搜索 PDF/DOCX 字段并替换
- 🎨 保持原字体、字号、颜色、位置、排版一致
- 📋 支持批量替换

**模块 B — 公章处理：**
- 🧠 自动分析文档角色关系（投保人/被保险人/受益人/甲乙方）
- 🖼️ 通过 draw-ppb API 为每个公司生成专属公章
- 📍 自动定位签章位置 + 角色→位置映射
- 🎲 随机化盖印（旋转、偏移、墨色变化）

**安装与使用：**
```bash
cp -r pdf-edit-ppb ~/.workbuddy/skills/

# 保单字段更新
"帮我把这份保单上的投保人改成张三，联系电话改成13800138000"

# 文档盖章
"帮我在这份理赔书上盖章"
```

## 目录结构

```
ppb-skills/
├── draw-ppb/
│   ├── SKILL.md
│   ├── scripts/draw.py
│   └── references/api.md
└── pdf-edit-ppb/
    └── SKILL.md
```
