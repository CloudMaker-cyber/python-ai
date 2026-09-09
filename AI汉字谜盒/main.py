from fastapi import FastAPI
from fastapi.responses import FileResponse
from starlette.staticfiles import StaticFiles
from fastapi.staticfiles import StaticFiles

# 创建FastAPI实例
app = FastAPI(title="AI汉字谜盒")

#挂载静态文件的存放目录
app.mount("/static", StaticFiles(directory="static"), name="static")

# 定义路径操作函数
@app.get("/")
async def root():
    print("访问项目首页")
    return FileResponse("static/index.html")

if __name__ == '__main__':
    import uvicorn

    uvicorn.run(app,host='127.0.0.1',port=8000)