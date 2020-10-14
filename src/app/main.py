from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def home() -> dict:
    """Check if system is alive and get version info"""
    return {
        'name': "Test Service",
        'message': "Hello world",
        'version': "0.1",
    }
