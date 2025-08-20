# 🤖 Discord LLM Auto-Reply Bot

> AI-powered Discord companion with persona customization, smart reply probability, async delays, keyword triggers, excluded IDs, and short-term conversation memory.

⚠️ **Disclaimer**  
This project is for **educational and experimental purposes only**.  
Using selfbots violates [Discord's Terms of Service](https://discord.com/terms).  
**Use at your own risk** — all consequences (ban, account termination, etc.) are your sole responsibility.  
By using this tool, you acknowledge you are doing so **consciously and responsibly**.

---

## ✨ Features

- 🎭 **Custom Persona** — controlled via `persona_prompt` on config.json
- ⏱ **Natural Delay** — random reply delay (70–120s) with async scheduling
- 🧠 **Conversation Memory** — per-user history (up to 6 messages), auto-expiring after 30 minutes
- 🎲 **Reply Probability** — control how often the bot replies
- 🔑 **Trigger Keywords** — replies only when specific keywords are detected
- 🚫 **Excluded IDs** — skip certain user/bot IDs
- 🧠 **LLM Powered** — by Google **Gemini 2.5 Flash**

---

## ⚙️ Configuration

This project uses **two config files**: `.env` (for tokens and api) and `config.json` (for bot settings).

---

### 1) Environment Variables (`.env`)

Create a `.env` file in the project root (or copy from the example):
```bash
cp .env.example .env
```

## 📦 Installation

Clone the repo and install dependencies:

```bash
git clone https://github.com/USERNAME/discord-llm-auto-reply-bot.git
cd discord-llm-auto-reply-bot
pip install -r requirements.txt
```

![Visitor Count](https://hits.seeyoufarm.com/api/count/incr/badge.svg?url=https://github.com/alugods/discord-llm-auto-reply-bot&title=Visitors)



