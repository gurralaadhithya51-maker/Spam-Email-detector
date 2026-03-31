# Spam & Malware Email Detector

A simplified web-based application built with Flask (backend) and Vanilla JavaScript (frontend). This project analyzes email content using basic heuristics to classify it as **spam, ham, or containing malware**. This is ideal for a straightforward college presentation showing how pattern matching works!

## Features

- **Text Analysis**: Paste raw email text for instant analysis
- **File Upload**: Upload `.eml`, `.txt`, or `.msg` files for analysis
- **Heuristic Spam Filter**: Detects spam based on common spam trigger keywords, excessive ALL CAPS, and overused exclamation/money symbols.
- **Malware Detection**: Simple keyword checking for dangerous extensions (like `.exe`, `.bat`) and terms (like `payload`, `trojan`, `ransomware`) within the text to flag malicious intent.
- **Standalone Simplicity**: Runs efficiently from a single Python file (`app.py`), without needing complex Machine Learning training or setting up a database.

## Tech Stack

- **Backend**: Python, Flask
- **Frontend**: HTML, CSS, JavaScript

## Installation & Running

1. Ensure the Python virtual environment is active and dependencies are installed.
2. The simplest way to run on Windows is to run `RunWebUI.bat` located in the main directory.
3. To safely stop the server, run `StopWebUI.bat`.

## Project Structure

```
spam-detector/
├── backend/
│   ├── app.py          # Simplified Flask API server & Heuristic Logic
│   └── uploads/        # Temporary storage for uploaded test files
├── frontend/
│   ├── index.html      # Main UI
│   ├── styles.css      # Custom Styling
│   └── app.js          # Logic to handle API requests and UI updates
└── requirements.txt    # Python dependencies
```

## API Endpoints

- `GET /` - Serve frontend UI
- `POST /api/analyze-text` - Analyze pasted text for spam and malware
- `POST /api/analyze-file` - Analyze uploaded email file for spam and malware

## College Project Note
This is a deliberately simplified college presentation project demonstrating how to build a fully localized web server capable of text parsing and heuristic matching logic. No external AI models or databases are needed.