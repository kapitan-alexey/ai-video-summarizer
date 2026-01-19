import asyncio

from aiogram import Bot, Dispatcher, types, executor

from bot import bot

from handlers import command_start_handler, echo_handler, mock_interview_start_handler

from services.update_validator import RedisUpdateValidator


dp = Dispatcher(bot=bot)
dp.register_message_handler(command_start_handler, commands=['start','run'])
dp.register_message_handler(mock_interview_start_handler, commands=['mockme'])
dp.register_message_handler(echo_handler)


async def process_event(event, dp: Dispatcher):

    Bot.set_current(dp.bot)
    update = types.Update.to_object(event)

    new_update = update['update_id']
    if not RedisUpdateValidator().validate_update(new_update):
        return
    
    print('event:', event)

    await dp.process_update(update)


async def main(event):
    await process_event(event, dp)
    return 'ok'


def lambda_handler(event, context):
    """AWS Lambda handler."""

    return asyncio.get_event_loop().run_until_complete(main(event))


if __name__ == '__main__': 
    executor.start_polling(dp, skip_updates=True)