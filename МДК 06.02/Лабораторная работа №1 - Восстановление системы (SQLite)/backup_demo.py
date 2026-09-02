# -*- coding: utf-8 -*-
"""Демонстрация резервного копирования и восстановления БД SQLite."""
import os
import shutil
import sqlite3
import sys

sys.stdout.reconfigure(encoding="utf-8")

SP = (r"C:\Users\ADMINI~1\AppData\Local\Temp\2\claude\C--Users-Administrator"
      r"\344c183c-a5c9-4b1b-938f-a3b1a5c34ba8\scratchpad")
WORK = os.path.join(SP, "restore_demo")
os.makedirs(WORK, exist_ok=True)

SRC = (r"C:\Users\Administrator\Desktop\MDK 06.02\Лабораторная работа №1 - "
       r"Восстановление системы (SQLite)\Программы"
       r"\3 - Library Management System (библиотека)\library.db")

DB = os.path.join(WORK, "library.db")
BAK = os.path.join(WORK, "library_backup.db")
shutil.copy2(SRC, DB)


def count():
    con = sqlite3.connect(DB)
    n = con.execute("SELECT COUNT(*) FROM Library").fetchone()[0]
    con.close()
    return n


print("1. Исходное состояние базы")
print("   записей в таблице Library:", count())

print("\n2. Создание резервной копии (копирование файла БД)")
shutil.copy2(DB, BAK)
print("   создан файл library_backup.db,", os.path.getsize(BAK), "байт")

print("\n3. Имитация аварии: удаление всех данных")
con = sqlite3.connect(DB)
con.execute("DELETE FROM Library")
con.commit()
con.close()
print("   выполнен запрос: DELETE FROM Library")
print("   записей в таблице Library:", count())

print("\n4. Восстановление базы из резервной копии")
shutil.copy2(BAK, DB)
print("   файл library_backup.db скопирован на место library.db")
print("   записей в таблице Library:", count())

print("\n5. Проверка целостности восстановленной базы")
con = sqlite3.connect(DB)
print("   PRAGMA integrity_check:", con.execute("PRAGMA integrity_check").fetchone()[0])
rows = con.execute("SELECT BK_ID, BK_NAME FROM Library ORDER BY BK_ID LIMIT 3").fetchall()
con.close()
print("   первые записи:", "; ".join(f"{a} - {b}" for a, b in rows))
print("\nДанные восстановлены полностью.")
