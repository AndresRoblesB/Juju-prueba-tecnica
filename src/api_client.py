import json
from datetime import datetime
import os
import shutil

def sample_to_raw_orders(since: str):

    "Arguments:    since: str in format YYYY-MM-DD\n" 

    input_file = 'sample_data/api_orders.json'
    output_file = 'output/raw/orders.json'
    
    # Verificamos que el archivo de entrada exista
    if not os.path.exists(input_file):
        print(f"Error: El archivo {input_file} no existe")
        return   
    
    # Crear directorio de salida si no existe
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    
    # Leemos archivo json de entrada
    try:
        with open(input_file, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError:
        print(f'Invalid JSON format in: {input_file}')
        return
    
    since_date = datetime.strptime(since, '%Y-%m-%d')
    
    # Filtramos desde fecha since
    filtered_data = []
    invalid_count = 0
    
    for record in data:
        try:
            # Verificamos que created_at existe y no es None
            if 'created_at' not in record or record['created_at'] is None:
                print(f"Warning: Registro sin fecha ignorado - order_id: {record.get('order_id')}")
                invalid_count += 1
                continue

            # Parseamos la fecha
            date_str = record['created_at'].split('T')[0]
            record_date = datetime.strptime(date_str, '%Y-%m-%d')
            
            if record_date >= since_date:
                filtered_data.append(record)
        except Exception as e:
            print(f"Error procesando record {record.get('order_id')}: {e}")
            invalid_count += 1
    
    # Verificamos si hay datos para exportar
    if not filtered_data:
        print(f"No se encontraron registros desde {since}")
        return
    
    # Exportar archivo de ordenes filtrado por fecha since
    with open(output_file, 'w') as f:
        json.dump(filtered_data, f, indent=2)
    
    
    print(f'Exported: {output_file}')
    print(f'Total registros exportados: {len(filtered_data)}')
    if invalid_count > 0:
        print(f'Total registros inválidos ignorados: {invalid_count}')

def sample_to_raw_products():
    input_file = 'sample_data/products.csv'
    output_file = 'output/raw/products.csv'
    
    #Verificamos que el archivo de entrada exista
    if not os.path.exists(input_file):
        print(f"Error: El archivo {input_file} no existe")
        return   
    
    # Copiar archivo a raw
    shutil.copy2(input_file, output_file)
    print(f'Exported: {output_file}')


def sample_to_raw_users():
    input_file = 'sample_data/users.csv'
    output_file = 'output/raw/users.csv'
    
    #Verificamos que el archivo de entrada exista
    if not os.path.exists(input_file):
        print(f"Error: El archivo {input_file} no existe")
        return   
    
    # Copiar archivo a raw
    shutil.copy2(input_file, output_file)
    print(f'Exported: {output_file}')
