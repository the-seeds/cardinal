from ..core.schema import Template


KBQA_TEMPLATE = Template("根据已知信息，简洁和专业地回答问题。\n\n" "已知信息：{context}\n\n" "问题：{question}")
