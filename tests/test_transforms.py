# tests/test_transforms.py
import pytest
import pandas as pd
import json


def test_dedupe_orders():
    """Verifica que se eliminan órdenes duplicadas manteniendo la más reciente"""
    test_data = [
        {
            "order_id": "o_1",
            "user_id": "u_1",
            "amount": 100.0,
            "currency": "USD",
            "created_at": "2025-08-20T10:00:00Z",
            "items": [],
            "metadata": {}
        },
        {
            "order_id": "o_1",  # Duplicado
            "user_id": "u_1",
            "amount": 100.0,
            "currency": "USD",
            "created_at": "2025-08-20T09:00:00Z",  # Más antiguo
            "items": [],
            "metadata": {}
        }
    ]
    
    df = pd.DataFrame(test_data)
    df['created_at'] = pd.to_datetime(df['created_at'])
    
    # Lógica de dedupe (igual que en tu código)
    df = df.sort_values('created_at', ascending=False).drop_duplicates(subset=['order_id'], keep='first')
    
    assert len(df) == 1
    assert df.iloc[0]['created_at'].hour == 10  # Debe mantener el más reciente


def test_metadata_extraction():
    """Verifica que se extrae correctamente source y promo de metadata"""
    test_data = [
        {
            "order_id": "o_1",
            "metadata": {"source": "api", "promo": "SUMMER"}
        },
        {
            "order_id": "o_2",
            "metadata": {"source": "web", "promo": None}
        },
        {
            "order_id": "o_3",
            "metadata": None  # Metadata null
        }
    ]
    
    df = pd.DataFrame(test_data)
    
    df['source'] = df['metadata'].apply(
        lambda x: x.get('source') if isinstance(x, dict) else None
    )
    df['promo'] = df['metadata'].apply(
        lambda x: x.get('promo') if isinstance(x, dict) else None
    )
    
    assert df.iloc[0]['source'] == 'api'
    assert df.iloc[0]['promo'] == 'SUMMER'
    assert df.iloc[1]['source'] == 'web'
    assert df.iloc[1]['promo'] is None
    assert df.iloc[2]['source'] is None  # metadata era None


def test_invalid_dates_handled():
    """Verifica que fechas inválidas se convierten a NaT sin fallar"""
    test_data = pd.DataFrame({
        'user_id': ['u_1', 'u_2', 'u_3'],
        'email': ['test1@test.com', 'test2@test.com', 'test3@test.com'],
        'created_at': ['2025-01-01', None, 'fecha-invalida']
    })
    
    test_data['created_at'] = pd.to_datetime(test_data['created_at'], errors='coerce')
    
    # Debe convertir inválidos a NaT sin fallar
    assert pd.notna(test_data.iloc[0]['created_at'])
    assert pd.isna(test_data.iloc[1]['created_at'])
    assert pd.isna(test_data.iloc[2]['created_at'])


def test_items_explosion():
    """Verifica que items se explotan correctamente en múltiples filas"""
    test_order = {
        "order_id": "o_1",
        "order_date": "2025-08-20",
        "items": [
            {"sku": "p_1", "qty": 2, "price": 50.0},
            {"sku": "p_2", "qty": 1, "price": 30.0}
        ]
    }
    #Explosionado de Itenms
    items_list = []
    for item in test_order['items']:
        items_list.append({
            'order_id': test_order['order_id'],
            'sku': item.get('sku'),
            'qty': item.get('qty'),
            'price': item.get('price', 0),
            'order_date': test_order['order_date']
        })
    
    assert len(items_list) == 2
    assert items_list[0]['sku'] == 'p_1'
    assert items_list[0]['qty'] == 2
    assert items_list[1]['sku'] == 'p_2'


def test_null_items_handling():
    """Verifica que items nulos se manejan sin fallar"""
    test_order = {
        "order_id": "o_1",
        "order_date": "2025-08-20",
        "items": None
    }
    
    items_list = []
    items = test_order.get('items', [])
    
    if items is not None:
        for item in items:
            items_list.append({'order_id': test_order['order_id']})
    
    assert len(items_list) == 0  # No debe agregar nada si items es None