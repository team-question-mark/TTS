from gtts import gTTS
import os
from fastapi import FastAPI
from pydantic import BaseModel
import boto3
from dotenv import load_dotenv
from fastapi import Response
import json
import uuid
from fastapi.middleware.cors import CORSMiddleware

origins = ["*"]

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# .env 파일 로드
load_dotenv()

# .env 파일에서 환경 변수 읽기
AWS_ACCESS_KEY = os.getenv("AWS_ACCESS_KEY")
AWS_SECRET_KEY = os.getenv("AWS_SECRET_KEY")

#버킷 이름
BUCKET_NAME = os.getenv("BUCKET_NAME")
BUCKET_URL = os.getenv("BUCKET_URL")


class TTS_req(BaseModel):
    sentence: str

class TTS_res(BaseModel):
    speaking_audio: str    

def text_to_speech(sentence, language='ko'):
    # 텍스트를 음성으로 변환
    tts = gTTS(text=sentence, lang=language)
    uid_= str(uuid.uuid4())
    filename = f"temp_{uid_}.mp3"
    tts.save(filename)
    return filename


def upload_file_to_s3(filename, object_name):
    print("s3_connection")
    s3= boto3.client('s3',
                          aws_access_key_id=AWS_ACCESS_KEY,
                          aws_secret_access_key=AWS_SECRET_KEY)
    s3.upload_file(filename, BUCKET_NAME, object_name)
    res = BUCKET_URL+"/"+object_name
    print('res is  ', res)
    return res



@app.post("/tts")
async def tts(request: TTS_req):
    filename = text_to_speech(request.sentence)
    file_path = "TTS/"+filename
    print('file path is  ',file_path)
    s3_url = upload_file_to_s3(filename, file_path)
    response_data= {"speaking_audio":s3_url}
    return Response(content=json.dumps(response_data), media_type="application/json")