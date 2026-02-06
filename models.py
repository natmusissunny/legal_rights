"""
数据模型定义
使用 Pydantic v2 进行数据验证
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class LegalSection(BaseModel):
    """法律章节模型"""
    title: str = Field(description="章节标题")
    content: str = Field(description="章节内容")
    subsections: List['LegalSection'] = Field(default=[], description="子章节列表")
    level: int = Field(default=1, description="标题层级")


class StructuredContent(BaseModel):
    """结构化内容模型"""
    url: str = Field(description="来源URL")
    title: str = Field(description="文档标题")
    sections: List[LegalSection] = Field(description="章节列表")
    scraped_at: datetime = Field(description="抓取时间")


class Document(BaseModel):
    """文档片段模型（用于向量检索）"""
    id: str = Field(description="文档唯一ID")
    content: str = Field(description="文档内容")
    source_url: str = Field(description="来源URL")
    section_title: Optional[str] = Field(default=None, description="所属章节标题")
    metadata: Dict[str, Any] = Field(default={}, description="元数据")
    embedding: Optional[List[float]] = Field(default=None, description="向量表示")


class QuestionType(str, Enum):
    """问题类型枚举"""
    COMPENSATION = "经济补偿"  # N补偿相关
    CALCULATION = "赔偿计算"  # 具体金额计算
    PROCEDURE = "维权流程"  # 如何维权
    LEGAL_BASIS = "法律依据"  # 法律条文查询
    CASE_ANALYSIS = "案例分析"  # 类似案例
    GENERAL = "一般咨询"  # 其他问题


class Answer(BaseModel):
    """答案模型"""
    question: str = Field(description="用户问题")
    answer_text: str = Field(description="答案正文")
    question_type: QuestionType = Field(description="问题类型")
    relevant_docs: List[Document] = Field(default=[], description="相关文档片段")
    confidence: float = Field(ge=0.0, le=1.0, description="置信度")
    sources: List[str] = Field(default=[], description="引用的URL来源")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")

    def display(self) -> str:
        """格式化显示答案"""
        output = []
        output.append("\n" + "=" * 80)
        output.append(f"📝 问题: {self.question}")
        output.append(f"🏷️  类型: {self.question_type.value}")
        output.append("=" * 80)
        output.append(f"\n💡 解答:\n{self.answer_text}\n")

        if self.sources:
            output.append("📖 法律依据和来源:")
            for i, source in enumerate(self.sources, 1):
                output.append(f"   {i}. {source}")

        output.append(f"\n📊 置信度: {self.confidence:.2%}")
        output.append("\n⚠️  免责声明: 本回答仅供参考，具体情况请咨询专业律师。")
        output.append("=" * 80 + "\n")

        return "\n".join(output)


class ConversationTurn(BaseModel):
    """对话轮次模型"""
    question: str = Field(description="用户问题")
    answer: Answer = Field(description="AI回答")
    timestamp: datetime = Field(default_factory=datetime.now, description="时间戳")


class ConversationContext(BaseModel):
    """对话上下文模型"""
    turns: List[ConversationTurn] = Field(default=[], description="对话历史")
    user_info: Dict[str, Any] = Field(default={}, description="用户信息（可选）")

    def add_turn(self, question: str, answer: Answer):
        """添加一轮对话"""
        turn = ConversationTurn(question=question, answer=answer)
        self.turns.append(turn)

    def get_recent_turns(self, n: int = 3) -> List[ConversationTurn]:
        """获取最近N轮对话"""
        return self.turns[-n:] if len(self.turns) > n else self.turns

    def reset(self):
        """重置对话历史"""
        self.turns = []
        self.user_info = {}


# 启用嵌套模型的前向引用
LegalSection.model_rebuild()
