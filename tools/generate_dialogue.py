"""对话式日报生成脚本（产出与 TTS 一致的口播母本：{DATE}-article.md）"""
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from pipeline.llm import call_llm
from tools.tts_paths import article_md_path

BRIEFING_CONTENT = """今日日报内容：

🔥 今日必看
1. Figma 推出 AI 自动布局功能，说句话就能生成完整页面
2. Anthropic 将 Claude 上下文窗口扩展至 100 万 tokens

📌 值得关注
3. NNg 报告：78% 的 AI 产品存在严重可用性问题
4. a16z 合伙人：大多数 AI 产品周留存率不足 10%
5. Canva 以 8 亿美元收购 Framer
6. Vercel 发布 v0 企业版，Design Token 集成

🛠 工具雷达
7. Penpot 开源设计工具新增 AI 功能
8. 10 个免费 AI 设计工具合集

💡 编辑视角
AI 工具正在从「能力展示」进入「工作流融合」阶段。"""

SYSTEM_PROMPT = """你是一个对话式日报生成助手。

角色设定：
- Qearl：设计师，直接、犀利、爱挑战、经常提出不同看法
- 李达达：产品经理，理性、好奇、善于总结、偶尔被问到

要求：
1. 基于提供的日报内容，生成 3000-5000 字的对话文章
2. 3-4 个主题讨论，每主题 2-3 轮观点碰撞
3. 必须有真正的讨论，不能一方总是同意另一方
4. 口语化，像真实对话
5. 每轮发言 50-150 字
6. 结构：开场 -> 主题讨论 -> 结尾"""

USER_PROMPT = f"""请基于以下日报内容，生成对话式解读文章：

{BRIEFING_CONTENT}

请生成完整的对话文章，包含开场、3-4 个主题讨论、结尾。"""

def main():
    print("正在生成对话式文章...")
    result = call_llm(SYSTEM_PROMPT, USER_PROMPT, max_tokens=8000)

    # 保存到文件（与 pipeline 约定一致，供 TTS 读取）
    output_path = article_md_path()
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(result)

    print(f"✓ 对话文章已保存到 {output_path}")
    print(f"  字符数: {len(result)}")

if __name__ == "__main__":
    main()