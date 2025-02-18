from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler, Application
import requests
import time

# Define states for the conversation
GENDER_CHOICE, STYLE_CHOICE, ORIGINAL_PHOTO = range(3)
girl1 = "https://www.dropbox.com/scl/fi/px3txxw79jgrsqevvqy95/girl1.jpg?rlkey=fr1yfszqyzksfftsggdeoq7vg&st=5wiybsxh&dl=1"
girl2 = "https://www.dropbox.com/scl/fi/7ewwbqo3benikm928fgaq/girl2.jpg?rlkey=jo8wxpj8ihk33l9xarlyf8bbw&st=1gum620l&dl=1"
man1 = "https://www.dropbox.com/scl/fi/tp837x30sl6k6fk03ewkh/man1.jpg?rlkey=2991qei1bkf64czkwi86nvfxo&st=h4gfq94y&dl=1"
man2 = "https://www.dropbox.com/scl/fi/mxac1nv9q020ue80kipz0/man2.jpg?rlkey=c7z2vf5orircy2m8phceg60d0&st=g8ks9aar&dl=1"

# Add bot commands description
BOT_COMMANDS = [
    ("start", "🎨 Начать генерацию вашей новой аватарки")
]

async def start(update: Update, context: CallbackContext) -> int:
    # Set bot commands
    await context.bot.set_my_commands(BOT_COMMANDS)
    
    keyboard = [[KeyboardButton("👩 Женщина")]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        '👋 Привет! Я бот, который поможет вам создать стильную аватарку! \n\n'
        '🎯 Для начала выберите ваш пол:',
        reply_markup=reply_markup
    )
    return GENDER_CHOICE

async def handle_gender_choice(update: Update, context: CallbackContext) -> int:
    gender = update.message.text
    if gender != "👩 Женщина":
        await update.message.reply_text("❌ Пожалуйста, выберите '👩 Женщина' используя кнопку.")
        return GENDER_CHOICE
    
    # First send the selection confirmation
    await update.message.reply_text(
        f'✅ Вы выбрали: *{gender}*',
        parse_mode='Markdown'
    )
    
    # Show style choices with emojis
    keyboard = [
        [KeyboardButton("💰 Old Money")],
        [KeyboardButton("🌸 Весна")],
        [KeyboardButton("🧘‍♀️ Медитация")],
        [KeyboardButton("📚 Фото с книгами")],
        [KeyboardButton("⚪ Фото ЧБ")]
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
        'x-api-key': '5824186e2dba4ab4af7156dff9443158_3a82a28931364c439b0bf2e8059dd7ea_andoraitools' 
    }

    data = {
        "imageUrl": context.user_data['original_photo'],
        "styleImageUrl": "",
        "textPrompt": text_prompt,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        order_id = response.json().get("body", {}).get("orderId")
        context.user_data['order_id'] = order_id
        await update.message.reply_text("✨ Запрос успешно отправлен! По готовности я пришлю вам вашу аватарку!")
        await check_status(update, context)
    else:
        await update.message.reply_text(f"❌ Запрос не удался. Код ошибки: {response.status_code}")
        await update.message.reply_text(response.text)

    return ConversationHandler.END

async def check_status(update: Update, context: CallbackContext) -> None:
    url = 'https://api.lightxeditor.com/external/api/v1/order-status'
    api_key = '5824186e2dba4ab4af7156dff9443158_3a82a28931364c439b0bf2e8059dd7ea_andoraitools' 

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