#!/bin/bash

# Setup script for the Streamlit Hospital Report Generator

echo "🏥 Setting up Hospital Pest Control Report Generator..."

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3 first."
    exit 1
fi

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed. Please install pip3 first."
    exit 1
fi

echo "📦 Installing Python dependencies..."

# Install dependencies
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully!"
else
    echo "❌ Failed to install dependencies. Please check the error messages above."
    exit 1
fi

echo ""
echo "🚀 Setup complete! You can now run the application using:"
echo ""
echo "For the Streamlit web app:"
echo "    streamlit run app.py"
echo ""
echo "For the original script:"
echo "    python3 main.py"
echo ""
echo "📝 Make sure you have:"
echo "   1. A .env file with your API endpoints"
echo "   2. The Plantilla.docx template file"
echo "   3. All data processing modules in the correct directories"
echo ""
echo "Happy reporting! 📊"