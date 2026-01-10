# Design Notes - Pipeline ETL

## 1. Stack Tecnológico

**Decisión**: pandas + CSV (sin PySpark, DuckDB, ni MSSQL)

**Justificación**: Volumen pequeño (< 1GB), sencillez y mejor reproducibilidad evitando instalación de dependencias externas. pandas es suficiente para transformaciones requeridas (joins, dedupe, filtros). Migración a DuckDB/PySpark solo si se manejan volumen medianamente grandes o cuando se necesiten usar queries SQL complejas ( o simplemente si la persona se siente más cómodo usando lenguaje SQL).

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

Los datos de prueba van desde 2025-08-20 hasta el 2025-08-27, para que se tenga en cuenta.

---

## 3. Idempotencia

**Técnica**: Deduplicación en curated usando `order_id` como clave única
- En raw: se permite duplicados (refleja fuente real)
- En curated: `drop_duplicates(subset=['order_id'], keep='first')` basado en timestamp más reciente
- Re-ejecutar el job reemplaza archivos de salida (sobrescritura, no append)

---

## 4. Estrategia de Particionado (Curated)

**fact_order**: Particionado por `order_date` (YYYY-MM-DD) usando Hive-style partitions pensando en que se usará en la nube con herramientas cómo S3 o Athena

Se manejó dos tablas para fact_order: Fact_order_header y fact_order_detail. Esto se hizo para normalizar la información y evitar repetir registros en la tabla debido a al campo items. De esta forma queda mucho mejor organizada la información y se disminuyen los errores.


## 5. Auditoría

Para este caso se realizan validacioes básicas y se usa print() para lanzar algunas alertas, sin embargo, en producción mi recomendación es usar la libería de Python Logging para guardar logs de forma más profesional y si está en la nube (en un EC2 tal vez) apoyarse en CloudWatch (usando el agent) para guardar los logs y realizar las alertas en bases reglas definidas allá.

Por otro lado, tambien estaría la opción de usar Airflow para Orquestar el flujo y tener una visión más clara y centralizada de las ejecuiones

## 6. Reproducibilidad

Se decidió crear un repositorio de GutHub para este proyecto, de esta forma podemos tener acceso a las distintas versiones y commits que se han realizado y adicional nos sirve para tener una sóla versión del código con las dependencias y librerías que se necesitan para funcionar.

El çódigo se puede correr en Windows generando los entornos virtuales, sin embargo, el uso de Docker mejora la reproducibilidad por mucho debido a que sólo debemos preocuparnos por lanzar la imagen de docker y automaticamente instalará las dependencias necesarias. De esta forma evitamos que en algunos computadores no pueda funcionar, además, permite una integración más fácil a entornos Linux aumentando la posibilidad de usar CI/CD en una futura ocasión para realizar los depliegues.