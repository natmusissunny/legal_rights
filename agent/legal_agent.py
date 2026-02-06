"""
法律维权智能Agent
核心问答逻辑，整合RAG和LLM API
"""
from typing import Optional
from datetime import datetime

from ..models import Answer, QuestionType
from ..config import Config
from .llm_factory import create_llm_client, LLMClientBase
from .prompt_templates import PromptTemplates
from .conversation_manager import ConversationManager
from ..knowledge import KnowledgeRetriever


class LegalAgent:
    """法律维权智能Agent"""

    def __init__(
        self,
        llm_client: Optional[LLMClientBase] = None,
        retriever: Optional[KnowledgeRetriever] = None,
        conversation_manager: Optional[ConversationManager] = None
    ):
        """
        初始化Agent

        Args:
            llm_client: LLM客户端（自动选择或手动指定）
            retriever: 知识检索器
            conversation_manager: 对话管理器
        """
        self.llm = llm_client or create_llm_client()
        self.retriever = retriever or KnowledgeRetriever(auto_load=True)
        self.conversation = conversation_manager or ConversationManager()
        self.templates = PromptTemplates()

    def ask(
        self,
        question: str,
        use_context: bool = True,
        top_k: int = None
    ) -> Answer:
        """
        单次问答

        Args:
            question: 用户问题
            use_context: 是否使用对话上下文
            top_k: 检索文档数量

        Returns:
            答案对象
        """
        top_k = top_k or Config.TOP_K_RESULTS

        print(f"\n🤔 问题: {question}")
        print("-" * 70)

        # 1. 分类问题类型
        print("📋 分析问题类型...", end=" ")
        question_type = self._classify_question(question)
        print(f"✅ {question_type.value}")

        # 2. 检索相关文档
        print(f"🔍 检索相关文档 (Top-{top_k})...", end=" ")
        try:
            relevant_docs_with_scores = self.retriever.retrieve(
                query=question,
                top_k=top_k
            )
            relevant_docs = [doc for doc, score in relevant_docs_with_scores]
            scores = [score for doc, score in relevant_docs_with_scores]
            print(f"✅ 找到 {len(relevant_docs)} 个相关文档")

            # 显示相关度
            if relevant_docs:
                avg_score = sum(scores) / len(scores)
                print(f"   平均相关度: {avg_score:.4f}")

        except Exception as e:
            print(f"⚠️  检索失败: {e}")
            relevant_docs = []
            scores = []

        # 3. 构建Prompt
        print("💭 构建提示词...", end=" ")

        if use_context and self.conversation.has_context():
            # 多轮对话模式
            history = self.conversation.get_conversation_history()
            prompt = self.templates.build_follow_up_prompt(
                previous_qa=history[-3:],  # 最近3轮
                current_question=question
            )
        else:
            # RAG模式
            prompt = self.templates.build_rag_prompt(
                question=question,
                context_documents=relevant_docs,
                question_type=question_type
            )

        print("✅")

        # 4. 调用Claude生成答案
        print("🤖 生成回答...", end=" ")
        try:
            answer_text = self.llm.complete(
                prompt=prompt,
                system=self.templates.SYSTEM_ROLE,
                temperature=0.7
            )
            print("✅")
        except Exception as e:
            print(f"❌ 失败: {e}")
            answer_text = "抱歉，我遇到了一些技术问题，无法生成回答。请稍后再试。"

        # 5. 计算置信度
        confidence = self._calculate_confidence(scores, question_type)

        # 6. 提取来源
        sources = list(set(doc.source_url for doc in relevant_docs))

        # 7. 创建答案对象
        answer = Answer(
            question=question,
            answer_text=answer_text,
            question_type=question_type,
            relevant_docs=relevant_docs,
            confidence=confidence,
            sources=sources,
            created_at=datetime.now()
        )

        # 8. 保存到对话历史
        self.conversation.add_turn(question, answer)

        return answer

    def chat(self, question: str, top_k: int = None) -> Answer:
        """
        多轮对话（带上下文）

        Args:
            question: 用户问题
            top_k: 检索文档数量

        Returns:
            答案对象
        """
        return self.ask(question, use_context=True, top_k=top_k)

    def reset_conversation(self):
        """重置对话历史"""
        self.conversation.reset()
        print("✅ 对话历史已重置")

    def get_conversation_summary(self) -> str:
        """
        获取对话摘要

        Returns:
            对话摘要
        """
        return self.conversation.get_summary()

    def _classify_question(self, question: str) -> QuestionType:
        """
        分类问题类型

        Args:
            question: 用户问题

        Returns:
            问题类型
        """
        # 简单的关键词匹配
        question_lower = question.lower()

        # 赔偿计算
        if any(kw in question_lower for kw in ["计算", "多少钱", "金额", "算", "几个月"]):
            return QuestionType.CALCULATION

        # 维权流程
        if any(kw in question_lower for kw in ["怎么办", "如何", "流程", "仲裁", "起诉", "维权"]):
            return QuestionType.PROCEDURE

        # 法律依据
        if any(kw in question_lower for kw in ["法律", "法规", "规定", "依据", "条文"]):
            return QuestionType.LEGAL_BASIS

        # 经济补偿
        if any(kw in question_lower for kw in ["补偿", "赔偿", "n+1", "2n"]):
            return QuestionType.COMPENSATION

        # 默认为一般咨询
        return QuestionType.GENERAL

    def _calculate_confidence(
        self,
        retrieval_scores: list[float],
        question_type: QuestionType
    ) -> float:
        """
        计算答案置信度

        Args:
            retrieval_scores: 检索相关度分数
            question_type: 问题类型

        Returns:
            置信度（0-1）
        """
        if not retrieval_scores:
            return 0.5  # 无检索结果，中等置信度

        # 基础置信度 = 平均检索分数
        avg_score = sum(retrieval_scores) / len(retrieval_scores)

        # 根据问题类型调整
        type_weight = {
            QuestionType.LEGAL_BASIS: 1.0,  # 法律依据最可靠
            QuestionType.COMPENSATION: 0.9,
            QuestionType.CALCULATION: 0.85,
            QuestionType.PROCEDURE: 0.9,
            QuestionType.CASE_ANALYSIS: 0.8,
            QuestionType.GENERAL: 0.7
        }

        weight = type_weight.get(question_type, 0.8)
        confidence = avg_score * weight

        # 限制在0-1范围
        return max(0.0, min(1.0, confidence))


def main():
    """测试Legal Agent"""
    print("🧪 测试 Legal Agent")
    print("=" * 80)

    # 检查配置
    if not Config.CLAUDE_API_KEY:
        print("❌ 请先配置 CLAUDE_API_KEY")
        return

    # 检查索引
    index_path = Config.VECTORS_DIR / "index.faiss"
    if not index_path.exists():
        print("⚠️  向量索引不存在，将使用空索引")
        print("   运行 python scripts/test_vector_index.py 构建索引")

    # 初始化Agent
    try:
        agent = LegalAgent()
        print("✅ Agent初始化成功\n")
    except Exception as e:
        print(f"❌ Agent初始化失败: {e}")
        return

    # 测试问答
    questions = [
        "如何计算N+1经济补偿金？",
        "公司恶意辞退不给补偿怎么办？",
        "劳动仲裁需要准备什么材料？"
    ]

    for i, question in enumerate(questions, 1):
        print(f"\n{'='*80}")
        print(f"测试 {i}/{len(questions)}")
        print('='*80)

        try:
            answer = agent.ask(question)
            print(answer.display())
        except Exception as e:
            print(f"❌ 回答失败: {e}")
            import traceback
            traceback.print_exc()

    # 显示对话摘要
    print("\n" + "=" * 80)
    print("📊 对话摘要")
    print("=" * 80)
    print(agent.get_conversation_summary())

    print("\n✅ 测试完成")


if __name__ == "__main__":
    main()
