import pandas as pd
import psycopg2

conn = psycopg2.connect(
    host="localhost", port=5432,
    database="postgres", 
    user="postgres", 
    password="admin"
)
cursor = conn.cursor()

df = pd.read_excel("Stock_Items_import.xlsx")
print(f"Строк в файле: {len(df)}")

ok, skip = 0, 0
for _, row in df.iterrows():
    cursor.execute(
        "SELECT product_id FROM products WHERE name=%s AND manufacturer=%s",
        (row['Наименование товара'].strip(), row['Производство'].strip())
    )
    p = cursor.fetchone()
    if p is None:
        print(f"НЕТ товара: {row['Наименование товара']} / {row['Производство']}")
        skip += 1
        continue

    cursor.execute("SELECT size_id FROM sizes WHERE value=%s",
                   (row['Вариант исполнения'].strip(),))
    s = cursor.fetchone()
    if s is None:
        print(f"НЕТ размера: {row['Вариант исполнения']}")
        skip += 1
        continue

    cursor.execute(
        """INSERT INTO stock_items (product_id, size_id, quantity, price)
           VALUES (%s,%s,%s,%s)
           ON CONFLICT (product_id, size_id) DO UPDATE
           SET quantity=EXCLUDED.quantity, price=EXCLUDED.price""",
        (p[0], s[0], int(row['Количество доступное для заказа']),
         float(row['Цена варианта']))
    )
    ok += 1

conn.commit()
cursor.close()
conn.close()
print(f"Импорт остатков: вставлено/обновлено {ok}, пропущено {skip}")