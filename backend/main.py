from fastapi import FastAPI
from routes import router as chat_router
from student_crud_routes import router as student_router
from analytics import router as analytics_router
import uvicorn

import uvicorn

app = FastAPI()

app.include_router(chat_router)
app.include_router(student_router)
app.include_router(analytics_router)


@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI app!"}

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


