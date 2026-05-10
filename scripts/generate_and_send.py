#!/usr/bin/env python3
"""
Generate an AI / computational materials briefing with OpenAI Responses API
and send it by SMTP email.

Secrets are read from environment variables. Never hard-code passwords or keys.
"""

from __future__ import annotations

import argparse
import os
import smtplib
import ssl
import sys
import traceback
from datetime import datetime, timezone, timedelta
from email.message import EmailMessage
from pathlib import Path

from openai import OpenAI


ROOT = Path(__file__).resolve().parents[1]
PROMPT_DIR = ROOT / "prompts"


SUBJECTS = {
    "daily": "每日 AI 前沿简报｜ChatGPT / Claude / Gemini / DeepSeek",
    "weekly": "每周 AI 与金属计算材料学前沿周报",
}


def env(name: str, default: str | None = None, required: bool = False) -> str:
    value = os.getenv(name, default)
    if required and not value:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value or ""


def beijing_now() -> str:
    tz = timezone(timedelta(hours=8))
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")


def load_prompt(kind: str) -> str:
    prompt_file = PROMPT_DIR / f"{kind}.md"
    if not prompt_file.exists():
        raise FileNotFoundError(f"Prompt file not found: {prompt_file}")

    date_hint = f"\n\n当前北京时间：{beijing_now()}。\n请优先筛选最近、可靠、可验证的信息。"
    return prompt_file.read_text(encoding="utf-8") + date_hint


def extract_text(response) -> str:
    # Recent OpenAI SDKs expose output_text. Keep a fallback for safety.
    text = getattr(response, "output_text", None)
    if text:
        return text.strip()

    chunks: list[str] = []
    for item in getattr(response, "output", []) or []:
        for content in getattr(item, "content", []) or []:
            value = getattr(content, "text", None)
            if value:
                chunks.append(value)
    return "\n".join(chunks).strip()


def generate_report(kind: str) -> str:
    client = OpenAI(api_key=env("OPENAI_API_KEY", required=True))
    model = env("OPENAI_MODEL", "gpt-4.1-mini")
    prompt = load_prompt(kind)

    # Prefer the GA web_search tool. If unavailable in the account/model,
    # fall back to the preview tool.
    last_error: Exception | None = None
    for tool_type in ("web_search", "web_search_preview"):
        try:
            response = client.responses.create(
                model=model,
                tools=[{"type": tool_type}],
                tool_choice="auto",
                input=prompt,
            )
            text = extract_text(response)
            if not text:
                raise RuntimeError("OpenAI response was empty.")
            return text
        except Exception as exc:  # noqa: BLE001
            last_error = exc

    raise RuntimeError(f"Failed to generate report: {last_error}") from last_error


def build_email(subject: str, body: str) -> EmailMessage:
    mail_from = env("MAIL_FROM", env("SMTP_USER"), required=True)
    mail_to = env("MAIL_TO", required=True)

    msg = EmailMessage()
    msg["From"] = mail_from
    msg["To"] = mail_to
    msg["Subject"] = subject
    msg.set_content(body, subtype="plain", charset="utf-8")
    return msg


def send_email(subject: str, body: str) -> None:
    smtp_host = env("SMTP_HOST", required=True)
    smtp_port = int(env("SMTP_PORT", "465"))
    smtp_user = env("SMTP_USER", required=True)
    smtp_password = env("SMTP_PASSWORD", required=True)
    use_ssl = env("SMTP_SSL", "true").lower() in {"1", "true", "yes", "y"}

    msg = build_email(subject, body)

    if use_ssl:
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL(smtp_host, smtp_port, context=context, timeout=60) as server:
            server.login(smtp_user, smtp_password)
            server.send_message(msg)
    else:
        with smtplib.SMTP(smtp_host, smtp_port, timeout=60) as server:
            server.starttls(context=ssl.create_default_context())
            server.login(smtp_user, smtp_password)
            server.send_message(msg)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--kind", choices=["daily", "weekly"], required=True)
    args = parser.parse_args()

    subject = SUBJECTS[args.kind]

    try:
        report = generate_report(args.kind)
        footer = (
            "\n\n---\n"
            f"自动生成时间：北京时间 {beijing_now()}\n"
            "说明：请自行核验关键事实与来源；不要把自动简报当作唯一依据。\n"
        )
        send_email(subject, report + footer)
        print(f"Sent {args.kind} report successfully.")
        return 0
    except Exception as exc:  # noqa: BLE001
        error_body = (
            f"{subject} 生成或发送失败。\n\n"
            f"北京时间：{beijing_now()}\n"
            f"错误类型：{type(exc).__name__}\n"
            f"错误信息：{exc}\n\n"
            "Traceback:\n"
            f"{traceback.format_exc()}\n"
        )

        # Try to send a failure email if SMTP is configured.
        try:
            send_email(f"[失败] {subject}", error_body)
        except Exception:
            print("Failed to send failure email.", file=sys.stderr)
            print(error_body, file=sys.stderr)

        raise


if __name__ == "__main__":
    raise SystemExit(main())
