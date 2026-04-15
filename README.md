# 🎬 AI Shorts Factory

Generate 5 faceless YouTube Shorts scripts — with hooks, CTAs, thumbnail prompts & viral scores — from any topic.

---

## 🚀 Quick Start

### 1. Clone / Navigate
```bash
cd prototype-shorts
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set your OpenAI API key
```bash
export OPENAI_API_KEY=sk-proj-your-key-here
```

### 4. Run locally
```bash
streamlit run app.py
```

App opens at `http://localhost:8501`

---

## 📁 Project Structure
```
prototype-shorts/
├── app.py                  ← Main Streamlit app
├── requirements.txt         ← Dependencies
├── README.md               ← This file
└── .streamlit/
    └── config.toml         ← Dark theme + wide layout config
```

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| **5 Shorts per topic** | Unique angles, hooks, and CTAs |
| **Viral Score** | Hook strength × CTA quality (0-100) |
| **Hook Strength** | Heuristic based on opener type, numbers, intrigue |
| **Watch Time Estimate** | Based on 150 WPM speaking pace, capped at 60s |
| **Thumbnail Prompts** | AI-generated image prompts for each Short |
| **Export** | Download all 5 as a formatted .txt file |

---

## 💰 Monetization Plan

### Tiered Pricing
| Tier | Price | Shorts / day | Features |
|------|-------|--------------|----------|
| **Free** | $0 | 5 | Full script generation + export |
| **Pro** | $19/mo | Unlimited | Priority generation, saved topics, bulk export, thumbnail gen |

### Revenue Model
- **SaaS subscription** — simple, predictable MRR
- **Upsell path** — free users hit limit → upgrade prompt
- **Add-ons (future)** — AI thumbnail generation ($0.10/image), voice-over narration ($5/short)

### Launch Stack
- **Frontend**: Streamlit Cloud (free tier → upgrade to paid Sharing)
- **Auth**: Streamlit authentication or external (LemonSqueezy, Gumroad)
- **Payments**: LemonSqueezy for subscriptions ($19/mo Pro)
- **API costs**: ~$0.002/short (GPT-4o-mini) → healthy 900%+ margin at scale

### Go-to-Market
1. Post demo on X/Twitter with working Shorts examples
2. Submit to ProductHunt launch when Pro tier live
3. Collaborate with faceless Shorts creators on YouTube
4. Reddit: r/shorts, r/YouTubeTutorials, r/passive_income

---

## 🔧 Tech Stack

- **Streamlit** — frontend + UI
- **OpenAI GPT-4o-mini** — script generation
- **Streamlit Cloud** — deployment (free tier available)

---

## 📝 Notes

- Free tier = 5 shorts/day per session (no auth = browser-based limit)
- Pro tier requires session/auth tracking
- Thumbnail prompts are designed for Midjourney / Ideogram / DALL-E
- All scripts are designed for **faceless** content (no face required)
