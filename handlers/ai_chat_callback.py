"""AI tutor chat callback handler."""

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ContextTypes

from database import get_session
from models import User, AIChat, Topic
from sqlalchemy import select
from services.user_service import get_or_create_user
from services.ai_service import ask_ai_tutor


async def ai_chat_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle AI tutor interactions."""
    query = update.callback_query
    await query.answer()

    data = query.data  # ai_chat_{topic_id}, ai_ask, ai_clear
    user = query.from_user

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)

        if data.startswith("ai_chat_"):
            topic_id = int(data.replace("ai_chat_", ""))
            await start_ai_chat(query, db_user, topic_id, session, context)
        elif data == "ai_ask":
            await query.edit_message_text(
                "🤖 <b>ИИ-тьютр</b>\n\n"
                "Задай любой вопрос по теме. Я помогу разобраться!\n\n"
                "Напиши вопрос сообщением...",
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton("◀️ Назад", callback_data="menu_ai")
                ]]),
                parse_mode="HTML",
            )
            context.user_data["ai_chat_mode"] = True
        elif data == "ai_clear":
            await clear_ai_chat(query, db_user, session)


async def start_ai_chat(query, db_user: User, topic_id: int, session, context):
    """Start AI chat for a specific topic."""
    topic_result = await session.execute(
        select(Topic).where(Topic.id == topic_id)
    )
    topic = topic_result.scalar_one_or_none()

    if not topic:
        await query.edit_message_text("❌ Тема не найдена")
        return

    # Get recent chat history
    history_result = await session.execute(
        select(AIChat)
        .where(AIChat.user_id == db_user.id, AIChat.topic_id == topic_id)
        .order_by(AIChat.created_at.desc())
        .limit(10)
    )
    history = list(reversed(history_result.scalars().all()))

    text = f"🤖 <b>ИИ-тьютр: {topic.title}</b>\n\n"

    if history:
        text += "<b>История:</b>\n"
        for msg in history[-5:]:
            role = "👤" if msg.message_role == "user" else "🤖"
            text += f"{role} {msg.content[:100]}...\n"
        text += "\n"

    text += "Задай вопрос по этой теме:"

    context.user_data["ai_chat_topic"] = topic_id
    context.user_data["ai_chat_mode"] = True

    keyboard = [
        [InlineKeyboardButton("🗑 Очистить историю", callback_data="ai_clear")],
        [InlineKeyboardButton("◀️ К теме", callback_data=f"topic_{topic_id}")],
    ]

    await query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode="HTML",
    )


async def clear_ai_chat(query, db_user: User, session):
    """Clear AI chat history."""
    from models import AIChat
    await session.execute(
        AIChat.__table__.delete().where(AIChat.user_id == db_user.id)
    )
    await session.commit()

    await query.answer("История очищена", show_alert=True)
    await query.edit_message_text(
        "🤖 <b>ИИ-тьютр</b>\n\nИстория чата очичена. Задавай новые вопросы!",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("◀️ Назад", callback_data="menu_ai")
        ]]),
        parse_mode="HTML",
    )


# Message handler for AI chat (called from main.py message handler)
async def handle_ai_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle user message in AI chat mode."""
    if not context.user_data.get("ai_chat_mode"):
        return False

    topic_id = context.user_data.get("ai_chat_topic")
    if not topic_id:
        await update.message.reply_text("❌ Тема не выбрана. Используй меню ИИ-тьютра.")
        return True

    user = update.effective_user
    question = update.message.text

    async with get_session() as session:
        db_user = await get_or_create_user(session, user.id, user.username, user.first_name, user.last_name)

        # Save user message
        user_msg = AIChat(
            user_id=db_user.id,
            topic_id=topic_id,
            message_role="user",
            content=question,
        )
        session.add(user_msg)

        # Get AI response
        answer, tokens = await ask_ai_tutor(session, db_user, topic_id, question)

        # Save AI response
        ai_msg = AIChat(
            user_id=db_user.id,
            topic_id=topic_id,
            message_role="assistant",
            content=answer,
            tokens_used=tokens,
        )
        session.add(ai_msg)
        await session.commit()

    await update.message.reply_text(
        f"🤖 <b>ИИ-тьютр:</b>\n\n{answer}",
        parse_mode="HTML",
    )

    return True