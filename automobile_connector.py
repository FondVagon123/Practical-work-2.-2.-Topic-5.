import pandas as pd
import numpy as np
import os # Додаємо для встановлення робочої директорії, якщо потрібно

# Переконайтеся, що файл даних знаходиться в цій же папці
FILE_NAME = 'Automobile_data.csv'

def load_automobile_data():
    """
    Завантажує, очищає та готує дані автомобілів для OLAP-аналізу.
    
    1. Обробляє пропущені значення '?'.
    2. Перейменовує колонки для зручності.
    3. Конвертує ключові показники ('Price', 'Horsepower') у числовий тип.
    4. Фільтрує дані за японськими виробниками.
    """
    try:
        # 1. Завантаження даних та обробка '?' як відсутніх значень
        df = pd.read_csv(FILE_NAME, na_values='?')
        
        # 2. Перейменування колонок
        # Припускаємо, що колонки йдуть у порядку, наданому раніше користувачем
        df.columns = [
            'symboling', 'Normalized_Losses', 'Brand', 'Fuel_Type', 
            'Aspiration', 'Num_of_Doors', 'Body_Style', 'Drive_Type', 
            'Engine_Location', 'Wheel_Base', 'Length', 'Width', 'Height', 
            'Curb_Weight', 'Engine_Type', 'Num_of_Cylinders', 'Engine_Size', 
            'Fuel_System', 'Bore', 'Stroke', 'Compression_Ratio', 
            'Horsepower', 'Peak_RPM', 'City_MPG', 'Highway_MPG', 'Price'
        ]
        
        # 3. Очищення та Перетворення Типів Даних
        numeric_cols = ['Normalized_Losses', 'Horsepower', 'Peak_RPM', 'Price']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce') 

        # 4. Обробка відсутніх значень
        # Заповнюємо 'Price' та 'Horsepower' медіаною
        df['Price'].fillna(df['Price'].median(), inplace=True)
        df['Horsepower'].fillna(df['Horsepower'].median(), inplace=True)
        # Заповнюємо 'Num_of_Doors' найчастішим значенням
        df['Num_of_Doors'].fillna(df['Num_of_Doors'].mode()[0], inplace=True)
        
        # 5. Фільтрація за Японськими Виробниками (тема аналізу)
        japanese_brands = ['toyota', 'honda', 'nissan', 'mazda', 'subaru', 'mitsubishi', 'isuzu']
        df_filtered = df[df['Brand'].isin(japanese_brands)].copy()
        
        return df_filtered
        
    except FileNotFoundError:
        print(f"❌ Помилка: Файл '{FILE_NAME}' не знайдено.")
        return None
    except Exception as e:
        print(f"❌ Виникла помилка під час обробки даних: {e}")
        return None

if __name__ == '__main__':
    data = load_automobile_data()
    if data is not None:
        print(f"✅ Dataframe готовий для аналізу. Кількість записів: {len(data)}")
