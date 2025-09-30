from fastapi import FastAPI

# Our server daemon
app = FastAPI(title="Tetsuya")

# used by a lot of things, needs to be a bottom-dependency
