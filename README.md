# 📰 DataHalo - AI-Powered Media Integrity Platform

<div align="center">

![DataHalo Logo](https://img.shields.io/badge/DataHalo-Media%20Integrity-00bfff?style=for-the-badge)
[![Live Demo](https://img.shields.io/badge/Live-Demo-success?style=for-the-badge)](https://datahalo.vercel.app)
[![License](https://img.shields.io/badge/License-MIT-blue?style=for-the-badge)](LICENSE)

**Rebuilding Trust in Media — One Article at a Time**

[Features](#-features) • [Tech Stack](#-tech-stack) • [Installation](#-installation) • [Usage](#-usage) • [API](#-api-endpoints) • [Contributing](#-contributing)

</div>

---

## 🌟 Overview

DataHalo is an **AI-powered media integrity platform** that analyzes journalist profiles, tracks
media narratives, and provides transparency insights. Built for citizens, researchers, journalists,
and academics who want to understand media patterns and make informed decisions.

### 🎯 Key Capabilities

- **📊 Journalist Profile Analysis** - Comprehensive transparency assessment using AI
- **🔍 Narrative Analyzer** - Track how media coverage evolves over time
- **📈 Pattern Recognition** - Identify coordinated messaging and manipulation indicators
- **🗞️ News Intelligence** - AI-powered news analysis with multiple perspectives
- **🔬 Research Tools** - Export data for academic research with proper citations

---

## ✨ Features

### 1. **Journalist Profile Analyzer**

- **Halo Score™** - Influence, transparency, and engagement fingerprint (0-100)
- **Work Pattern Analysis** - Coverage topics, writing tone, and consistency
- **Political Affiliation Detection** - Evidence-based bias identification
- **Digital Presence Tracking** - Social media reach and media affiliations
- **Career Highlights** - Awards, notable works, and controversies

### 2. **Narrative Analyzer** 🆕

- **Timeline Visualization** - See how stories develop over time
- **Manipulation Detection** - Identifies coordinated campaigns and propaganda
- **Sentiment Analysis** - Track tone shifts across coverage
- **Source Clustering** - Reveals which outlets push specific narratives
- **Export & Citation** - Academic-ready data with proper attribution

### 3. **News Intelligence Dashboard**

- **AI Perspectives** - Analyze news from 5 different viewpoints:
    - General Public
    - Finance Analyst
    - Government Exam Aspirant
    - Tech Student
    - Business Student
- **Smart Feed** - Personalized analysis based on perspective
- **Real-time Updates** - Fresh news fetched and analyzed continuously

### 4. **Journalists Gallery**

- **Browse Analyzed Profiles** - 50+ journalists with complete analysis
- **Search & Filter** - Find by name, topic, or Halo Score level
- **Quick Stats** - Articles analyzed, political affiliation, main topics

---

## 🛠️ Tech Stack

### Frontend

```
React + TypeScript
├── Vite - Lightning-fast build tool
├── TailwindCSS - Utility-first styling
├── Framer Motion - Smooth animations
├── Shadcn/ui - Beautiful component library
├── React Router - Client-side routing
└── Lucide Icons - Modern icon system
```

### Backend

```
Python FastAPI
├── FastAPI - High-performance async API
├── MongoDB - Document database
├── NVIDIA NIM - AI model inference
├── NewsAPI - News aggregation
├── SerpAPI - Web scraping
└── Python-dotenv - Environment management
```

### AI & Analysis

```
AI Pipeline
├── Llama 3.1 70B - Journalist analysis
├── Qwen 2.5 Coder 32B - News intelligence
├── NLP Processing - Sentiment & tone analysis
├── Pattern Recognition - Narrative detection
└── Smart Prompting - Context-aware AI
```

---

## 🚀 Installation

### Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- MongoDB Atlas account (or local MongoDB)
- API Keys (see [Configuration](#-configuration))

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/datahalo.git
cd datahalo
```

### 2. Frontend Setup

```bash
# Install dependencies
npm install

# Create environment file
cp .env.example .env

# Add your configuration
VITE_API_URL=http://localhost:8000
```

### 3. Backend Setup

```bash
cd Backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create environment file
cp .env.example .env
```

### 4. Configuration

Create `.env` in the Backend folder:

```env
# MongoDB
MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/datahalo

# API Keys
NVIDIA_API_KEY=nvapi-xxxxxxxxxxxxxxxxxxxxx
NEWS_API_KEY=xxxxxxxxxxxxxxxxxxxxx
SERP_API_KEY=xxxxxxxxxxxxxxxxxxxxx

# Optional
PORT=8000
```

### 5. Start Development Servers

**Terminal 1 - Backend:**

```bash
cd Backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**

```bash
npm run dev
```

Visit `http://localhost:5173` 🎉

---

## 📖 Usage

### Analyze a Journalist

1. **Navigate to Analyzer** section on landing page
2. **Enter journalist name** (e.g., "Ravish Kumar")
3. **Click "Analyze Profile"**
4. View comprehensive analysis:
    - Halo Score & Level
    - Political Affiliation
    - Work Patterns
    - Career Highlights
    - Controversies

### Track Media Narratives

1. **Go to Narrative Analyzer** (top-right button)
2. **Enter topic** (e.g., "Elections 2024")
3. **Select timeframe** (7 days to 6 months)
4. **Click "Analyze Narrative"**
5. Review:
    - Trend analysis
    - Manipulation indicators
    - Key narratives
    - Timeline visualization

### Export Research Data

1. **Complete narrative analysis**
2. **Click "Export Data"** button
3. Download JSON with:
    - Full analysis data
    - Academic citation
    - Timestamp metadata

```json
{
  "metadata": {
    "exportDate": "2024-01-15T10:30:00Z",
    "platform": "DataHalo Narrative Analyzer",
    "citation": "DataHalo. (2024). Narrative Analysis: Elections 2024..."
  },
  "analysis": { ... }
}
```

---

## 🔌 API Endpoints

### Journalist Analysis

```http
POST /analyze
Content-Type: application/json

{
  "name": "Journalist Name"
}
```

**Response:**

```json
{
  "status": "success",
  "journalist": "Journalist Name",
  "articlesAnalyzed": 45,
  "aiProfile": {
    "haloScore": {
      "score": 78,
      "level": "Established"
    },
    "politicalAffiliation": {
      "primary": "Independent/Centrist",
      "confidence": "High"
    }
  }
}
```

### Narrative Analysis

```http
POST /analyze-narrative
Content-Type: application/json

{
  "topic": "Elections 2024",
  "days": 30
}
```

### News Intelligence

```http
GET /news?category=technology
GET /refresh-news?category=business
POST /smart-feed?pov=finance analyst
```

### Journalists Gallery

```http
GET /journalists?limit=50
GET /journalist/{name}
```

[View Complete API Documentation →](docs/API.md)

---

## 🏗️ Project Structure

```
datahalo/
├── src/                          # Frontend source
│   ├── components/               # React components
│   │   ├── HeroSection.tsx
│   │   ├── JournalistAnalyzer.tsx
│   │   ├── News.tsx
│   │   └── SideNav.tsx
│   ├── pages/                    # Route pages
│   │   ├── Index.tsx
│   │   ├── JournalistProfile.tsx
│   │   ├── JournalistsGallery.tsx
│   │   └── NarrativeAnalyzer.tsx
│   └── lib/                      # Utilities
│
├── Backend/                      # Python backend
│   ├── main.py                   # FastAPI app
│   ├── news_fetcher.py           # News aggregation
│   ├── utils/
│   │   ├── ai_analysis.py        # Journalist AI analysis
│   │   ├── smart_analysis.py     # News intelligence
│   │   ├── serp_scraper.py       # Web scraping
│   │   └── scrapy_helpers.py     # Scraping utilities
│   └── requirements.txt
│
├── public/                       # Static assets
├── docs/                         # Documentation
└── README.md
```

---

## 🧪 Development

### Run Tests

```bash
# Frontend tests
npm run test

# Backend tests
cd Backend
pytest
```

### Linting

```bash
# Frontend
npm run lint

# Backend
cd Backend
pylint *.py utils/*.py
```

### Build for Production

```bash
# Frontend
npm run build

# Backend
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

---

## 🌐 Deployment

### Frontend (Vercel)

1. Connect repository to Vercel
2. Set environment variables:
   ```
   VITE_API_URL=https://your-backend.onrender.com
   ```
3. Deploy automatically on push

### Backend (Render)

1. Create new Web Service
2. Build command: `pip install -r requirements.txt`
3. Start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
4. Add environment variables

---

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. **Fork the repository**
2. **Create feature branch** (`git checkout -b feature/AmazingFeature`)
3. **Commit changes** (`git commit -m 'Add AmazingFeature'`)
4. **Push to branch** (`git push origin feature/AmazingFeature`)
5. **Open Pull Request**

### Contribution Guidelines

- Follow existing code style
- Add tests for new features
- Update documentation
- Keep commits atomic and meaningful

---

## 📊 Performance

- ⚡ **< 2s** page load time
- 🚀 **< 30s** journalist analysis
- 📈 **< 15s** narrative analysis
- 🔄 **Real-time** news updates
- 💾 **Smart caching** for repeat queries

---

## 🔐 Security

- 🔒 **Environment variables** for sensitive data
- 🛡️ **CORS protection** on API
- 🔑 **API key rotation** supported
- 🚫 **Rate limiting** on endpoints
- 📝 **Audit logs** for analysis requests

---

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 👥 Team

**DataHalo** is built and maintained by passionate developers committed to media transparency.

- Lead Developer: [Your Name](https://github.com/yourusername)
- Contributors: [View All](https://github.com/yourusername/datahalo/graphs/contributors)

---

## 🙏 Acknowledgments

- **NVIDIA NIM** - AI model infrastructure
- **NewsAPI** - News aggregation service
- **MongoDB** - Database platform
- **Vercel** - Frontend hosting
- **Render** - Backend hosting
- **Open Source Community** - Inspiration and tools

---

## 📞 Support

- 📧 Email: support@datahalo.com
- 💬 Discord: [Join Community](https://discord.gg/datahalo)
- 🐛 Issues: [GitHub Issues](https://github.com/yourusername/datahalo/issues)
- 📖 Docs: [Documentation](https://docs.datahalo.com)

---

## 🗺️ Roadmap

### Q1 2024

- [ ] Browser extension
- [ ] Mobile app (React Native)
- [ ] Advanced visualization dashboards
- [ ] Multi-language support

### Q2 2024

- [ ] Fact-checking integration
- [ ] Source credibility database
- [ ] API webhooks
- [ ] Custom analysis models

### Q3 2024

- [ ] White-label solution
- [ ] Enterprise features
- [ ] Advanced analytics
- [ ] Real-time alerts

---

## 📈 Stats

![GitHub stars](https://img.shields.io/github/stars/yourusername/datahalo?style=social)
![GitHub forks](https://img.shields.io/github/forks/yourusername/datahalo?style=social)
![GitHub issues](https://img.shields.io/github/issues/yourusername/datahalo)
![GitHub pull requests](https://img.shields.io/github/issues-pr/yourusername/datahalo)

---

<div align="center">

**Made with ❤️ for Media Transparency**

[Website](https://datahalo.vercel.app) • [Documentation](https://docs.datahalo.com) • [API](https://api.datahalo.com)

⭐ Star us on GitHub if DataHalo helps you!

</div>
