import pygame
import threading
import pyttsx3
import speech_recognition as sr
import time
import requests
import json
from datetime import datetime

pygame.init()

WIDTH, HEIGHT = 500, 500
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Talking Robot")

closed_mouth = pygame.transform.smoothscale(pygame.image.load("robo_fechado.png"), (WIDTH, HEIGHT))
open_mouth = pygame.transform.smoothscale(pygame.image.load("robo_aberto.png"), (WIDTH, HEIGHT))

speaking = False

# === METRICS ===================================================
metrics = {
    "total_interactions": 0,
    "total_llm_time": 0,
    "total_recognition_time": 0,
    "total_speech_time": 0,
    "recognition_errors": 0,
    "llm_errors": 0
}

def save_metrics():
    """Save metrics to JSON file"""
    with open("robot_metrics.json", "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4, ensure_ascii=False)
    print("\n📊 Metrics saved to 'robot_metrics.json'")

def show_report():
    """Display performance report"""
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE REPORT")
    print("=" * 60)
    print(f"Total interactions: {metrics['total_interactions']}")
    
    if metrics['total_interactions'] > 0:
        print(f"\n⏱️  AVERAGE TIMES:")
        print(f"   Speech recognition: {metrics['total_recognition_time']/metrics['total_interactions']:.2f}s")
        print(f"   LLM processing: {metrics['total_llm_time']/metrics['total_interactions']:.2f}s")
        print(f"   Speech synthesis: {metrics['total_speech_time']/metrics['total_interactions']:.2f}s")
        print(f"   Total time per interaction: {(metrics['total_recognition_time']+metrics['total_llm_time']+metrics['total_speech_time'])/metrics['total_interactions']:.2f}s")
    
    print(f"\n❌ ERRORS:")
    print(f"   Recognition failures: {metrics['recognition_errors']}")
    print(f"   LLM failures: {metrics['llm_errors']}")
    print("=" * 60 + "\n")

# === LLM QUERY (Ollama) ========================================
def query_llm(prompt):
    start = time.time()
    
    try:
        url = "http://localhost:11434/api/generate"
        payload = {
            "model": "phi3:mini",
            "prompt": f"You are a helpful assistant. You must respond ONLY in English language. Answer briefly and directly. User question: {prompt}",
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": -1
            }
        }
        
        print("📡 Sending request to Ollama...")
        response = requests.post(url, json=payload, timeout=30)
        
        elapsed = time.time() - start
        
        if response.status_code == 200:
            data = response.json()
            reply = data.get("response", "").strip()
            
            if reply:
                metrics['total_llm_time'] += elapsed
                print(f"⏱️  LLM response time: {elapsed:.2f}s")
                print(f"📝 Output tokens: ~{len(reply.split())} words")
                return reply
            else:
                metrics['llm_errors'] += 1
                return "The AI returned an empty response."
        else:
            metrics['llm_errors'] += 1
            return f"Error {response.status_code} while querying the AI."
            
    except requests.exceptions.ConnectionError:
        metrics['llm_errors'] += 1
        print("❌ Error: Could not connect to Ollama.")
        return "Failed to connect to the Ollama server."
    except requests.exceptions.Timeout:
        metrics['llm_errors'] += 1
        print("❌ Error: Request timed out.")
        return "The AI took too long to respond."
    except Exception as e:
        metrics['llm_errors'] += 1
        print(f"❌ Error querying AI: {type(e).__name__} - {e}")
        return "An error occurred while accessing the AI."

# === SPEAK ======================================================
def speak(text):
    global speaking
    start = time.time()
    
    speaking = True
    engine = pyttsx3.init()

    voices = engine.getProperty('voices')
    english_voice_found = False
    
    # Try to find an English voice (more comprehensive search)
    for v in voices:
        v_name_lower = v.name.lower()
        v_id_lower = v.id.lower()
        
        if any(keyword in v_name_lower or keyword in v_id_lower 
               for keyword in ["english", "en-", "en_", "us", "uk", "zira", "david"]):
            engine.setProperty('voice', v.id)
            english_voice_found = True
            print(f"✅ Using English voice: {v.name}")
            break
    
    if not english_voice_found:
        print("⚠️  No English voice detected, using default voice")
        if voices:
            engine.setProperty('voice', voices[0].id)
            print(f"   Default voice: {voices[0].name}")

    engine.setProperty('rate', 155)
    engine.say(text)
    engine.runAndWait()
    engine.stop()
    speaking = False
    
    elapsed = time.time() - start
    metrics['total_speech_time'] += elapsed
    print(f"🔊 Speech synthesis time: {elapsed:.2f}s")

# === MOUTH ANIMATION ============================================
def animate_speech():
    flag = False
    clock = pygame.time.Clock()
    while speaking:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
        
        flag = not flag
        screen.blit(open_mouth if flag else closed_mouth, (0, 0))
        pygame.display.flip()
        clock.tick(6)
    
    screen.blit(closed_mouth, (0, 0))
    pygame.display.flip()

# === SPEECH RECOGNITION =========================================
def listen():
    start = time.time()
    
    r = sr.Recognizer()
    r.dynamic_energy_threshold = True
    r.pause_threshold = 0.8
    
    with sr.Microphone() as source:
        print("🎤 Robot listening... speak now.")
        r.adjust_for_ambient_noise(source, duration=0.5)
        
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=10)
        except sr.WaitTimeoutError:
            return "timeout"

    try:
        text = r.recognize_google(audio, language="en-US")
        elapsed = time.time() - start
        metrics['total_recognition_time'] += elapsed
        
        print(f"✅ You said: {text}")
        print(f"⏱️  Recognition time: {elapsed:.2f}s")
        return text

    except sr.UnknownValueError:
        metrics['recognition_errors'] += 1
        return "i did not understand"
    except sr.RequestError:
        metrics['recognition_errors'] += 1
        return "connection error"

# === VOICE DEBUG (Optional - run at startup) ===================
def show_available_voices():
    """Display all available TTS voices on the system"""
    print("\n" + "=" * 60)
    print("🔊 AVAILABLE TEXT-TO-SPEECH VOICES")
    print("=" * 60)
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for i, v in enumerate(voices, 1):
        print(f"{i}. {v.name}")
        print(f"   ID: {v.id}")
        print(f"   Languages: {v.languages}")
        print()
    engine.stop()
    print("=" * 60 + "\n")

# Initial screen
screen.blit(closed_mouth, (0, 0))
pygame.display.flip()

print("=" * 60)
print("🤖 ENGLISH LLM ROBOT WITH PERFORMANCE METRICS")
print("=" * 60)
print("💡 Make sure Ollama is running: ollama serve")
print("📊 Metrics will be collected automatically")
print("🔤 Say 'report' to display statistics")
print("🔊 Say 'voices' to see available TTS voices")
print("=" * 60 + "\n")

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
    
    user_text = listen()
    
    if user_text == "timeout":
        continue

    if user_text.lower() == "exit":
        reply = "Goodbye!"
        t1 = threading.Thread(target=speak, args=(reply,))
        t1.start()
        animate_speech()
        t1.join()
        running = False
        break
    
    if user_text.lower() == "report":
        show_report()
        continue
    
    if user_text.lower() == "voices":
        show_available_voices()
        continue

    metrics['total_interactions'] += 1
    
    print(f"\n🕐 Interaction #{metrics['total_interactions']} - {datetime.now().strftime('%H:%M:%S')}")
    print(f"📥 Input: {user_text}")
    print(f"🔤 Input words: {len(user_text.split())}")
    
    start_total = time.time()
    reply = query_llm(user_text)
    print(f"📤 Output: {reply}{'...' if len(reply) > 100 else ''}")

    t1 = threading.Thread(target=speak, args=(reply,))
    t1.start()
    animate_speech()
    t1.join()
    
    total_elapsed = time.time() - start_total
    print(f"⏱️  Total interaction time: {total_elapsed:.2f}s")
    print("-" * 60)

save_metrics()
show_report()

pygame.quit()
print("👋 Robot terminated")
