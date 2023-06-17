import json
from typing import Any, Union

from fastapi import FastAPI

from schemas import all_schemas

from routers.routers import router as router_functions

app = FastAPI()

app.include_router(router_functions)


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/schemas", response_model=dict[str, dict[str, Any]]
                                    | Union[*all_schemas])
async def schemas():
    schems = {}
    for schema in all_schemas:
        schems[schema.__name__] = schema.schema()
    return schems
