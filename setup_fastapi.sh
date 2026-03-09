#!/bin/bash
# Quick start script for FastAPI + Django + AI integration

set -e

echo "🚀 FastAPI + Django + AI Integration Setup"
echo "==========================================="
echo ""

# Check Python version
echo "✓ Checking Python version..."
python_version=$(python --version)
echo "  $python_version"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  .env file not found!"
    echo "Creating .env from .env.example..."
    cp .env.example .env
    echo "✓ Created .env"
    echo ""
    echo "📝 Please edit .env and add your OpenAI API key:"
    echo "   OPENAI_API_KEY=sk_your_actual_key_here"
    echo ""
    echo "   Get a free key from: https://platform.openai.com/api-keys"
else
    echo "✓ .env file exists"
fi

# Load environment
echo ""
echo "Loading environment..."
set -a
source .env
set +a

# Check if activated in venv
if [ -z "$VIRTUAL_ENV" ]; then
    echo "⚠️  Virtual environment not activated!"
    echo "Please run: source .venv/bin/activate"
    exit 1
fi

echo "✓ Virtual environment activated"

# Install dependencies
echo ""
echo "Installing dependencies..."
pip install -r requirements.text --quiet
echo "✓ Dependencies installed"

# Create services directory if needed
mkdir -p services

echo ""
echo "✅ Setup complete!"
echo ""
echo "📚 Next steps:"
echo ""
echo "1️⃣  Start Django (Terminal 1):"
echo "   python manage.py runserver"
echo ""
echo "2️⃣  Start FastAPI (Terminal 2):"
echo "   python fastapi_app.py"
echo ""
echo "3️⃣  View API docs:"
echo "   http://127.0.0.1:8001/docs"
echo ""
echo "4️⃣  Test in Django:"
echo "   from services import get_ai_client"
echo "   with get_ai_client() as client:"
echo "       desc = client.generate_description_local('Jeans', 'Bottoms', 49.99)"
echo ""
echo "📖 Full guide: README_FASTAPI_SETUP.md"
