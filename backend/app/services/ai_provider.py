import json
from typing import Any

from app.core.config import settings


class AIProvider:
    def __init__(self) -> None:
        # Defer heavy client initialization until first use to avoid import-time failures.
        self.openai_client = None
        self.gemini_model = None
        self.langchain_openai = None
        self.langchain_gemini = None
        self._initialized = False

    def _ensure_initialized(self) -> None:
        if self._initialized:
            return
        self._initialized = True

        chatgpt_key = settings.chatgpt_api_key or settings.openai_api_key
        if chatgpt_key:
            try:
                from openai import AsyncOpenAI

                self.openai_client = AsyncOpenAI(api_key=chatgpt_key)
            except Exception:
                self.openai_client = None

        if settings.gemini_api_key:
            try:
                import google.generativeai as genai

                genai.configure(api_key=settings.gemini_api_key)
                self.gemini_model = genai.GenerativeModel(settings.gemini_model)
            except Exception:
                self.gemini_model = None

        try:
            from langchain_google_genai import ChatGoogleGenerativeAI
            from langchain_openai import ChatOpenAI

            if chatgpt_key:
                try:
                    self.langchain_openai = ChatOpenAI(
                        api_key=chatgpt_key,
                        model=settings.openai_model,
                        temperature=0.2,
                    )
                except Exception:
                    self.langchain_openai = None
            if settings.gemini_api_key:
                try:
                    self.langchain_gemini = ChatGoogleGenerativeAI(
                        google_api_key=settings.gemini_api_key,
                        model=settings.gemini_model,
                        temperature=0.2,
                    )
                except Exception:
                    self.langchain_gemini = None
        except Exception:
            self.langchain_openai = None
            self.langchain_gemini = None

    @staticmethod
    def _extract_json(content: str) -> dict[str, Any] | None:
        try:
            return json.loads(content)
        except Exception:
            start = content.find("{")
            end = content.rfind("}")
            if start != -1 and end != -1 and end > start:
                try:
                    return json.loads(content[start : end + 1])
                except Exception:
                    return None
        return None

    async def _complete_with_langchain(self, model: Any, system_prompt: str, user_prompt: str) -> dict[str, Any] | None:
        try:
            from langchain_core.messages import HumanMessage, SystemMessage

            response = await model.ainvoke([SystemMessage(content=system_prompt), HumanMessage(content=user_prompt)])
            content = getattr(response, "content", "") or ""
            parsed = self._extract_json(content)
            if parsed is not None:
                return parsed
        except Exception:
            return None
        return None

    async def complete_json(
        self,
        system_prompt: str,
        user_prompt: str,
        fallback: dict[str, Any],
        provider: str | None = None,
    ) -> dict[str, Any]:
        # Ensure provider clients are initialized lazily
        self._ensure_initialized()

        requested_provider = (provider or "auto").lower()

        if requested_provider in {"auto", "openai"}:
            result = None
            if self.langchain_openai:
                result = await self._complete_with_langchain(self.langchain_openai, system_prompt, user_prompt)
            if result is None and self.openai_client:
                try:
                    response = await self.openai_client.chat.completions.create(
                        model=settings.openai_model,
                        response_format={"type": "json_object"},
                        messages=[
                            {"role": "system", "content": system_prompt},
                            {"role": "user", "content": user_prompt},
                        ],
                        temperature=0.2,
                    )
                    content = response.choices[0].message.content or "{}"
                    result = self._extract_json(content)
                except Exception:
                    result = None

            if result is not None:
                result.setdefault("provider", "openai")
                return result

            if requested_provider == "openai":
                fallback.setdefault("provider", "fallback")
                return fallback

        if requested_provider in {"auto", "gemini"}:
            result = None
            if self.langchain_gemini:
                result = await self._complete_with_langchain(self.langchain_gemini, system_prompt, user_prompt)
            if result is None and self.gemini_model:
                try:
                    prompt = (
                        f"{system_prompt}\n\n"
                        "Respond ONLY with a valid JSON object.\n"
                        f"User request:\n{user_prompt}"
                    )
                    response = await self.gemini_model.generate_content_async(prompt)
                    text = response.text.strip()
                    result = self._extract_json(text)
                except Exception:
                    result = None

            if result is not None:
                result.setdefault("provider", "gemini")
                return result

        fallback.setdefault("provider", "fallback")
        return fallback


ai_provider = AIProvider()
