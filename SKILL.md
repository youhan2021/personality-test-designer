---
name: personality-test-designer
description: 根据给定主题，设计一个完整的人格测试方案，输出 Markdown 设计稿，并自动生成可交互 HTML 预览
trigger: "设计.*人格测试|创建.*测试题目|仿造SBTI|设计一个新的性格测试|设计一个.*人格测试"
---

# personality-test-designer

根据给定主题，设计一个完整的人格测试方案，包含题目、人格类型、评分算法，并自动生成可交互 HTML 预览。

## 工作流程

```
用户说"设计一个 XX 人格测试"
  → 生成 Markdown 设计稿
  → 生成可交互 HTML 问卷
  → 启动预览服务器
  → 返回预览 URL
```

## 第一步：设计测试方案

### 输入

用户只需提供一个主题方向，例如：
- "设计一个关于职场的人格测试"
- "设计一个单身狗专属的人格测试"
- "设计一个二次元主题的性格测试"

### 维度设计（12个维度 × 2题 = 24道主测）

```
S(自我):   S1-自我认知, S2-内在驱动, S3-上进心
E(情感):   E1-信任感,   E2-投入度,    E3-独立/依赖
A(态度):   A1-善恶观,   A2-行动风格,  A3-目标感
Ac(行动):  Ac1-冒险/保守, Ac2-果断/犹豫, Ac3-计划性
So(社交):  So1-线下社交, So2-亲密度,  So3-自我呈现
```

每道题格式：
```python
{"id":"q1", "dim":"S1", "text":"题目文字", "options":[
    {"label":"A选项", "value":3},
    {"label":"B选项", "value":2},
    {"label":"C选项", "value":1}
]}
```

### 人格类型（20标准 + 2隐藏）

- **隐藏人格 HHHH**：24题全部选A，触发"卷王之王"
- **隐藏人格 DRUNK**：24题全部选C，触发"摆烂仙人"

### Markdown 输出格式

```
# [测试名称] 人格测试设计稿

## 1. 测试概述
## 2. 维度定义（12个）
## 3. 完整题目清单（24道）
## 4. 人格类型完整列表（20种，不含隐藏人格）
## 5. 评分算法

**隐藏人格检测**（硬编码，无需在 JSON 中传递）：
- 全选 A（所有题 value=3，最高分）→ DRUNK「卷王之王」
- 全选 C（所有题 value=1，最低分）→ HHHH「摆烂仙人」

检测与题目顺序无关，只检查所有答案是否相同。
```

### 关键约束

- 题目要有"冒犯但有趣"的风格，类似 SBTI
- 人格类型名称要有梗，一眼能记住
- 输出语言与用户主题一致（中文主题输出中文）

---

## 第二步：生成 HTML 问卷

设计稿完成后，立即调用 Python 脚本生成 HTML：

```bash
python3 ~/.hermes/skills/productivity/personality-test-designer/scripts/build_html.py \
    --test-name "测试名称" \
    --test-subtitle "副标题" \
    --data-json '{"questions":[...], "types":[...]}'
```

脚本会：
1. 从 `template.html` 读取模板
2. 将题目数据、人格数据嵌入 JS
3. 输出 HTML 文件到 `/home/ubuntu/.hermes/preview/问卷_{名称}_{时间戳}.html`
4. 打印 `HTML_FILE:<path>`

**数据格式（JSON）**：

```json
{
  "questions": [
    {"id":"q1", "dim":"S1", "text":"...", "options":[{"label":"A","value":3},{"label":"B","value":2},{"label":"C","value":1}]}
  ],
  "types": [
    {"code":"ENFP", "cn":"二次元交际花", "pattern":"HHH-HHH-HHH-HHH-HHH", "intro":"一句话", "desc":"详细描述"}
  ]
}
```

**注意**：由于 JSON 中含中文，命令行传参时需确保 JSON 正确转义。推荐使用 Python 直接调用脚本函数而非 shell。

---

## 第三步：启动预览服务器

HTML 生成后，立即启动服务器：

```bash
python3 ~/.hermes/skills/productivity/personality-test-designer/scripts/start_server.py \
    /home/ubuntu/.hermes/preview/问卷_xxx.html
```

脚本会：
1. 读取 `config.env` 获得端口和绑定地址
2. 启动 HTTP 服务器
3. 打印 `PREVIEW_URL:http://host:port/filename`

**配置文件 `config.env`**：

```env
# 端口（0 = 自动分配随机端口）
PREVIEW_PORT=3000

# 绑定地址
#   127.0.0.1 = 仅本机访问
#   0.0.0.0   = 局域网可访问（填公网 IP 则外网可访问）
PREVIEW_HOST=0.0.0.0
```

---

## 第四步：返回结果

向用户返回：
1. Markdown 设计稿（完整内容）
2. 预览 URL（格式：`http://{PREVIEW_HOST}:{PREVIEW_PORT}/问卷_xxx.html`）
3. 提示：手机/局域网设备可直接访问，刷新页面可重新作答

---

## 目录结构

```
personality-test-designer/
├── SKILL.md              # 本文件
├── template.html         # HTML 问卷模板
├── config.env            # 服务器配置（gitignored）
├── config.env.example    # 配置模板
├── .gitignore
└── scripts/
    ├── build_html.py       # HTML 生成脚本
    └── start_server.py   # 服务器启动脚本
```

## 注意事项

- 服务器在后台 daemon 线程运行，永久有效（直到进程结束）
- 每次新设计会生成新的 HTML 文件，旧文件保留在 `/home/ubuntu/.hermes/preview/`
- `execute_code` 环境无法绑定非本机地址，需通过终端 `nohup` 启动服务器以支持外网访问
