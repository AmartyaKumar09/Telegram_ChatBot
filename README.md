# Telegram_ChatBot
# 🌙 Mood-Aware Voice Note Bot

A personal Telegram bot that acts as a **"Digital Jar of Notes"**. It allows an Admin (you) to record voice notes or write texts tagged by specific moods. The Receiver (her) can then request a message based on how she is feeling, receiving a random, unplayed note from the collection.

## ✨ Features

* **🎙 Voice & Text Support:** Upload voice notes or fallback to text poetry.
* **🎭 Mood Tagging:** Categorize messages into `Romantic`, `Sad`, or `Hope`.
* **🔄 Smart Rotation:** Ensures she never gets the same message twice until she has heard them all.
* **🔁 Auto-Reset:** Automatically reshuffles the "jar" when all messages in a mood have been played.
* **☁️ Cloud Database:** Uses PostgreSQL to ensure data is never lost, even when the bot restarts.
* **⌨️ Interactive Menu:** Easy-to-use button interface for the user.

## 🛠️ Tech Stack

* **Python 3.10+**
* **pyTelegramBotAPI** (Telebot)
* **PostgreSQL** (Database)
* **Railway** (Hosting Platform)

---

## 🚀 Local Setup (Running on your computer)

1. **Clone the repository**
   ```bash
   git clone [https://github.com/yourusername/your-repo-name.git](https://github.com/yourusername/your-repo-name.git)
   cd your-repo-name
