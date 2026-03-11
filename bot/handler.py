from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from core.agent import Agent
import asyncio

router= Router()
reminder_days = None
agent = None
my_id = None
def init_agent(cfg):
    global agent, my_id, router,reminder_days
    agent = Agent(cfg)
    my_id = cfg["telegram"]["my_id"]
    
    reminder_days = cfg["telegram"]["reminder_days"]
    router.message.filter(F.from_user.id == my_id)


class NewNoteStates(StatesGroup):
    waiting_for_title = State()
    waiting_for_content = State()



@router.message(Command('start'))
async def start_handler(message: Message):
    await message.answer("Привет! Я твой Obsidian агент \n\n/ask - спросить\n/connections - связи\n/stale - старые заметки\n/new - создать заметку")

@router.message(Command('ask'))
async def ask_handler(message: Message):
    if message.from_user.id != my_id:
        return
    question= message.text.removeprefix('/ask').strip()
    if not question:
        await message.answer("Напиши вопрос: /ask что такое функции")
        return

    await message.answer("🔍 Ищу в заметках...")
    answer = await asyncio.to_thread(agent.answer_question, question)
    await message.answer(answer)

@router.message(Command('connections'))
async def connection_handler(message: Message):
    file=message.text.removeprefix('/connections').strip()
    if not file:
        await message.answer("укажите файл")
        return
    result = await asyncio.to_thread(agent.find_connection, file)
    await message.answer(result) 

@router.message(Command('stale'))
async def stale_handler(message: Message):
    result = await asyncio.to_thread(agent.get_stale_notes, reminder_days)  # ← to_thread + reminder_days
    await message.answer(result)

@router.message(Command('new'))
async def new_handler(message: Message, state: FSMContext):
    await state.set_state(NewNoteStates.waiting_for_title)
    await message.answer("Введи название заметки:")

@router.message(NewNoteStates.waiting_for_title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await state.set_state(NewNoteStates.waiting_for_content)
    await message.answer("Теперь введи текст заметки:")

@router.message(NewNoteStates.waiting_for_content)
async def get_content(message: Message, state: FSMContext):
    data = await state.get_data()
    title = data["title"]
    path = await asyncio.to_thread(agent.create_note, title, message.text)
    await state.clear()
    await message.answer(f" Заметка создана: {path}")