from fastapi import FastAPI

# Initialize the FastAPI app with some basic metadata
app = FastAPI(
    title="Simple API",
    description="A basic FastAPI application",
    version="1.0.0"
)

@app.get("/")
async def read_root():
    """
    Root endpoint that returns a simple welcome message.
    """
    return {"message": "Hello, FastAPI!"}

@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str | None = None):
    """
    Retrieve an item by its ID.
    
    - **item_id**: The ID of the item to retrieve (Path parameter, validated as an integer)
    - **q**: An optional search query (Query parameter)
    """
    return {"item_id": item_id, "q": q}
