from typing import Any
from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel
from fastapi.staticfiles import StaticFiles
import os
from datetime import datetime
import json

# 生成会话标识(当前时间)
def generate_session_id():
    return datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


class ApiResponse(BaseModel):
    code: int
    message: str
    data: Any
# 创建FastAPI实例
app = FastAPI(title="AI汉字谜盒")

#挂载静态文件的存放目录
app.mount("/static", StaticFiles(directory="static"), name="static")

#生成会话存放目录sessions
if not os.path.exists("sessions"):
    os.makedirs("sessions")


# 定义路径操作函数
@app.get("/")
async def root():
    print("访问项目首页")
    return FileResponse("static/index.html")

#新建对话


@app.post("/api/sessions")
async def create_session():
    print("新建对话")
    #1.生成会话标识（名字）
    session_id = generate_session_id()
    print("会话标识：",session_id)
    #2.组装会话信息并保存到sessions目录下
    session_data = {
        "current_session": session_id,
        "messages": []
    }
    with open(f"sessions/{session_id}.json", "w", encoding="utf-8") as f:
        json.dump(session_data, f, ensure_ascii=False, indent=2)

    #3.返回数据
    return ApiResponse(code=200, message="会话创建成功", data=session_id)

















if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app,host='127.0.0.1',port=8000)