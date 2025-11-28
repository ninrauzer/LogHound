# Ejemplos de Configuración

## Ejemplo 1: Modo ERROR (por defecto)
Solo muestra errores críticos en consola.

```json
{
  "base_path": "C:\\LogOps",
  "extensions": [".log", ".txt", ".csv"],
  "reporte_path": "C:\\LogOps\\reportes\\ResumenLogHound.txt",
  "verbose": "ERROR",
  "search_string": "",
  "ip_suspicious_threshold": 50
}
```

## Ejemplo 2: Buscar un usuario específico

```json
{
  "base_path": "C:\\LogOps",
  "extensions": [".log", ".txt", ".csv"],
  "reporte_path": "C:\\LogOps\\reportes\\ResumenLogHound.txt",
  "verbose": "ERROR",
  "search_string": "renan3695",
  "ip_suspicious_threshold": 50
}
```

## Ejemplo 3: Ver TODO (máxima verbosidad)

```json
{
  "base_path": "C:\\LogOps",
  "extensions": [".log", ".txt", ".csv"],
  "reporte_path": "C:\\LogOps\\reportes\\ResumenLogHound.txt",
  "verbose": "TODO",
  "search_string": "",
  "ip_suspicious_threshold": 50
}
```

## Ejemplo 4: Buscar transferencias de un archivo

```json
{
  "base_path": "C:\\LogOps",
  "extensions": [".log", ".txt", ".csv"],
  "reporte_path": "C:\\LogOps\\reportes\\ResumenLogHound.txt",
  "verbose": "WARNING",
  "search_string": "/data/important_file.csv",
  "ip_suspicious_threshold": 50
}
```

## Ejemplo 5: Análisis de IP específica

```json
{
  "base_path": "C:\\LogOps",
  "extensions": [".log", ".txt", ".csv"],
  "reporte_path": "C:\\LogOps\\reportes\\ResumenLogHound.txt",
  "verbose": "ERROR",
  "search_string": "192.168.1.100",
  "ip_suspicious_threshold": 30
}
```

## 📝 Notas

- **verbose**: Define qué se muestra en consola durante el escaneo
- **search_string**: Búsqueda case-insensitive de cualquier texto
- **ip_suspicious_threshold**: Número de eventos para considerar una IP sospechosa
- El reporte SIEMPRE incluye todos los datos, independiente del modo verbose
