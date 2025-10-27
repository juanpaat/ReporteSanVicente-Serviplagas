import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import numpy as np
from datetime import datetime
from config import meses_esp




## plots
def plot_tendencia_total_eliminacion(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    """
    Generate a bar + line + point chart showing the monthly trend of total species captures.

    Parameters:
    -----------
    df : pd.DataFrame
        Transformed lamparas DataFrame with 'Mes' and species columns.

    Returns:
    --------
    None
    """

    # Columnas de especies capturadas
    species_cols = df.filter(regex =r'^(Cantidad de )').columns.tolist()

    # Group and sum total captures
    trend_df = df.groupby('Mes')[species_cols].sum().sum(axis=1).reset_index()

    # Renombrar las columnas
    trend_df.columns = ['Mes', 'total']

    # Sort 'Mes' if in 'Mon YYYY' format
    try:
        # Create reverse mapping (Spanish -> English)  
        meses_eng = {v: k for k, v in meses_esp.items()}
        
        # Convert Spanish months to English for sorting
        def spanish_month_to_datetime(mes_str):
            for spanish, english in meses_eng.items():
                if spanish in mes_str:
                    english_mes = mes_str.replace(spanish, english)
                    return pd.to_datetime(english_mes, format='%b %Y')
            return pd.to_datetime(mes_str, format='%b %Y')
        
        # Get unique months and sort them
        unique_months = trend_df['Mes'].unique()
        sorted_months = sorted(unique_months, key=spanish_month_to_datetime)
        
        trend_df['Mes'] = pd.Categorical(
            trend_df['Mes'],
            categories=sorted_months,
            ordered=True
        )
    except Exception as e:
        print(f"[Warning] Could not parse and sort 'Mes': {e}")

    # Crear figura y eje
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.set_style("whitegrid")


    # Bars
    bars = sns.barplot(data=trend_df, x='Mes', y='total', alpha=0.1, color='steelblue',
                       edgecolor='black', linewidth=0.5, ax=ax)

    # Line
    sns.lineplot(data=trend_df, x='Mes', y='total', color='black', marker='o',
                 markersize=8, linewidth=2, ax=ax)

    # Labels on points - using the actual x positions from the plot
    for i, row in trend_df.iterrows():
        ax.text(x=row['Mes'],
                y= row['total'] + max(trend_df['total']) * 0.02,
                s= str(int(row['total'])),
                ha='center', va='bottom',
                fontsize=9, weight='bold',
                bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8, edgecolor='none'))


    # Formatting
    ax.set_title("Tendencia de capturas mensuales", fontsize=14, weight='bold', pad=20)
    ax.set_ylabel("Total de capturas", fontsize=12)
    ax.set_xlabel("")
    ax.tick_params(axis='x', rotation=45, labelsize=10)
    ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
    ax.set_axisbelow(True)

    y_max = trend_df['total'].max()
    ax.set_ylim(0, y_max * 1.1)

    if y_max > 1000:
        from matplotlib.ticker import FuncFormatter
        ax.yaxis.set_major_formatter(FuncFormatter(lambda x, p: f'{int(x):,}'))

    fig.tight_layout()
    return trend_df, fig



def plot_nivel_de_infestación(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:

    # Find the most recent 'Mes'
    try:
        df = df.copy()  # Avoid modifying original DataFrame
        
        # Create reverse mapping (Spanish -> English)  
        meses_eng = {v: k for k, v in meses_esp.items()}
        
        # Convert Spanish months to English for parsing
        def spanish_month_to_datetime(mes_str):
            for spanish, english in meses_eng.items():
                if spanish in mes_str:
                    english_mes = mes_str.replace(spanish, english)
                    return pd.to_datetime(english_mes, format='%b %Y')
            return pd.NaT
        
        df['Mes_dt'] = df['Mes'].apply(spanish_month_to_datetime)

        # Check if any dates were parsed successfully
        if df['Mes_dt'].isna().all():
            print("[Error] No se encontraron fechas válidas en la columna 'Mes'")
            return

        latest_month = df.loc[df['Mes_dt'].notna(), 'Mes_dt'].max()
        # Keep Spanish format for caption
        latest_month_spanish = df.loc[df['Mes_dt'] == latest_month, 'Mes'].iloc[0]
        caption = f"Periodo: {latest_month_spanish}"

    except Exception as e:
        print(f"[Error] Falló al identificar el mes más reciente: {e}")
        return

    # Filter to most recent month
    filtered = df[df['Mes'] == latest_month_spanish].copy()

    valores_de_referencia = {
        'Cucaracha Americana': {'bajo': 20, 'medio': 50},
        'Cucaracha Alemana': {'bajo': 20, 'medio': 50},
        'Hormigas': {'bajo': 100, 'medio': 200},
        'Moscas': {'bajo': 5, 'medio': 20},
        'Mosquitos': {'bajo': 5, 'medio': 15},
        'Zancudos': {'bajo': 5, 'medio': 15},
        'Ratón casero': {'bajo': 1, 'medio': 3},
        'Rata Noruega': {'bajo': 1, 'medio': 3},
        'Ratón de tejado': {'bajo': 1, 'medio': 3}
    }

    # Identificar columnas de hallazgos
    columnas_hallazgos = [col for col in filtered.columns if col.startswith('Cantidad de hallazgos de')]
    
    # Función para clasificar un valor
    def clasificar_valor(valor, umbral_bajo, umbral_medio):
        if pd.isna(valor) or valor == 0:
            return 'Sin evidencia'
        elif valor <= umbral_bajo:
            return 'Bajo'
        elif valor <= umbral_medio:
            return 'Medio'
        else:
            return 'Alto'
        
     # Clasificar cada columna de hallazgos
    for col in columnas_hallazgos:
        # Extraer el nombre de la plaga de la columna
        nombre_plaga = col.replace('Cantidad de hallazgos de ', '')
        
        # Obtener umbrales para esta plaga
        if nombre_plaga in valores_de_referencia:
            umbral_bajo = valores_de_referencia[nombre_plaga]['bajo']
            umbral_medio = valores_de_referencia[nombre_plaga]['medio']
        else:
            # Umbrales genéricos si no se encuentra la plaga específica
            umbral_bajo = 50
            umbral_medio = 100
        
        # Crear columna de clasificación
        col_clasificacion = f'Clasificación {nombre_plaga}'
        filtered[col_clasificacion] = filtered[col].apply(
            lambda x: clasificar_valor(x, umbral_bajo, umbral_medio)
        )

    # Get classification columns
    columnas_clasificacion = [col for col in filtered.columns if col.startswith('Clasificación')]

    # Melt the DataFrame to long format for plotting
    melted_df = filtered.melt(
        id_vars='Orden de Mantenimiento',
        value_vars=columnas_clasificacion,
        var_name='Plaga',
        value_name='Nivel de Infestación'
    )
    
    # Clean up plaga names (remove "Clasificación " prefix)
    melted_df['Plaga'] = melted_df['Plaga'].apply(lambda x: x.replace('Clasificación ', ''))
    
    # Count occurrences per infestation level and plaga
    plot_df = melted_df.groupby(['Nivel de Infestación', 'Plaga']).agg({
        'Orden de Mantenimiento': 'count'
    }).reset_index()
    
    # Define infestation level order (excluding 'Sin evidencia')
    niveles = ['Alto', 'Medio', 'Bajo']
    
    # Filter out 'Sin evidencia' from plot data
    plot_df = plot_df[plot_df['Nivel de Infestación'] != 'Sin evidencia']
    
    # Reindex to include all levels for all plagas
    idx = pd.MultiIndex.from_product(
        [niveles, melted_df['Plaga'].unique()],
        names=['Nivel de Infestación', 'Plaga']
    )
    plot_df = plot_df.set_index(['Nivel de Infestación', 'Plaga']).reindex(idx, fill_value=0).reset_index()
    
    # Set categorical order for plotting
    plot_df['Nivel de Infestación'] = pd.Categorical(
        plot_df['Nivel de Infestación'], 
        categories=niveles, 
        ordered=True
    )
    
    # Create summary DataFrame for return (human-readable format)
    summary_df = plot_df.groupby('Nivel de Infestación')['Orden de Mantenimiento'].sum().reset_index()
    summary_df.columns = ['Nivel de Infestación', 'Cantidad de Órdenes']
    
    # Plot - Create faceted plot
    sns.set_style("whitegrid")
    g = sns.FacetGrid(plot_df, col='Plaga', col_wrap=3, height=4, aspect=1.2, sharey=True, sharex=False)

    # Map the barplot
    g.map_dataframe(
        sns.barplot, 
        x='Nivel de Infestación', 
        y='Orden de Mantenimiento',
        palette=['#333333', '#666666', '#999999'],
        edgecolor='black', 
        linewidth=1,
        order=niveles
    )

    # Add value labels on bars
    def add_labels(data, **kwargs):
        ax = plt.gca()
        for i, nivel in enumerate(niveles):
            subset = data[data['Nivel de Infestación'] == nivel]
            if not subset.empty:
                value = subset['Orden de Mantenimiento'].values[0]
                if value > 0:  # Only show label if value is greater than 0
                    ax.text(
                        i, value + 0.3, str(int(value)), 
                        ha='center', va='bottom', fontsize=9, weight='bold',
                        bbox=dict(boxstyle='round,pad=0.3', facecolor='white', 
                                  alpha=0.8, edgecolor='none')
                    )

    g.map_dataframe(add_labels)

    # Formatting
    g.set_titles("{col_name}", fontsize=11, weight='bold')
    g.set_axis_labels("Nivel de Infestación", "Órdenes de Mantenimiento", fontsize=10)
    g.fig.suptitle(
        f"Órdenes de Mantenimiento por Nivel de Infestación y Plaga - {latest_month_spanish}", 
        fontsize=14, weight='bold', y=1.02
    )

    # Rotate x labels for all subplots
    for ax in g.axes.flat:
        ax.tick_params(axis='x', rotation=45, labelsize=9)
        ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5)
        ax.set_axisbelow(True)

    plt.tight_layout()

    return summary_df, g.fig


def plot_plagas_por_especie_mes(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    """
    Genera un gráfico facetado de líneas/barras/puntos que muestra la cantidad de cada especie de plaga por mes.

    Argumentos:
    ----------
    df : pd.DataFrame
        Correctivos DataFrame transformado que contiene las columnas:
        - 'Mes'
        - 'Cantidad de hallazgos de ...' (varias columnas de especies)

    Returns:
    -------
    tuple[pd.DataFrame, plt.Figure]
        DataFrame resumido por mes y la figura del gráfico generado.
    """
    # Columnas que empiezan por 'Cantidad de hallazgos de '
    df_columns = df.filter(regex=r'^Cantidad de hallazgos de ').columns.tolist()
    
    # Group and summarize by month
    grouped = df.groupby('Mes')[df_columns].sum().reset_index()

    # Renombrar las columnas (remove prefix)
    rename_dict = {col: col.replace('Cantidad de hallazgos de ', '') for col in df_columns}
    grouped.rename(columns=rename_dict, inplace=True)

    # Melt into long format
    long_df = grouped.melt(id_vars='Mes', var_name='Plaga', value_name='Cantidad')

    # Sort 'Mes' if in 'Mon YYYY' format
    try:
        # Create reverse mapping (Spanish -> English)  
        meses_eng = {v: k for k, v in meses_esp.items()}
        
        # Convert Spanish months to English for sorting
        def spanish_month_to_datetime(mes_str):
            for spanish, english in meses_eng.items():
                if spanish in mes_str:
                    english_mes = mes_str.replace(spanish, english)
                    return pd.to_datetime(english_mes, format='%b %Y')
            return pd.to_datetime(mes_str, format='%b %Y')
        
        # Get unique months and sort them
        unique_months = long_df['Mes'].unique()
        sorted_months = sorted(unique_months, key=spanish_month_to_datetime)
        
        long_df['Mes'] = pd.Categorical(
            long_df['Mes'],
            categories=sorted_months,
            ordered=True
        )
        grouped['Mes'] = pd.Categorical(
            grouped['Mes'],
            categories=sorted_months,
            ordered=True
        )
    except Exception as e:
        print(f"[Warning] Could not parse and sort 'Mes': {e}")

    # Faceted plot with seaborn
    g = sns.FacetGrid(long_df, col='Plaga', col_wrap=3, sharey=False, sharex=False, height=3.5)
    g.map_dataframe(sns.barplot, x='Mes', y='Cantidad', alpha=0.1, color='steelblue')
    g.map_dataframe(sns.lineplot, x='Mes', y='Cantidad', marker="o", color='black')

    # Format each subplot
    for ax in g.axes.flatten():
        # Rotate x-axis labels using tick_params (cleaner approach)
        ax.tick_params(axis='x', rotation=45, labelsize=6)

        # Force x-axis labels to show on all subplots
        ax.tick_params(axis='x', labelbottom=True)

        # Add vertical gridlines
        ax.grid(True, axis='x', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
        # Keep existing horizontal gridlines (if any) or add them
        ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')

        # Y-axis formatting
        y_min, y_max = ax.get_ylim()
        y_max = math.ceil(y_max)
        y_min = math.floor(y_min)
        step = max(1, math.ceil((y_max - y_min) / 5))
        ax.set_yticks(range(y_min, y_max + 1, step))
        ax.set_ylim(bottom=0)

    g.set_titles("{col_name}", fontsize=11, weight='bold')
    g.set_axis_labels("", "Cantidad de hallazgos", fontsize=10)
    g.fig.suptitle("Cantidad de hallazgos por especie en el tiempo", fontsize=14, weight='bold')
    g.fig.subplots_adjust(top=0.92)  # Espacio para el título

    plt.tight_layout()
    return grouped, g.fig



