# Hospital Pest Control Report Generator 🏥

Automated system for generating comprehensive pest control reports for hospital locations (Medellín and Rionegro). Available as both a **Streamlit web application** and **command-line script**.

## 🚀 Features

### Web Application (Streamlit)
- **Interactive UI**: User-friendly web interface
- **Real-time Data**: Cached API data loading with refresh capability- **Flexible Reports**: Generate for individual locations or both
- **Month Filtering**: Exclude specific months from analysis
- **Progress Tracking**: Visual indicators during report generation
- **Instant Download**: Direct browser downloads of Word documents
- **Error Handling**: Comprehensive error reporting

### Command Line Interface
- **Automated Processing**: Script-based execution
- **Batch Processing**: Generate multiple reports
- **Scheduled Execution**: Integrate with cron jobs

## 🛠️ Quick Start

### 1. Installation
```bash
# Run the setup script
./setup.sh

# Or manually install dependencies

pip install -r requirements.txt
```

### 2. Configuration
Create a `.env` file with your API endpoints:
```env
prev_API=https://your-api-endpoint/preventivos
roe_API=https://your-api-endpoint/roedores  
lam_API=https://your-api-endpoint/lamparas
```

### 3. Usage

**Web Application (Recommended):**
```bash
streamlit run app.py
# Then open http://localhost:8501
```

**Command Line:**
```bash
python main.py
```

## 📁 Project Structure

```
ReporteSanVicente-Serviplagas/
├── app.py                     # Streamlit web application
├── main.py                    # Command-line script
├── report_generator.py        # Core report generation
├── config.py                  # Configuration settings
├── Plantilla.docx            # Word template
├── .env                      # API endpoints (create this)
│
├── data_preprocessing/        # Data processing modules
├── data_visualization/        # Chart generation modules  
└── Engine/                   # Word document generation
```

## 🎯 Data Processing

### Supported Data Types
- **Preventivos**: Preventive treatments, pest evidence, pesticide usage
- **Roedores**: Rodent stations, bait consumption, elimination trends
- **Lámparas**: Lamp traps, species capture, status monitoring

### Processing Features
- Multi-source API integration
- Location-based filtering (Medellín/Rionegro)
- Date management and month exclusion
- Data validation and error handling
- UTF-8 encoding support for Spanish characters

## 📊 Visualizations

### Generated Charts
- **Preventive Treatments**: Area plots, time series, trend analysis
- **Rodent Control**: Station status, elimination trends
- **Lamp Traps**: Status monitoring, species capture analysis

### Chart Features
- High-resolution output (300 DPI)
- Professional styling with consistent colors
- Spanish language labels
- Automatic number formatting

## � Report Generation

### Word Document Features
- Professional layout with embedded charts and tables
- Native Word tables with proper formatting
- Location-specific sections (med_*, rio_*)
- Automatic template variable replacement
- In-memory generation for web downloads

### Template Requirements
Ensure `Plantilla.docx` contains placeholders:
- `{{med_preventivos_1_plot}}`, `{{med_preventivos_1_tabla}}`
- `{{med_roedores_1_plot}}`, `{{med_roedores_1_tabla}}`
- `{{med_lamparas_1_plot}}`, `{{med_lamparas_1_tabla}}`
- Corresponding Rionegro placeholders (`rio_*`)

## 🔧 Dependencies

- `pandas==2.3.2` - Data manipulation
- `matplotlib==3.10.6` - Visualizations
- `seaborn==0.13.2` - Statistical plots
- `streamlit==1.28.0` - Web application
- `docxtpl==0.20.1` - Word templates
- `python-docx==1.2.0` - Document manipulation
- `requests==2.31.0` - API communication
- `python-dotenv==1.1.1` - Environment variables

## � Troubleshooting

### Common Issues

**API Connection Failed**
- Verify `.env` file contains correct URLs
- Check internet connection
- Confirm API server availability

**Template Errors**
- Ensure `Plantilla.docx` exists in project root
- Verify all required placeholders are present
- Check file permissions

**Memory Issues**
- Process one location at a time for large datasets
- Close unnecessary applications
- Consider increasing system memory

### Error Messages

**"Error loading API data"**
- Check API endpoints and network connectivity
- Verify API response format

**"Error generating report"**
- Validate Word template integrity
- Review error details in application logs

## � Development

### Adding New Visualizations
1. Create function in appropriate `data_visualization/` module
2. Add function call to `report_generator.py`
3. Update Word template with new placeholders

### Modifying Data Processing
1. Update functions in `data_preprocessing/` modules
2. Test with both web and CLI interfaces
3. Verify output compatibility

## 📄 License

Proprietary software for Serviplagas hospital pest control reporting.

---

**Sistema de Reportes de Control de Plagas** 📊🏥

*Generación automatizada de informes profesionales para servicios de control de plagas en hospitales*