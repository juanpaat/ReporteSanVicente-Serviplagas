import pandas as pd
import config as cfg
from typing import Tuple


def _buscar_columna(columnas: list, pest_name: str, prefijo: str) -> str:
    """
    Busca la columna que corresponde a un tipo de plaga dado un prefijo.
    Maneja inconsistencias de nombres (ej: 'Cucaracha' vs 'Cucarachas').

    Args:
        columnas (list): Lista de nombres de columnas del DataFrame.
        pest_name (str): Nombre del tipo de plaga (ej: 'Hormigas').
        prefijo (str): Prefijo de la columna (ej: 'Qu\u00e9 especie de').

    Returns:
        str: Nombre de la columna encontrada, o None.
    """
    # Intento exacto
    exacta = f'{prefijo} {pest_name}'
    if exacta in columnas:
        return exacta

    # Intento con/sin 's' al final
    pest_lower = pest_name.lower().rstrip('s')
    for col in columnas:
        if col.startswith(prefijo):
            col_tail = col[len(prefijo):].strip().lower().rstrip('s')
            if col_tail == pest_lower:
                return col
    return None


def convertir_columnas_a_filas(df: pd.DataFrame) -> pd.DataFrame:
    """
    Crea una fila por cada tipo de plaga con evidencia (Evidencia de plagas/X == 1).
    Para cada plaga agrega las columnas: Qu\u00e9 especie, Cantidad, Ubicaci\u00f3n exacta.

    Args:
        df (pd.DataFrame): El DataFrame con columnas de evidencia de plagas.

    Returns:
        pd.DataFrame: DataFrame con una fila por cada plaga evidenciada.
    """
    # Columnas de evidencia de plagas (binarias)
    ev_cols = [c for c in df.columns if c.startswith('Evidencia de plagas/')]

    # Columnas base que se mantienen en cada fila
    base_cols = [c for c in df.columns
                 if not c.startswith('Evidencia de plagas/')
                 and not c.startswith('Qu\u00e9 especie de')
                 and not c.startswith('cantidad de')
                 and not c.startswith('Ubicaci\u00f3n exacta de')
                 and c != 'Evidencia de plagas']

    todas_las_columnas = list(df.columns)

    rows = []
    for _, row in df.iterrows():
        tiene_alguna = False
        for ev_col in ev_cols:
            if row.get(ev_col, 0) == 1:
                tiene_alguna = True
                pest_name = ev_col.split('/', 1)[1]

                # Buscar columnas correspondientes
                col_especie = _buscar_columna(todas_las_columnas, pest_name, 'Qu\u00e9 especie de')
                col_cantidad = _buscar_columna(todas_las_columnas, pest_name, 'cantidad de')
                col_ubicacion = _buscar_columna(todas_las_columnas, pest_name, 'Ubicaci\u00f3n exacta de')

                # Construir fila
                new_row = {col: row[col] for col in base_cols}
                new_row['Evidencia de plagas'] = pest_name
                new_row['Qu\u00e9 especie'] = str(row.get(col_especie, '')) if col_especie else ''
                new_row['Cantidad'] = row.get(col_cantidad, '') if col_cantidad else ''
                new_row['Ubicaci\u00f3n exacta'] = str(row.get(col_ubicacion, '')) if col_ubicacion else ''

                # Limpiar NaN
                for k in ('Qu\u00e9 especie', 'Cantidad', 'Ubicaci\u00f3n exacta'):
                    if str(new_row[k]) in ('nan', 'None'):
                        new_row[k] = ''

                rows.append(new_row)

        # Si no tiene ninguna evidencia, agregar fila con 'Sin evidencia'
        if not tiene_alguna:
            new_row = {col: row[col] for col in base_cols}
            new_row['Evidencia de plagas'] = 'Sin evidencia'
            new_row['Qu\u00e9 especie'] = ''
            new_row['Cantidad'] = ''
            new_row['Ubicaci\u00f3n exacta'] = ''
            rows.append(new_row)

    if not rows:
        result_cols = base_cols + ['Evidencia de plagas', 'Qu\u00e9 especie', 'Cantidad', 'Ubicaci\u00f3n exacta']
        return pd.DataFrame(columns=result_cols)

    return pd.DataFrame(rows)


def ordenar_columnas_zonas_comunes(df: pd.DataFrame) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Ordena las columnas del DataFrame seg\u00fan el orden especificado.

    Args:
        df (pd.DataFrame): El DataFrame original.

    Returns:
        A tuple of two pd.DataFrame: The DataFrame with the main columns ordered, and the DataFrame with all columns ordered.
    """

    # Orden predefinido de columnas principales
    main_columns = [
        'Fecha',
        'Mes',
        'Sede',
        'T\u00e9cnicos',
        'Evidencia de plagas',
        'Qu\u00e9 especie',
        'Cantidad',
        'Ubicaci\u00f3n exacta']

    # Orden predefinido de todas las columnas
    all_columns = [
        'Fecha',
        'Fecha pandas',
        'Mes',
        'Sede',
        'T\u00e9cnicos',
        'Evidencia de plagas',
        'Qu\u00e9 especie',
        'Cantidad',
        'Ubicaci\u00f3n exacta']

    # Filtrar solo columnas que existen
    main_columns = [c for c in main_columns if c in df.columns]
    all_columns = [c for c in all_columns if c in df.columns]

    return df[main_columns], df[all_columns]
