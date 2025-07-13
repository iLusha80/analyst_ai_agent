import streamlit as st
import pandas as pd

# 1. Заголовок приложения
st.title('Простое веб-приложение на Streamlit')

# 2. Интерактивный слайдер
st.header('1. Интерактивный слайдер')
x = st.slider('Выберите число', min_value=0, max_value=100, value=25)

# 3. Вывод результата на основе значения слайдера
st.write(f'Квадрат числа {x} равен {x**2}')

# 4. Демонстрация работы с данными (Pandas)
st.header('2. Работа с данными')
st.write('Это пример отображения DataFrame:')

df = pd.DataFrame({
    'Колонка A': [1, 2, 3, 4],
    'Колонка B': [10, 20, 30, 40]
})

# Streamlit автоматически преобразует DataFrame в красивую интерактивную таблицу
st.write(df)

# 5. Кнопка
st.header('3. Кнопка')
if st.button('Нажми на меня'):
    st.balloons() # Показывает воздушные шарики!
    st.success('Кнопка была нажата!')