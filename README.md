# 🤖 Robotic English Assistant – Local AI Robot (Phi-3 Mini + Python)

This project implements an **interactive educational robot powered by local AI**, using:

* **Speech recognition** (SpeechRecognition + Google Speech API)
* **Local language generation** via **Phi-3 Mini** running on **Ollama**
* **Text-to-speech synthesis** in English (pyttsx3)
* **Graphical mouth animation** using Pygame
* **A complete performance metrics system**

Everything runs on **conventional hardware**, without GPUs, and without relying on cloud-based LLM services.

---

## 📌 Main Features

* 🎤 **English speech recognition** with automatic noise adjustment

* 🧠 **Local LLM processing** using Phi-3 Mini

* 🔊 **English speech synthesis** with automatic voice selection

* 😀 **Mouth animation** synchronized with speech

* 📊 **Performance metrics**, including:

  * Average speech recognition time
  * Average LLM processing time
  * Speech synthesis time
  * Number of interactions
  * Recognition and LLM failure counts

* 📑 Automatic generation of `robot_metrics.json`

* 🧩 **Voice commands**:

  * **"report"** → shows a full performance report
  * **"voices"** → lists available TTS voices
  * **"exit"** → closes the robot

---

## 🛠️ Requirements

### **Python 3.10+**

Install dependencies:

```bash
pip install pygame pyttsx3 SpeechRecognition requests pyaudio
```

If PyAudio fails on Windows:

```bash
pip install pipwin
pipwin install pyaudio
```

---

## 🧠 Installing Ollama + Phi-3 Mini

1. Download Ollama:
   [https://ollama.com/download](https://ollama.com/download)

2. Start the server:

```bash
ollama serve
```

3. Pull the model:

```bash
ollama pull phi3:mini
```

---

## 🎨 Required Images

Place the following files in the same folder as your script:

* `robo_fechado.png`
* `robo_aberto.png`

---

## ▶️ Running the Robot

```bash
python robot.py
```

You should see:

```
🤖 ENGLISH LLM ROBOT WITH PERFORMANCE METRICS
Make sure Ollama is running...
Say 'report' to display statistics
Say 'voices' to list TTS voices
```

---

## 🎙️ Voice Commands

| Command                     | Action                            |
| --------------------------- | --------------------------------- |
| **Any question in English** | The robot answers in English      |
| **report**                  | Shows performance statistics      |
| **voices**                  | Lists available system TTS voices |
| **exit**                    | Closes the robot                  |

---

## 📊 Metrics File

The system automatically generates:

```
robot_metrics.json
```

Example:

```json
{
  "total_interactions": 12,
  "total_llm_time": 17.52,
  "total_recognition_time": 9.33,
  "total_speech_time": 14.22,
  "recognition_errors": 2,
  "llm_errors": 1
}
```

---

## 🧩 System Architecture

```
Microphone → Speech Recognition → Text
                    ↓
             Ollama (Phi-3 Mini)
                    ↓
                Response
                    ↓
           pyttsx3 (English voice)
                    ↓
        Mouth Animation (Pygame)
```

---

## 🎓 Educational Purpose

This project demonstrates that it is possible to:

* Use **local AI** in schools
* Run LLMs on low-cost hardware
* Enable real-time voice interaction
* Avoid dependency on cloud services
* Support robotics, STEM, and computer science education

---

## 📄 License

You may freely modify, adapt, and use this project for educational and academic purposes.

