"""
批量测试问题脚本
测试Agent对多个问题的回答质量
"""
import sys
import time
from pathlib import Path
from datetime import datetime

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.agent import LegalAgent
from legal_rights.config import Config


# 测试问题集
TEST_QUESTIONS = [
    # 经济补偿类
    "公司辞退员工应该给补偿吗？",
    "什么情况下可以获得经济补偿？",
    "被公司开除有补偿吗？",

    # 计算类
    "如何计算N+1补偿？",
    "工作3年月薪8000，被辞退应该赔多少？",
    "2N赔偿金怎么算？",

    # 维权流程类
    "公司不给补偿怎么办？",
    "劳动仲裁需要准备什么材料？",
    "如何申请劳动仲裁？",

    # 法律依据类
    "经济补偿的法律依据是什么？",
    "劳动法关于补偿的规定？",
    "N+1的法律条文是什么？",

    # 特殊情况
    "试用期被辞退有补偿吗？",
    "严重违纪被开除有补偿吗？",
    "公司倒闭有补偿吗？",
]


def print_header(title: str):
    """打印标题"""
    print("\n" + "=" * 80)
    print(title.center(80))
    print("=" * 80)


def print_question_result(question: str, answer, duration: float, index: int, total: int):
    """打印问题结果"""
    print(f"\n[{index}/{total}] {question}")
    print("-" * 80)
    print(f"问题类型: {answer.question_type.value}")
    print(f"置信度: {answer.confidence:.2%}")
    print(f"相关文档: {len(answer.relevant_docs)} 个")
    print(f"回答长度: {len(answer.answer_text)} 字符")
    print(f"耗时: {duration:.2f}秒")

    # 显示答案预览
    preview = answer.answer_text[:200].replace('\n', ' ')
    print(f"\n答案预览: {preview}...")

    # 评分
    score = "🟢" if answer.confidence >= 0.8 else "🟡" if answer.confidence >= 0.6 else "🔴"
    print(f"评分: {score}")


def save_report(results: list, output_path: Path):
    """保存测试报告"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# 批量测试报告\n\n")
        f.write(f"测试时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"测试问题数: {len(results)}\n\n")

        # 统计
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        avg_duration = sum(r['duration'] for r in results) / len(results)

        f.write("## 总体统计\n\n")
        f.write(f"- 平均置信度: {avg_confidence:.2%}\n")
        f.write(f"- 平均响应时间: {avg_duration:.2f}秒\n")
        f.write(f"- 高置信度(>=80%): {sum(1 for r in results if r['confidence'] >= 0.8)}\n")
        f.write(f"- 中置信度(60-80%): {sum(1 for r in results if 0.6 <= r['confidence'] < 0.8)}\n")
        f.write(f"- 低置信度(<60%): {sum(1 for r in results if r['confidence'] < 0.6)}\n")

        # 问题类型分布
        from collections import Counter
        type_dist = Counter(r['type'] for r in results)

        f.write("\n## 问题类型分布\n\n")
        for qtype, count in type_dist.items():
            f.write(f"- {qtype}: {count}\n")

        # 详细结果
        f.write("\n## 详细结果\n\n")

        for i, r in enumerate(results, 1):
            f.write(f"### {i}. {r['question']}\n\n")
            f.write(f"- **类型**: {r['type']}\n")
            f.write(f"- **置信度**: {r['confidence']:.2%}\n")
            f.write(f"- **耗时**: {r['duration']:.2f}秒\n")
            f.write(f"- **相关文档**: {r['relevant_docs']} 个\n")
            f.write(f"\n**答案**:\n\n{r['answer']}\n\n")
            f.write("---\n\n")

    print(f"\n✅ 报告已保存: {output_path}")


def main():
    """主函数"""
    print_header("📝 批量测试问题")

    # 检查配置
    if not Config.CLAUDE_API_KEY:
        print("❌ 错误: 未配置 CLAUDE_API_KEY")
        return False

    # 检查索引
    index_path = Config.VECTORS_DIR / "index.faiss"
    if not index_path.exists():
        print("❌ 错误: 向量索引不存在")
        print("请先运行: python -m legal_rights build-kb")
        return False

    # 初始化Agent
    print("\n初始化Agent...", end=" ")
    try:
        agent = LegalAgent()
        print("✅")
    except Exception as e:
        print(f"❌ 失败: {e}")
        return False

    # 测试问题
    print(f"\n开始测试 {len(TEST_QUESTIONS)} 个问题...")

    results = []
    start_total = time.time()

    for i, question in enumerate(TEST_QUESTIONS, 1):
        try:
            start = time.time()
            answer = agent.ask(question, use_context=False)
            duration = time.time() - start

            print_question_result(question, answer, duration, i, len(TEST_QUESTIONS))

            results.append({
                'question': question,
                'type': answer.question_type.value,
                'confidence': answer.confidence,
                'answer': answer.answer_text,
                'relevant_docs': len(answer.relevant_docs),
                'duration': duration
            })

            # 避免速率限制
            if i < len(TEST_QUESTIONS):
                time.sleep(1)

        except Exception as e:
            print(f"\n❌ 问题 {i} 失败: {e}")
            continue

    total_duration = time.time() - start_total

    # 打印摘要
    print_header("📊 测试摘要")

    print(f"\n测试完成: {len(results)}/{len(TEST_QUESTIONS)}")
    print(f"总耗时: {total_duration:.1f}秒")

    if results:
        avg_confidence = sum(r['confidence'] for r in results) / len(results)
        avg_duration = sum(r['duration'] for r in results) / len(results)

        print(f"\n平均置信度: {avg_confidence:.2%}")
        print(f"平均响应时间: {avg_duration:.2f}秒")

        # 置信度分布
        high = sum(1 for r in results if r['confidence'] >= 0.8)
        medium = sum(1 for r in results if 0.6 <= r['confidence'] < 0.8)
        low = sum(1 for r in results if r['confidence'] < 0.6)

        print(f"\n置信度分布:")
        print(f"  🟢 高 (>=80%): {high}")
        print(f"  🟡 中 (60-80%): {medium}")
        print(f"  🔴 低 (<60%): {low}")

        # 保存报告
        output_path = Config.PROJECT_ROOT / "test_report.md"
        save_report(results, output_path)

    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 已取消")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
