from fastapi import FastAPI
from langserve import add_routes
from app.chain import full_chain
from fastapi.responses import RedirectResponse
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()


app = FastAPI(
    title="DB Ticket Agent",
    version="1.0",
    description="LLM based AI agentfor getting information about tickets",
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],   
    allow_headers=["*"],   
    expose_headers=["*"],  
)


@app.get("/")
async def redirect_root_to_docs():
    return RedirectResponse("/docs")

add_routes(app,full_chain,path="/db-agent")

 

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
