from pydantic import BaseModel, Field
from typing import Optional
from bson import ObjectId

# Optional: Support for MongoDB's ObjectId in Pydantic
class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")


# Main form schema
class MRIFormSchema(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id")
    name: str
    phone: str
    bloodGroup: str
    age: int
    image_path: str  # local path or cloud URL

    class Config:
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
