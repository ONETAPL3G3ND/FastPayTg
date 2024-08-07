from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
import redis
from pydantic import BaseModel
import DataClass
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

mongo_client = MongoClient("mongodb://mongo:27017")
db = mongo_client["key_value_db"]
collection = db["key_value_collection"]
redis_client = redis.StrictRedis(host='redis', port=6379, db=0)

@app.post("/set/{key}")
def set_value(key: str, key_value: DataClass.KeyValue):
    value = key_value.value
    collection.update_one({"key": key}, {"$set": {"value": value}}, upsert=True)
    redis_client.set(key, value, ex=60)
    return {"message": f"Key '{key}' set to '{value}'"}


@app.get("/get/{key}")
def get_value(key: str):
    value = redis_client.get(key)
    if value:
        return {"key": key, "value": value.decode('utf-8')}

    result = collection.find_one({"key": key})
    if result:
        redis_client.set(key, result["value"], ex=60)
        return {"key": key, "value": result["value"]}

    raise HTTPException(status_code=404, detail="Key not found")


@app.delete("/delete/{key}")
def delete_value(key: str):
    result = collection.delete_one({"key": key})
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Key not found")

    redis_client.delete(key)
    return {"message": f"Key '{key}' deleted"}
