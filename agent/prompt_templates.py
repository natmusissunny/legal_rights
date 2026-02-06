"""
Prompt 模板
为不同类型的问题提供专业的提示词
"""
from typing import List, Optional
from ..models import QuestionType, Document


class PromptTemplates:
    """Prompt 模板管理器"""

    # 系统角色定义
    SYSTEM_ROLE = """你是一位专业的劳动法律师助手，专注于离职员工的劳动法维权咨询。

你的职责：
1. 基于提供的法律文档和案例，为用户提供准确的法律建议
2. 解释相关的法律条文和规定
3. 指导用户如何维护自己的合法权益
4. 计算经济补偿金（N、N+1、2N等）

回答要求：
1. 准确：引用具体的法律条文和规定
2. 专业：使用正确的法律术语
3. 实用：提供可操作的建议
4. 谨慎：说明法律风险和注意事项
5. 简洁：避免冗长，直接回答关键问题

重要提示：
- 如果信息不足，主动询问必要的细节
- 计算补偿金时，明确列出计算步骤
- 建议用户在重要决策前咨询当地律师
- 始终在回答末尾添加免责声明"""

    @staticmethod
    def build_rag_prompt(
        question: str,
        context_documents: List[Document],
        question_type: Optional[QuestionType] = None
    ) -> str:
        """
        构建RAG提示（基于检索结果回答）

        Args:
            question: 用户问题
            context_documents: 检索到的相关文档
            question_type: 问题类型

        Returns:
            完整的提示词
        """
        # 构建上下文
        context_parts = []
        for i, doc in enumerate(context_documents, 1):
            section_info = f"【{doc.section_title}】" if doc.section_title else ""
            context_parts.append(
                f"## 参考文档 {i} {section_info}\n"
                f"{doc.content}\n"
            )

        context = "\n".join(context_parts)

        # 根据问题类型调整指令
        type_specific_instruction = ""
        if question_type == QuestionType.CALCULATION:
            type_specific_instruction = """
这是一个补偿金计算问题。请：
1. 明确列出计算公式
2. 逐步展示计算过程
3. 给出最终金额
4. 说明可能的调整因素
"""
        elif question_type == QuestionType.PROCEDURE:
            type_specific_instruction = """
这是一个维权流程问题。请：
1. 按步骤列出具体流程
2. 说明每步需要的材料
3. 提示注意事项和时限
4. 给出建议和Tips
"""
        elif question_type == QuestionType.LEGAL_BASIS:
            type_specific_instruction = """
这是一个法律依据问题。请：
1. 引用具体的法律条文
2. 解释法条的含义
3. 说明适用条件
4. 举例说明
"""

        prompt = f"""# 用户问题
{question}

# 相关法律文档
{context}

# 回答指导
{type_specific_instruction}

请基于以上参考文档，为用户提供专业、准确、实用的解答。

回答要求：
1. 直接回答问题，不要重复问题内容
2. 引用参考文档中的具体内容
3. 使用清晰的结构（标题、列表等）
4. 如果文档中信息不完整，说明哪些信息缺失
5. 在回答末尾添加：**免责声明：本回答仅供参考，具体情况请咨询专业律师。**

请开始回答："""

        return prompt

    @staticmethod
    def build_clarification_prompt(
        question: str,
        missing_info: List[str]
    ) -> str:
        """
        构建澄清提示（需要更多信息）

        Args:
            question: 用户问题
            missing_info: 缺失的信息列表

        Returns:
            澄清提示
        """
        missing_points = "\n".join(f"{i}. {info}" for i, info in enumerate(missing_info, 1))

        prompt = f"""用户问题：{question}

为了给出准确的解答，我需要了解以下信息：

{missing_points}

请用简洁、友好的语气询问用户这些信息。"""

        return prompt

    @staticmethod
    def build_calculation_prompt(
        work_years: float,
        monthly_salary: float,
        situation: str,
        additional_info: Optional[str] = None
    ) -> str:
        """
        构建补偿金计算提示

        Args:
            work_years: 工作年限
            monthly_salary: 月平均工资
            situation: 离职情况
            additional_info: 额外信息

        Returns:
            计算提示
        """
        prompt = f"""请计算经济补偿金：

# 基本信息
- 工作年限：{work_years} 年
- 月平均工资：{monthly_salary} 元
- 离职情况：{situation}
"""

        if additional_info:
            prompt += f"- 补充说明：{additional_info}\n"

        prompt += """
# 计算要求
1. 判断适用哪种补偿标准（N、N+1、2N）
2. 列出计算公式
3. 逐步计算
4. 给出最终金额
5. 说明可能的调整因素（如工资上限）

请开始计算："""

        return prompt

    @staticmethod
    def build_follow_up_prompt(
        previous_qa: List[tuple[str, str]],
        current_question: str
    ) -> str:
        """
        构建追问提示（多轮对话）

        Args:
            previous_qa: 之前的问答对 [(question, answer), ...]
            current_question: 当前问题

        Returns:
            追问提示
        """
        history = []
        for i, (q, a) in enumerate(previous_qa, 1):
            history.append(f"【问题{i}】{q}")
            history.append(f"【回答{i}】{a[:200]}...")  # 只保留前200字

        history_text = "\n\n".join(history)

        prompt = f"""# 对话历史
{history_text}

# 当前问题
{current_question}

请基于之前的对话上下文，回答当前问题。注意保持话题的连贯性。

请开始回答："""

        return prompt

    @staticmethod
    def build_summary_prompt(
        conversation: List[tuple[str, str]]
    ) -> str:
        """
        构建对话总结提示

        Args:
            conversation: 对话历史 [(question, answer), ...]

        Returns:
            总结提示
        """
        qa_text = []
        for i, (q, a) in enumerate(conversation, 1):
            qa_text.append(f"Q{i}: {q}")
            qa_text.append(f"A{i}: {a}")

        conversation_text = "\n".join(qa_text)

        prompt = f"""请总结以下对话的核心内容：

{conversation_text}

总结要求：
1. 提取用户的主要问题和关切点
2. 概括给出的建议和方案
3. 列出关键的法律依据
4. 指出未解决的问题（如有）

请用3-5个要点进行总结："""

        return prompt

    @staticmethod
    def classify_question(question: str) -> str:
        """
        构建问题分类提示

        Args:
            question: 用户问题

        Returns:
            分类提示
        """
        prompt = f"""请判断以下问题的类型，从这些选项中选择一个：

1. 经济补偿 - 关于是否应该获得补偿、补偿条件等
2. 赔偿计算 - 需要计算具体金额（N、N+1、2N等）
3. 维权流程 - 询问如何维权、仲裁、诉讼等流程
4. 法律依据 - 询问相关法律条文和规定
5. 案例分析 - 询问类似案例或情况分析
6. 一般咨询 - 其他一般性问题

用户问题：{question}

请直接回答类型名称（如：赔偿计算）："""

        return prompt


def main():
    """测试Prompt模板"""
    print("🧪 测试 Prompt 模板")
    print("=" * 70)

    # 测试RAG Prompt
    print("\n[测试1] RAG Prompt")
    print("-" * 70)

    from ..models import Document, QuestionType

    docs = [
        Document(
            id="doc1",
            content="经济补偿按劳动者在本单位工作的年限，每满一年支付一个月工资的标准向劳动者支付。",
            source_url="https://example.com",
            section_title="经济补偿的标准"
        ),
        Document(
            id="doc2",
            content="用人单位未提前30日通知的，应额外支付一个月工资作为代通知金，这就是N+1补偿。",
            source_url="https://example.com",
            section_title="N+1补偿"
        )
    ]

    prompt = PromptTemplates.build_rag_prompt(
        question="如何计算N+1补偿？",
        context_documents=docs,
        question_type=QuestionType.CALCULATION
    )

    print(prompt[:500] + "...\n")

    # 测试计算Prompt
    print("\n[测试2] 计算 Prompt")
    print("-" * 70)

    calc_prompt = PromptTemplates.build_calculation_prompt(
        work_years=3.5,
        monthly_salary=8000,
        situation="公司提前通知解除劳动合同"
    )

    print(calc_prompt)

    print("\n" + "=" * 70)
    print("✅ 测试完成")


if __name__ == "__main__":
    main()
