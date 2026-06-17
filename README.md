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

## 目录结构

```
ppb-skills/
└── right-code-draw/
    ├── SKILL.md          # 技能定义（触发规则、使用流程）
    ├── scripts/
    │   └── draw.py       # Python CLI 工具
    └── references/
        └── api.md        # API 完整参考文档
```
