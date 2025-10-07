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
        filename = generate_report_for_locations(
            locations=["Medellín", "Rionegro"],
            mes_excluir='Oct 2025',
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