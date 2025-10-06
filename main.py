import os
import pandas as pd
from dotenv import load_dotenv
from data_preprocessing.pipeline import leer_data, procesar_preventivos, procesar_lamparas, procesar_roedores

#viuals
from data_visualization.preventivos import generate_order_area_plot, generate_plagas_timeseries_facet, generate_total_plagas_trend_plot
from data_visualization.roedores import generate_roedores_station_status_plot, plot_tendencia_eliminacion_mensual
from data_visualization.lamparas import plot_estado_lamparas_por_mes, plot_estado_lamparas_con_leyenda, plot_capturas_especies_por_mes, plot_tendencia_total_capturas

# Report
from Engine.engine import InformeHospitalGenerator   

load_dotenv()

# Cargar datos desde las APIs
prev =  leer_data(os.getenv("prev_API"))
roed =  leer_data(os.getenv("roe_API"))
lamp =  leer_data(os.getenv("lam_API"))



# Procesar datos Medellín
prev_med , df_prev_med_full = procesar_preventivos(prev[prev['Sede'] == 'Medellín'])
roed_med , df_roed_med_full = procesar_roedores(roed[roed['Sede'] == 'Medellín'])
lamp_med , df_lamp_med_full = procesar_lamparas(lamp[lamp['Sede'] == 'Medellín'])

# Procesar datos Rionegro
prev_rionegro , df_prev_rionegro_full = procesar_preventivos(prev[prev['Sede'] == 'Rionegro'])
roed_rionegro , df_roed_rionegro_full = procesar_roedores(roed[roed['Sede'] == 'Rionegro'])
lamp_rionegro , df_lamp_rionegro_full = procesar_lamparas(lamp[lamp['Sede'] == 'Rionegro'])


mes_excluir = 'Oct 2025'

df_prev_med_full = df_prev_med_full[df_prev_med_full['Mes'] != mes_excluir]
df_roed_med_full = df_roed_med_full[df_roed_med_full['Mes'] != mes_excluir]
df_lamp_med_full = df_lamp_med_full[df_lamp_med_full['Mes'] != mes_excluir] 
df_prev_rionegro_full = df_prev_rionegro_full[df_prev_rionegro_full['Mes'] != mes_excluir]
df_roed_rionegro_full = df_roed_rionegro_full[df_roed_rionegro_full['Mes'] != mes_excluir]
df_lamp_rionegro_full = df_lamp_rionegro_full[df_lamp_rionegro_full['Mes'] != mes_excluir]



# Example usage
if __name__ == "__main__":

    # Inicializar generador con plantilla de prueba
    informe = InformeHospitalGenerator(
        template_path='Plantilla.docx',
    )


    # Medellín
    # Preventivos
    informe.agregar_resultado_completo(generate_order_area_plot, 
                                       df_prev_med_full,
                                        'med_preventivos_1_plot',
                                        'med_preventivos_1_tabla',
                                        )
    informe.agregar_resultado_completo(generate_plagas_timeseries_facet, 
                                    df_prev_med_full,
                                    'med_preventivos_2_plot',
                                    'med_preventivos_2_tabla')
    informe.agregar_resultado_completo(generate_total_plagas_trend_plot, 
                                    df_prev_med_full,
                                    'med_preventivos_3_plot',
                                    'med_preventivos_3_tabla')
    
    # Roedores
    informe.agregar_resultado_completo(generate_roedores_station_status_plot, 
                                    df_roed_med_full,
                                    'med_roedores_1_plot',
                                    'med_roedores_1_tabla')
    informe.agregar_resultado_completo(plot_tendencia_eliminacion_mensual,
                                    df_roed_med_full,
                                    'med_roedores_2_plot',
                                    'med_roedores_2_tabla')

    # Lámparas
    informe.agregar_resultado_completo(plot_estado_lamparas_por_mes,
                                    df_lamp_med_full,
                                    'med_lamparas_1_plot',
                                    'med_lamparas_1_tabla')
    informe.agregar_resultado_completo(plot_estado_lamparas_con_leyenda,
                                    df_lamp_med_full,
                                    'med_lamparas_2_plot',
                                    'med_lamparas_2_tabla')
    informe.agregar_resultado_completo(plot_capturas_especies_por_mes,
                                    df_lamp_med_full,
                                    'med_lamparas_3_plot',
                                    'med_lamparas_3_tabla')
    informe.agregar_resultado_completo(plot_tendencia_total_capturas,
                                    df_lamp_med_full,
                                    'med_lamparas_4_plot',
                                    'med_lamparas_4_tabla')
    


    # Rionegro
    # Preventivos
    informe.agregar_resultado_completo(generate_order_area_plot, 
                                       df_prev_rionegro_full,
                                        'rio_preventivos_1_plot',
                                        'rio_preventivos_1_tabla',
                                        )
    informe.agregar_resultado_completo(generate_plagas_timeseries_facet, 
                                    df_prev_rionegro_full,
                                    'rio_preventivos_2_plot',
                                    'rio_preventivos_2_tabla')
    informe.agregar_resultado_completo(generate_total_plagas_trend_plot, 
                                    df_prev_rionegro_full,
                                    'rio_preventivos_3_plot',
                                    'rio_preventivos_3_tabla')
    
    # Roedores
    informe.agregar_resultado_completo(generate_roedores_station_status_plot, 
                                    df_roed_rionegro_full,
                                    'rio_roedores_1_plot',
                                    'rio_roedores_1_tabla')
    informe.agregar_resultado_completo(plot_tendencia_eliminacion_mensual,
                                    df_roed_rionegro_full,
                                    'rio_roedores_2_plot',
                                    'rio_roedores_2_tabla')

    # Lámparas
    informe.agregar_resultado_completo(plot_estado_lamparas_por_mes,
                                    df_lamp_rionegro_full,
                                    'rio_lamparas_1_plot',
                                    'rio_lamparas_1_tabla')
    informe.agregar_resultado_completo(plot_estado_lamparas_con_leyenda,
                                    df_lamp_rionegro_full,
                                    'rio_lamparas_2_plot',
                                    'rio_lamparas_2_tabla')
    informe.agregar_resultado_completo(plot_capturas_especies_por_mes,
                                    df_lamp_rionegro_full,
                                    'rio_lamparas_3_plot',
                                    'rio_lamparas_3_tabla')
    informe.agregar_resultado_completo(plot_tendencia_total_capturas,
                                    df_lamp_rionegro_full,
                                    'rio_lamparas_4_plot',
                                    'rio_lamparas_4_tabla')



    # Generar informe final
    informe.generar_informe('INFORME_OCTUBRE_2024_RIONEGRO.docx')