import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.storage.memory import MemoryStorage
from config import TOKEN, WEATHER_API_KEY
import random
import aiohttp

bot = Bot(token=TOKEN)
dp = Dispatcher(storage=MemoryStorage())


# Группа состояний
class WeatherStates(StatesGroup):
    waiting_for_city = State()


@dp.message(CommandStart())
async def start(message: Message):
    await message.answer("Привет, я бот. Я умею показывать погоду в вашем городе. Для получения информации введите команду /help")


@dp.message(Command("help"))
async def help(message: Message):
    await message.answer("Этот бот умеет выполнять команды: "
                         "\n/start "
                         "\n/help "
                         "\n/pogoda - Информация о погоде в вашем городе "
                         "\n Могу показывать красивые фотографии погоды: "
                         "\n/photo_summer - погода летом "
                         "\n/photo_winter - погода зимой "
                         "\n/photo_spring - погода весной "
                         "\n/photo_autumn - погода осенью ")


async def fetch_weather(city: str):
    async with aiohttp.ClientSession() as session:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=metric&lang=ru"
        async with session.get(url) as response:
            if response.status == 200:
                data = await response.json()
                return data
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
        description = weather_data['weather'][0]['description']
        temp = weather_data['main']['temp']
        feels_like = weather_data['main']['feels_like']
        humidity = weather_data['main']['humidity']
        wind_speed = weather_data['wind']['speed']

        response_message = (
            f"Погода в городе {city}:\n"
            f"Описание: {description}\n"
            f"Температура: {temp}°C\n"
            f"Ощущается как: {feels_like}°C\n"
            f"Влажность: {humidity}%\n"
            f"Скорость ветра: {wind_speed} м/с"
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

async def main():
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
