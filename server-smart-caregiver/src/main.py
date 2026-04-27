import os
import jinja2
from fastapi import FastAPI, Request

from src.app.routers import auth_google

try:
    from workers import WorkerEntrypoint
except ImportError:
    # Dummy class for local development where 'workers' package might fail to load
    class WorkerEntrypoint:
        pass

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    # dotenv is not available in Cloudflare Workers runtime
    pass

environment = jinja2.Environment()
template = environment.from_string("Hello, {{ name }}!")

app = FastAPI()

app.include_router(auth_google.router)


@app.get("/")
async def root():   
    message = "This is an example of FastAPI with Jinja2 - go to /hi/<name> to see a template rendered"
    return {"message": message}


@app.get("/hi/{name}")
async def say_hi(name: str):
    message = template.render(name=name)
    return {"message": message}


@app.get("/env")
async def env(req: Request):
    # Fallback for local development without pywrangler
    cf_env = req.scope.get("env")
    if cf_env:
        message_val = getattr(cf_env, "MESSAGE", "No MESSAGE in Cloudflare env")
    else:
        message_val = os.getenv("MESSAGE", "Default Local Message")
        
    message = f"Here is an example of getting an environment variable: {message_val}"
    return {"message": message}


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        import asgi

        return await asgi.fetch(app, request.js_object, self.env)
