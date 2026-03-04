"""
High School Management System API.

A simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from copy import deepcopy
import os
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

INITIAL_ACTIVITIES = {
    "Chess Club": {
        "description": "Learn strategies and compete in chess tournaments",
        "schedule": "Fridays, 3:30 PM - 5:00 PM",
        "max_participants": 12,
        "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
    },
    "Programming Class": {
        "description": "Learn programming fundamentals and build software projects",
        "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
    },
    "Basketball": {
        "description": "Team sport focusing on basketball skills and competitive play",
        "schedule": "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        "max_participants": 15,
        "participants": ["alex@mergington.edu"]
        },
        "Tennis Club": {
        "description": "Learn tennis techniques and participate in matches",
        "schedule": "Saturdays, 10:00 AM - 12:00 PM",
        "max_participants": 10,
        "participants": ["jessica@mergington.edu"]
        },
        "Drama Club": {
        "description": "Perform in theatrical productions and develop acting skills",
        "schedule": "Thursdays, 4:00 PM - 5:30 PM",
        "max_participants": 25,
        "participants": ["ryan@mergington.edu", "sarah@mergington.edu"]
        },
        "Art Studio": {
        "description": "Explore painting, drawing, and sculpture techniques",
        "schedule": "Tuesdays and Fridays, 3:30 PM - 4:30 PM",
        "max_participants": 18,
        "participants": ["maya@mergington.edu"]
        },
        "Debate Team": {
        "description": "Develop argumentation and public speaking skills",
        "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
        "max_participants": 16,
        "participants": ["christopher@mergington.edu", "isabella@mergington.edu"]
        },
        "Science Club": {
        "description": "Conduct experiments and explore scientific discoveries",
        "schedule": "Thursdays, 3:30 PM - 4:30 PM",
        "max_participants": 20,
        "participants": ["david@mergington.edu"]
        },
    "Gym Class": {
        "description": "Physical education and sports activities",
        "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        "max_participants": 30,
        "participants": ["john@mergington.edu", "olivia@mergington.edu"]
    }
}


class ActivityStore:
    def __init__(self):
        self._mongo_available = False
        self._memory_activities = deepcopy(INITIAL_ACTIVITIES)
        self._collection = None

        mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
        mongo_db_name = os.getenv("MONGODB_DB", "mergington_school")
        mongo_collection_name = os.getenv("MONGODB_COLLECTION", "activities")

        try:
            client = MongoClient(mongo_uri, serverSelectionTimeoutMS=1500)
            client.admin.command("ping")
            self._collection = client[mongo_db_name][mongo_collection_name]
            self._collection.create_index("name", unique=True)
            self._seed_if_empty()
            self._mongo_available = True
        except PyMongoError:
            self._mongo_available = False

    def _seed_if_empty(self):
        if self._collection is None:
            return
        if self._collection.count_documents({}) > 0:
            return

        documents = []
        for name, data in INITIAL_ACTIVITIES.items():
            document = {"name": name, **data}
            documents.append(document)
        self._collection.insert_many(documents)

    def get_activities(self):
        if not self._mongo_available:
            return deepcopy(self._memory_activities)

        activities = {}
        for doc in self._collection.find({}, {"_id": 0}):
            name = doc.pop("name")
            activities[name] = doc
        return activities

    def signup(self, activity_name: str, email: str):
        if not self._mongo_available:
            if activity_name not in self._memory_activities:
                raise HTTPException(status_code=404, detail="Activity not found")

            activity = self._memory_activities[activity_name]
            if email in activity["participants"]:
                raise HTTPException(status_code=400, detail="Student already signed up for this activity")

            activity["participants"].append(email)
            return

        activity = self._collection.find_one({"name": activity_name}, {"_id": 0, "participants": 1})
        if activity is None:
            raise HTTPException(status_code=404, detail="Activity not found")
        if email in activity.get("participants", []):
            raise HTTPException(status_code=400, detail="Student already signed up for this activity")

        self._collection.update_one(
            {"name": activity_name},
            {"$addToSet": {"participants": email}},
        )

    def unregister(self, activity_name: str, email: str):
        if not self._mongo_available:
            if activity_name not in self._memory_activities:
                raise HTTPException(status_code=404, detail="Activity not found")
            activity = self._memory_activities[activity_name]
            if email in activity["participants"]:
                activity["participants"].remove(email)
                return True
            return False

        activity = self._collection.find_one({"name": activity_name}, {"_id": 0, "participants": 1})
        if activity is None:
            raise HTTPException(status_code=404, detail="Activity not found")

        if email not in activity.get("participants", []):
            return False

        self._collection.update_one(
            {"name": activity_name},
            {"$pull": {"participants": email}},
        )
        return True


store = ActivityStore()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    return store.get_activities()



@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    store.signup(activity_name, email)
    return {"message": f"Signed up {email} for {activity_name}"}


# Teilnehmer aus Aktivität entfernen
@app.post("/activities/{activity_name}/unregister")
async def unregister_participant(activity_name: str, email: str):
    removed = store.unregister(activity_name, email)
    if removed:
        return {"success": True}
    return {"success": False, "detail": "Teilnehmer nicht gefunden."}
