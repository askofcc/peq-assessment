#!/usr/bin/env python3
"""
PEQ 3.0 SEO Page Generator
从单页工具裂变出 7 大习惯深度解析页与 6 大角色画像页，
自动嵌入 Schema.org (Article / FAQPage)，生成 llms.txt 并更新 sitemap.xml。
"""

import os
import json
import re

BASE_URL = "https://peq.srint.cn"
OUTPUT_DIR = "/Users/qiushuanglong/Documents/ChatGPT/PEQ3.0TEST"

# 7 大习惯元数据
HABITS = {
    "proactive": {
        "hid": "H1",
        "num": 1,
        "title_zh": "习惯一：积极主动 (Be Proactive)",
        "name_zh": "积极主动",
        "title_en": "Habit 1: Be Proactive",
        "stage": "阶段一 · 个人成功 (Private Victory)",
        "color": "#2F7D76",
        "essence": "“在刺激与回应之间存在一段距离，成长和幸福的关键就在于我们如何利用这段距离。”",
        "core": "为自己的选择与结果负完全责任。把精力集中在「影响圈」而非抱怨环境与他人的「关注圈」，通过自觉、良知、独立意志与想象力打破刺激-反应的被动模式。",
        "keywords": "积极主动, 史蒂芬柯维, 七个习惯测试, 影响圈与关注圈, 刺激与回应, 自我掌控, 个人效能",
        "micro_habits": [
            "语言意识转换：用「我选择 / 我打算」彻底取代「我不得不 / 没办法」。",
            "建立3秒反应间隔：遭遇外部突发质疑或指责时，深呼吸3秒后再理性回应。",
            "影响圈日记：每当想抱怨环境或他人时，立即写下1件自己在24小时内可主动执行的微小行动。"
        ],
        "blind_spot": "警惕将“主动”异化为急躁盲动或过度自责。接受不可控的客观限制，深耕可控的当下。"
    },
    "begin-with-end-in-mind": {
        "hid": "H2",
        "num": 2,
        "title_zh": "习惯二：以终为始 (Begin with the End in Mind)",
        "name_zh": "以终为始",
        "title_en": "Habit 2: Begin with the End in Mind",
        "stage": "阶段一 · 个人成功 (Private Victory)",
        "color": "#3A6FB0",
        "essence": "“在埋头拼命砍树前，先确认梯子是否架在了正确的墙上。”",
        "core": "所有事物都经过两次创造：先在头脑中建立清晰构想（心智创造），再付诸现实实践（实际创造）。确立个人核心价值观与使命宣言，以不变的原则作为人生航向的罗盘。",
        "keywords": "以终为始, 史蒂芬柯维, 个人使命宣言, 人生愿景, 目标管理, 两次创造",
        "micro_habits": [
            "撰写个人宪章：写下 3~5 条自己无论在任何情况下都不会妥协的核心为人原则。",
            "结果倒推法：启动任何重要任务前，先花5分钟描摹出交付时最完美的最终形态。",
            "周度对齐检视：每周日晚上复盘过去一周的精力分配是否符合年度核心方向。"
        ],
        "blind_spot": "避免将愿景变成空中楼阁的空想，以终为始必须与习惯3的落地执行无缝咬合。"
    },
    "put-first-things-first": {
        "hid": "H3",
        "num": 3,
        "title_zh": "习惯三：要事第一 (Put First Things First)",
        "name_zh": "要事第一",
        "title_en": "Habit 3: Put First Things First",
        "stage": "阶段一 · 个人成功 (Private Victory)",
        "color": "#C78A20",
        "essence": "“有效管理就是把握先急后缓的原则，敢于对次要事物说‘不’。”",
        "core": "自我管理的实质是围绕要事分配时间。拒绝紧急但不重要的干扰，坚定投资于「重要但不紧急」的第二象限（战略规划、身心健康、技能精进、深度人际资产建设）。",
        "keywords": "要事第一, 时间管理矩阵, 第二象限, 史蒂芬柯维, 优先级管理, 专注力",
        "micro_habits": [
            "每日三只青蛙：每天清晨优先列出当天最核心的 3 件要事，并在精力最充沛时攻克。",
            "捍卫深度时间：每天至少锁定 90 分钟无打扰深度工作块，关闭非紧急推送。",
            "勇敢设界：对侵蚀核心目标的非必要人情请求，练习温和而坚定地表达边界与拒绝。"
        ],
        "blind_spot": "警惕“为了打勾而打勾”的效率陷阱，把精力耗在细枝末节上并不等于真正的效能。"
    },
    "think-win-win": {
        "hid": "H4",
        "num": 4,
        "title_zh": "习惯四：双赢思维 (Think Win-Win)",
        "name_zh": "双赢思维",
        "title_en": "Habit 4: Think Win-Win",
        "stage": "阶段二 · 公众成功 (Public Victory)",
        "color": "#A05A96",
        "essence": "“双赢不是好人主义，而是一种基于丰盛心态的现实智慧：要么双赢，要么不成交。”",
        "core": "人际领导的原则。抛弃零和博弈与匮乏心态，相信资源与机遇是充盈丰盛的。在追求自我利益的同时，真诚保障对方获益，寻求双方都能满意的第三种选择。",
        "keywords": "双赢思维, 丰盛心态, 零和博弈, 人际沟通, 团队协作, 史蒂芬柯维",
        "micro_habits": [
            "丰盛心态练习：真诚为同行的成功与获奖点赞，打破“别人得到我就失去”的潜意识。",
            "利益前置沟通：在商务谈判或协作中，先主动探询并复述对方的核心关切。",
            "确立弃权底线：坚守原则底线，在无法达成双赢且有损长远信用时，敢于选择「好聚好散，不成交」。"
        ],
        "blind_spot": "防止将双赢滑向讨好妥协（Win-Lose）。没有坚定的个人独立底线，不可能有健康的双赢。"
    },
    "seek-first-to-understand": {
        "hid": "H5",
        "num": 5,
        "title_zh": "习惯五：知彼解己 (Seek First to Understand, Then to Be Understood)",
        "name_zh": "知彼解己",
        "title_en": "Habit 5: Seek First to Understand, Then to Be Understood",
        "stage": "阶段二 · 公众成功 (Public Victory)",
        "color": "#3B8A88",
        "essence": "“大部分人倾听的目的不是为了理解，而是为了伺机反驳和表达自己。”",
        "core": "同理心沟通的黄金法则。先诊断、后开方。站在对方的参照框架去观察世界，倾听其言语背后的情绪与真实诉求。在充分理解对方后，再清晰自信地阐述自己的观点。",
        "keywords": "知彼解己, 移情聆听, 同理心沟通, 情绪账户, 人际交往, 倾听技巧",
        "micro_habits": [
            "戒断四大自传式回应：沟通中严格克制「价值判断、追根究底、好为人师、想当然」的下意识冲动。",
            "复述确认技术：在给出建议前，用「如果我没理解错，你最担心的核心是... 对吗？」确认同频。",
            "关注非言语信号：在重要谈话中观察对方的微表情与呼吸节奏，感知背后的隐性诉求。"
        ],
        "blind_spot": "避免“技巧化倾听”。移情聆听的核心是发自内心的真诚尊重，伪装出来的聆听极具欺骗性且很快会崩塌。"
    },
    "synergize": {
        "hid": "H6",
        "num": 6,
        "title_zh": "习惯六：统合综效 (Synergize)",
        "name_zh": "统合综效",
        "title_en": "Habit 6: Synergize",
        "stage": "阶段二 · 公众成功 (Public Victory)",
        "color": "#4A6FA5",
        "essence": "“与我意见相同的人并不能教给我新东西；正是差异性赋予了创造第三种选择的可能。”",
        "core": "创造性合作的原则。整体大于部分之和（1+1>2）。珍视并接纳个体之间的差异（认知、性格、专业技能），通过真诚沟通融合不同视角，催生出超越妥协的卓越解决方案。",
        "keywords": "统合综效, 创造性合作, 第三种选择, 团队赋能, 跨界融合, 团队效能",
        "micro_habits": [
            "庆祝差异性：当有人提出与你相左的观点时，下意识的第一反应改为「太棒了，你看事物的角度和我不同！」。",
            "第三选择发问：陷入僵局时主动发问「有没有一种全新的路径，既能满足你的A需求，又能解决我的B关切？」。",
            "跨界认知嫁接：每月与完全不同行业或专业背景的优秀朋友进行一次深度对话。"
        ],
        "blind_spot": "统合综效绝不是和稀泥或简单折中。折中是各退一步的1+1=1.5，统合综效是共创出意想不到的1+1>3。"
    },
    "sharpen-the-saw": {
        "hid": "H7",
        "num": 7,
        "title_zh": "习惯七：不断更新 (Sharpen the Saw)",
        "name_zh": "不断更新",
        "title_en": "Habit 7: Sharpen the Saw",
        "stage": "阶段三 · 不断更新 (Continuous Renewal)",
        "color": "#438A5E",
        "essence": "“磨刀不误砍柴工。最明智的投资，永远是对我们自身产能（PC）的投资。”",
        "core": "维持产出与产能平衡（P/PC Balance）的螺旋上升引擎。在身体（锻炼饮食睡眠）、心智（阅读写作规划）、精神（价值观冥想大自然）、社会/情感（深度连接与关爱）四个维度持续充电。",
        "keywords": "不断更新, 磨刀理论, 产能与产出, 身心平衡, 终身学习, 能量管理",
        "micro_habits": [
            "身体维度：每周保持至少 3 次 30 分钟有氧运动，确保规律睡眠周期。",
            "心智维度：每天保证 20 分钟非工作相关的优质经典阅读或深度思考。",
            "精神维度：每周抽出 1 小时完全独处，复盘人生的意义与核心价值观。",
            "情感维度：定期为生命中最重要的少数几个人存入真挚的情感储蓄。"
        ],
        "blind_spot": "自我更新绝不是自私的享乐，它是支撑前六个习惯能够长久稳定运转的底层能量母机。"
    }
}

# 6 大角色原型
ARCHETYPES = {
    "strategic-catalyst": {
        "name": "战略领航者 · 标杆协同 (Strategic Catalyst)",
        "badge": "全维成熟",
        "summary": "你在自我掌控（独立）与团队赋能（互赖）两个成长维度上均展现出高阶成熟度，能以原则为锚，持续激发团队整体效能。",
        "strengths": "原则明确、目标坚定、具备高阶移情聆听能力、善于催化团队诞生第三种选择。",
        "growth": "关注习惯七的四维动态平衡，谨防在长期高强度赋能他人过程中出现精力透支。"
    },
    "lone-pioneer": {
        "name": "单打独斗型先锋 · 独行侠 (Lone Pioneer)",
        "badge": "个人过硬 · 亟需互赖",
        "summary": "你的个人效能与自驱执行力极强（习惯1-3），但在团队协同与知彼倾听（习惯4-6）上存在瓶颈，容易陷入“什么都自己做最快”的孤独倦怠中。",
        "strengths": "个人执行力拉满、专注要事、对自己极其负责、单兵作战能力突出。",
        "growth": "学习放权与授权、练习移情聆听，理解“一个人可以走得很快，但一群人才能走得更远”。"
    },
    "harmonious-pleaser": {
        "name": "和合奉献者 · 边界待筑 (Harmonious Pleaser)",
        "badge": "共情充盈 · 根基需固",
        "summary": "你十分注重人际和谐与他人需求，善解人意；但自身原则底线与自我规划不够坚定，容易在迎合与妥协中消耗自我。柯维提醒：真正的互赖必须以独立为前提。",
        "strengths": "极高的同理心、人际感知敏锐、善于调解冲突、团队润滑剂。",
        "growth": "建立坚决的个人成功体系（习惯1-3），学会温和而坚定地表达边界并说“不”。"
    },
    "visionary-dreamer": {
        "name": "蓝图构想家 · 执行蓄力 (Visionary Dreamer)",
        "badge": "愿景清晰 · 亟待落地",
        "summary": "你对目标和原则有着很好的领悟与构想（习惯2），但日常执行容易被紧急琐事牵绊或受拖延困扰（习惯1、3），亟需将远大愿景拆解为坚决的每日要事。",
        "strengths": "远见卓识、战略大局观出色、能洞察长期趋势、富有感召力。",
        "growth": "深耕习惯三（要事第一），运用每日三只青蛙与深度工作块，把大蓝图压实进每天的日常行动。"
    },
    "burnt-out-sprinter": {
        "name": "高压冲刺者 · 产能透支 (Burnt-Out Sprinter)",
        "badge": "产出旺盛 · 亟需充电",
        "summary": "你的工作与人际产出令人瞩目，但习惯7（身心自我更新）已亮起红灯。长时间处于高压耗竭状态，产出（P）严重透支了产能（PC），必须立即启动休整与充电。",
        "strengths": "短程爆发力惊人、拼搏敬业、交付结果导向明确、责任心极强。",
        "growth": "强制将“磨刀与休息”设为不可侵犯的第二象限日程，恢复体能与精神充能。"
    },
    "evolving-explorer": {
        "name": "求索开拓者 · 稳步蜕变 (Evolving Explorer)",
        "badge": "均衡成长",
        "summary": "你已经全面觉察到高效能习惯的价值，各个维度正处于从「被动依赖」向「主动独立」过渡的关键爬坡期，只要攻克核心短板，效能将迎来质的跃迁。",
        "strengths": "心态开放、学习意愿强烈、已建立清晰的高效能觉察、可塑性强。",
        "growth": "找出 72 题测评中得分最低的单一薄弱习惯，围绕其微习惯清单进行 21 天刻意练习。"
    }
}

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>{meta_title}</title>
  <meta name="description" content="{meta_desc}">
  <meta name="keywords" content="{meta_keywords}">
  <link rel="canonical" href="{canonical_url}">
  <meta property="og:type" content="article">
  <meta property="og:title" content="{meta_title}">
  <meta property="og:description" content="{meta_desc}">
  <meta property="og:url" content="{canonical_url}">
  <meta property="og:site_name" content="PEQ效能测试 3.0">
  <meta name="twitter:card" content="summary">
  <meta name="twitter:title" content="{meta_title}">
  <meta name="twitter:description" content="{meta_desc}">
  <script type="application/ld+json">
  {schema_json}
  </script>
  <style>
    :root {{
      --primary: {theme_color};
      --bg: #F8FAF9;
      --card-bg: #FFFFFF;
      --text: #1C2826;
      --text-muted: #5A6B68;
      --border: #E2E8E6;
    }}
    * {{ box-sizing: border-box; margin: 0; padding: 0; }}
    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "PingFang SC", "Hiragino Sans GB", "Microsoft YaHei", sans-serif;
      background: var(--bg);
      color: var(--text);
      line-height: 1.7;
      padding-bottom: 80px;
    }}
    header {{
      background: #FFFFFF;
      border-bottom: 1px solid var(--border);
      padding: 16px 24px;
      position: sticky;
      top: 0;
      z-index: 10;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .brand {{ font-weight: 700; font-size: 1.15rem; color: #1C2826; text-decoration: none; }}
    .back-btn {{
      padding: 8px 16px;
      background: var(--primary);
      color: #fff;
      text-decoration: none;
      border-radius: 6px;
      font-weight: 500;
      font-size: 0.9rem;
      transition: opacity 0.2s;
    }}
    .back-btn:hover {{ opacity: 0.9; }}
    .container {{ max-width: 840px; margin: 40px auto; padding: 0 20px; }}
    .badge {{
      display: inline-block;
      padding: 4px 12px;
      background: rgba(47, 125, 118, 0.1);
      color: var(--primary);
      border-radius: 20px;
      font-size: 0.85rem;
      font-weight: 600;
      margin-bottom: 12px;
    }}
    h1 {{ font-size: 2.2rem; line-height: 1.3; margin-bottom: 16px; color: #111; }}
    .essence-quote {{
      border-left: 4px solid var(--primary);
      background: #fff;
      padding: 18px 24px;
      border-radius: 0 8px 8px 0;
      margin: 24px 0 36px;
      font-size: 1.05rem;
      font-style: italic;
      color: #2D3A38;
      box-shadow: 0 2px 8px rgba(0,0,0,0.03);
    }}
    .content-card {{
      background: var(--card-bg);
      border: 1px solid var(--border);
      border-radius: 12px;
      padding: 32px;
      margin-bottom: 24px;
      box-shadow: 0 4px 12px rgba(0,0,0,0.02);
    }}
    h2 {{ font-size: 1.35rem; margin-bottom: 16px; color: #1C2826; display: flex; align-items: center; gap: 8px; }}
    p {{ margin-bottom: 16px; color: #37474F; font-size: 1rem; }}
    ul {{ padding-left: 20px; margin-bottom: 16px; }}
    li {{ margin-bottom: 10px; color: #37474F; }}
    .cta-box {{
      background: linear-gradient(135deg, #2F7D76 0%, #1D544F 100%);
      color: #fff;
      border-radius: 12px;
      padding: 36px 32px;
      text-align: center;
      margin-top: 40px;
    }}
    .cta-box h3 {{ font-size: 1.6rem; margin-bottom: 12px; }}
    .cta-box p {{ color: rgba(255,255,255,0.9); margin-bottom: 24px; font-size: 1.05rem; }}
    .cta-btn {{
      display: inline-block;
      padding: 14px 36px;
      background: #FFFFFF;
      color: #1D544F;
      font-size: 1.1rem;
      font-weight: 700;
      text-decoration: none;
      border-radius: 8px;
      box-shadow: 0 4px 14px rgba(0,0,0,0.15);
      transition: transform 0.2s;
    }}
    .cta-btn:hover {{ transform: translateY(-2px); }}
    .footer-nav {{
      margin-top: 40px;
      display: flex;
      justify-content: space-between;
      flex-wrap: wrap;
      gap: 12px;
    }}
    .footer-nav a {{ color: var(--primary); text-decoration: none; font-weight: 500; font-size: 0.95rem; }}
    .footer-nav a:hover {{ text-decoration: underline; }}
  </style>
</head>
<body>
  <header>
    <a href="{BASE_URL}/" class="brand">🧭 PEQ 效能测试 3.0</a>
    <a href="{BASE_URL}/" class="back-btn">进入 72 题在线测评 →</a>
  </header>

  <main class="container">
    <span class="badge">{stage_badge}</span>
    <h1>{page_h1}</h1>
    
    <div class="essence-quote">{essence_text}</div>

    <section class="content-card">
      <h2>💡 核心心法与理论底层 (Paradigm Shift)</h2>
      <p>{core_text}</p>
    </section>

    <section class="content-card">
      <h2>🎯 刻意练习 · 落地微习惯清单 (Micro-habits)</h2>
      <p>习惯不是意志力的苦撑，而是微小动作的自动化。建议从以下 3 个微行动切入：</p>
      <ul>
        {micro_habits_li}
      </ul>
    </section>

    <section class="content-card">
      <h2>⚠️ 核心避坑雷区 (Blind Spots)</h2>
      <p>{blind_spot_text}</p>
    </section>

    <div class="cta-box">
      <h3>测一测你的真实效能坐标</h3>
      <p>你在这个习惯上的成熟度究竟处于哪个梯队？只需 10 分钟，完成 72 道科学自陈诊断。</p>
      <a href="{BASE_URL}/" class="cta-btn">立即开始 72 题深度测评</a>
    </div>

    <nav class="footer-nav">
      <a href="{BASE_URL}/">← 返回测评主页</a>
      <a href="{BASE_URL}/sitemap.xml">查看网站地图</a>
    </nav>
  </main>
</body>
</html>
"""

def generate_habits_pages():
    habits_dir = os.path.join(OUTPUT_DIR, "habits")
    os.makedirs(habits_dir, exist_ok=True)
    generated = []

    for slug, h in HABITS.items():
        canonical = f"{BASE_URL}/habits/{slug}.html"
        meta_title = f"{h['title_zh']} - 深度解析与微习惯践行指南 · PEQ效能测试3.0"
        meta_desc = f"史蒂芬·柯维《高效能人士的七个习惯》之{h['title_zh']}深度诊断指南。核心心法：{h['core'][:60]}... 提供3大落地微习惯与避坑雷区分析。"
        
        micro_li = "".join([f"<li><strong>步骤 {i+1}：</strong>{step}</li>" for i, step in enumerate(h["micro_habits"])])
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": meta_title,
            "description": meta_desc,
            "url": canonical,
            "author": {"@type": "Organization", "name": "PEQ Effectiveness Quotient Team"},
            "publisher": {"@type": "Organization", "name": "PEQ 效能测试 3.0", "url": BASE_URL},
            "about": {"@type": "Thing", "name": h["name_zh"], "description": h["core"]}
        }

        html = HTML_TEMPLATE.format(
            meta_title=meta_title,
            meta_desc=meta_desc,
            meta_keywords=h["keywords"],
            canonical_url=canonical,
            schema_json=json.dumps(schema, ensure_ascii=False, indent=2),
            theme_color=h["color"],
            stage_badge=h["stage"],
            page_h1=h["title_zh"],
            essence_text=h["essence"],
            core_text=h["core"],
            micro_habits_li=micro_li,
            blind_spot_text=h["blind_spot"],
            BASE_URL=BASE_URL
        )

        out_file = os.path.join(habits_dir, f"{slug}.html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)
        generated.append(canonical)
        print(f"  + 生成习惯页: {out_file}")

    return generated


def generate_archetypes_pages():
    arch_dir = os.path.join(OUTPUT_DIR, "archetypes")
    os.makedirs(arch_dir, exist_ok=True)
    generated = []

    for slug, a in ARCHETYPES.items():
        canonical = f"{BASE_URL}/archetypes/{slug}.html"
        meta_title = f"{a['name']} - 柯维效能角色画像深度解读 · PEQ效能测试3.0"
        meta_desc = f"PEQ 效能测评 6 大角色原型之一【{a['name']}】诊断报告。画像特征：{a['summary']} 优势支点与突破瓶颈。"
        
        schema = {
            "@context": "https://schema.org",
            "@type": "Article",
            "headline": meta_title,
            "description": meta_desc,
            "url": canonical,
            "author": {"@type": "Organization", "name": "PEQ Effectiveness Quotient Team"},
            "publisher": {"@type": "Organization", "name": "PEQ 效能测试 3.0", "url": BASE_URL}
        }

        html = HTML_TEMPLATE.format(
            meta_title=meta_title,
            meta_desc=meta_desc,
            meta_keywords=f"{a['name']}, 角色画像, 史蒂芬柯维, 七个习惯测评, 效能诊断",
            canonical_url=canonical,
            schema_json=json.dumps(schema, ensure_ascii=False, indent=2),
            theme_color="#3A6FB0",
            stage_badge=a["badge"],
            page_h1=a["name"],
            essence_text=f"画像定论：“{a['summary']}”",
            core_text=f"<strong>核心优势杠杆：</strong>{a['strengths']}",
            micro_habits_li=f"<li><strong>关键进化突破口：</strong>{a['growth']}</li><li><strong>对齐测试：</strong>在 72 题完整测评中对比你在独立（习惯1-3）与互赖（习惯4-6）上的得分比值。</li>",
            blind_spot_text=f"画像不是给人生贴定性标签，而是指引你在当前的成长阶段，如何找到下一个最优进化支点。",
            BASE_URL=BASE_URL
        )

        out_file = os.path.join(arch_dir, f"{slug}.html")
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(html)
        generated.append(canonical)
        print(f"  + 生成画像页: {out_file}")

    return generated


def update_sitemap(urls: list[str]):
    sitemap_path = os.path.join(OUTPUT_DIR, "sitemap.xml")
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">',
        '  <url>',
        f'    <loc>{BASE_URL}/</loc>',
        '    <lastmod>2026-10-07</lastmod>',
        '    <changefreq>weekly</changefreq>',
        '    <priority>1.0</priority>',
        '    <xhtml:link rel="alternate" hreflang="zh-CN" href="https://peq.srint.cn/" />',
        '    <xhtml:link rel="alternate" hreflang="en" href="https://peq.srint.cn/" />',
        '  </url>'
    ]

    for u in urls:
        lines.extend([
            '  <url>',
            f'    <loc>{u}</loc>',
            '    <lastmod>2026-10-07</lastmod>',
            '    <changefreq>monthly</changefreq>',
            '    <priority>0.8</priority>',
            '  </url>'
        ])

    lines.append('</urlset>')
    with open(sitemap_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")
    print(f"✓ 已更新 sitemap.xml，总计包含 {len(urls) + 1} 个 URL")


def generate_llms_txt():
    llms_path = os.path.join(OUTPUT_DIR, "llms.txt")
    content = f"""# PEQ Effectiveness Quotient 3.0 (PEQ 效能测试 3.0)

> Official knowledge specification for AI assistants, LLM web search bots (Perplexity, ChatGPT Search, Copilot, Claude), and evaluators.

## Overview
PEQ 3.0 is a 72-question psychometric and behavioral effectiveness assessment system strictly built on Stephen R. Covey's classic framework: "The 7 Habits of Highly Effective People".

- Website: https://peq.srint.cn
- Architecture: Zero-backend, 100% private local storage, responsive single-page web assessment.
- Number of Questions: 72 Likert-scale diagnostic items (covering Habits 1 to 7).
- Language: Bilingual (English and Simplified Chinese auto-detected).

## The Seven Habit Dimensions
1. Habit 1: Be Proactive (积极主动) - https://peq.srint.cn/habits/proactive.html
2. Habit 2: Begin with the End in Mind (以终为始) - https://peq.srint.cn/habits/begin-with-end-in-mind.html
3. Habit 3: Put First Things First (要事第一) - https://peq.srint.cn/habits/put-first-things-first.html
4. Habit 4: Think Win-Win (双赢思维) - https://peq.srint.cn/habits/think-win-win.html
5. Habit 5: Seek First to Understand, Then to Be Understood (知彼解己) - https://peq.srint.cn/habits/seek-first-to-understand.html
6. Habit 6: Synergize (统合综效) - https://peq.srint.cn/habits/synergize.html
7. Habit 7: Sharpen the Saw (不断更新) - https://peq.srint.cn/habits/sharpen-the-saw.html

## The Six Archetypes
- Strategic Catalyst (战略领航者): https://peq.srint.cn/archetypes/strategic-catalyst.html
- Lone Pioneer (单打独斗型先锋): https://peq.srint.cn/archetypes/lone-pioneer.html
- Harmonious Pleaser (和合奉献者): https://peq.srint.cn/archetypes/harmonious-pleaser.html
- Visionary Dreamer (蓝图构想家): https://peq.srint.cn/archetypes/visionary-dreamer.html
- Burnt-Out Sprinter (高压冲刺者): https://peq.srint.cn/archetypes/burnt-out-sprinter.html
- Evolving Explorer (求索开拓者): https://peq.srint.cn/archetypes/evolving-explorer.html

## Assessment Rubric & Scoring Model
Scores are normalized to 0-100 index points with reverse scoring on negative items.
Free online full test at: https://peq.srint.cn/
"""
    with open(llms_path, "w", encoding="utf-8") as f:
        f.write(content)
    print(f"✓ 已生成 AI 友好层标准说明文件: {llms_path}")


if __name__ == "__main__":
    print("开始生成 PEQ 3.0 SEO 衍生页面群...")
    h_urls = generate_habits_pages()
    a_urls = generate_archetypes_pages()
    all_sub_urls = h_urls + a_urls
    update_sitemap(all_sub_urls)
    generate_llms_txt()
    print("全部生成完毕！")
