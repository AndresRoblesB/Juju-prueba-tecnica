import sys
from src.api_client import sample_to_raw_orders, sample_to_raw_products, sample_to_raw_users
from src.transforms import run_transformations


def main(since):
    """
    Pipeline ETL principal
    
    Arguments:
        since: str - Fecha en formato YYYY-MM-DD para filtrar órdenes
    """
    print("="*50)
    print(f"Iniciando ETL Job - since: {since}")
    print("="*50)

    #EXtraccion
    print("1. Extracción - Moviendo datos a raw/...")
    sample_to_raw_orders(since)
    sample_to_raw_products()
    sample_to_raw_users()
    print("Extracción completada")

    #Transformacion
    print("2. Transformacion- Procesando datos a curated/...")
    run_transformations()
    print("Transformacion Completada")
    
    print("\n" + "="*50)
    print("ETL Job finalizado exitosamente")
    print("="*50)


if __name__ == '__main__':
    # Leer parámetro since desde línea de comandos si se necesita
    if len(sys.argv) > 1:
        since = sys.argv[1]
    else:
        # Valor por defecto
        since = '2025-08-20'
        print(f"No se proporcionó fecha, usando valor por defecto: {since}")
    
    main(since)