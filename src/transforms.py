import pandas as pd
import os
from datetime import datetime

def create_dim_user():

    try:
        """Transforma raw/users.csv a curated/dim_user.parquet"""
        df = pd.read_csv("output/raw/users.csv")

        # Realizamos transformacion de fechas
        df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce') #Hacemos esto para evitar errores cuando la fecha sea invalida o nula
        df['created_at'] = df['created_at'].dt.date

        df = df.dropna(subset=['user_id', 'email'])  #Se asume que son obligatorios, cualquier registro sin estos campos se elimina
        df = df.drop_duplicates(subset=['user_id'], keep='first')    #Eliminamos duplicados basandonos en user_id, manteniendo el primero

        dim_user = df[['user_id', 'email', 'country', 'created_at']]    #Seleccionamos solo las columnas necesarias ( así mantenemos un esquema estandar)

        dim_user.to_parquet("output/curated/dim_user.parquet", index=False)

        print(f"Registros creados en Dim User: {len(dim_user)}")

    except Exception as e:
        print(f"Error creando dim_user: {e}")

def create_dim_product():
    """Transforma raw/products.csv a curated/dim_product.parquet"""

    df = pd.read_csv("output/raw/products.csv")

    df = df.dropna(subset=['sku']) # Eliminamos filas sin sku
    df = df.drop_duplicates(subset=['sku'], keep='first')

    dim_product = df[['sku', 'name', 'category', 'price']]

    dim_product.to_parquet("output/curated/dim_product.parquet", index=False)

    print(f"Registros creados en Dim Product: {len(dim_product)}")

def create_fact_order_header():
    """Transforma raw/orders.json a curated/fact_order_header/ (particionado)"""

    df = pd.read_json("output/raw/orders.json")

    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['order_date'] = df['created_at'].dt.date # Se crea otra columna para particionar

    #Deduplicamos la informacion basandonos en order_id y dejando el más reciente de created_at
    df = df.sort_values('created_at', ascending=False).drop_duplicates(subset=['order_id'], keep='first')

    # Extraemos campos de metadata como columnas usando una lambda
    df['source'] = df['metadata'].apply(
        lambda x: x.get('source') if isinstance(x, dict) else None
    )
    df['promo'] = df['metadata'].apply(
        lambda x: x.get('promo') if isinstance(x, dict) else None
    )


    # Seleccionar columnas del header
    fact_order = df[[
        'order_id',
        'user_id',
        'amount',
        'currency',
        'order_date',
        'created_at',
        'source',
        'promo'
    ]]

    fact_order = fact_order.dropna(subset=['order_id', 'user_id']) # Si no tiene order_id o user_id se asume que el registro es invalido

    # Exportar particionado por fecha
    for date in fact_order['order_date'].unique():
        partition_df = fact_order[fact_order['order_date'] == date]
        output_dir = f'output/curated/fact_order_header/order_date={date}'
        os.makedirs(output_dir, exist_ok=True) #Creamos las carpetas necesarias
        partition_df.to_parquet(f'{output_dir}/part-0.parquet', index=False) #Part-0 por si acaso se necesita mas adelante particionar internamente o recorrer batches  

    print(f"Registros creados en Fact Order Header: {len(fact_order)} y numero de días procesados: {len(fact_order['order_date'].unique())} ")    

def create_fact_order_details():

    """Transforma raw/order_details.json a curated/fact_order_details/ (particionado)"""

    df = pd.read_json("output/raw/orders.json")

    df['created_at'] = pd.to_datetime(df['created_at'], errors='coerce')
    df['order_date'] = df['created_at'].dt.date # Se crea otra columna para particionar

    #Deduplicamos la informacion basandonos en order_id y dejando el más reciente de created_at
    df = df.sort_values('created_at', ascending=False).drop_duplicates(subset=['order_id'], keep='first')

    item_list=[]

    for _, row in df.iterrows():
        order_id = row['order_id']
        order_date = row['order_date']
        items = row.get('items', [])
        
        if items is not None:
            for item in items:
                item_record = {
                    'order_id': order_id,
                    'sku': item.get('sku'),
                    'qty': item.get('qty'),
                    'price': item.get('price', 0), # Si no hay precio entonces 0
                    'order_date': order_date
                }
                item_list.append(item_record)
        else:
            print(f"Warning: order_id {order_id} tiene items nulos")
    fact_order_details = pd.DataFrame(item_list)

    fact_order_details = fact_order_details.dropna(subset=['order_id', 'sku'])

    # Exportar particionado por fecha
    for date in fact_order_details['order_date'].unique():
        partition_df = fact_order_details[fact_order_details['order_date'] == date]
        output_dir = f'output/curated/fact_order_details/order_date={date}'
        os.makedirs(output_dir, exist_ok=True)
        partition_df.to_parquet(f'{output_dir}/part-0.parquet', index=False)

    print(f"Registros creados en Fact Order Details: {len(fact_order_details)}  y numero de días procesados: {len(fact_order_details['order_date'].unique())}")


def run_transformations():
    """Ejecuta todas las transformaciones"""
    print("Iniciando transformaciones...")
    create_dim_user()
    create_dim_product()
    create_fact_order_header()
    create_fact_order_details()
    print("Transformaciones completadas")
