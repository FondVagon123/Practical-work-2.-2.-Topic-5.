import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
# Імпортуємо функцію-конектор
from automobile_connector import load_automobile_data 

# Створення папки для результатів
OUTPUT_DIR = "olap_auto_results"
if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- 1. Завантаження даних ---
# Увага: Ця функція викликає automobile_connector.py, який має бути у тій же папці!
df = load_automobile_data()

if df is None or df.empty:
    print("❌ Дані не завантажено, OLAP-аналіз неможливий.")
    exit()

# --- 2. Slice: Ціна за Брендами та Типом Приводу ---
def olap_slice(df: pd.DataFrame):
    """
    Показник: Price (Медіанна ціна)
    Виміри: Brand (Рядки), Drive_Type (Колонки)
    """
    pivot = pd.pivot_table(
        df,
        values='Price',
        index=['Brand'],
        columns=['Drive_Type'],
        aggfunc='median',
        fill_value=0
    )
    print("\n--- OLAP Slice: Медіанна Ціна за Брендами та Типом Приводу ---")
    print(pivot)
    return pivot

# --- 3. Drill Down: Деталізація Ціни ---
def olap_drill_down(df: pd.DataFrame):
    """
    Показник: Price (Медіанна ціна)
    Виміри: Brand -> Body_Style (Рядки), Drive_Type -> Fuel_Type (Колонки)
    """
    pivot = pd.pivot_table(
        df,
        values='Price',
        index=['Brand', 'Body_Style'],
        columns=['Drive_Type', 'Fuel_Type'],
        aggfunc='median',
        fill_value=0
    )
    print("\n--- OLAP Drill Down: Медіанна Ціна за Сегментом та Типом Приводу/Палива ---")
    # Відображаємо перші 10 рядків/колонок для читабельності
    print(pivot.iloc[:10, :10])
    return pivot

# --- 4. Rotate/Roll-up та Візуалізація: Ціна vs. Потужність ---
def olap_rotate_analysis(df: pd.DataFrame):
    """
    Показники: Horsepower (Середня потужність), Price (Середня ціна)
    Виміри: Brand -> Body_Style (Рядки)
    """
    # Розрахунок середньої ціни та потужності для сегментів
    pivot = pd.pivot_table(
        df,
        values=['Horsepower', 'Price'],
        index=['Brand', 'Body_Style'],
        aggfunc={'Horsepower': 'mean', 'Price': 'mean'}
    )
    # Сортуємо за середньою ціною для виявлення преміальних моделей
    pivot = pivot.sort_values(by='Price', ascending=False)
    print("\n--- OLAP Rotate: Середня Потужність та Ціна за Бренд/Кузов ---")
    print(pivot)
    
    # Виклик функції візуалізації
    plot_rotate_analysis(pivot.reset_index())

    return pivot

# --- 5. Візуалізація Rotate (З додаванням plt.show()) ---
def plot_rotate_analysis(df_pivot: pd.DataFrame):
    """Будує графік та відображає його на екрані."""
    
    if df_pivot.empty:
        print("❌ Неможливо побудувати графік: таблиця Rotate Analysis порожня.")
        return
    
    # Об'єднуємо бренд та кузов для осі X
    df_pivot['Segment'] = df_pivot['Brand'] + ' (' + df_pivot['Body_Style'] + ')'
    
    # Для кращої читабельності візьмемо топ-15 сегментів за ціною
    df_plot = df_pivot.head(15).sort_values(by='Horsepower', ascending=False)

    plt.figure(figsize=(14, 8))
    
    # Подвійна вісь Y для порівняння двох показників
    ax1 = sns.barplot(data=df_plot, x='Segment', y='Price', color='skyblue', label='Середня Ціна', dodge=False)
    
    ax2 = ax1.twinx()
    sns.lineplot(data=df_plot, x='Segment', y='Horsepower', color='red', marker='o', ax=ax2, label='Середня Потужність', linewidth=3)
    
    # Оформлення
    plt.title("OLAP Rotate: Топ-15 Японських Автомобільних Сегментів (Ціна vs. Потужність)")
    ax1.set_xlabel("Сегмент (Бренд + Тип Кузова)")
    ax1.set_ylabel("Середня Ціна (USD)", color='skyblue')
    ax2.set_ylabel("Середня Потужність (HP)", color='red')
    ax1.tick_params(axis='x', rotation=45)
    
    # Об'єднання легенд
    lines, labels = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines + lines2, labels + labels2, loc='upper right')

    plt.tight_layout()
    
    plot_path = os.path.join(OUTPUT_DIR, "auto_rotate_analysis.png")
    plt.savefig(plot_path)
    
    # --- РЯДОК ДЛЯ ВІДОБРАЖЕННЯ ГРАФІКА В ОКРЕМНОМУ ВІКНІ ---
    plt.show() 
    
    plt.close() # Закриваємо вікно після відображення/збереження
    print(f"\n📈 Графік збережено як '{plot_path}'")

# --- 6. Виконання аналізу та збереження ---
if __name__ == '__main__':
    
    slice_result = olap_slice(df)
    drill_result = olap_drill_down(df)
    rotate_result = olap_rotate_analysis(df) # Викликає графік всередині

    # Збереження OLAP-таблиць у CSV
    if not slice_result.empty:
        slice_result.to_csv(os.path.join(OUTPUT_DIR, "auto_slice_result.csv"))
    if not drill_result.empty:
        drill_result.to_csv(os.path.join(OUTPUT_DIR, "auto_drill_result.csv"))
    if not rotate_result.empty:
        rotate_result.to_csv(os.path.join(OUTPUT_DIR, "auto_rotate_result.csv"))

    print("\n✅ OLAP-аналіз японських автовиробників завершено. Перевірте папку 'olap_auto_results'.")
