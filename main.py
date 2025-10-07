"""
Script original de generación de reportes - ahora usa el módulo refactorizado report_generator
Este script mantiene compatibilidad hacia atrás mientras aprovecha la nueva estructura modular
"""

from report_generator import generate_report_for_locations


def main():
    """
    Función principal para generar reportes para ambas ubicaciones
    Mantiene el mismo comportamiento que el script original
    """
    try:
        print("🚀 Iniciando generación de reportes...")
        print("📍 Procesando ambas ubicaciones: Medellín y Rionegro")
        
        # Generar reporte para ambas ubicaciones (mismo comportamiento original)
        from datetime import date, timedelta
        
        # Usar rango de fechas por defecto (último año)
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        filename = generate_report_for_locations(
            locations=["Medellín", "Rionegro"],
            start_date=start_date,
            end_date=end_date,
            template_path='Plantilla.docx',
            return_buffer=False  # Guardar a archivo en lugar de retornar buffer
        )
        
        print(f"✅ ¡Generación de reporte completada exitosamente!")
        print(f"📄 Archivo de salida: {filename}")
        
    except Exception as e:
        print(f"❌ Error generando reporte: {str(e)}")
        raise


if __name__ == "__main__":
    main()