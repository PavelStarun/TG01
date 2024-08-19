import os
import random
import asyncio
import aiohttp
import aiofiles
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from googletrans import Translator
from gtts import gTTS
import tempfile
from config import TOKEN, WEATHER_API_KEY

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Создание необходимых директорий
IMG_DIR = 'tmp'
if not os.path.exists(IMG_DIR):
    os.makedirs(IMG_DIR)

translator = Translator()


class WeatherStates(StatesGroup):
    waiting_for_city = State()


class TranslateStates(StatesGroup):
    waiting_for_text = State()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer(
        "Привет, я бот. Я умею: \nпоказывать погоду в вашем городе, \nпереводить текст в аудио(с переводом с русского на английский), \nприсылать фото, \nпереводить текст с русского на английский. Для получения дополнительной информации введите команду /help")


@dp.message(Command("help"))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды: "
                         "\n/start - приветственное сообщение "
                         "\n/help - информация о командах "
                         "\n/pogoda - Информация о погоде в вашем городе "
                         "\n/photo_summer - погода летом "
                         "\n/photo_winter - погода зимой "
                         "\n/photo_spring - погода весной "
                         "\n/photo_autumn - погода осенью"
                         "\n/translate - перевести текст в аудио")


async def fetch_weather(city: str):
    async with aiohttp.ClientSession() as session:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        async with session.get(url) as response:
            if response.status == 200:
                return await response.json()
            else:
                print(f"Error fetching weather data: {response.status}")
                return None


@dp.message(Command("pogoda"))
async def start_pogoda(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, введите название города:")
    await state.set_state(WeatherStates.waiting_for_city)


@dp.message(WeatherStates.waiting_for_city)
async def get_weather(message: Message, state: FSMContext):
    city = message.text.strip()
    weather_data = await fetch_weather(city)

    if weather_data:
        response_message = (
            f"Погода в городе {city}:\n"
            f"Описание: {weather_data['weather'][0]['description']}\n"
            f"Температура: {weather_data['main']['temp']}°C\n"
            f"Ощущается как: {weather_data['main']['feels_like']}°C\n"
            f"Влажность: {weather_data['main']['humidity']}%\n"
            f"Скорость ветра: {weather_data['wind']['speed']} м/с"
        )
        await message.answer(response_message)
    else:
        await message.answer("Не удалось получить данные о погоде. Проверьте название города и попробуйте снова.")

    await state.clear()


@dp.message(F.text == "погода")
async def ask_city(message: Message):
    await message.answer("Используйте команду /pogoda для получения информации о погоде в вашем городе.")


@dp.message(Command("photo_summer"))
async def photo_summer(message: Message):
    list = [
        "https://www.zastavki.com/pictures/originals/2015/Nature_A_bright_summer_sun_in_the_sky_093669_.jpg",
        "https://baldezh.top/uploads/posts/2021-03/1617071312_32-p-oboi-leto-solntse-34.jpg",
        "https://baldezh.top/uploads/posts/2021-04/1617343347_16-p-oboi-prirodnie-yavleniya-letom-17.jpg",
        "https://skate-star.ru/wp-content/uploads/d/2/9/d2905a5885b52b65b73cf3c95995be30.jpeg",
    ]
    rand_photo = random.choice(list)
    await message.answer_photo(rand_photo, caption="Это фотография погоды летом")


@dp.message(Command("photo_winter"))
async def photo_winter(message: Message):
    list = [
        "https://vsegda-pomnim.com/uploads/posts/2023-07/1689050691_vsegda-pomnim-com-p-pogoda-zima-foto-10.jpg",
        "https://gagaru.club/uploads/posts/2023-02/1677113066_gagaru-club-p-pogoda-krasivaya-krasivo-78.jpg",
        "https://get.wallhere.com/photo/winter-trees-snow-hoarfrost-traces-silence-sky-682207.jpg",
    ]
    rand_photo = random.choice(list)
    await message.answer_photo(rand_photo, caption="Это фотография погоды зимой")


@dp.message(Command("photo_spring"))
async def photo_spring(message: Message):
    list = [
        "https://www.inpearls.ru/img/pearls/1990707-8113.jpg",
        "https://balthazar.club/o/uploads/posts/2023-10/1696584341_balthazar-club-p-priroda-rannei-vesnoi-oboi-1.jpg",
        "https://ug.ru/wp-content/uploads/2021/03/mart.jpg",
    ]
    rand_photo = random.choice(list)
    await message.answer_photo(rand_photo, caption="Это фотография погоды весной")


@dp.message(Command("photo_autumn"))
async def photo_autumn(message: Message):
    list = [
        "https://photocentra.ru/images/main78/787816_main.jpg",
        "https://i01.fotocdn.net/s217/2c2c1f9f76b67c4d/public_pin_l/2966897448.jpg",
        "https://get.wallhere.com/photo/sunlight-landscape-forest-nature-grass-park-branch-morning-Belgium-path-spring-tree-autumn-leaf-plant-botanicgarden-woodland-grove-temperate-broadleaf-and-mixed-forest-deciduous-meise-flemishbrabant-873449.jpg",
    ]
    rand_photo = random.choice(list)
    await message.answer_photo(rand_photo, caption="Это фотография погоды осенью")


@dp.message(Command("translate"))
async def ask_text(message: Message, state: FSMContext):
    await message.answer("Напишите текст, который хотите перевести в аудио:")
    await state.set_state(TranslateStates.waiting_for_text)


@dp.message(TranslateStates.waiting_for_text)
async def text_to_audio(message: Message, state: FSMContext):
    text = message.text
    translated_text = translator.translate(text, dest="ru").text
    tts = gTTS(translated_text, lang='ru')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as temp_audio:
        tts.save(temp_audio.name)
        temp_audio_path = temp_audio.name
    audio_file = FSInputFile(temp_audio_path)
    await message.answer_voice(audio_file)
    os.remove(temp_audio_path)
    await state.clear()


@dp.message(F.photo)
async def react_photo(message: Message):
    list = ['Ого, какая фотка!', 'Непонятно, что это такое', 'Не отправляй мне такое больше']
    rand_answ = random.choice(list)
    await message.answer(rand_answ)
    file_path = os.path.join(IMG_DIR, f'{message.photo[-1].file_unique_id}.jpg')
    await bot.download(message.photo[-1], destination=file_path)
    await message.answer(f"Фото сохранено как {file_path}")


@dp.message()
async def handle_text(message: Message):
    text_to_translate = message.text
    translated_text = translator.translate(text_to_translate, src='auto', dest='en').text
    await message.answer(translated_text)


async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
