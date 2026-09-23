from pydantic import BaseModel


class GeneratePlanSchema(BaseModel):
    exam_id: str