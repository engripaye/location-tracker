# 🚀 LocationTracker API

A secure, real-time location sharing platform built with Python and FastAPI that enables users to share their live GPS location with trusted contacts through secure tracking links.

## 📖 Overview

LocationTracker API is a backend service designed to solve a real-world safety and coordination challenge: allowing individuals to securely share their live whereabouts with trusted people during travel or emergencies.

Instead of constantly sending location updates manually, users can create a tracking session and generate a secure share link that can be sent to family members, friends, colleagues, or emergency contacts. Authorized recipients can then view the latest location information in real time.

This project demonstrates modern backend engineering practices, RESTful API design, authentication, geolocation processing, secure session management, and scalable architecture using Python.

---

## 🎯 Problem Statement

People often need a secure way to share their location when:

* Traveling alone
* Going on long-distance trips
* Meeting someone in unfamiliar locations
* Coordinating logistics and deliveries
* Providing emergency contacts with their whereabouts
* Sharing location during outdoor activities

LocationTracker provides a secure and privacy-focused solution that allows users to control who can access their location and for how long.

---

## ✨ Features

### Authentication & Security

* User Registration
* User Login
* JWT Authentication
* Password Hashing with BCrypt
* Secure Token Generation

### Location Tracking

* Create Tracking Sessions
* Generate Secure Share Tokens
* Upload GPS Coordinates
* Retrieve Latest Location
* Session Management
* Track Location Accuracy

### Privacy Controls

* User-Owned Tracking Sessions
* Secure Share Links
* Controlled Access to Location Data
* Session Expiration Support (Future Enhancement)

### API Features

* RESTful API Architecture
* FastAPI Documentation
* Request Validation
* Database Persistence
* Error Handling

---

## 🏗️ System Architecture

```text
User A (Traveler)
        │
        ▼
Create Tracking Session
        │
        ▼
Generate Secure Share Token
        │
        ▼
Send Token to Trusted Contact
        │
        ▼
Upload GPS Coordinates
        │
        ▼
LocationTracker API
        │
        ▼
PostgreSQL Database
        │
        ▼
User B Retrieves Latest Location
```

---

## 🛠️ Technology Stack

### Backend

* Python 3.12+
* FastAPI
* SQLAlchemy
* Pydantic

### Database

* PostgreSQL
* Supabase PostgreSQL (Cloud)

### Security

* JWT Authentication
* Passlib BCrypt
* Python-JOSE

### Deployment

* Docker
* Render
* Railway
* AWS

---

## 📂 Project Structure

```text
location-tracker-backend/
│
├── app/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── security.py
│   ├── dependencies.py
│   │
│   ├── routes/
│   │   ├── auth.py
│   │   ├── sessions.py
│   │   └── tracking.py
│   │
│   └── services/
│       └── token_service.py
│
├── requirements.txt
├── .env
└── README.md
```

---

## 🔑 Core API Endpoints

### Authentication

| Method | Endpoint       | Description       |
| ------ | -------------- | ----------------- |
| POST   | /auth/register | Register new user |
| POST   | /auth/login    | Authenticate user |

### Tracking Sessions

| Method | Endpoint            | Description            |
| ------ | ------------------- | ---------------------- |
| POST   | /sessions/start     | Start tracking session |
| POST   | /sessions/{id}/stop | Stop tracking session  |

### Location Tracking

| Method | Endpoint                     | Description              |
| ------ | ---------------------------- | ------------------------ |
| POST   | /track/{session_id}/location | Upload GPS coordinates   |
| GET    | /track/{share_token}         | Retrieve latest location |

---

## 🔒 Security Considerations

This project follows several security best practices:

* Passwords are never stored in plain text
* BCrypt hashing for credential protection
* JWT-based authentication
* Secure share token generation
* Request validation using Pydantic
* Database transaction management
* Controlled access to tracking sessions

---

## 📈 Future Enhancements

### Real-Time Tracking

* WebSocket Integration
* Live GPS Streaming
* Automatic Location Refresh

### Advanced Mapping

* Google Maps Integration
* OpenStreetMap Support
* Reverse Geocoding
* Route Visualization

### Emergency Features

* SOS Alerts
* Emergency Contact Notifications
* Panic Button
* Safe Arrival Confirmation

### Scalability

* Redis Caching
* Kafka Event Streaming
* Microservices Architecture
* Kubernetes Deployment

### Analytics

* Travel History
* Distance Calculations
* Movement Analytics
* Location Insights

---

## 🚀 Running Locally

Clone the repository:

```bash
git clone https://github.com/yourusername/location-tracker-backend.git
```

Navigate into the project:

```bash
cd location-tracker-backend
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Configure environment variables:

```env
DATABASE_URL=your_database_url
JWT_SECRET=your_secret_key
```

Start the server:

```bash
uvicorn app.main:app --reload
```

API Documentation:

```text
http://localhost:8000/docs
```

---

## 💡 Engineering Highlights

This project demonstrates:

* Backend API Design
* Authentication & Authorization
* Geolocation Data Processing
* Database Modeling
* Secure Token Management
* RESTful Architecture
* FastAPI Development
* PostgreSQL Integration
* Software Design Principles

---

## 👨‍💻 About The Developer

Built by **Olabowale Babatunde Ipaye** — Backend Engineer specializing in:

* Python & FastAPI
* Java & Spring Boot
* Microservices Architecture
* Event-Driven Systems
* PostgreSQL & Database Design
* Cloud-Native Backend Development

I enjoy building software solutions that solve real-world problems through scalable backend systems, clean architecture, and secure API design.

---

### ⭐ If you found this project interesting, consider giving it a star and connecting with me on LinkedIn.
