"""
对话管理器
管理多轮对话的上下文和历史
"""
from typing import List, Optional
from datetime import datetime

from ..models import ConversationContext, ConversationTurn, Answer


class ConversationManager:
    """对话管理器"""

    def __init__(self, max_history: int = 10):
        """
        初始化对话管理器

        Args:
            max_history: 最大保留的对话轮数
        """
        self.context = ConversationContext()
        self.max_history = max_history

    def add_turn(self, question: str, answer: Answer):
        """
        添加一轮对话

        Args:
            question: 用户问题
            answer: AI回答
        """
        self.context.add_turn(question, answer)

        # 限制历史长度
        if len(self.context.turns) > self.max_history:
            self.context.turns = self.context.turns[-self.max_history:]

    def get_recent_turns(self, n: int = 3) -> List[ConversationTurn]:
        """
        获取最近的对话

        Args:
            n: 获取最近N轮

        Returns:
            对话轮次列表
        """
        return self.context.get_recent_turns(n)

    def get_conversation_history(self) -> List[tuple[str, str]]:
        """
        获取对话历史（问答对格式）

        Returns:
            [(question, answer_text), ...]
        """
        return [
            (turn.question, turn.answer.answer_text)
            for turn in self.context.turns
        ]

    def get_messages_for_claude(self, include_last: int = 5) -> List[dict]:
        """
        获取适合Claude API的消息格式

        Args:
            include_last: 包含最近N轮对话

        Returns:
            [{"role": "user/assistant", "content": "..."}, ...]
        """
        messages = []
        recent_turns = self.context.turns[-include_last:] if include_last > 0 else []

        for turn in recent_turns:
            messages.append({
                "role": "user",
                "content": turn.question
            })
            messages.append({
                "role": "assistant",
                "content": turn.answer.answer_text
            })

        return messages

    def has_context(self) -> bool:
        """
        是否有对话上下文

        Returns:
            是否有历史对话
        """
        return len(self.context.turns) > 0

    def get_last_question_type(self) -> Optional[str]:
        """
        获取上一个问题的类型

        Returns:
            问题类型
        """
        if not self.context.turns:
            return None
        return self.context.turns[-1].answer.question_type.value

    def reset(self):
        """重置对话历史"""
        self.context.reset()

    def set_user_info(self, key: str, value):
        """
        设置用户信息

        Args:
            key: 信息键
            value: 信息值
        """
        self.context.user_info[key] = value

    def get_user_info(self, key: str, default=None):
        """
        获取用户信息

        Args:
            key: 信息键
            default: 默认值

        Returns:
            信息值
        """
        return self.context.user_info.get(key, default)

    def extract_user_situation(self) -> dict:
        """
        从对话中提取用户情况

        Returns:
            用户情况字典
        """
        situation = {
            "work_years": self.get_user_info("work_years"),
            "monthly_salary": self.get_user_info("monthly_salary"),
            "termination_reason": self.get_user_info("termination_reason"),
            "notice_period": self.get_user_info("notice_period"),
        }

        # 从对话历史中提取信息
        for turn in self.context.turns:
            question = turn.question.lower()

            # 尝试提取工作年限
            if "年" in question and not situation["work_years"]:
                import re
                match = re.search(r'(\d+\.?\d*)\s*年', question)
                if match:
                    situation["work_years"] = float(match.group(1))

            # 尝试提取工资
            if "工资" in question or "薪资" in question:
                import re
                match = re.search(r'(\d+)', question)
                if match and not situation["monthly_salary"]:
                    situation["monthly_salary"] = int(match.group(1))

        return situation

    def get_summary(self) -> str:
        """
        获取对话摘要

        Returns:
            对话摘要文本
        """
        if not self.context.turns:
            return "暂无对话历史"

        lines = [
            f"对话轮数: {len(self.context.turns)}",
            f"问题类型: {', '.join(set(t.answer.question_type.value for t in self.context.turns))}",
        ]

        # 如果有用户信息，添加到摘要
        if self.context.user_info:
            lines.append("\n用户情况:")
            for key, value in self.context.user_info.items():
                if value:
                    lines.append(f"  - {key}: {value}")

        # 最近3个问题
        recent = self.get_recent_turns(3)
        if recent:
            lines.append("\n最近问题:")
            for i, turn in enumerate(recent, 1):
                lines.append(f"  {i}. {turn.question}")

        return "\n".join(lines)


def main():
    """测试对话管理器"""
    print("🧪 测试对话管理器")
    print("=" * 70)

    from ..models import Answer, QuestionType

    manager = ConversationManager(max_history=5)

    # 模拟对话
    print("\n[测试1] 添加对话")
    print("-" * 70)

    # 第一轮
    answer1 = Answer(
        question="我在公司工作了3年被辞退，有补偿吗？",
        answer_text="根据劳动法，工作满一年的员工被辞退应该获得经济补偿...",
        question_type=QuestionType.COMPENSATION,
        confidence=0.9,
        sources=["https://example.com"]
    )
    manager.add_turn(answer1.question, answer1)

    # 第二轮
    answer2 = Answer(
        question="怎么计算补偿金？",
        answer_text="补偿金 = 工作年限 × 月平均工资...",
        question_type=QuestionType.CALCULATION,
        confidence=0.95,
        sources=["https://example.com"]
    )
    manager.add_turn(answer2.question, answer2)

    # 第三轮
    answer3 = Answer(
        question="如果公司不给怎么办？",
        answer_text="您可以申请劳动仲裁...",
        question_type=QuestionType.PROCEDURE,
        confidence=0.85,
        sources=["https://example.com"]
    )
    manager.add_turn(answer3.question, answer3)

    print(f"✅ 已添加 {len(manager.context.turns)} 轮对话")

    # 测试获取历史
    print("\n[测试2] 获取对话历史")
    print("-" * 70)

    history = manager.get_conversation_history()
    for i, (q, a) in enumerate(history, 1):
        print(f"\n轮次 {i}:")
        print(f"  问: {q}")
        print(f"  答: {a[:50]}...")

    # 测试Claude消息格式
    print("\n[测试3] Claude消息格式")
    print("-" * 70)

    messages = manager.get_messages_for_claude(include_last=2)
    for msg in messages:
        print(f"{msg['role']:10s}: {msg['content'][:60]}...")

    # 测试用户信息
    print("\n[测试4] 用户信息")
    print("-" * 70)

    manager.set_user_info("work_years", 3)
    manager.set_user_info("monthly_salary", 8000)

    situation = manager.extract_user_situation()
    print("提取的用户情况:")
    for key, value in situation.items():
        if value:
            print(f"  {key}: {value}")

    # 测试摘要
    print("\n[测试5] 对话摘要")
    print("-" * 70)

    summary = manager.get_summary()
    print(summary)

    print("\n" + "=" * 70)
    print("✅ 测试完成")


if __name__ == "__main__":
    main()
