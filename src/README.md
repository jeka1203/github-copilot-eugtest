# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities
- Persist activities and participants in MongoDB

## Getting Started

1. Install the dependencies:

   ```
   pip install -r ../requirements.txt
   ```

2. MongoDB lokal starten (empfohlen via Docker Compose):

   ```
   docker compose up -d mongodb
   ```

   Die Compose-Datei liegt im Projekt-Root.

   Alternativ direkt auf dem System installieren/starten:

   ```
   sudo apt update
   sudo apt install -y mongodb
   sudo systemctl enable --now mongodb
   ```

   Alternativ kannst du eine externe MongoDB-Instanz (z. B. Atlas) nutzen.

3. Optional: Verbindung konfigurieren (Standard ist `mongodb://localhost:27017`):

   ```
   export MONGODB_URI="mongodb://localhost:27017"
   export MONGODB_DB="mergington_school"
   export MONGODB_COLLECTION="activities"
   ```

4. Run the application:

   ```
   uvicorn app:app --reload
   ```

5. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Die Daten werden primär in MongoDB gespeichert.

Wenn MongoDB nicht erreichbar ist, fällt die Anwendung automatisch auf In-Memory-Speicherung zurück.
