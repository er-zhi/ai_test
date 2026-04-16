# ai_test

Test repo for **Kai** (Kodif AI) — powered by `claude-code-action`.

## Usage

Mention `@kai` in any PR comment or issue to trigger the bot:

```
@kai review this PR
@kai fix the failing test
@kai explain the changes in auth.ts
@kai run tests and report results
```

## Notification Service

**Multi-channel notification support:**
- **Email**: SMTP-based delivery
- **Slack**: Webhook integration for channel notifications
- **Telegram**: Bot API for direct messages

Features: bulk send, auto-retry, notification history, 30-day retention cleanup. All notifications are stored in SQLite for history lookup and audit tracking.

## Setup

1. Add `ANTHROPIC_API_KEY` to repo secrets
2. The workflow in `.github/workflows/kai.yml` handles the rest
