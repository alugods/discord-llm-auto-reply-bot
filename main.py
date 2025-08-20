import os
import json
import random
import asyncio
import time
from dotenv import load_dotenv
import discord
from discord.ext import commands, tasks
import google.generativeai as genai
from collections import deque

# Load config & secrets
load_dotenv()
with open('config.json') as f:
    config = json.load(f)

TOKEN = os.getenv("DISCORD_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
TRIGGER_KEYWORDS = config.get("trigger_keywords", [])
REPLY_PROBABILITY = config.get("reply_probability", 0.8) #set here and on config.json too for reply probability (optional)
DEFAULT_RESPONSE = config.get("default_response", "Interesting.")
TARGET_GUILD_ID = config.get("target_guild_id")
TARGET_CHANNEL_ID = config.get("target_channel_id")
PERSONA_PROMPT = config.get("persona_prompt")
EXCLUDED_BOT_IDS = config.get("excluded_bot_ids", [])  # ⛔ Daftar bot yang di-skip

# Init Gemini
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# Init Discord bot — NO intents
bot = commands.Bot(command_prefix="!", self_bot=True)

priority_buffer = deque(maxlen=2)
message_buffer = deque(maxlen=35)
conversation_history = {}      # {user_id: [msg1, msg2, ...]}
history_timestamp = {}         # {user_id: last_interaction_time}

BAD_REPLIES = ["ok", "okay", "yes", "cool", "haha", "lmao"]

@bot.event
async def on_ready():
    print(f"[READY] Logged in as {bot.user}")
    auto_reply_loop.start()

@bot.event
async def on_message(message):
    if message.author == bot.user:
        return

    # ⛔ Skip jika pesan dari bot lain yang dikecualikan
    if message.author.id in EXCLUDED_BOT_IDS:
        return

    if message.guild and message.guild.id == TARGET_GUILD_ID and message.channel.id == TARGET_CHANNEL_ID:
        content = message.content.lower() if message.content else ""

        is_reply_to_bot = (
            message.reference
            and isinstance(message.reference.resolved, discord.Message)
            and message.reference.resolved.author.id == bot.user.id
        )

        if any(bad == content.strip() for bad in BAD_REPLIES) or len(content) < 17:
            return  # Skip pesan pendek

        if is_reply_to_bot:
            user_id = message.author.id
            prev = message.reference.resolved.content

            # Simpan history
            conversation_history.setdefault(user_id, []).append(f"Bot: {prev}")
            conversation_history[user_id].append(f"User: {message.content}")
            conversation_history[user_id] = conversation_history[user_id][-6:]

            # Update timestamp
            history_timestamp[user_id] = time.time()

            priority_buffer.append(message)

        elif any(kw in content for kw in TRIGGER_KEYWORDS):
            if random.random() <= REPLY_PROBABILITY:
                message_buffer.append(message)

    await bot.process_commands(message)

@tasks.loop(seconds=10)
async def auto_reply_loop():
    if not priority_buffer and not message_buffer:
        return

    # Clean expired history (older than 30 minutes = 1800 seconds)
    now = time.time()
    for uid in list(conversation_history.keys()):
        last = history_timestamp.get(uid, 0)
        if now - last > 1800:
            conversation_history.pop(uid, None)
            history_timestamp.pop(uid, None)

    wait_time = random.randint(70, 120)
    await asyncio.sleep(wait_time)

    message = None
    if priority_buffer:
        message = priority_buffer.popleft()
    elif message_buffer:
        message = message_buffer.popleft()

    if not message:
        return

    # ⛔ Jangan balas bot yang dikecualikan
    if message.author.id in EXCLUDED_BOT_IDS:
        print(f"[SKIP] Message from excluded bot: {message.author.name}")
        return

    try:
        user_id = message.author.id
        reply = await generate_reply(message.content, user_id)
        if reply:
            await message.reply(reply)
            print(f"[REPLIED] {message.author.name}: {reply}")

            # Update conversation + timestamp
            conversation_history.setdefault(user_id, []).append(f"Bot: {reply}")
            conversation_history[user_id] = conversation_history[user_id][-6:]
            history_timestamp[user_id] = time.time()
    except Exception as e:
        print(f"[ERROR] {e}")

async def generate_reply(content, user_id=None):
    history = conversation_history.get(user_id, [])
    formatted_history = "\n".join(history)

    full_prompt = (
        f"{PERSONA_PROMPT}\n\n"
        f"Here's the conversation so far:\n{formatted_history}\n"
        f"Now the user said: \"{content}\"\n"
        f"Reply naturally and chill like a role model."
    )
    response = model.generate_content(full_prompt)
    if response and response.text:
        return response.text.strip()
    else:
        return DEFAULT_RESPONSE

bot.run(TOKEN)

