import os
import telebot
from google import genai
from google.genai import types

# Masukkan Token Bot Telegram Anda dari BotFather
TELEGRAM_BOT_TOKEN = "MASUKKAN_TOKEN_TELEGRAM_DI_SINI"

# Masukkan API Key Gemini pribadi Anda (dari aistudio.google.com)
GEMINI_API_KEY = "MASUKKAN_API_KEY_GEMINI_DI_SINI"

# Inisialisasi bot dan klien Gemini
bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    try:
        # Kirim pesan konfirmasi sedang memproses
        sent_msg = bot.reply_to(message, "⏳ Sedang membaca resi dan mencari titik lokasi...")
        
        # Ambil file foto ukuran terbesar dari Telegram
        fileID = message.photo[-1].file_id
        file_info = bot.get_file(fileID)
        downloaded_file = bot.download_file(file_info.file_path)
        
        # Simpan sementara foto resi
        image_path = "resi_temp.jpg"
        with open(image_path, 'wb') as new_file:
            new_file.write(downloaded_file)
            
        # Buka file untuk dikirim ke Gemini
        with open(image_path, 'rb') as img:
            image_bytes = img.read()

        # Prompt instruksi untuk Gemini
        prompt = (
            "Analisis gambar resi pengiriman ini. Cari koordinat GPS (latitude, longitude) "
            "atau alamat lengkap tujuan pengiriman yang tertera pada gambar. "
            "Berikan HANYA format link Google Maps dengan format persis seperti ini: "
            "https://www.google.com/maps/search/?api=1&query=LAT,LONG "
            "Jika koordinat tidak ditemukan, berikan alamat teks lengkapnya."
        )

        # Panggil Gemini API (menggunakan model gemini-2.5-flash)
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[
                types.Part.from_bytes(data=image_bytes, mime_type='image/jpeg'),
                prompt
            ]
        )

        result_text = response.text.strip()
        
        # Kirim hasil ke Telegram
        bot.edit_message_text(
            chat_index := message.chat.id,
            message_id=sent_msg.message_id,
            text=f"📍 **Hasil Deteksi Lokasi:**\n\n{result_text}",
            parse_mode="Markdown"
        )
        
        # Hapus file foto sementara
        if os.path.exists(image_path):
            os.remove(image_path)
            
    except Exception as e:
        bot.reply_to(message, f"❌ Terjadi kesalahan: {str(e)}")

print("Bot Telegram aktif dan siap menerima foto resi...")
bot.infinity_polling()