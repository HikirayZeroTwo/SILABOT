import re
from typing import Dict

from aiogram import Bot, Router
from aiogram.filters import BaseFilter, Command, CommandObject
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
import config
import random

router = Router()
user_points: Dict[int, int] = {}


class HelpRequest(StatesGroup):
    waiting_for_text = State()


def normalize_text(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\sа-яё]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", " ", text).strip()


def get_user_points(user_id: int) -> int:
    return user_points.get(user_id, 100)


def add_user_points(user_id: int, delta: int) -> int:
    new_points = get_user_points(user_id) + delta
    if new_points < 0:
        new_points = 0
    user_points[user_id] = new_points
    return new_points

class IsInConfigSila(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        normalized_text = normalize_text(message.text)
        return normalized_text in config.sila

class IsInConfigPlaki(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        if not message.text:
            return False
        normalized_text = normalize_text(message.text)
        return normalized_text in config.plaki

@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "Приветики пистолетики, я бот сили💪\n"
        "Отправь мне сообщение о том что ты сильни, я дам тебе очков💯\n\n"
        "Или беги в менюшку -> /menu\n"
    )


@router.message(Command("menu"))
async def menu(message: Message):
    await message.answer(
        'Команды:\n'
        "/points - пасматри скока у тибя ачков💯\n"
        "/motivation - рандомная мотивашка💞\n"
        "/pomogi - пожалуйся мине сюда🥺\n"
        "/help - подсказка по командамℹ️\n"
    )

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "Я даю тибе очки за то что ти сильни💪\n\n"
        "Как это работает:\n"
        "- Напиши: Я сильная -> +10 очков\n"
        "- Команда /points покажет твои очечки\n"
        "- Команда /motivation даст мотивашку\n"
        "- Команда /pomogi отправит мне твою жалобку"
    )

@router.message(Command('motivation'))
async def motivation(message: Message):
    rnd = random.choice(config.motivation)
    await message.answer(rnd)

@router.message(Command('points'))
async def points(message: Message):
    user_id = message.from_user.id
    points_value = get_user_points(user_id)
    await message.answer(f'У тебя: {points_value} очков силы 💪')

@router.message(Command('pomogi'))
async def pomogi(message: Message, command: CommandObject, state: FSMContext):
    help_text = (command.args or "").strip()
    if help_text:
        await send_to_admin(message, help_text)
        await message.answer("Отправил бяке. Ты молодечик, что написала🥺💕")
        return

    await state.set_state(HelpRequest.waiting_for_text)
    await message.answer("Напиши, что случилось, и я передам бяке")


@router.message(HelpRequest.waiting_for_text)
async def pomogi_text(message: Message, state: FSMContext):
    text = (message.text or "").strip()
    if not text:
        await message.answer("Я могу передать только текстовое сообщение. Попробуй еще раз.")
        return

    await send_to_admin(message, text)
    await state.clear()
    await message.answer("Сообщение отправлено бяке. Скоро он тибе ответит 💋")


async def send_to_admin(message: Message, text: str) -> None:
    if not config.SUPPORT_BOT_TOKEN or not config.SUPPORT_CHAT_ID:
        await message.answer("Сервис помощи пока не настроен. Попробуй чуть позже.")
        return

    username = f"@{message.from_user.username}" if message.from_user.username else "без username"
    admin_text = (
        "Новое сообщение через /pomogi\n"
        f"User ID: {message.from_user.id}\n"
        f"Username: {username}\n"
        f"Имя: {message.from_user.full_name}\n\n"
        f"Текст:\n{text}"
    )
    support_bot = Bot(token=config.SUPPORT_BOT_TOKEN)
    try:
        await support_bot.send_message(chat_id=config.SUPPORT_CHAT_ID, text=admin_text)
    finally:
        await support_bot.session.close()


@router.message(IsInConfigSila())
async def sila(message: Message):
    user_id = message.from_user.id
    new_points = add_user_points(user_id, 10)
    await message.answer(
        'Умничкааа, ты стала сильнее 💋\n'
        f'У тебя: {new_points} очков силы 💪'
    )
    
@router.message(IsInConfigPlaki())
async def plaki(message: Message):
    user_id = message.from_user.id
    new_points = add_user_points(user_id, -10)
    await message.answer(
        'Не обесценивай себя котя, -10 очков 😫\n'
        f'У тебя: {new_points} очков силы 💪'
    )
    
@router.message()
async def echo_msg(message: Message):
    await message.answer('Не пон. Попробуй /menu или /help 😨')