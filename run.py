import pandas as pd
import random
import getopt
import sys
from dotenv import load_dotenv, find_dotenv
import os
import sqlalchemy as db

load_dotenv(find_dotenv())

# Вариант для запуска через консоль. Напрример через крон
connection = engine = db.create_engine(os.getenv('DB')).connect()
# connection = engine = db.create_engine('sqlite:///database.db').connect()

def sum_Qliq_Qoil(table:str):
    '''На входе путь и название фала в виде path_to_file/table.xlsx'''

    # получение данных из таблицы
    df = pd.read_excel(table, header=[0, 1, 2])

    # Добавление даты. Выбрал небольшой период чтобы было что группирвоать.
    days = [str(random.randint(1, 5)).zfill(2) for _ in range(len(df))]
    dates = pd.to_datetime([f'2023-06-{day}' for day in days])
    df.insert(loc=0, column='Dates', value=dates)

    # Удалил 'id' и 'company'. Я предполагаю они нам не нужны т.к мы считаем только тотал по датам.
    df = df.sort_index(axis=1)
    df = df.drop(['id', 'company'], axis=1)
    df['Dates'] = df['Dates'].dt.date
    df = df.groupby(['Dates']).sum()

    # Захардкодил, если будет необхоидмо и это можно автоматизировать.
    df['fact_Qliq'] = df[[('fact', 'Qliq', 'data1'), ('fact', 'Qliq', 'data2')]].sum(axis=1)
    df['fact_Qoil'] = df[[('fact', 'Qoil', 'data1'), ('fact', 'Qoil', 'data2')]].sum(axis=1)
    df['forecast_Qliq'] = df[[('forecast', 'Qliq', 'data1'), ('forecast', 'Qliq', 'data2')]].sum(axis=1)
    df['forecast_Qoil'] = df[[('forecast', 'Qoil', 'data1'), ('forecast', 'Qoil', 'data2')]].sum(axis=1)
    df_end = df.iloc[:, -4:]

    df_end = df_end.reset_index()
    df_end.columns = df_end.columns.droplevel(level=[1, 2])
    print(df_end)
    df_end.to_sql('total', connection, if_exists='append', index=False, index_label='Dates')
try:
    # Сделал для запуска из консоли. Например через тот же крон
    options, args = getopt.getopt(sys.argv[1:], 'h', ['help'])
    for option, argument in options:
        if option == '-h':
            print('Usage: run.py <input_file>.xlsx')
            sys.exit()
    # TODO: запускать через консоль либо напрямую
    # sum_Qliq_Qoil('table.xlsx')
    sum_Qliq_Qoil(*sys.argv[1:])
except:
    print('Usage: run.py <input_file>.xlsx')
    sys.exit(2)
