from enum import Enum   #Import Enum and create a sub-class that inherits from str and from Enum.
from fastapi import FastAPI

# Declare path parametr
# Then create a path parameter with a type annotation using the enum class you created (ModelName):
class ModelName(str, Enum):  
    alexnet = "alexnet"
    resnet = "resnet"
    lenet = "lenet"


app =FastAPI()
#root
@app.get('/')
async def root():
    return {"message" : "Hello World"}

#path parameter
#The value of the path parameter item_id will be passed to your function as the argument item_id.
@app.get('/items/{items_id}')
async def  read_items(items_id: int):
 return {"items_id": {items_id}}

#Declare a path parameter
@app.get("/models/{model_name}")
async def get_model(model_name: ModelName):
    if model_name is ModelName.alexnet:
        return {"model_name": model_name, "message": "Deep Learning FTW!"}

    if model_name.value == "lenet":
        return {"model_name": model_name, "message": "LeCNN all the images"}

    return {"model_name": model_name, "message": "Have some residuals"}
 #path parameter
@app.get("/files/{file_path:path}")
async def read_file(file_path: str):
    return {"file_path": file_path}
 #Query parameter
fake_items_db = [{"item_name": "Foo"}, {"item_name": "Bar"}, {"item_name": "Baz"}]


@app.get("/items/")
async def read_item(skip: int = 0, limit: int = 10):
    return fake_items_db[skip : skip + limit]

#Optional parameter
@app.get("/items/{item_id}")
async def read_items(item_id: str, q: str | None = None):
    if q:
        return {"item_id": item_id, "q": q}
    return {"item_id": item_id}

@app.get("/users/{user_id}/items/{item_id}")
async def read_user_item(
    user_id: int, item_id: str, q: str | None = None, short: bool = False
):
    item = {"item_id": item_id, "owner_id": user_id}
    if q:
        item.update({"q": q})
    if not short:
        item.update(
            {"description": "This is an amazing item that has a long description"}
        )
    return item

@app.get("/items/{item_id}")
async def read_user_items(item_id: str, needy: str):
    item = {"item_id": item_id, "needy": needy}
    return item