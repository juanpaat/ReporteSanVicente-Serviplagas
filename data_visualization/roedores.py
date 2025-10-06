import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
import math
from config import meses_esp



def generate_roedores_station_status_plot(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    """
    Genera un gráfico de barras agrupadas y líneas que muestra el estado de las estaciones de roedores a lo largo del tiempo.

    Parameters:
    ----------
    df : pd.DataFrame
        The 'roedores' DataFrame containing monthly station status counts and a 'Mes' column.

    Returns:
    -------
    plt.Figure
        The matplotlib figure object ready for insertion into Word document
    """
    # extraer columnas que empiezan con "Estado de la estación/"
    columnas_estado_estacion = df.filter(regex = r"Estado de la estación/").columns.tolist()

    # Agrupar y resumir las métricas de estado por mes
    grouped = df.groupby('Mes')[columnas_estado_estacion].sum().reset_index()

    # Renombrar las columnas para eliminar el prefijo "Estado de la estación/"
    rename_dict = {col: col.replace('Estado de la estación/', '') for col in columnas_estado_estacion}
    grouped.rename(columns=rename_dict, inplace=True)


    # Melt into long format
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

    # Create FacetGrid
    g = sns.FacetGrid(long_df, col='Estado', col_wrap=3, sharey=False, sharex=False, height=3.5)

    # Map plotting functions
    g.map_dataframe(sns.barplot, x='Mes', y='Cantidad', alpha=0.1, color='steelblue')
    g.map_dataframe(sns.lineplot, x='Mes', y='Cantidad', marker='o', color='black')

    # Customize each subplot
    for ax in g.axes.flatten():
        # Rotate x-axis labels using plt.setp to avoid warnings
        plt.setp(ax.get_xticklabels(), rotation=45, ha='right', fontsize=6)
        ax.tick_params(axis='x', labelbottom=True)

        # Gridlines
        ax.grid(True, axis='x', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
        ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')

        # Y-axis formatting
        y_min, y_max = ax.get_ylim()
        y_max = math.ceil(y_max)
        y_min = math.floor(y_min)
        step = max(1, math.ceil((y_max - y_min) / 5))
        ax.set_yticks(range(y_min, y_max + 1, step))
        ax.set_ylim(bottom=0)

    # Set titles and labels
    g.set_titles("{col_name}")
    g.set_axis_labels("", "Cantidad")
    g.fig.suptitle("Estado de la estación en el tiempo", fontsize=14)
    g.fig.subplots_adjust(top=0.92)

    # Apply tight layout
    g.fig.tight_layout()

    # Return the figure object
    return grouped, g.fig


def plot_tendencia_eliminacion_mensual(df: pd.DataFrame) -> tuple[pd.DataFrame, plt.Figure]:
    """
    Generate a bar + line + point chart showing monthly rodent elimination trend ("Consumido").

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with rodent control data including 'Mes' and status columns

    Returns:
    --------
    plt.Figure
        The matplotlib figure object ready for insertion into Word document
    """

    # extraer columnas que empiezan con "Estado de la estación/"
    columnas_estado_estacion = df.filter(regex = r"Estado de la estación/").columns.tolist()

    # Agrupar y resumir las métricas de estado por mes
    grouped = df.groupby('Mes')[columnas_estado_estacion].sum().reset_index()

    # Renombrar las columnas para eliminar el prefijo "Estado de la estación/"
    rename_dict = {col: col.replace('Estado de la estación/', '') for col in columnas_estado_estacion}
    grouped.rename(columns=rename_dict, inplace=True)

    # Melt into long format
    long_df = grouped.melt(id_vars='Mes', var_name='Estado', value_name='Cantidad')

    # Filter only rows where Estado is "Cambio de cebo por consumo"
    filtered_df = long_df[long_df['Estado'] == 'Cambio de cebo por consumo'].copy()

    # Group by month and summarize
    summary = filtered_df.groupby('Mes').agg(
        **{'Total de eliminación por mes': ('Cantidad', 'sum')}
    ).reset_index()

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
        unique_months = summary['Mes'].unique()
        sorted_months = sorted(unique_months, key=spanish_month_to_datetime)
        
        summary['Mes'] = pd.Categorical(
            summary['Mes'],
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

    # Create figure and axis explicitly
    fig, ax = plt.subplots(figsize=(10, 5))
    sns.set_style("whitegrid")

    # Bar chart
    bars = sns.barplot(
        data=summary,
        x='Mes',
        y='Total de eliminación por mes',
        alpha=0.1,
        color='steelblue',
        edgecolor='black',
        ax=ax
    )

    # Line chart
    sns.lineplot(
        data=summary,
        x='Mes',
        y='Total de eliminación por mes',
        marker='o',
        markersize=20,
        color='black',
        ax=ax
    )

    # Annotate each point with white text
    for i, row in summary.iterrows():
        ax.text(
            x=row['Mes'],
            y=row['Total de eliminación por mes'],
            s=str(int(row['Total de eliminación por mes'])),
            ha='center',
            va='center',
            color='white',
            fontsize=8,
            weight='light'
        )

    # Formatting
    ax.set_title("Tendencia de eliminación mensual", fontsize=14, weight='bold')
    ax.set_xlabel("")
    ax.set_ylabel("Tendencia de consumo por mes")

    ax.grid(True, axis='y', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')
    ax.grid(True, axis='x', alpha=0.3, linestyle='-', linewidth=0.5, color='gray')

    # Fix rotation using plt.setp to avoid warnings
    plt.setp(ax.get_xticklabels(), rotation=45, ha='right')

    # Remove all spines at once
    for spine in ax.spines.values():
        spine.set_visible(False)

    # Y-axis ticks
    y_min, y_max = ax.get_ylim()
    y_min = math.floor(y_min)
    y_max = math.ceil(y_max)
    step = max(1, 2)  # Fixed step of 2
    ax.set_yticks(range(y_min, int(y_max) + 1, step))
    ax.set_ylim(bottom=0)

    fig.tight_layout()

    # Return the figure object
    return grouped, fig



