from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def home():
    return {"message": "Web scraper running!"}
