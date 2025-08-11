# 🤖 BenchHub LLM Integration

This project automates the generation of personalized development suggestion emails based on Microsoft Forms survey responses. It integrates a local **Mistral LLM**, **OneDrive file sync**, and **Outlook email automation** to create a seamless upskilling workflow.


It also serves as an automated workflow for proactively supporting bench employees from Testing Discipline at Endava, by providing tailored development recommendations based on individual survey inputs. Designed as part of an internal innovation challenge, the project encourages continuous learning and engagement during periods without client allocation.

---

## 🚀 Quickstart Guide

### 1. Clone the Repository

```bash
git clone https://github.com/YouSteen/BenchHub_LLM_integration.git
cd BenchHub_LLM_integration
```

### 2. Run Initial Setup

Navigate to the `scripts/` folder and run:

```bash
scripts/setup.bat
```

This will:

- Install all required dependencies listed in `requirements.txt`
- Create necessary folders and configs

### 3. Start the Application

Run:

```bash
scripts/watch_and_build.bat
```

This will:

- Launch the console-based UI
- Let you choose between email sending, config options, or file preview

> ⚠️ **Email generation won't work out of the box!**
> You must first:

1. Download a quantized version of the **Mistral model** (GGUF format)
2. Install **C++ Build Tools** (required by `llama.cpp` backend)

---

## 🔄 Application Flow – Visual Guide

### 🔹 Step 1 – Microsoft Forms Survey

➡️ ![Step 1 – Survey](flow/survey.png)

Employees fill out a Microsoft Form with office location, learning goals, and upskilling preferences.

---

### 🔹 Step 2 – Excel File Synced via OneDrive

➡️ ![Step 2 – Excel](flow/excel.png)

Responses are saved in a `.xlsx` file and automatically synced locally via OneDrive. This file is parsed by the application.

---

### 🔹 Step 3 – Console UI Interaction

➡️ ![Step 3 – CLI UI](flow/ui.png)

A terminal-based interface allows:

- Running the email generator
- Configuring OneDrive paths and CC emails
- Previewing survey entries
- Exiting the app

---

### 🔹 Step 4 – LLM-Powered Email Generation

➡️ ![Step 4 – Email](flow/email.png)

The application:

- Extracts 3 key answers per user
- Passes them into a prompt
- Sends the prompt to the **Mistral LLM**
- Wraps the generated message into a personalized Outlook email

---

### 🔹 Step 5 – Delivery Log Tracking

➡️ ![Step 5 – Log](flow/sent_log.png)

Each email (sent or failed) is tracked in `sent_log.xlsx` with:

- Timestamp
- Status (Success / Error)
- Details for debugging if needed

---

## 📁 Project Structure

```
BenchHub_LLM_integration/
├── build/               # Build artifacts
├── flow/                # Visual documentation (screenshots)
│   ├── survey.png
│   ├── excel.png
│   ├── ui.png
│   ├── email.png
│   └── sent_log.png
├── scripts/             # .bat setup and launch scripts
├── src/                 # Source code
│   ├── menu/            # UI options (send, preview, config, exit), LLM handling and prompt logic
│   └── utils/           # File handling, Excel parsing, email logic
├── requirements.txt     # Python dependencies
├── watch_and_build.py   # Dev environment runner
└── README.md            # You're here :)
```

---

## 🧱 Requirements

- Python 3.10+
- Microsoft Outlook Desktop App
- Installed:
  - `llama-cpp-python`
  - `openpyxl`, `pandas`, `python-dotenv`, etc.

### 🛠 Additional Setup

- Download a Mistral model (e.g. [`mistral-7b-instruct.Q4_K_M.gguf`](https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF))
- Install [**C++ Build Tools**](https://visualstudio.microsoft.com/visual-cpp-build-tools/) (required by `llama.cpp` backend)
- Setup OneDrive sync on local machine

---

## 📬 Example Use Case

1. Team members complete survey
2. Manager runs the app and sends personalized development suggestions
3. Each interaction is tracked, logged, and automated — no manual follow-up needed

---

## 🙌 Contributors

- **Iustin-Mihai Stanciu** – Author, developer, integrator
- **Sincaru Nicola-Diana** – Author, developer, integrator
- **Vataselu Andrei** – Author, developer, integrator
- 🧪 Inspired by real-world upskilling flows at **Endava**

---
