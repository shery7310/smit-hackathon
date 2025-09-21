from fastapi import FastAPI
from routes import router
import uvicorn

app = FastAPI()

app.include_router(router, prefix="/chat")

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI app!"}

# Run with: uvicorn main:app --reload
if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)


