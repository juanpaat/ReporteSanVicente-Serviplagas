import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import math
import numpy as np
from datetime import datetime
from config import meses_esp



def plot_estado_lamparas_por_mes(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    """
    Generate a faceted bar/line/point chart showing monthly lamp condition trends.

    Parameters:
    -----------
    df : pd.DataFrame
        Transformed DataFrame with columns: 'Mes', lamp status columns.

    Returns:
    --------
    None
    """
    # Columnas estado de la lampara
    columnas = df.filter(regex =r'^Estado de la lámpara/').columns.tolist()

    # Group and summarize by month
    grouped = df.groupby('Mes')[columnas].sum().reset_index()

    # Renombrar las columnas
    rename_dict = {col: col.replace('Estado de la lámpara/', '') for col in columnas}
    grouped.rename(columns=rename_dict, inplace=True)

    # Melt to long format
    long_df = grouped.melt(id_vars='Mes', var_name='Estado', value_name='Cantidad')

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

    # Plot
    g = sns.FacetGrid(long_df, col='Estado', col_wrap=3, sharey=False, sharex=False, height=3.5)
    g.map_dataframe(sns.barplot, x='Mes', y='Cantidad', alpha=0.1, color='steelblue', edgecolor='black')
    g.map_dataframe(sns.lineplot, x='Mes', y='Cantidad', marker='o', color='black')

    for ax in g.axes.flatten():
        # Rotate and size x-axis labels
        ax.tick_params(axis='x', rotation=45, labelsize=6)
        ax.tick_params(axis='x', labelbottom=True)

        # Gridlines
        ax.grid(True, axis='x', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
        ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')

        # Y-axis scaling and ticks
        y_min, y_max = ax.get_ylim()
        y_max = math.ceil(y_max)
        y_min = math.floor(y_min)
        step = max(1, math.ceil((y_max - y_min) / 5))
        ax.set_yticks(range(y_min, y_max + 1, step))
        ax.set_ylim(bottom=0)

    g.set_titles("{col_name}")
    g.set_axis_labels("", "Cantidad de lámparas")
    g.fig.suptitle("Estado de la estación en el tiempo", fontsize=14)
    g.fig.subplots_adjust(top=0.92)

    plt.tight_layout()
    return grouped, g.fig



def plot_estado_lamparas_con_leyenda(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    """
    Genera un gráfico de dispersión con burbujas que muestra el estado de las lámparas por área en el mes más reciente.

    Parameters:
    -----------
    df : pd.DataFrame
        Transformed DataFrame with 'Mes', 'Lámpara', and lamp status columns.
    save_path : str, optional
        Path to save the plot. If None, plot is displayed only.

    Returns:
    --------
    None
    """

    
    # Columnas estado de la lampara luego eliminar la parte del prefijo
    raw_status_cols = df.filter(regex =r'^Estado de la lámpara/').columns.tolist()
    status_cols = [col.replace('Estado de la lámpara/', '') for col in raw_status_cols]

    # Renombrar las columnas
    rename_dict = {col: col.replace('Estado de la lámpara/', '') for col in raw_status_cols}
    df.rename(columns=rename_dict, inplace=True)


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


    # Group and summarize lamp conditions
    grouped = filtered.groupby('Lámpara').agg({
        col: 'sum' for col in status_cols
    }).reset_index()

    # Add total visits
    grouped['Total de visitas'] = grouped[status_cols].sum(axis=1)

    # Remove lamps with no visits
    grouped = grouped[grouped['Total de visitas'] > 0]

    if grouped.empty:
        print("[Warning] No lamp data found for visualization")
        return

    # Melt to long format
    all_cols = status_cols + ['Total de visitas']
    long_df = grouped.melt(id_vars='Lámpara',
                           value_vars=all_cols,
                           var_name='Estado',
                           value_name='Cantidad')


    # Ensure proper ordering of status categories
    long_df['Estado'] = pd.Categorical(long_df['Estado'], categories=all_cols, ordered=True)

    # Enhanced color map
    custom_palette = {
        'Buena potencia': '#2E8B57',  
        'Deteriorada': '#FF8C00',  
        'Apagada': '#DC143C',  
        'Bombillo averiado': '#DC143C', 
        'Desconectada': '#DC143C', 
        'Faltante': '#DC143C',  
        'Lámina saturada': '#FF8C00',  
        'Obstruida': '#FF8C00', 
        'Baja potencia': '#FF8C00',
        'Total de visitas': "#000000"  
    }

    # Calculate optimal figure size
    n_lamps = len(grouped['Lámpara'].unique())
    n_states = len(all_cols)
    fig_width = max(16, n_states * 0.8)  # Wider for legend
    fig_height = max(8, n_lamps * 0.5)

    # Filter out NaN values for plotting (zeros will remain as small dots)
    plot_data = long_df.dropna(subset=['Cantidad'])

    if plot_data.empty:
        print("[Warning] No data to plot after filtering")
        return

    # Create figure with subplot for legend
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(fig_width, fig_height),
                                   gridspec_kw={'width_ratios': [3, 1]})

    # Main plot on left
    scatter_plot = sns.scatterplot(
        data=plot_data,
        x='Estado',
        y='Lámpara',
        size='Cantidad',
        hue='Estado',
        palette=custom_palette,
        legend=False,
        sizes=(15, 800),  # Smaller minimum size for zeros
        edgecolor='black',
        linewidth=0.7,
        marker='o',
        alpha=0.8,
        ax=ax1
    )

    # Add text labels to main plot (only for values > 0)
    for i, row in plot_data[plot_data['Cantidad'] > 0].iterrows():
        # Choose text color based on bubble color intensity
        estado = row['Estado']
        if estado in ['Total de visitas', 'Bombillo averiado', 'Desconectada', 'Faltante', 'Baja potencia']:
            text_color = 'white'
        else:
            text_color = 'white'

        ax1.text(
            x=row['Estado'],
            y=row['Lámpara'],
            s=int(row['Cantidad']),
            ha='center',
            va='center',
            color=text_color,
            fontsize=8,
            fontweight='light'
        )

    # Format main plot
    ax1.set_title("Estado de las lámparas por área", fontsize=16, fontweight='light', pad=20)
    ax1.set_xlabel("Estado de la lámpara", fontsize=12, fontweight='light')
    ax1.set_ylabel("Lámpara", fontsize=12, fontweight='light')
    ax1.tick_params(axis='x', rotation=90, labelsize=10)
    ax1.tick_params(axis='y', labelsize=10)
    ax1.grid(True, axis='both', linestyle='--', alpha=0.3, linewidth=0.5)

    # Create custom legend on right
    ax2.axis('off')

    status_meanings = {
        'Buena potencia': 'Lámpara funcionando bien',
        'Deteriorada': 'Requiere mantenimiento',
        'Lámina saturada': 'Superficie llena de insectos',
        'Obstruida': 'Visión obstruida',
        'Baja potencia': 'Funciona con poca intensidad',
        'Apagada': 'Sin funcionamiento',
        'Bombillo averiado': 'Bombillo dañado',
        'Desconectada': 'Sin conexión eléctrica',
        'Faltante': 'Lámpara no instalada',
        'Total de visitas': 'Total de inspecciones'
    }

    # Only show legend items that exist in the data
    existing_estados = plot_data['Estado'].unique()

    y_pos = 0.95
    ax2.text(0.05, 0.98, "Estado", fontsize=14, fontweight='light',
             transform=ax2.transAxes, va='top')

    for estado, descripcion in status_meanings.items():
        if estado in existing_estados:
            # Draw colored circle
            ax2.scatter(0.1, y_pos, s=300, c=custom_palette[estado],
                        edgecolor='black', linewidth=1, transform=ax2.transAxes)

            # Add text description
            ax2.text(0.2, y_pos, f"{estado}",
                     fontsize=10, va='center', ha='left', fontweight='light',
                     transform=ax2.transAxes)
            ax2.text(0.2, y_pos - 0.03, f"{descripcion}",
                     fontsize=9, va='center', ha='left', style='italic',
                     transform=ax2.transAxes, color='gray')
            y_pos -= 0.08

    # Remove spines for cleaner look
    for spine in ax1.spines.values():
        spine.set_visible(False)
    
    # Add size legend
    if y_pos > 0.2:  # Only if there's space
        ax2.text(0.05, y_pos - 0.05, "Tamaño del círculo:", fontsize=11, fontweight='bold',
                 transform=ax2.transAxes)
        ax2.text(0.05, y_pos - 0.08, "= Cantidad de casos", fontsize=10,
                 transform=ax2.transAxes, color='gray')

    # Add overall title and caption
    fig.text(0.99, 0.01, caption, horizontalalignment='right',
             fontsize=10, style='normal', alpha=0.7)

    # Adjust layout
    plt.tight_layout()
    plt.subplots_adjust(top=0.92, bottom=0.08)

    return grouped, fig







def plot_capturas_especies_por_mes(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    """
    Generate a faceted bar/line/point chart showing monthly captures of various insect species.

    Parameters:
    -----------
    df : pd.DataFrame
        Transformed lamparas DataFrame with 'Mes' and species capture columns.

    Returns:
    --------
    None
    """
    # Columnas de especies capturadas
    columnas = df.filter(regex =r'^(Cantidad de )').columns.tolist()
    
    # Group and summarize by month
    grouped = df.groupby('Mes')[columnas].sum().reset_index() 

    # Renombrar las columnas
    rename_dict = {col: col.replace('Cantidad de ', '').capitalize() for col in columnas}
    grouped.rename(columns=rename_dict, inplace=True)



    # Melt to long format
    long_df = grouped.melt(id_vars='Mes', var_name='Especie', value_name='Cantidad')

    # Ensure Mes is ordered chronologically
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

    # Faceted plot
    g = sns.FacetGrid(long_df, col='Especie', col_wrap=3, sharey=False, sharex=False, height=3.5)
    g.map_dataframe(sns.barplot, x='Mes', y='Cantidad', alpha=0.1, color='steelblue', edgecolor='black')
    g.map_dataframe(sns.lineplot, x='Mes', y='Cantidad', marker='o', color='black')

    # Style each axis
    for ax in g.axes.flatten():
        ax.tick_params(axis='x', rotation=45, labelsize=6)
        ax.tick_params(axis='x', labelbottom=True)
        ax.grid(True, axis='x', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
        ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')

        # Adjust y-ticks dynamically
        y_min, y_max = ax.get_ylim()
        y_max = math.ceil(y_max)
        y_min = math.floor(y_min)
        step = max(1, math.ceil((y_max - y_min) / 5))
        ax.set_yticks(range(y_min, y_max + 1, step))
        ax.set_ylim(bottom=0)

    g.set_titles("{col_name}")
    g.set_axis_labels("", "Cantidad")
    g.fig.suptitle("Cantidad de capturas de especies por mes", fontsize=14)
    g.fig.subplots_adjust(top=0.92)

    plt.tight_layout()
    return grouped, g.fig






def plot_tendencia_total_capturas(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
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



