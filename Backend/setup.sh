#!/bin/bash

echo "🚀 Setting up DataHalo Backend..."

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Install spaCy model
echo "🧠 Installing spaCy English model..."
python -m spacy download en_core_web_sm

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Creating template..."
    cat > .env << EOF
# DataHalo Environment Variables
NVIDIA_API_KEY=your_nvidia_api_key_here
MONGO_URI=your_mongodb_connection_string
SERP_API_KEY=your_serp_api_key
NEWS_API_KEY=your_news_api_key
EOF
    echo "✅ Created .env template. Please add your API keys!"
else
    echo "✅ .env file exists"
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "To start the server:"
echo "  python -m uvicorn main:app --reload --port 8000"
echo ""
echo "Or use the run script:"
echo "  ./run_server.sh"
