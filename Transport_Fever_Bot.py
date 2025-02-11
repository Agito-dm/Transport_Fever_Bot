import mysql.connector
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, MessageHandler, filters, ConversationHandler

# Подключение к базе данных
db = mysql.connector.connect(
    host="localhost",
    user="Bot",
    password="12345",  # тестовый пароль
    database="PassengerTransport"
)

# Определение состояний
ROLE_SELECTION, PASSWORD_INPUT = range(2)

# Глобальная переменная для хранения роли пользователя
user_roles = {}
# Определение таблиц и их ключевых полей
TABLES = {
    "Bus": ("bus_number", ["model", "color", "capacity", "technical_inspection_date"]),
    "Driver": ("driver_id", ["passport_serial_number", "full_name", "phone_number"]),
    "Flight": ("flight_number", ["bus_number", "route_number", "departure_date", "arrival_date", "departure_time", "arrival_time", "driver_id"]),
    "FlightProfit": ("flight_number", ["tickets_sold", "total_income"]),
    "Passenger": ("passport_serial_number", ["passenger_name", "email", "phone_number"]),
    "Route": ("route_number", ["departure_station", "arrival_station", "route_length"]),
    "Ticket": ("ticket_number", ["seat_number", "price", "flight_number", "luggage", "passenger_passport"]),
    "TicketPrice": ("price", ["mileage_threshold"])
}


# Приветственное сообщение
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [
        ["Администратор", "Пользователь"]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Выберите вашу роль:', reply_markup=reply_markup)
    return ROLE_SELECTION

# Обработка выбора роли
async def role_selection(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    role = update.message.text
    user_id = update.message.chat.id

    if role == "Администратор":
        await update.message.reply_text("Введите пароль:")
        return PASSWORD_INPUT

    user_roles[user_id] = "Пользователь"
    await update.message.reply_text("Вы стали пользователем. Используйте /help для получения списка команд.")
    return ConversationHandler.END

# Обработка ввода пароля
async def password_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text
    if password == "12345":
        user_roles[update.message.chat.id] = "Администратор"
        await update.message.reply_text("Вы стали администратором! Используйте /help для получения списка команд.")
    else:
        user_roles[update.message.chat.id] = "Пользователь"
        await update.message.reply_text("Неверный пароль. Вы стали пользователем. Используйте /help для получения списка команд.")
    
    return ConversationHandler.END

# Команда /help
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    role = user_roles.get(update.message.chat.id, "Пользователь")
    if role == "Администратор":
        help_text = (
            "Доступные команды для администратора:\n"
            "/start - Приветственное сообщение и информация о боте.\n"
            "/help - Показать это сообщение с доступными командами.\n"
            "/choose_table - Выберите таблицу для работы (Bus, Driver, Flight и т.д.).\n"
            "/show_records <table_name> - Показать первые 20 записей из выбранной таблицы.\n"
            "/next - Показать следующие 20 записей.\n"
            "/prev - Показать предыдущие 20 записей.\n"
            "/find_record <table_name> <key_value> - Найти запись по ключевому полю в указанной таблице.\n"
            "/add_record <table_name> <field1> <field2> ... - Добавить новую запись в выбранную таблицу.\n"
            "/update_record <table_name> <key_value> <field1> <field2> ... - Обновить запись по ключевому полю.\n"
            "/delete_record <table_name> <key_value> - Удалить запись по ключевому полю в указанной таблице.\n"
            "/add_flight <flight_number> <bus_number> <route_number> <departure_date> <arrival_date> <departure_time> <arrival_time> <driver_id> - Добавить рейс.\n"
            "/add_bus <bus_number> <model> <color> <capacity> <technical_inspection_date> - Добавить автобус.\n"
            "/add_ticket <ticket_number> <seat_number> <price> <flight_number> <luggage> <passenger_passport> - Добавить билет.\n"
            "/generate_sales_report <quarter> <year> - Сформировать отчет о продажах."
        )
    else:
        help_text = (
            "Доступные команды для пользователя:\n"
            "/start - Приветственное сообщение и информация о боте.\n"
            "/help - Показать это сообщение с доступными командами.\n"
            "/show_records <table_name> - Показать первые 20 записей из выбранной таблицы.\n"
            "/next - Показать следующие 20 записей.\n"
            "/prev - Показать предыдущие 20 записей."
        )
    
    await update.message.reply_text(help_text)

# Обработка текстовых сообщений
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = update.message.chat.id
    print(f"Получено сообщение от {user_id}: {update.message.text}")  # Логирование

    # Получение роли пользователя
    role = user_roles.get(user_id)
    if not role:
        await update.message.reply_text("Сначала выберите роль с помощью команды /start.")
        return

    # Обработка команд
    command_parts = update.message.text.split()  # Разделение команды и аргумента
    command = command_parts[0]  # Получение команду
    args = command_parts[1:]  # Получение аргументы

    if role == "Администратор":
        if command == '/choose_table':
            await choose_table(update, context)
        elif command == '/show_records':
            context.args = args  # Передача аргументов в контекст
            await show_records(update, context)
        elif command == '/next':
            await next_page(update, context)
        elif command == '/prev':
            await prev_page(update, context)
        elif command == '/find_record':
            await find_record(update, context)
        elif command == '/add_record':
            await add_record(update, context)
        elif command == '/update_record':
            await update_record(update, context)
        elif command == '/delete_record':
            await delete_record(update, context)
        elif command == '/add_flight':
            await add_flight(update, context)
        elif command == '/add_bus':
            await add_bus(update, context)
        elif command == '/add_ticket':
            await add_ticket(update, context)
        elif command == '/generate_sales_report':
            await generate_sales_report(update, context)
        else:
            await update.message.reply_text("Неизвестная команда для администратора.")
    
    else:  # Для пользователя
        if command == '/show_records':
            context.args = args  # Передача аргументов в контекст
            await show_records(update, context)
        elif command == '/next':
            await next_page(update, context)
        elif command == '/prev':
            await prev_page(update, context)
        else:
            await update.message.reply_text("Вы пользователь. Используйте команду /help для получения списка команд.")

# Команда для выбора таблицы
async def choose_table(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    table_list = "\n".join(TABLES.keys())
    await update.message.reply_text(f"Выберите таблицу:\n{table_list}\nВведите имя таблицы для просмотра.")

# Команда для отображения записей выбранной таблицы
async def show_records(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Пожалуйста, укажите имя таблицы после команды. Например: /show_records Flight")
        return

    table_name = context.args[0]
    if table_name not in TABLES:
        await update.message.reply_text("Неверное имя таблицы. Попробуйте еще раз.")
        return

    context.user_data['table'] = table_name  # Сохранение выбранной таблицы
    context.user_data['page'] = 0  # Сброс страницы

    await display_records(update, context)  # Показываем записи

# Функция для отображения записей из выбранной таблицы
async def display_records(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    table_name = context.user_data['table']
    page = context.user_data.get('page', 0)
    offset = page * 20  # Расчет смещения для выборки 20 записей

    cursor = db.cursor()
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 20 OFFSET {offset}")  # Запрос к базе данных
    records = cursor.fetchall()

    if records:
        message = '\n'.join([str(record) for record in records])  # Форматирование записей
        await update.message.reply_text(message)
    else:
        await update.message.reply_text('Нет больше записей.')

    # Инструкции для навигации
    await update.message.reply_text(
        "Используйте /next для следующих 20 записей и /prev для предыдущих."
    )

# Команда для перехода к следующей странице записей
async def next_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.user_data['page'] += 1
    await display_records(update, context)

# Команда для перехода к предыдущей странице записей
async def prev_page(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if context.user_data.get('page', 0) > 0:
        context.user_data['page'] -= 1  # Уменьшаем номер страницы, если это возможно
    await display_records(update, context)

# Команда для поиска записи по ключевому полю
async def find_record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Используйте: /find_record <имя таблицы> <ключевое поле>")
        return

    table_name = context.args[0]
    key_value = context.args[1]

    if table_name not in TABLES:
        await update.message.reply_text("Неверное имя таблицы. Попробуйте еще раз.")
        return

    cursor = db.cursor()
    key_column = TABLES[table_name][0]  # Ключевое поле
    cursor.execute(f"SELECT * FROM {table_name} WHERE {key_column} = %s", (key_value,))
    record = cursor.fetchone()

    if record:
        await update.message.reply_text(f"Найдена запись: {record}")
    else:
        await update.message.reply_text('Запись не найдена.')

# Команда для добавления новой записи
async def add_record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 3:  # Минимум 3 аргумента: имя таблицы и 2 значения
        await update.message.reply_text('Используйте: /add_record <имя таблицы> <значения>')
        return

    table_name = context.args[0]

    # Проверяем, что таблица существует
    if table_name not in TABLES:
        await update.message.reply_text("Неверное имя таблицы. Попробуйте еще раз.")
        return

    # Получение списка полей в таблице
    fields = TABLES[table_name][1]  # Поля для вставки

    if len(context.args) - 1 != len(fields):  # Проверка на количество полей
        required_fields = ", ".join(fields)
        await update.message.reply_text(f"Используйте: /add_record {table_name} <{required_fields}>.")
        return

    # Получение значения для записи
    values = context.args[1:]  # Все аргументы после имени таблицы

    try:
        cursor = db.cursor()
        placeholders = ", ".join(["%s"] * len(values))  # Подготовка плейсхолдеров
        sql_query = f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})"
        cursor.execute(sql_query, values)
        db.commit()

        await update.message.reply_text('Запись добавлена.')
    except mysql.connector.Error as err:
        await update.message.reply_text(f'Ошибка: {err}')
    finally:
        cursor.close()  # Закрытие курсора

# Команда для обновления записи
async def update_record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:
        await update.message.reply_text("Используйте: /add_record <имя таблицы> <ключевое поле> <значения>")
        return

    table_name = context.args[0]
    key_value = context.args[1]

    if table_name not in TABLES:
        await update.message.reply_text("Неверное имя таблицы. Попробуйте еще раз.")
        return

    fields = TABLES[table_name][1]  # Получение списка полей
    if len(context.args) != len(fields) + 2:
        required_fields = ", ".join(fields)
        await update.message.reply_text(f"Используйте: /update_record {table_name} {key_value} <{required_fields}>")
        return

    values = context.args[2:]  # Значения для обновления
    cursor = db.cursor()
    set_clause = ", ".join([f"{field} = %s" for field in fields])  # Формирование части запроса для обновления
    cursor.execute(f"UPDATE {table_name} SET {set_clause} WHERE {TABLES[table_name][0]} = %s", values + [key_value])
    db.commit()

    await update.message.reply_text('Запись обновлена.')

# Команда для удаления записи
async def delete_record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) < 2:  # Проверка, передано ли имя таблицы и ключ
        await update.message.reply_text("Используйте: /delete_record <имя таблицы> <ключевое поле>")
        return

    table_name = context.args[0]
    key_value = context.args[1]

    if table_name not in TABLES:
        await update.message.reply_text("Неверное имя таблицы. Попробуйте еще раз.")
        return

    cursor = db.cursor()
    key_column = TABLES[table_name][0]
    
    cursor.execute(f"DELETE FROM {table_name} WHERE {key_column} = %s", (key_value,))
    
    if cursor.rowcount > 0:  # Проверка, была ли запись удалена
        db.commit()
        await update.message.reply_text('Запись удалена.')
    else:
        await update.message.reply_text('Запись не найдена.')
    
    cursor.close()


# Команда для добавления автобусного рейса
async def add_flight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 8:
        await update.message.reply_text("Используйте: /add_flight <flight_number> <bus_number> <route_number> <departure_date> <arrival_date> <departure_time> <arrival_time> <driver_id>")
        return

    flight_number = context.args[0]
    bus_number = context.args[1]
    route_number = context.args[2]
    departure_date = context.args[3]
    arrival_date = context.args[4]
    departure_time = context.args[5]
    arrival_time = context.args[6]
    driver_id = context.args[7]

    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO Flight (flight_number, bus_number, route_number, departure_date, arrival_date, departure_time, arrival_time, driver_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (flight_number, bus_number, route_number, departure_date, arrival_date, departure_time, arrival_time, driver_id))
        db.commit()
        await update.message.reply_text("Запись успешно добавлена.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при добавлении записи: {e}")
    finally:
        cursor.close()

# Команда для добавления автобуса
async def add_bus(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 4:
        await update.message.reply_text("Используйте: /add_bus <bus_number> <model> <color> <capacity> <technical_inspection_date>")
        return

    bus_number = context.args[0]
    model = context.args[1]
    color = context.args[2]
    capacity = context.args[3]
    technical_inspection_date = context.args[4]

    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO Bus (bus_number, model, color, capacity, technical_inspection_date) VALUES (?, ?, ?, ?, ?)",
            (bus_number, model, color, capacity, technical_inspection_date))
        db.commit()
        await update.message.reply_text("Запись успешно добавлена.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при добавлении записи: {e}")
    finally:
        cursor.close()

# Команда для добавления билета
async def add_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 6:
        await update.message.reply_text("Используйте: /add_ticket <ticket_number> <seat_number> <price> <flight_number> <luggage> <passenger_passport>")
        return

    ticket_number = context.args[0]
    seat_number = context.args[1]
    price = context.args[2]
    flight_number = context.args[3]
    luggage = context.args[4]
    passenger_passport = context.args[5]

    cursor = db.cursor()
    try:
        cursor.execute("INSERT INTO Ticket (ticket_number, seat_number, price, flight_number, luggage, passenger_passport) VALUES (?, ?, ?, ?, ?, ?)",
            (ticket_number, seat_number, price, flight_number, luggage, passenger_passport))
        db.commit()
        await update.message.reply_text("Запись успешно добавлена.")
    except Exception as e:
        await update.message.reply_text(f"Ошибка при добавлении записи: {e}")
    finally:
        cursor.close()

# Команда для генерации отчета о продажах
async def generate_sales_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if len(context.args) != 2:
        await update.message.reply_text("Используйте: /generate_sales_report <quarter> <year>")
        return

    try:
        quarter = int(context.args[0])
        year = int(context.args[1])

        # Проверка корректности квартала
        if quarter < 1 or quarter > 4:
            await update.message.reply_text("Квартал должен быть от 1 до 4.")
            return

        # Определение диапазона дат для квартала
        if quarter == 1:
            start_date = f"{year}-01-01"
            end_date = f"{year}-03-31"
        elif quarter == 2:
            start_date = f"{year}-04-01"
            end_date = f"{year}-06-30"
        elif quarter == 3:
            start_date = f"{year}-07-01"
            end_date = f"{year}-09-30"
        else:  # quarter == 4
            start_date = f"{year}-10-01"
            end_date = f"{year}-12-31"

        # Создание нового курсора для выполнения запроса
        cursor = db.cursor()
        cursor.execute("""
            SELECT flight_number, SUM(tickets_sold) AS total_tickets, SUM(total_income) AS total_income
            FROM FlightProfit
            WHERE date BETWEEN ? AND ?
            GROUP BY flight_number
        """, (start_date, end_date))  # Передача параметров

        results = cursor.fetchall()

        # Форматирование отчета
        report_lines = ["Отчет о продажах:\n"]
        report_lines.append(f"{'Рейс':<15}{'Продано билетов':<20}{'Общий доход'}\n")
        report_lines.append("-" * 50)

        for row in results:
            flight_number, total_tickets, total_income = row
            report_lines.append(f"{flight_number:<15}{total_tickets:<20}{total_income}")

        report_text = "\n".join(report_lines)
        await update.message.reply_text(report_text)

    except Exception as e:
        await update.message.reply_text(f"Ошибка при генерации отчета: {e}")
    finally:
        cursor.close()  # Закрытие курсора после использования

# Основная функция для запуска бота
def main():
    app = ApplicationBuilder().token("7368544503:AAGepSah_mr3HBPuPRZ4MONSmJ_ifxd3cnI").build()

    # Определение последовательности разговоров
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ROLE_SELECTION: [MessageHandler(filters.TEXT, role_selection)],
            PASSWORD_INPUT: [MessageHandler(filters.TEXT, password_input)],
        },
        fallbacks=[],
    )

    # Регистрация всех команд
    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("choose_table", choose_table))
    app.add_handler(CommandHandler("show_records", show_records))
    app.add_handler(CommandHandler("next", next_page))
    app.add_handler(CommandHandler("prev", prev_page))
    app.add_handler(CommandHandler("find_record", find_record))
    app.add_handler(CommandHandler("add_record", add_record))
    app.add_handler(CommandHandler("update_record", update_record))
    app.add_handler(CommandHandler("delete_record", delete_record))
    app.add_handler(CommandHandler("add_flight", add_flight))
    app.add_handler(CommandHandler("add_bus", add_bus))
    app.add_handler(CommandHandler("add_ticket", add_ticket))
    app.add_handler(CommandHandler("generate_sales_report", generate_sales_report))

    # Обработка текстовых сообщений
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()  # Запуск бота

if __name__ == '__main__':
    main()  # Запуск основной функции
