import pandas as pd



def agregar_columna_num_estacion(df: pd.DataFrame) -> pd.DataFrame:
    """
    Combina las columnas de número de estación de Medellín y Rionegro en una sola columna 'Número de estación'.
    """
    # Fill NaN with empty strings before concatenation
    Medellin = df['Número de estación Medellín'].fillna(0).astype(int)
    Rionegro = df['Número de estación Rionegro'].fillna(0).astype(int)
    
    # Concatenate with space separator
    df.loc[:, 'Numero de estación'] = (Rionegro + Medellin).astype(int)

    # Drop original columns
    df.drop(columns=['Número de estación Medellín', 'Número de estación Rionegro'], inplace=True)
    
    return df
	
def unir_columna_consumido(df: pd.DataFrame) -> pd.DataFrame:
    """
    Unir las columnas 'Estado de la estación/Consumido' y 'Estado de la estación/Cambio de cebo por consumo'
    """
    df.loc[:, 'Estado de la estación/Cambio de cebo por consumo'] = df['Estado de la estación/Consumido'] + df['Estado de la estación/Cambio de cebo por consumo']
    df.drop(columns=['Estado de la estación/Consumido'], inplace=True, errors='ignore')
    return df

def ordenar_columnas_roedores(df: pd.DataFrame, orden: list = None) -> pd.DataFrame:
    """
    """
    columnas_plaguicidas_utilizados = [col for col in df.columns if col.startswith('Plaguicida/')]
    columnas_estado_de_estacion = [col for col in df.columns if col.startswith('Estado de la estación/')]   

    # Orden predefinido de columnas principales
    main_columns = ([
        'ID',
        'Fecha',
        'Mes',
        'Sede',
        'Técnicos',
        'Numero de estación',
        'Estado de la estación']
        +columnas_estado_de_estacion+
        ['Plaguicidas utilizados',
        'Localización',
        'Observaciones'])

    # Orden predefinido de columnas principales
    all_columns = ([
        'ID',
        'Fecha',
        'Fecha pandas',
        'Mes',
        'Sede',
        'Técnicos',
        'Numero de estación',
        'Estado de la estación']
        +columnas_estado_de_estacion+
        ['Plaguicidas utilizados']
        +columnas_plaguicidas_utilizados+
        ['Localización',
        'Observaciones'])
    
    return df[main_columns], df[all_columns]
