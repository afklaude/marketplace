# AFKlaude

Let Claude cook. Approve requests from your phone while you're AFK.

## Install

```
/plugin marketplace add afklaude/marketplace
/plugin install afk@afklaude
```

## Configure

Add to your Claude Code settings at any level:

| Level | File Path | Use Case |
|-------|-----------|----------|
| User | `~/.claude/settings.json` | Available in all projects |
| Project | `.claude/settings.json` | Shared with team (committed to git) |
| Local | `.claude/settings.local.json` | Personal project override (gitignored) |

```json
{
  "env": {
    "AFKLAUDE_TOKEN": "your-api-key"
  }
}
```

## Commands

- `/afk:afk` — Enable AFK mode. Requests go to Slack/Discord.
- `/afk:back` — Disable AFK mode. Back to normal prompts.

## License

MIT
