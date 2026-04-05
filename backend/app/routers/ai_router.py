# backend/app/routers/ai_router.py
from fastapi import APIRouter
from pydantic import BaseModel
from typing import Any, Dict, Optional, List

from app.core.ai.intent_engine import parse_intent
from app.core.story.story_engine import story_engine

router = APIRouter(prefix="/ai", tags=["AI"])

# ================================
# Drift → AsyncAIFlow Bridge
# ================================
_ASYNCAIFLOW_URL = "http://localhost:8080/run"
_recent_issues: set = set()


def _looks_like_issue(text: str) -> bool:
    keywords = ["修复", "bug", "问题", "异常", "不生效", "报错"]
    return any(k in text for k in keywords)


def _forward_to_asyncaiflow(raw: str) -> None:
    """Fire-and-forget：把 issue 转发给 AsyncAIFlow，失败一律静默。"""
    issue = raw[:128]  # Phase 3: 输入截断
    if issue in _recent_issues:  # Phase 3: 防重复触发
        return
    _recent_issues.add(issue)
    if len(_recent_issues) > 200:  # 防止集合无限增长
        _recent_issues.clear()
    print(f"[Drift→AsyncAIFlow] issue={issue}")  # Phase 4: 可观测性日志
    try:
        import httpx
        with httpx.Client(trust_env=False) as client:
            resp = client.post(
                _ASYNCAIFLOW_URL,
                json={
                    "issue": issue,
                    "repo_context": "drift-system",
                    "file": "backend",
                },
                timeout=1.5,  # Phase 3: 防阻塞 ≤ 2s
            )
        print(f"[Drift→AsyncAIFlow] resp={resp.status_code} workflowId={resp.json().get('data',{}).get('workflowId','?')}")
    except Exception as e:
        print(f"[Drift→AsyncAIFlow] ERROR: {type(e).__name__}: {e}")  # 容错，不影响 Drift 主流程


# ================================
# 请求模型
# ================================
class IntentRequest(BaseModel):
    player_id: str = "default"
    text: str
    world_state: Optional[Dict[str, Any]] = None


# ================================
# 返回模型（⭐ 多意图版）
# ================================
class IntentResponse(BaseModel):
    status: str
    intents: List[Dict[str, Any]]


# ================================
# 路由：多意图自然语言解析
# ================================
@router.post("/intent", response_model=IntentResponse)
def ai_intent(req: IntentRequest):
    """
    玩家一句自然语言 → 多意图解析
    不推进剧情，只返回：
    {
      "status": "ok",
      "intents": [ ... ]
    }
    """
    result = parse_intent(
        player_id=req.player_id,
        text=req.text,
        world_state=req.world_state or {},
        story_engine=story_engine,
    )

    # Phase 1: Drift → AsyncAIFlow Bridge Hook（在 return 前）
    for intent in result["intents"]:
        raw = intent.get("raw_text", "")
        if raw and _looks_like_issue(raw):
            _forward_to_asyncaiflow(raw)

    # parse_intent 已经返回 {status, intents}
    return IntentResponse(
        status=result["status"],
        intents=result["intents"]
    )