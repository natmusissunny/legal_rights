"""
测试智能问答Agent
完整测试从问题到答案的全流程
"""
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root.parent))

from legal_rights.agent import LegalAgent
from legal_rights.config import Config


def test_single_question():
    """测试单个问题"""
    print("🧪 [测试1] 单个问题问答")
    print("=" * 80)

    try:
        agent = LegalAgent()
        print("✅ Agent初始化成功\n")
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return False

    question = "如何计算N+1经济补偿金？"

    try:
        answer = agent.ask(question)
        print("\n" + "=" * 80)
        print("📝 回答结果")
        print("=" * 80)
        print(answer.display())
        return True
    except Exception as e:
        print(f"❌ 回答失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_turn_conversation():
    """测试多轮对话"""
    print("\n\n🧪 [测试2] 多轮对话")
    print("=" * 80)

    try:
        agent = LegalAgent()
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return False

    questions = [
        "我在公司工作了3年被辞退了",
        "公司说是因为业绩不好",
        "我应该能拿到多少补偿？",
        "如果公司不给怎么办？"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n【轮次 {i}】")
        print("-" * 70)
        print(f"用户: {question}")

        try:
            answer = agent.chat(question)
            print(f"\n助手 (置信度: {answer.confidence:.2%}):")
            print(answer.answer_text[:300] + "...")
        except Exception as e:
            print(f"❌ 回答失败: {e}")
            return False

    # 显示对话摘要
    print("\n" + "=" * 80)
    print("📊 对话摘要")
    print("=" * 80)
    print(agent.get_conversation_summary())

    return True


def test_different_question_types():
    """测试不同类型的问题"""
    print("\n\n🧪 [测试3] 不同问题类型")
    print("=" * 80)

    try:
        agent = LegalAgent()
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return False

    questions = [
        ("经济补偿", "公司恶意辞退员工应该获得补偿吗？"),
        ("赔偿计算", "工作5年月薪10000元，N+1补偿是多少？"),
        ("维权流程", "被公司辞退不给补偿应该怎么维权？"),
        ("法律依据", "经济补偿的法律依据是什么？"),
    ]

    results = []

    for expected_type, question in questions:
        print(f"\n问题: {question}")
        print("-" * 70)

        try:
            answer = agent.ask(question, use_context=False)
            print(f"✅ 问题类型: {answer.question_type.value}")
            print(f"   置信度: {answer.confidence:.2%}")
            print(f"   相关文档: {len(answer.relevant_docs)} 个")
            print(f"   回答长度: {len(answer.answer_text)} 字符")

            results.append(True)
        except Exception as e:
            print(f"❌ 失败: {e}")
            results.append(False)

    return all(results)


def test_with_no_index():
    """测试无索引情况"""
    print("\n\n🧪 [测试4] 无索引情况")
    print("=" * 80)

    # 暂时重命名索引文件
    index_path = Config.VECTORS_DIR / "index.faiss"
    backup_path = Config.VECTORS_DIR / "index.faiss.backup"

    has_index = index_path.exists()

    if has_index:
        index_path.rename(backup_path)
        print("⚠️  已临时隐藏索引文件")

    try:
        agent = LegalAgent()
        print("✅ Agent初始化成功（无索引模式）\n")

        question = "什么是经济补偿金？"
        answer = agent.ask(question)

        print(f"问题: {question}")
        print(f"✅ 生成了回答 ({len(answer.answer_text)} 字符)")
        print(f"   置信度: {answer.confidence:.2%}")
        print(f"   相关文档: {len(answer.relevant_docs)} 个")

        result = True
    except Exception as e:
        print(f"❌ 失败: {e}")
        result = False
    finally:
        # 恢复索引文件
        if has_index and backup_path.exists():
            backup_path.rename(index_path)
            print("\n✅ 索引文件已恢复")

    return result


def main():
    """主测试函数"""
    print("🚀 智能问答Agent完整测试")
    print("=" * 80)
    print()

    # 检查API密钥
    if not Config.CLAUDE_API_KEY:
        print("❌ 错误: 未配置 CLAUDE_API_KEY")
        print("   请在 .env 文件中添加: CLAUDE_API_KEY=sk-ant-api03-...")
        return

    print("✅ API密钥已配置")

    # 检查索引
    index_path = Config.VECTORS_DIR / "index.faiss"
    if index_path.exists():
        print("✅ 向量索引已存在")
    else:
        print("⚠️  向量索引不存在（部分功能可能受限）")
        print("   运行 python scripts/test_vector_index.py 构建索引")

    print()

    # 运行测试
    results = {
        "single_question": False,
        "multi_turn": False,
        "question_types": False,
        "no_index": False
    }

    # 测试1: 单个问题
    results["single_question"] = test_single_question()

    # 测试2: 多轮对话
    if results["single_question"]:
        results["multi_turn"] = test_multi_turn_conversation()

    # 测试3: 不同问题类型
    if results["single_question"]:
        results["question_types"] = test_different_question_types()

    # 测试4: 无索引情况
    if results["single_question"]:
        results["no_index"] = test_with_no_index()

    # 总结
    print("\n\n" + "=" * 80)
    print("📊 测试总结")
    print("=" * 80)

    for test_name, success in results.items():
        status = "✅ 通过" if success else "❌ 失败"
        print(f"  {test_name:20s}: {status}")

    all_pass = all(results.values())
    print("\n" + "=" * 80)
    if all_pass:
        print("🎉 所有测试通过！")
    else:
        print("⚠️  部分测试失败")
    print("=" * 80)


if __name__ == "__main__":
    main()
