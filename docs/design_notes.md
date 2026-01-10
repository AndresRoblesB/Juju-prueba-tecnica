# Design Notes - Pipeline ETL

## 1. Stack Tecnológico

**Decisión**: pandas + CSV (sin PySpark, DuckDB, ni MSSQL)

**Justificación**: Volumen pequeño (< 1GB), sencillez y mejor reproducibilidad evitando instalación de dependencias internas. pandas es suficiente para transformaciones requeridas (joins, dedupe, filtros). Migración a DuckDB/PySpark solo si se manejan volumen medianamente grandes o cuando se necesiten usar queries SQL complejas ( o simplemente si la persona se siente más cómodo usando lenguaje SQL).

---

## 2. Estrategia de Capa Raw

### Orders (api_orders.json → raw/orders.json)
- **Filtrado incremental**: Parámetro `--since` filtra órdenes >= fecha especificada
- **Registros sin fecha descartados**:Se asume que los registros que no tengan fecha no son necesarios debido a que normalmente los KPI de ventas se leen en base a la fecha (Venta po dia, mes, etc)
- **Justificación**: Evita cargar historial completo, soporta cargas incrementales, órdenes sin fecha no son analizables

### Users & Products (CSV → raw/)
- **Copia completa sin particionado**: Se copian todos los registros sin filtrar por fecha
- **Justificación**: 
  - Tablas dimensionales pequeñas y relativamente estáticas
  - Joins con fact_order requieren acceso a todos los clientes/productos históricos
  - La fecha de creación del cliente es irrelevante vs. sus datos transaccionales

---

## 3. Idempotencia

**Técnica**: Deduplicación en curated usando `order_id` como clave única
- En raw: se permite duplicados (refleja fuente real)
- En curated: `drop_duplicates(subset=['order_id'], keep='first')` basado en timestamp más reciente
- Re-ejecutar el job reemplaza archivos de salida (sobrescritura, no append)

---

## 4. Estrategia de Particionado (Curated)

**fact_order**: Particionado por `order_date` (YYYY-MM-DD) usando Hive-style partitions pensando en que se usará en la nube con herramientas cómo S3 o Athena