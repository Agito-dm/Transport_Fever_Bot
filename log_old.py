# Команда для добавления записи
# Команда для добавления новой записи
# async def add_record(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
#     if not context.args:
#         await update.message.reply_text("Пожалуйста, укажите имя таблицы и значения для добавления.")
#         return

#     table_name = context.args[0]
#     if table_name not in TABLES:
#         await update.message.reply_text("Неверное имя таблицы. Попробуйте еще раз.")
#         return

#     fields = TABLES[table_name][1]  # Получаем список полей
#     required_fields = ", ".join(fields)

#     if len(context.args) != len(fields) + 1:
#         await update.message.reply_text(f"Используйте: /add_record {table_name} <{required_fields}>")
#         return

#     values = context.args[1:]  # Значения для вставки
#     cursor = db.cursor()
#     placeholders = ", ".join(["%s"] * len(values))  # Подготовка плейсхолдеров для SQL
#     cursor.execute(f"INSERT INTO {table_name} ({', '.join(fields)}) VALUES ({placeholders})", values)
#     db.commit()

#     await update.message.reply_text('Запись добавлена.')