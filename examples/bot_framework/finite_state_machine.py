import logging

from vk import types
from vk import VK
from vk.bot_framework import Dispatcher, get_group_id, AsyncStorage
from vk.bot_framework.storages import TTLDictStorage, RedisStorage
from vk.bot_framework.addons.finite_state_machine import (
    FiniteStateMachine, State
)
from vk.utils import TaskManager

logging.basicConfig(level="INFO")

bot_token = "123"
vk = VK(bot_token)
task_manager = TaskManager(vk.loop)
api = vk.get_api()

dp = Dispatcher(vk)
storage = AsyncStorage()  # fsm supports async AsyncStorage, TTLDictStorage and RedisStorage
dp.storage = storage


fsm = FiniteStateMachine(dp.storage)


class RegistrationState:
    name = State(title="name", storage=dp.storage)
    age = State(title="age", storage=dp.storage)
    sex = State(title="sex", storage=dp.storage)


@dp.message_handler(text="start")
async def test(msg: types.Message, data):
    await fsm.set_state(RegistrationState.name, msg.from_id)
    return await msg.answer("what is your name?")


@dp.message_handler(state=RegistrationState.name)
async def test2(msg: types.Message, data):
    await fsm.set_state(
        RegistrationState.age, msg.from_id, extra_state_data={"name": msg.text}
    )
    return await msg.answer("How old are you?")


@dp.message_handler(state=RegistrationState.age)
async def test3(msg: types.Message, data):

    if not msg.text.isdigit():
        return await msg.answer("Wrong age, try again")

    await fsm.set_state(
        RegistrationState.sex, msg.from_id, extra_state_data={"age": msg.text}
    )
    return await msg.answer("Tell me your sex")


@dp.message_handler(state=RegistrationState.sex)
async def test4(msg: types.Message, data):
    await fsm.add_data(msg.from_id, state_data={"sex": msg.text})
    user_data = await fsm.get_data(msg.from_id)
    await msg.answer(f"Thanks for registration, your data - {user_data}")
    await fsm.finish(msg.from_id)


async def run():
    dp.run_polling(await get_group_id(vk))


if __name__ == "__main__":
    task_manager.add_task(run)
    task_manager.run(auto_reload=False)
