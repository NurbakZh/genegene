from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, Application
import requests
import time

# Define states for the conversation
GENDER_CHOICE, STYLE_CHOICE, ORIGINAL_PHOTO = range(3)
girl1 = "https://www.dropbox.com/scl/fi/px3txxw79jgrsqevvqy95/girl1.jpg?rlkey=fr1yfszqyzksfftsggdeoq7vg&st=5wiybsxh&dl=1"
girl2 = "https://www.dropbox.com/scl/fi/7ewwbqo3benikm928fgaq/girl2.jpg?rlkey=jo8wxpj8ihk33l9xarlyf8bbw&st=1gum620l&dl=1"
man1 = "https://www.dropbox.com/scl/fi/g9h1uctxdos3hm2rxzqpx/photo_2025-02-19_21-08-53.jpg?rlkey=yvmy84enskvfpsqc1ig4he3bw&st=mdoprd0n&dl=1"
man2 = "https://www.dropbox.com/scl/fi/uq0iir5r4ebmg6242c5gs/photo_2025-02-19_21-08-54.jpg?rlkey=9md5erazckn0f2hxsqyyl24ah&st=3d4ad2di&dl=2"

# Add bot commands description
BOT_COMMANDS = [
    ("start", "🎨 Начать генерацию вашей новой аватарки")
]

async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [KeyboardButton("👩 Женщина")],
        [KeyboardButton("👨 Мужчина")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        '👋 Привет! Я бот, который поможет вам создать стильную аватарку! \n\n'
        '🎯 Для начала выберите ваш пол:',
        reply_markup=reply_markup
    )
    return GENDER_CHOICE

async def handle_gender_choice(update: Update, context: CallbackContext) -> int:
    gender = update.message.text
    context.user_data['gender'] = gender  # Store gender for later use
    
    if gender not in ["👩 Женщина", "👨 Мужчина"]:
        await update.message.reply_text("❌ Пожалуйста, выберите пол используя кнопки.")
        return GENDER_CHOICE
    
    # First send the selection confirmation
    await update.message.reply_text(
        f'✅ Вы выбрали: *{gender}*',
        parse_mode='Markdown'
    )
    
    # Show different style choices based on gender
    if gender == "👩 Женщина":
        keyboard = [
            [KeyboardButton("💰 Old Money")],
            [KeyboardButton("🌸 Весна")],
            [KeyboardButton("🧘‍♀️ Медитация")],
            [KeyboardButton("📚 Фото с книгами")],
            [KeyboardButton("⚪ Фото ЧБ")]
        ]
    else:  # Мужчина
        keyboard = [
            [KeyboardButton("🏔️ Горы 1")],
            [KeyboardButton("🏔️ Горы 2")],
            [KeyboardButton("🌌 Космос 1")],
            [KeyboardButton("🌌 Космос 2")]
        ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        '🎨 Выберите стиль для вашей аватарки:',
        reply_markup=reply_markup
    )
    return STYLE_CHOICE

async def handle_style_choice(update: Update, context: CallbackContext) -> int:
    style = update.message.text
    style_name = style  # Store the exact style text for the response
    gender = context.user_data.get('gender')
    
    # Prompts for women
    if gender == "👩 Женщина":
        if style == "💰 Old Money":
            context.user_data['text_prompt'] = [
                "a woman standing in an opulent indoor setting with soft, ambient lighting. She is dressed in a white blazer with a deep V-neck, paired with tailored black trousers and classic black heels. Her hair is styled in soft waves, and she wears minimal, elegant jewelry. The background includes luxurious furnishings, such as a velvet armchair, a marble fireplace, and ornate gold-framed mirrors. The overall mood should be one of understated luxury and classic sophistication",
                "a woman posing in a sophisticated indoor environment with warm, ambient lighting. She is wearing a simple yet elegant white dress with thin straps, cinched at the waist with a delicate belt. Her hair is styled in a chic updo, and she wears pearl earrings and a matching bracelet. The background features elegant decor, such as a grand piano, a crystal chandelier, and plush drapery. The atmosphere should convey timeless elegance and refinement",
                "a woman standing on a boat with a scenic waterfront view in the background. She is dressed in a classic white shirt with rolled-up sleeves, tucked into high-waisted navy trousers. Her hair is styled in a neat ponytail, and she wears aviator sunglasses. The boat's deck is made of polished wood, and the water is calm, reflecting the clear blue sky. The scene should convey a sense of timeless elegance and sophistication, with a hint of adventure.",
            ]
        elif style == "🌸 Весна":
            context.user_data['text_prompt'] = ["A beautiful young woman with long, flowing wavy hair, wearing a floral wreath made of spring flowers like cherry blossoms and tulips. She is in a blooming spring garden with pink cherry trees and fresh green grass. She wears a light, airy dress in pastel colors. The lighting is soft and natural, creating a fresh, romantic spring atmosphere."]
        elif style == "🧘‍♀️ Медитация":
            context.user_data['text_prompt'] = ["image of a serene woman meditating outdoors at sunset. She is sitting cross-legged on a woven mat, wearing a flowing white outfit that drapes gracefully around her. Her hands rest gently on her lap, holding a polished brass bowl. The setting features a tranquil landscape with a calm body of water reflecting the warm hues of the sunset. Rocky terrain and scattered wildflowers add texture to the foreground, while distant mountains and soft, golden clouds complete the background. The soft, diffused lighting of the setting sun bathes the scene in a peaceful, warm glow, enhancing the overall sense of calm and serenity."]
        elif style == "📚 Фото с книгами":
            context.user_data['text_prompt'] = ["a woman reading a book in a dimly lit, cozy room. She is seated comfortably in an armchair, wearing a warm, dark-colored sweater. A single candle on a nearby table casts a soft, warm glow, illuminating the pages of the book and creating gentle shadows on her face and surroundings. The background includes a few bookshelves filled with books, adding to the intellectual and serene atmosphere. The overall ambiance should be intimate, tranquil, and inviting"]
        elif style == "⚪ Фото ЧБ":
            context.user_data['text_prompt'] = ["A stunning black-and-white portrait of a young woman with delicate facial features, wearing a sleek black turtleneck. Her gaze is confident yet soft, with a subtle, natural expression. The lighting is dramatic, with high contrast and soft shadows emphasizing the contours of her face. Her hair is styled either in a sleek bob, a messy updo, or loose waves, adding character to the composition. The background is minimalistic, either a simple dark or light gradient, ensuring the focus remains on her face and expression. The image exudes elegance, sophistication, and a timeless cinematic aesthetic.",
            "A high-contrast black-and-white portrait of a woman with sharp, defined features, wearing a stylish black outfit. Her expression is poised and mysterious, with piercing eyes that capture attention. Soft lighting creates dramatic shadows, enhancing the depth and elegance of her face. Her hairstyle is either a sleek, tight bun, a voluminous wavy bob, or loose strands framing her face. The background is minimal, either softly blurred or featuring a striking interplay of light and shadow. The image has a cinematic, editorial feel, evoking sophistication, confidence, and timeless beauty."]
        else:
            await update.message.reply_text("❌ Пожалуйста, выберите стиль используя кнопки.")
            return STYLE_CHOICE
    
    # Prompts for men
    else:
        if style == "🏔️ Горы 1":
            context.user_data['text_prompt'] = [
                "A confident male mountaineer standing on a dramatic mountain peak at sunrise. He's wearing professional alpine climbing gear - a weatherproof jacket, climbing harness, and helmet. His face shows determination and achievement. The background features snow-capped peaks bathed in golden morning light, with dramatic clouds below. The composition captures both the majesty of the mountains and the triumph of the climber, with perfect visibility of his facial features. The lighting is crisp and clear, emphasizing the alpine environment."
            ]
        elif style == "🏔️ Горы 2":
            context.user_data['text_prompt'] = [
                "A male climber scaling a challenging rock face, captured from a side angle that clearly shows his face. He's wearing technical climbing gear - a fitted climbing shirt, chalk bag, and safety equipment. The background shows a vast mountain landscape with dramatic cliffs and a deep valley below. The lighting is natural and clear, highlighting both the intensity of the climb and the climber's focused expression. The scene conveys strength, skill, and adventure in a pristine mountain setting."
            ]
        elif style == "🌌 Космос 1":
            context.user_data['text_prompt'] = [
                "A male astronaut exploring the surface of an alien planet, his face seen through the perfectly clear glass dome of his helmet. His suit is advanced, featuring reinforced joints and an oxygen system. The landscape consists of a vast rocky terrain with a purple-hued sky, distant mountains, and glowing alien flora. The helmet's glass is free of reflections or particles, providing an unobstructed view of his focused expression as he observes the extraterrestrial environment."
            ]
        elif style == "🌌 Космос 2":
            context.user_data['text_prompt'] = [
                "A male astronaut floating outside a massive space station, gripping a robotic arm for stability. His face is clearly visible through the pristine visor of his helmet, showing deep concentration as he carefully maneuvers. His suit has a sleek, futuristic design with built-in thrusters and mission patches. The background showcases the enormous space station structure with the deep blackness of space beyond, dotted with distant stars. The helmet glass is perfectly transparent, ensuring no distortions or reflections obscure his expression."
            ]
        else:
            await update.message.reply_text("❌ Пожалуйста, выберите стиль используя кнопки.")
            return STYLE_CHOICE
    
    context.user_data['style'] = style_name
    await update.message.reply_text(
        f'✅ Вы выбрали: *{style_name}*\n\n📸 Теперь, пожалуйста, отправьте вашу фотографию.',
        parse_mode='Markdown'
    )
    return ORIGINAL_PHOTO

async def handle_original_photo(update: Update, context: CallbackContext) -> int:
    file = await update.message.photo[-1].get_file()
    context.user_data['original_photo'] = file.file_path
    # For old money style, use prompts one by one
    if "💰 Old Money" == context.user_data['style'] or "⚪ Фото ЧБ" == context.user_data['style']:
        # Get the next prompt index from user data, defaulting to 0
        prompt_index = context.user_data.get('prompt_index', 0)
        # Get the prompt at current index
        text_prompt = context.user_data['text_prompt'][prompt_index]
        # Increment index for next time, wrapping around to 0 if at end
        next_index = (prompt_index + 1) % len(context.user_data['text_prompt'])
        context.user_data['prompt_index'] = next_index
    else:
        # For other styles, just use the first prompt
        text_prompt = context.user_data.get('text_prompt')[0]

    url = 'https://api.lightxeditor.com/external/api/v1/avatar'
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': '0e677c1bd493442092d5b52ba285c889_7bab040d1230444aa90052848f59c7c6_andoraitools' 
    }

    style_image_url = ""
    if "🌌 Космос 2" == context.user_data['style']:
        style_image_url = man2

    data = {
        "imageUrl": context.user_data['original_photo'],
        "styleImageUrl": style_image_url,
        "textPrompt": text_prompt,
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()  # Raises an HTTPError for bad responses (4xx, 5xx)
        
        response_data = response.json()
        if not response_data:
            raise ValueError("Empty response received")
            
        order_id = response_data.get("body", {}).get("orderId")
        if not order_id:
            raise ValueError("No order ID in response")
            
        context.user_data['order_id'] = order_id
        await update.message.reply_text("✨ Запрос успешно отправлен! По готовности я пришлю вам вашу аватарку!")
        await check_status(update, context)
        
    except requests.exceptions.RequestException as e:
        await update.message.reply_text(f"❌ Ошибка сети при отправке запроса: {str(e)}")
    except ValueError as e:
        await update.message.reply_text(f"❌ Ошибка в ответе сервера: {str(e)}")
    except Exception as e:
        if response and response.text:
            if "5040, API_CREDITS_CONSUMED" in response.text:
                await update.message.reply_text("❌ Достигнут лимит запросов на сегодня. Пожалуйста, попробуйте завтра.")
            else:
                await update.message.reply_text(f"❌ Неожиданная ошибка: {str(e)}. Ответ сервера: {response.text}")
        else:
            await update.message.reply_text(f"❌ Неожиданная ошибка: {str(e)}")

    return ConversationHandler.END

async def check_status(update: Update, context: CallbackContext) -> None:
    url = 'https://api.lightxeditor.com/external/api/v1/order-status'
    api_key = '0e677c1bd493442092d5b52ba285c889_7bab040d1230444aa90052848f59c7c6_andoraitools' 

    order_id = context.user_data.get('order_id')
    if not order_id:
        await update.message.reply_text("Вы ещё не отправили изображение на обработку.")
        return

    headers = {
        'Content-Type': 'application/json',
        'x-api-key': api_key
    }

    payload = {"orderId": order_id}

    while True:
        response = requests.post(url, headers=headers, json=payload)
        if response.status_code == 2000 or response.status_code == 200:
            response_json = response.json()
            status = response_json.get("body", {}).get("status")
            output_url = response_json.get("body", {}).get("output")

            if status == "completed" or status == "active" and output_url:
                await update.message.reply_text("Изображение готово! Вот ваш результат:")
                await update.message.reply_photo(photo=output_url)
                return
            elif status in ["failed", "cancelled"]:
                await update.message.reply_text(f"Ошибка обработки. Статус: {status}.")
                return

        else:
            await update.message.reply_text(f"Ошибка запроса. Код: {response.status_code}, Ответ: {response.text}")
            return

        time.sleep(10)

def main():
    app = ApplicationBuilder().token("5120254425:AAF0I3xKI3Y08vjIHSBjGxGk-ZnIjSYlPhU").build()
    
    # Set up bot commands at startup
    async def post_init(application: Application):
        await application.bot.set_my_commands(BOT_COMMANDS)
    
    app.post_init = post_init
    
    app.add_handler(ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GENDER_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gender_choice)],
            STYLE_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_style_choice)],
            ORIGINAL_PHOTO: [MessageHandler(filters.PHOTO, handle_original_photo)]
        },
        fallbacks=[]
    ))
    
    app.run_polling()

if __name__ == '__main__':
    main()