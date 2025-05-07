import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from agents.preference_agent import PreferenceAgent
from agents.content_agent import ContentAgent
from agents.recommendation_agent import RecommendationAgent
from agents.coordinator import AgentCoordinator

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')

# Initialize agents
preference_agent = PreferenceAgent()
content_agent = ContentAgent()
recommendation_agent = RecommendationAgent()

# Create coordinator to manage agents
coordinator = AgentCoordinator(
    preference_agent=preference_agent,
    content_agent=content_agent,
    recommendation_agent=recommendation_agent
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hai! Saya adalah bot rekomendasi konten belajar untuk mahasiswa.\n\n"
        "Saya dapat membantu kamu mendapatkan rekomendasi bahan belajar berdasarkan minat dan waktu belajar yang kamu miliki.\n\n"
        "Gunakan /profile untuk mengatur preferensi belajarmu.\n"
        "Gunakan /recommend untuk mendapatkan rekomendasi konten belajar."
    )

async def profile_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Mari atur preferensi belajarmu. Tolong jawab beberapa pertanyaan berikut:\n\n"
        "1. Apa bidang studi atau jurusan yang kamu ambil?\n"
        "2. Topik apa yang sedang kamu pelajari?\n"
        "3. Berapa jam yang kamu miliki untuk belajar setiap harinya?\n\n"
        "Format jawabanmu: /setprofile jurusan;topik;jam_belajar\n"
        "Contoh: /setprofile Teknik Informatika;Machine Learning;2"
    )

async def set_profile(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_id = update.effective_user.id
        text = update.message.text.replace('/setprofile', '').strip()
        field, topic, hours = text.split(';')
        
        # Use preference agent to store user preferences
        await coordinator.set_user_preferences(user_id, {
            'field': field.strip(),
            'topic': topic.strip(),
            'hours': float(hours.strip())
        })
        
        await update.message.reply_text(
            f"Profil belajarmu telah diatur:\n"
            f"📚 Bidang: {field}\n"
            f"🔍 Topik: {topic}\n"
            f"⏱️ Waktu belajar: {hours} jam per hari\n\n"
            f"Gunakan /recommend untuk mendapatkan rekomendasi konten belajar."
        )
    except Exception as e:
        await update.message.reply_text(
            "Format tidak valid. Gunakan format: /setprofile jurusan;topik;jam_belajar\n"
            "Contoh: /setprofile Teknik Informatika;Machine Learning;2"
        )

async def recommend(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    # Check if user has set preferences
    if not await coordinator.has_preferences(user_id):
        await update.message.reply_text(
            "Kamu belum mengatur preferensi belajar. Gunakan /profile terlebih dahulu."
        )
        return
    
    await update.message.reply_text("🔍 Sedang mencari konten belajar yang sesuai untukmu...")
    
    # Get recommendations from coordinator
    recommendations = await coordinator.get_recommendations(user_id)
    
    if not recommendations:
        await update.message.reply_text(
            "Maaf, saya tidak dapat menemukan rekomendasi yang sesuai saat ini. Coba lagi nanti."
        )
    else:
        response = "🎓 Berikut rekomendasi konten belajar untukmu:\n\n"
        
        for i, rec in enumerate(recommendations, 1):
            response += f"{i}. {rec['title']}\n"
            response += f"   🔗 {rec['link']}\n"
            response += f"   ⏱️ Durasi: {rec['duration']}\n"
            response += f"   📝 {rec['description'][:100]}...\n\n"
        
        response += "Semoga membantu belajarmu! 📚"
        
        await update.message.reply_text(response)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Berikut perintah yang bisa kamu gunakan:\n\n"
        "/start - Memulai bot\n"
        "/profile - Mengatur preferensi belajar\n"
        "/setprofile - Menyimpan preferensi (format: jurusan;topik;jam_belajar)\n"
        "/recommend - Mendapatkan rekomendasi konten belajar\n"
        "/help - Menampilkan bantuan"
    )

def main():
    # Create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("profile", profile_command))
    application.add_handler(CommandHandler("setprofile", set_profile))
    application.add_handler(CommandHandler("recommend", recommend))

    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()