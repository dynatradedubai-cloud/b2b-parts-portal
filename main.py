from fastapi import FastAPI

app = FastAPI()

@app.get("/search")
def search(q: str):
    return [
        {
            "description": "Brake Pad",
            "brand": "Toyota",
            "vehicle": "Camry",
            "price": 100
        }
    ]
