import asyncio

from app.services.ai_provider import ai_provider


class SecurityCopilot:
    @staticmethod
    async def respond(
        message: str,
        context: dict | None = None,
        history: list[dict] | None = None,
        provider: str | None = None,
    ) -> dict:
        context = context or {}
        history = history or []
        history_lines = []
        for item in history[-10:]:
            role = item.get("role", "user")
            content = item.get("content", "")
            if content:
                history_lines.append(f"{role.title()}: {content}")

        fallback = {
            "answer": (
                "SentinelAI Copilot analyzed your request. Prioritize containment, evidence collection, "
                "root cause isolation, and immediate hardening of exposed attack surfaces."
            )
        }

        try:
            ai_result = await asyncio.wait_for(
                ai_provider.complete_json(
                    system_prompt=(
                        "You are SentinelAI OS, a cybersecurity copilot. "
                        "Answer in concise SOC language with practical defensive steps. "
                        "Keep the conversation natural and helpful like a chat assistant."
                    ),
                    user_prompt=(
                        f"Conversation history:\n{chr(10).join(history_lines) if history_lines else 'None'}\n\n"
                        f"Latest user message: {message}\n"
                        f"Context: {context}"
                    ),
                    fallback=fallback,
                    provider=provider,
                ),
                timeout=60,
            )
        except TimeoutError:
            ai_result = {**fallback, "provider": "fallback", "error": "timeout"}
        except Exception:
            ai_result = {**fallback, "provider": "fallback"}

        status = "ready" if ai_result.get("provider") in {"openai", "gemini"} else "fallback"
        reason = ai_result.get("error")

        return {
            "answer": ai_result.get("answer", fallback["answer"]),
            "provider": ai_result.get("provider", "fallback"),
            "status": status,
            **({"reason": reason} if reason else {}),
        }
