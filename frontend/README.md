# MediConnect AI - Production Web Application Frontend

MediConnect AI Frontend is a state-of-the-art Single Page Web Application (SPA) communicating in real time with the **FastAPI Backend** (`http://localhost:8000/api/v1`).

---

## 🎨 Design System & Highlights

* **Futuristic Dark-Mode Interface**: Built with Glassmorphism cards (`backdrop-filter: blur`), glowing cyan accents (`#00F2FE`), emerald indicators (`#10B981`), and typography powered by Google Fonts (`Outfit` & `Inter`).
* **Zero Fake Placeholders**: Every button, input form, search box, modal, and appointment status button is tied directly to the live FastAPI backend APIs.
* **Component Architecture**:
  * **API Client Layer (`js/api.js`)**: Handles JWT header injection, automatic token refresh (`/auth/refresh`), and structured error handling.
  * **Reactive State Store (`js/state.js`)**: Manages active user sessions, role-based permissions (`PATIENT`, `DOCTOR`, `ADMIN`), and active view routing.
  * **Realtime WebSockets (`js/app.js`)**: Connects to `ws://localhost:8000/api/v1/ws/notifications/{user_id}` for instant slide-in alert toasts.
  * **UI Component Engine (`js/components.js`)**: Skeleton loaders, empty states, error banners, and toast notifications.

---

## 🚀 How to Run the Frontend

Since the frontend is built using standard HTML5, CSS3, and ES Modules:

### Option 1: Double-Click or Open `index.html` in Web Browser
Simply open `C:\Users\rohit\Desktop\PROJECTS\mediconnect_ai\frontend\index.html` directly in Google Chrome, Microsoft Edge, or Firefox.

### Option 2: Run with Python HTTP Server
```powershell
cd C:\Users\rohit\Desktop\PROJECTS\mediconnect_ai\frontend
python -m http.server 3000
```
Open `http://localhost:3000` in your web browser!

---

## ⚡ Features & Workflow Guide

1. **Google Gemini AI Symptom Triage**:
   - Type symptoms in the **AI Clinical Triage** tab to generate instant preliminary triage outputs (`EMERGENCY`, `HIGH`, `MODERATE`, `LOW`) with recommended specializations and clinical summaries.
2. **Doctor Directory & Search**:
   - Search verified doctors by specialization (e.g. `Cardiology`, `Neurology`) with real consultation fee and license details.
3. **Appointment Scheduling**:
   - Select a doctor and schedule a date/time. Handles double-booking conflict prevention alerts (`HTTP 409`) gracefully.
4. **Clinical Schedule & State Machine**:
   - Switch between Patient and Doctor roles.
   - Update appointment status (`PENDING` -> `CONFIRMED` -> `COMPLETED` / `CANCELLED`) with clinical notes.
5. **Razorpay Checkout Modal**:
   - Create payment checkout orders and verify HMAC signatures.
