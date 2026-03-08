from __future__ import annotations

from typing import Any, Dict, List


SEMANTIC_FIELDS: Dict[str, Dict[str, Any]] = {
    "trade": {
        "tokens": [
            "trade",
            "merchant",
            "shop",
            "market",
            "buy",
            "sell",
            "交易",
            "商人",
            "市场",
            "买",
            "卖",
            "货物",
            "商品",
            "集市",
        ],
        "poetic": ["商队", "铃声", "驼队", "货箱", "旅商"],
        "environment": ["帐篷", "车队", "商路"],
        "root": "trade_post",
    },
    "travel": {
        "tokens": [
            "travel",
            "journey",
            "road",
            "wander",
            "旅行",
            "旅途",
            "远方",
            "道路",
            "出发",
        ],
        "poetic": ["风", "脚步", "天际", "沙丘", "地平线"],
        "environment": ["沙漠", "草原", "道路"],
        "root": "road",
    },
    "explore": {
        "tokens": [
            "explore",
            "discover",
            "ruin",
            "cave",
            "探索",
            "遗迹",
            "洞穴",
            "废墟",
            "古城",
        ],
        "poetic": ["尘封", "古老", "失落", "石门", "遗忘"],
        "environment": ["地下", "矿道", "石门"],
        "root": "mine",
    },
}


SEMANTIC_COMBOS: List[Dict[str, Any]] = [
    {
        "requires": {"trade", "travel"},
        "semantic": "caravan_trade",
        "root": "trade_post_caravan_camp",
        "bonus": 2,
    }
]


TOKEN_WEIGHT = 5
POETIC_WEIGHT = 2
ENVIRONMENT_WEIGHT = 1


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _normalize_keyword(value: Any) -> str:
    return str(value or "").strip().lower()


def _dedupe_keywords(values: List[str]) -> List[str]:
    deduped: List[str] = []
    seen: set[str] = set()
    for value in values:
        token = str(value or "").strip()
        if not token or token in seen:
            continue
        seen.add(token)
        deduped.append(token)
    return deduped


def _score_domain(text: str, domain_rule: Dict[str, Any]) -> tuple[int, List[Dict[str, Any]]]:
    total = 0
    hits: List[Dict[str, Any]] = []

    for token in domain_rule.get("tokens") or []:
        normalized = _normalize_keyword(token)
        if normalized and normalized in text:
            total += TOKEN_WEIGHT
            hits.append({"keyword": str(token), "source": "token", "weight": TOKEN_WEIGHT})

    for token in domain_rule.get("poetic") or []:
        normalized = _normalize_keyword(token)
        if normalized and normalized in text:
            total += POETIC_WEIGHT
            hits.append({"keyword": str(token), "source": "poetic", "weight": POETIC_WEIGHT})

    for token in domain_rule.get("environment") or []:
        normalized = _normalize_keyword(token)
        if normalized and normalized in text:
            total += ENVIRONMENT_WEIGHT
            hits.append({"keyword": str(token), "source": "environment", "weight": ENVIRONMENT_WEIGHT})

    return total, hits


def _combo_from_scores(scores: Dict[str, int]) -> Dict[str, Any] | None:
    if not scores:
        return None

    for combo in SEMANTIC_COMBOS:
        required = combo.get("requires")
        if not isinstance(required, set) or not required:
            continue
        if any(scores.get(domain, 0) <= 0 for domain in required):
            continue

        bonus = int(combo.get("bonus") or 0)
        score = sum(int(scores.get(domain, 0)) for domain in required) + max(0, bonus)
        return {
            "semantic": str(combo.get("semantic") or "caravan_trade"),
            "predicted_root": str(combo.get("root") or "trade_post_caravan_camp"),
            "score": score,
        }

    return None


def infer_semantic_from_text(text: str | None) -> Dict[str, Any]:
    normalized_text = _normalize_text(text)
    if not normalized_text:
        return {
            "semantic": "ambient",
            "predicted_root": "camp",
            "score": 0,
            "all_scores": {},
            "matched_keywords": [],
            "resolution": [],
        }

    score_by_domain: Dict[str, int] = {}
    hits_by_domain: Dict[str, List[Dict[str, Any]]] = {}

    for domain, rule in SEMANTIC_FIELDS.items():
        score, hits = _score_domain(normalized_text, rule)
        if score <= 0:
            continue
        score_by_domain[domain] = int(score)
        hits_by_domain[domain] = list(hits)

    if not score_by_domain:
        return {
            "semantic": "ambient",
            "predicted_root": "camp",
            "score": 0,
            "all_scores": {},
            "matched_keywords": [],
            "resolution": [],
        }

    combo = _combo_from_scores(score_by_domain)

    ranked_resolution = sorted(
        (
            {
                "semantic": domain,
                "score": int(score),
                "matches": list(hits_by_domain.get(domain) or []),
            }
            for domain, score in score_by_domain.items()
        ),
        key=lambda row: (-int(row.get("score") or 0), str(row.get("semantic") or "")),
    )

    all_matched_keywords = _dedupe_keywords(
        [
            str(match.get("keyword") or "")
            for rows in hits_by_domain.values()
            for match in rows
            if isinstance(match, dict)
        ]
    )

    if combo:
        return {
            "semantic": combo["semantic"],
            "predicted_root": combo["predicted_root"],
            "score": int(combo.get("score") or 0),
            "all_scores": dict(score_by_domain),
            "matched_keywords": all_matched_keywords,
            "resolution": ranked_resolution,
        }

    best_domain = sorted(
        score_by_domain.items(),
        key=lambda row: (-int(row[1]), str(row[0])),
    )[0][0]

    predicted_root = str(SEMANTIC_FIELDS.get(best_domain, {}).get("root") or "camp")
    return {
        "semantic": best_domain,
        "predicted_root": predicted_root,
        "score": int(score_by_domain.get(best_domain, 0)),
        "all_scores": dict(score_by_domain),
        "matched_keywords": all_matched_keywords,
        "resolution": ranked_resolution,
    }
