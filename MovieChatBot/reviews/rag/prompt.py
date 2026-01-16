def build_prompt(question: str, contexts: list[dict]):
    context_text = "\n\n---\n\n".join(c.get("doc", "") for c in contexts)

    return f"""
너는 영화 추천/정보 챗봇이다.
아래 [영화 데이터]에 있는 정보만 근거로 답해라.
모르면 'DB에 정보가 없어요'라고 말해라.

[영화 데이터]
{context_text}

[질문]
{question}
""".strip()
