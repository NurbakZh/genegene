from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
import requests
import time
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackContext, ConversationHandler

# Define states for the conversation
GENDER_CHOICE, ORIGINAL_PHOTO = range(2)
girl1 = "https://www.dropbox.com/scl/fi/px3txxw79jgrsqevvqy95/girl1.jpg?rlkey=fr1yfszqyzksfftsggdeoq7vg&st=5wiybsxh&dl=1"
girl2 = "https://www.dropbox.com/scl/fi/7ewwbqo3benikm928fgaq/girl2.jpg?rlkey=jo8wxpj8ihk33l9xarlyf8bbw&st=1gum620l&dl=1"
man1 = "https://www.dropbox.com/scl/fi/tp837x30sl6k6fk03ewkh/man1.jpg?rlkey=2991qei1bkf64czkwi86nvfxo&st=h4gfq94y&dl=1"
man2 = "https://www.dropbox.com/scl/fi/mxac1nv9q020ue80kipz0/man2.jpg?rlkey=c7z2vf5orircy2m8phceg60d0&st=g8ks9aar&dl=1"

async def start(update: Update, context: CallbackContext) -> int:
    keyboard = [
        [KeyboardButton("Мужчина"), KeyboardButton("Женщина")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text(
        'Здравствуйте! Я бот, который поможет вам сделать аватарку! Для начала выберите ваш пол:',
        reply_markup=reply_markup
    )
    return GENDER_CHOICE

async def handle_gender_choice(update: Update, context: CallbackContext) -> int:
    gender = update.message.text
    user_requests = context.user_data.get('gender_requests', 0)
    if gender == "Мужчина":
        context.user_data['style_photo'] = man1 if user_requests % 2 == 0 else man2
    elif gender == "Женщина":
        context.user_data['style_photo'] = girl1 if user_requests % 2 == 0 else girl2
    else:
        await update.message.reply_text("Пожалуйста, выберите пол используя кнопки.")
        return GENDER_CHOICE
    
    context.user_data['gender_requests'] = user_requests + 1  
    await update.message.reply_text('Теперь, пожалуйста, отправьте вашу фотографию.')
    return ORIGINAL_PHOTO

async def handle_original_photo(update: Update, context: CallbackContext) -> int:
    file = await update.message.photo[-1].get_file()
    context.user_data['original_photo'] = file.file_path
    if context.user_data.get('style_photo') in [man1, man2]:
        text_prompt = "realistic picture of a basketball athlete"
    else:
        text_prompt = "realistic picture of a woman in spring with nature"

    # Prepare the request with both photos
    url = 'https://api.lightxeditor.com/external/api/v1/avatar'
    headers = {
        'Content-Type': 'application/json',
        'x-api-key': '7b8496501ad740ac914f3c9873ee8c22_c8e762ffa6b84f7a9c401f0540733e5d_andoraitools' 
    }

    data = {
        "imageUrl": context.user_data['original_photo'],
        "styleImageUrl": context.user_data['style_photo'],
        "textPrompt": text_prompt,
    }

    response = requests.post(url, headers=headers, json=data)

    if response.status_code == 200:
        order_id = response.json().get("body", {}).get("orderId")
        context.user_data['order_id'] = order_id
        await update.message.reply_text("Запрос успешно отправлен! По готовности я пришлю вам вашу аватарку!")
        await check_status(update, context)
    else:
        await update.message.reply_text(f"Запрос не удался. Код ошибки: {response.status_code}")
        await update.message.reply_text(response.text)

    return ConversationHandler.END

async def check_status(update: Update, context: CallbackContext) -> None:
    url = 'https://api.lightxeditor.com/external/api/v1/order-status'
    api_key = '7b8496501ad740ac914f3c9873ee8c22_c8e762ffa6b84f7a9c401f0540733e5d_andoraitools' 

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

app = ApplicationBuilder().token("5120254425:AAF0I3xKI3Y08vjIHSBjGxGk-ZnIjSYlPhU").build()

app.add_handler(ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        GENDER_CHOICE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_gender_choice)],
        ORIGINAL_PHOTO: [MessageHandler(filters.PHOTO, handle_original_photo)]
    },
    fallbacks=[]
))

app.add_handler(CommandHandler("check_status", check_status))

app.run_polling()