# Personality Test Designer / 人格测试设计器

> Design a complete personality test in minutes — auto-generate interactive HTML preview with one click.
> 分分钟设计一套完整的人格测试方案 — 自动生成可交互的 HTML 问卷，一键启动预览服务器。

[English](#english) · [中文](#中文) · [快速开始](#快速开始-quick-start)

---

## English

### What is this?

A skill for designing **custom personality tests** on any topic. It generates:

- A complete **Markdown design document** (dimensions, questions, personality types, scoring algorithm)
- A fully **interactive HTML quiz** you can preview immediately in any browser
- A **live preview server** so you (and others on the same network) can take the test right away

### How it works

```
You say: "Design a workplace personality test"
  → Agent generates Markdown design document
  → Agent runs build_html.py → generates .html file
  → Agent runs start_server.py → preview server starts
  → You get a URL and can start taking the test instantly
```

### Features

| Feature | Description |
|---------|-------------|
| 15 dimensions | 5 categories × 3 dimensions each (Self, Emotion, Attitude, Action, Social) |
| 24 main questions | 2 questions per dimension |
| 20 standard types | MBTI-style personality archetypes |
| Radar chart | Visual profile of all 15 dimensions |
| Shuffled questions | Questions appear in random order each attempt |

### Architecture

```
personality-test-designer/
├── SKILL.md              # Skill definition & workflow guide
├── template.html         # Base HTML quiz template
├── config.env            # Server config (local only, gitignored)
├── config.env.example    # Config template
├── .gitignore
└── scripts/
    ├── build_html.py     # Generate quiz HTML from data
    └── start_server.py   # Launch HTTP preview server
```

### Configuration (config.env)

```env
# Preview server port (0 = auto-assign random port)
PREVIEW_PORT=3000

# Bind address
#   127.0.0.1 = local only
#   0.0.0.0   = accessible from LAN (fill in public IP for external access)
PREVIEW_HOST=0.0.0.0
```

### Workflow for developers

**1. Design the test** — Write the Markdown design doc (dimensions, questions, types).

**2. Generate HTML** (from your data):

```python
import subprocess, json

result = subprocess.run([
    "python3",
    "/home/ubuntu/.hermes/skills/productivity/personality-test-designer/scripts/build_html.py",
    "--test-name", "My Test",
    "--test-subtitle", "Discover yourself",
    "--data-json", json.dumps({
        "questions": [...],
        "types": [...]
    })
], capture_output=True, text=True)

html_file = result.stdout.strip().split("HTML_FILE:")[1]
```

**3. Start preview server:**

```python
result = subprocess.run([
    "python3",
    "/home/ubuntu/.hermes/skills/productivity/personality-test-designer/scripts/start_server.py",
    html_file
], capture_output=True, text=True)

url = result.stdout.strip().split("PREVIEW_URL:")[1]
```

---

## 中文

### 这是什么？

一个用于设计**自定义人格测试**的 skill。自动生成：

- 完整的 **Markdown 设计稿**（维度、题目、人格类型、评分算法）
- 完全**可交互的 HTML 问卷**，可在任何浏览器中直接作答
- **实时预览服务器**，你和同一网络的人都可以立即开始测试

### 工作流程

```
你说：设计一个职场人格测试
  → Agent 生成 Markdown 设计稿
  → Agent 运行 build_html.py → 生成 .html 文件
  → Agent 运行 start_server.py → 预览服务器启动
  → 获得 URL，立即可以开始测试
```

### 功能特性

| 功能 | 说明 |
|------|------|
| 15 个维度 | 5 大类 × 3 维度（自我、情感、态度、行动、社交） |
| 24 道主测题 | 每维度 2 题 |
| 20 种标准人格 | 类 MBTI 风格人格原型 |
| 雷达图 | 可视化展示 15 维度得分 |
| 题目乱序 | 每次作答题目顺序随机 |

### 目录结构

```
personality-test-designer/
├── SKILL.md              # Skill 定义与工作流程说明
├── template.html         # HTML 问卷模板
├── config.env            # 服务器配置（本地，gitignored）
├── config.env.example    # 配置模板
├── .gitignore
└── scripts/
    ├── build_html.py     # 从数据生成问卷 HTML
    └── start_server.py   # 启动 HTTP 预览服务器
```

### 配置说明（config.env）

```env
# 预览服务器端口（0 = 自动分配随机端口）
PREVIEW_PORT=3000

# 绑定地址
#   127.0.0.1 = 仅本机访问
#   0.0.0.0   = 局域网可访问（填公网 IP 则外网可访问）
PREVIEW_HOST=0.0.0.0
```

### API 调用示例

```python
import subprocess, json

# 1. 生成 HTML
result = subprocess.run([
    "python3",
    "/home/ubuntu/.hermes/skills/productivity/personality-test-designer/scripts/build_html.py",
    "--test-name", "测试名称",
    "--test-subtitle", "副标题",
    "--data-json", json.dumps({
        "questions": [...],    # 题目列表
        "types": [...],       # 标准人格列表

    })
], capture_output=True, text=True)

html_file = result.stdout.strip().split("HTML_FILE:")[1]

# 2. 启动服务器
result = subprocess.run([
    "python3",
    "/home/ubuntu/.hermes/skills/productivity/personality-test-designer/scripts/start_server.py",
    html_file
], capture_output=True, text=True)

url = result.stdout.strip().split("PREVIEW_URL:")[1]
print(f"Open: {url}")
```

---

## 快速开始 / Quick Start

```bash
# 克隆 skill
git clone https://github.com/youhan2021/personality-test-designer.git \
  ~/.hermes/skills/productivity/personality-test-designer

# 复制配置
cp config.env.example config.env

# 编辑配置（设置 PREVIEW_HOST 为你的公网 IP）
vim config.env
```

---

## License / 许可证

MIT
