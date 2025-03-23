import requests
import time
import os

# 设置 API Key（从环境变量读取或直接填写）
MESHY_API_KEY = os.getenv("MESHY_API_KEY") or "your_api_key_here"
headers = {
    "Authorization": f"Bearer {MESHY_API_KEY}",
    "Content-Type": "application/json"
}

# Text-to-3D 请求，直接生成带纹理的模型
generate_request = {
    "mode": "refine",  # 使用 refine 模式直接生成带纹理的模型
    "prompt": "a monster mask with red fangs, Samurai outfit with Japanese batik style",
    "negative_prompt": "low quality, low resolution, low poly, ugly",
    "art_style": "realistic",
    "should_remesh": True,
    "enable_pbr": True,  # 启用 PBR 材质，确保纹理更真实
    "resolution": "1024"  # 纹理分辨率，可选 512/1024/2048
}

# 发送请求
try:
    response = requests.post(
        "https://api.meshy.ai/openapi/v2/text-to-3d",
        headers=headers,
        json=generate_request
    )
    response.raise_for_status()
    task_id = response.json()["result"]
    print("Refine task created. Task ID:", task_id)

    # 轮询任务状态
    status_url = f"https://api.meshy.ai/openapi/v2/text-to-3d/{task_id}"
    while True:
        status_response = requests.get(status_url, headers=headers)
        status_response.raise_for_status()
        task_data = status_response.json()
        status = task_data["status"]
        print(f"任务状态: {status} | 进度: {task_data.get('progress', 0)}%")

        if status == "SUCCEEDED":
            print("任务完成！")
            model_url = task_data["model_urls"]["glb"]  # 获取 glb 格式模型
            print(f"带纹理的模型下载链接: {model_url}")
            break
        elif status in ["FAILED", "EXPIRED"]:
            print(f"任务失败或过期: {status}")
            break
        else:
            print("任务仍在进行中，5秒后重试...")
            time.sleep(5)

    # 下载生成的带纹理模型
    if status == "SUCCEEDED":
        model_response = requests.get(model_url)
        model_response.raise_for_status()
        with open("textured_monster_mask.glb", "wb") as f:
            f.write(model_response.content)
        print("带纹理的模型已下载至 textured_monster_mask.glb")

except requests.exceptions.RequestException as e:
    print(f"请求失败: {e}")
except KeyError as e:
    print(f"响应数据解析错误: {e}")