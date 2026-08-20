from pydantic import BaseModel, ConfigDict, Field


class QuestionRequest(BaseModel):
    question: str = Field(
        min_length=1, 
        max_length=500, 
        description="La question à poser à l'assistant FAQ intelligent.",
        examples=["Comment obtenir un acte de naissance ?"],
    )    
    model_config = ConfigDict(
        extra="forbid",
        str_strip_whitespace=True,
    )
    
    
    
class QuestionResponse(BaseModel):
    answer: str = Field(
        min_length=1,
        max_length=1000,
        description="La réponse générée par l'assistant FAQ intelligent à la question posée."
    )