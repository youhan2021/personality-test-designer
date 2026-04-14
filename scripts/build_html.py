#!/usr/bin/env python3
"""
generate_html.py — 生成可交互的人格测试 HTML 问卷

用法（两种模式）：
  1. 直接传 JSON 数据：
       python3 generate_html.py --test-name "二次元人格诊断" \
                                --test-subtitle "探索你在 ACG 世界里的真实人格画像" \
                                --data-json '{"questions":[...], "types":[...], "special_types":[...]}'

  2. 从 stdin 接收 Python 格式数据（skill 调用）：
       python3 generate_html.py --stdin
       数据格式见下方 STDIN_SCHEMA

输出：
  - HTML 文件路径到 stdout
  - 打印 HTML_FILE:<path>
"""

import argparse
import json
import pathlib
import sys
import time

# ── 常量 ────────────────────────────────────────────────────────────
SKILL_DIR = pathlib.Path(__file__).parent
TEMPLATE_FILE = SKILL_DIR / "template.html"
OUT_DIR = pathlib.Path("/home/ubuntu/.hermes/preview")
OUT_DIR.mkdir(exist_ok=True)

# 维度顺序和中文名（15维）
DIM_ORDER = ["S1","S2","S3","E1","E2","E3","A1","A2","A3","Ac1","Ac2","Ac3","So1","So2","So3"]
DIM_LABELS = {
    "S1":"自我认知","S2":"内在驱动","S3":"上进心",
    "E1":"信任感","E2":"投入度","E3":"独立/依赖",
    "A1":"善恶观","A2":"行动风格","A3":"目标感",
    "Ac1":"冒险/保守","Ac2":"果断/犹豫","Ac3":"计划性",
    "So1":"线下社交","So2":"亲密度","So3":"自我呈现"
}

# ── HTML 生成器 ─────────────────────────────────────────────────────
def generate_html(test_name, test_subtitle, questions, types, special_types):
    """
    questions: list of {id, dim, text, options: [{label, value}]}
    types:     list of {code, cn, pattern, intro, desc}
    special_types: list of {code, cn, intro, desc}
    """

    # 如果直接传了数据，用内嵌数据模式（不走模板替换）
    html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{test_name} · 人格测试</title>
  <style>
    :root {{
      --primary: #6c5ce7;
      --primary-dark: #5a4bd1;
      --bg: #0f0f1a;
      --card: #1a1a2e;
      --text: #e0e0e0;
      --text-dim: #888;
      --accent: #00cec9;
      --danger: #e17055;
      --success: #00b894;
      --radius: 16px;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: 'PingFang SC', 'Microsoft YaHei', sans-serif;
      background: var(--bg);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
      align-items: center;
      padding: 20px;
    }}
    .progress-wrap {{ width: 100%; max-width: 600px; margin-bottom: 30px; }}
    .progress-bar {{ width: 100%; height: 6px; background: #333; border-radius: 99px; overflow: hidden; }}
    .progress-fill {{ height: 100%; background: linear-gradient(90deg, var(--primary), var(--accent)); transition: width 0.4s ease; width: 0%; }}
    .progress-text {{ text-align: right; font-size: 13px; color: var(--text-dim); margin-top: 6px; }}
    .card {{ background: var(--card); border-radius: var(--radius); padding: 32px 28px; width: 100%; max-width: 600px; box-shadow: 0 8px 32px rgba(0,0,0,0.4); }}
    .start-screen h1 {{ font-size: 28px; margin-bottom: 12px; background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .start-screen .subtitle {{ color: var(--text-dim); font-size: 15px; line-height: 1.7; margin-bottom: 28px; }}
    .start-screen .tags {{ display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 32px; }}
    .tag {{ background: rgba(108,92,231,0.15); color: var(--accent); border-radius: 99px; padding: 4px 14px; font-size: 12px; border: 1px solid rgba(108,92,231,0.3); }}
    .question-text {{ font-size: 18px; line-height: 1.7; margin-bottom: 28px; color: var(--text); }}
    .options {{ display: flex; flex-direction: column; gap: 12px; }}
    .opt-btn {{ background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.1); border-radius: 12px; padding: 16px 20px; text-align: left; font-size: 16px; color: var(--text); cursor: pointer; transition: all 0.2s; position: relative; }}
    .opt-btn:hover {{ background: rgba(108,92,231,0.2); border-color: var(--primary); transform: translateX(4px); }}
    .opt-btn:active {{ transform: scale(0.98); }}
    .opt-label {{ display: inline-block; width: 28px; height: 28px; background: var(--primary); border-radius: 50%; text-align: center; line-height: 28px; font-size: 14px; font-weight: bold; margin-right: 12px; vertical-align: middle; }}
    .result-screen {{ text-align: center; }}
    .result-label {{ font-size: 13px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 3px; margin-bottom: 8px; }}
    .result-code {{ font-size: 48px; font-weight: 900; background: linear-gradient(135deg, var(--primary), var(--accent)); -webkit-background-clip: text; -webkit-text-fill-color: transparent; margin-bottom: 4px; }}
    .result-name {{ font-size: 26px; margin-bottom: 8px; }}
    .result-intro {{ color: var(--accent); font-size: 15px; margin-bottom: 28px; }}
    .result-desc {{ color: var(--text-dim); font-size: 14px; line-height: 1.8; text-align: left; margin-bottom: 28px; max-height: 200px; overflow-y: auto; padding: 16px; background: rgba(255,255,255,0.03); border-radius: 12px; }}
    .result-rank {{ text-align: left; margin-bottom: 24px; }}
    .result-rank h3 {{ font-size: 13px; color: var(--text-dim); text-transform: uppercase; letter-spacing: 2px; margin-bottom: 12px; }}
    .rank-item {{ display: flex; align-items: center; padding: 10px 14px; border-radius: 10px; margin-bottom: 8px; background: rgba(255,255,255,0.03); font-size: 14px; }}
    .rank-item .num {{ width: 24px; height: 24px; background: var(--primary); border-radius: 50%; text-align: center; line-height: 24px; font-size: 12px; margin-right: 12px; flex-shrink: 0; }}
    .rank-item .rname {{ flex: 1; }}
    .rank-item .rdist {{ color: var(--text-dim); font-size: 12px; margin-left: 12px; }}
    .chart-wrap {{ margin: 0 auto 24px; }}
    canvas#radar {{ display: block; margin: 0 auto; }}
    .restart-btn {{ background: var(--primary); color: #fff; border: none; border-radius: 99px; padding: 14px 36px; font-size: 16px; cursor: pointer; transition: background 0.2s; }}
    .restart-btn:hover {{ background: var(--primary-dark); }}
    .hidden {{ display: none !important; }}
    .special-hint {{ background: rgba(225,112,85,0.15); border: 1px solid rgba(225,112,85,0.3); border-radius: 10px; padding: 12px 16px; font-size: 13px; color: var(--danger); margin-bottom: 20px; text-align: center; }}
  </style>
</head>
<body>

<div class="progress-wrap hidden" id="progress-wrap">
  <div class="progress-bar"><div class="progress-fill" id="progress-fill"></div></div>
  <div class="progress-text" id="progress-text">0 / 0</div>
</div>

<div class="card start-screen" id="start-screen">
  <h1>{test_name}</h1>
  <p class="subtitle">{test_subtitle}</p>
  <div class="tags">
    <span class="tag">{len(questions)} 道题</span>
    <span class="tag">{len(types)} 种人格</span>
    <span class="tag">{len(special_types)} 个隐藏人格</span>
  </div>
  <button class="restart-btn" onclick="startQuiz()" style="width:100%;">开始测试 →</button>
</div>

<div class="card hidden" id="question-screen">
  <div class="special-hint hidden" id="special-hint"></div>
  <p class="question-text" id="q-text">题目加载中...</p>
  <div class="options" id="options"></div>
</div>

<div class="card result-screen hidden" id="result-screen">
  <p class="result-label">你的性格是</p>
  <div class="result-code" id="r-code">???</div>
  <div class="result-name" id="r-name">加载中...</div>
  <div class="result-intro" id="r-intro"></div>
  <div class="chart-wrap"><canvas id="radar" width="280" height="280"></canvas></div>
  <div class="result-desc" id="r-desc"></div>
  <div class="result-rank" id="r-rank">
    <h3>人格匹配排行榜</h3>
    <div id="rank-list"></div>
  </div>
  <button class="restart-btn" onclick="restart()">重新测试 ↻</button>
</div>

<script>
const DIM_ORDER = {json.dumps(DIM_ORDER, ensure_ascii=False)};
const DIM_LABELS = {json.dumps(DIM_LABELS, ensure_ascii=False)};
const QUESTIONS = {json.dumps(questions, ensure_ascii=False)};
const STANDARD_TYPES = {json.dumps(types, ensure_ascii=False)};
const SPECIAL_TYPES = {json.dumps(special_types, ensure_ascii=False)};
const LEVEL_THRESHOLDS = {{ L:[2,3], M:[4,4], H:[5,6] }};
const LEVEL_NUM = {{ L:1, M:2, H:3 }};
const MAX_DISTANCE = 30;
const FALLBACK_THRESHOLD = 60;

let state = {{ current:0, answers:{{}}, queue:[], isSpecial:false, isDrunk:false, hiddenCode:null }};

function parsePattern(p) {{ return p.replace(/-/g,'').split(''); }}
function calcDimScores(answers) {{
  const scores = {{}};
  for (const q of QUESTIONS) {{
    if (answers[q.id] == null) continue;
    scores[q.dim] = (scores[q.dim]||0) + answers[q.id];
  }}
  return scores;
}}
function scoresToLevels(scores) {{
  const levels = {{}};
  for (const [dim,score] of Object.entries(scores)) {{
    if (score <= LEVEL_THRESHOLDS.L[1]) levels[dim]='L';
    else if (score >= LEVEL_THRESHOLDS.H[0]) levels[dim]='H';
    else levels[dim]='M';
  }}
  return levels;
}}
function matchType(userLevels, pattern) {{
  const tp = parsePattern(pattern);
  let dist=0, exact=0;
  for (let i=0;i<DIM_ORDER.length;i++) {{
    const u = LEVEL_NUM[userLevels[DIM_ORDER[i]]||'M'];
    const t = LEVEL_NUM[tp[i]||'M'];
    dist += Math.abs(u-t);
    if (u===t) exact++;
  }}
  return {{ distance:dist, exact, similarity: Math.max(0,Math.round((1-dist/MAX_DISTANCE)*100)) }};
}}
function shuffle(arr) {{
  const a=[...arr];
  for(let i=a.length-1;i>0;i--){{const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}}
  return a;
}}

function startQuiz() {{
  state = {{ current:0, answers:{{}}, queue:shuffle([...QUESTIONS]), isSpecial:false, isDrunk:false, hiddenCode:null }};
  document.getElementById('start-screen').classList.add('hidden');
  document.getElementById('progress-wrap').classList.remove('hidden');
  document.getElementById('result-screen').classList.add('hidden');
  document.getElementById('question-screen').classList.remove('hidden');
  document.getElementById('special-hint').classList.add('hidden');
  renderQuestion();
}}

function renderQuestion() {{
  const q = state.queue[state.current];
  if (!q) {{ finishQuiz(); return; }}
  document.getElementById('progress-fill').style.width = ((state.current)/state.queue.length*100)+'%';
  document.getElementById('progress-text').textContent = `${{state.current}} / ${{state.queue.length}}`;
  document.getElementById('special-hint').classList.add('hidden');
  document.getElementById('q-text').textContent = q.text;
  const opts = document.getElementById('options');
  opts.innerHTML = '';
  const labels = ['A','B','C','D'];
  q.options.forEach((opt,idx)=>{{
    const btn = document.createElement('button');
    btn.className='opt-btn';
    btn.innerHTML=`<span class=\"opt-label\">${{labels[idx]||(idx+1)}}</span>${{opt.label}}`;
    btn.onclick=()=>{{ state.answers[q.id]=opt.value; state.current++; renderQuestion(); }};
    opts.appendChild(btn);
  }});
}}

function finishQuiz() {{
  document.getElementById('question-screen').classList.add('hidden');
  document.getElementById('progress-wrap').classList.add('hidden');
  const rs = document.getElementById('result-screen');
  rs.classList.remove('hidden');
  const scores = calcDimScores(state.answers);
  const levels = scoresToLevels(scores);
  const allTypes = STANDARD_TYPES.map(t=>({{...t,...matchType(levels,t.pattern)}}));
  allTypes.sort((a,b)=>a.distance-b.distance||b.exact-a.exact||b.similarity-a.similarity);
  const best = allTypes[0];
  if (best.similarity < FALLBACK_THRESHOLD) {{
    const fallback = SPECIAL_TYPES.find(t=>t.code==='HHHH')||SPECIAL_TYPES[0];
    showResult(fallback.code, fallback.cn, fallback.intro, fallback.desc, allTypes, levels);
  }} else {{
    showResult(best.code, best.cn, best.intro, best.desc, allTypes, levels);
  }}
}}

function showResult(code, cn, intro, desc, rankings, levels) {{
  document.getElementById('r-code').textContent = code;
  document.getElementById('r-name').textContent = cn;
  document.getElementById('r-intro').textContent = intro;
  document.getElementById('r-desc').textContent = desc;
  const list = document.getElementById('rank-list');
  list.innerHTML = '';
  rankings.slice(0,5).forEach((t,i)=>{{
    const div = document.createElement('div');
    div.className='rank-item';
    div.innerHTML=`<span class=\"num\">${{i+1}}</span><span class=\"rname\">${{t.code}} (${{t.cn}})</span><span class=\"rdist\">距离 ${{t.distance}}</span>`;
    list.appendChild(div);
  }});
  drawRadar(levels);
}}

function drawRadar(userLevels) {{
  const canvas = document.getElementById('radar');
  const ctx = canvas.getContext('2d');
  const cx = canvas.width/2, cy = canvas.height/2;
  const r = 100;
  const n = DIM_ORDER.length;
  const angleStep = (2*Math.PI)/n;
  ctx.clearRect(0,0,canvas.width,canvas.height);
  for (let level=1; level<=3; level++) {{
    ctx.beginPath();
    for (let i=0;i<=n;i++) {{
      const angle = i*angleStep - Math.PI/2;
      const radius = r * level / 3;
      const x = cx + radius*Math.cos(angle);
      const y = cy + radius*Math.sin(angle);
      i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
    }}
    ctx.strokeStyle = 'rgba(255,255,255,0.08)';
    ctx.lineWidth = 1;
    ctx.stroke();
  }}
  for (let i=0;i<n;i++) {{
    const angle = i*angleStep - Math.PI/2;
    ctx.beginPath();
    ctx.moveTo(cx,cy);
    ctx.lineTo(cx+r*Math.cos(angle), cy+r*Math.sin(angle));
    ctx.strokeStyle = 'rgba(255,255,255,0.1)';
    ctx.stroke();
  }}
  ctx.fillStyle='rgba(255,255,255,0.5)';
  ctx.font='11px PingFang SC';
  ctx.textAlign='center';
  ctx.textBaseline='middle';
  for (let i=0;i<n;i++) {{
    const angle = i*angleStep - Math.PI/2;
    ctx.fillText(DIM_LABELS[DIM_ORDER[i]]||DIM_ORDER[i], cx+(r+18)*Math.cos(angle), cy+(r+18)*Math.sin(angle));
  }}
  ctx.beginPath();
  for (let i=0;i<n;i++) {{
    const val = LEVEL_NUM[userLevels[DIM_ORDER[i]]||'M'];
    const angle = i*angleStep - Math.PI/2;
    const radius = r * val / 3;
    const x = cx + radius*Math.cos(angle);
    const y = cy + radius*Math.sin(angle);
    i===0 ? ctx.moveTo(x,y) : ctx.lineTo(x,y);
  }}
  ctx.closePath();
  ctx.fillStyle='rgba(108,92,231,0.3)';
  ctx.fill();
  ctx.strokeStyle='var(--accent)';
  ctx.lineWidth=2;
  ctx.stroke();
  for (let i=0;i<n;i++) {{
    const val = LEVEL_NUM[userLevels[DIM_ORDER[i]]||'M'];
    const angle = i*angleStep - Math.PI/2;
    ctx.beginPath();
    ctx.arc(cx+r*val/3*Math.cos(angle), cy+r*val/3*Math.sin(angle), 4, 0, 2*Math.PI);
    ctx.fillStyle='var(--accent)';
    ctx.fill();
  }}
}}

function restart() {{
  document.getElementById('result-screen').classList.add('hidden');
  document.getElementById('start-screen').classList.remove('hidden');
}}

document.getElementById('progress-wrap').classList.add('hidden');
</script>
</body>
</html>"""
    return html


def build_filename(test_name):
    ts = int(time.time())
    safe = "".join(c if c.isalnum() else "_" for c in test_name)
    return f"问卷_{safe}_{ts}.html"


# ── 主入口 ─────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description="生成人格测试 HTML 问卷")
    parser.add_argument("--test-name", required=True)
    parser.add_argument("--test-subtitle", default="")
    parser.add_argument("--data-json", type=str, help="JSON string with questions/types/special_types")
    args = parser.parse_args()

    data = json.loads(args.data_json) if args.data_json else {}

    questions = data.get("questions", [])
    types = data.get("types", [])
    special_types = data.get("special_types", [])

    html = generate_html(
        test_name=args.test_name,
        test_subtitle=args.test_subtitle,
        questions=questions,
        types=types,
        special_types=special_types,
    )

    out_file = OUT_DIR / build_filename(args.test_name)
    out_file.write_text(html, encoding="utf-8")
    print(f"HTML_FILE:{out_file}", flush=True)


if __name__ == "__main__":
    main()
