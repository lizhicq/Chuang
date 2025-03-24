import pyrender
import trimesh
import numpy as np
import imageio
from PIL import Image

def render_model(model_path="texture_output_model.glb"):
    # 加载 GLB 文件
    glb_file = model_path  # GLB 文件路径
    scene = trimesh.load(glb_file)
    pyrender_scene = pyrender.Scene.from_trimesh_scene(scene)

    # 获取模型的边界框，计算中心和大小
    bounding_box = scene.bounds
    model_center = (bounding_box[0] + bounding_box[1]) / 2  # 模型中心
    model_size = np.linalg.norm(bounding_box[1] - bounding_box[0])  # 模型对角线长度
    radius = model_size * 1.5  # 相机距离设置为模型大小的 1.5 倍

    # 设置相机
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1920/1080)
    camera_node = pyrender.Node(camera=camera, matrix=np.eye(4))
    pyrender_scene.add_node(camera_node)

    # 添加光源（点光源）
    light = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=5.0)
    light_node = pyrender.Node(light=light, matrix=np.eye(4))
    pyrender_scene.add_node(light_node)

    # 初始化渲染器
    r = pyrender.OffscreenRenderer(viewport_width=1920, viewport_height=1080)

    # 生成旋转动画帧
    frames = []
    for angle in range(0, 360, 3):
        # 更新相机位置（绕模型中心旋转）
        rad = np.radians(angle)
        camera_pose = np.array([
            [np.cos(rad), 0, np.sin(rad), radius * np.sin(rad)],
            [0, 1, 0, model_center[1]],  # 降低相机高度到模型中心
            [-np.sin(rad), 0, np.cos(rad), radius * np.cos(rad)],
            [0, 0, 0, 1]
        ])
        # 相机朝向模型中心
        camera_pose[:3, 3] += model_center - camera_pose[:3, 3] * 0.1  # 调整朝向

        # 更新光源位置（跟随相机）
        light_pose = camera_pose.copy()
        pyrender_scene.remove_node(light_node)
        light_node = pyrender.Node(light=light, matrix=light_pose)
        pyrender_scene.add_node(light_node)

        # 更新相机节点
        pyrender_scene.remove_node(camera_node)
        camera_node = pyrender.Node(camera=camera, matrix=camera_pose)
        pyrender_scene.add_node(camera_node)

        # 渲染当前帧
        color, _ = r.render(pyrender_scene)
        frames.append(color)

    # 保存为视频
    output_path = model_path.replace('.glb', '.mp4')
    imageio.mimwrite(output_path, frames, format="FFMPEG", fps=24, codec="libx264")

    # 清理
    r.delete()
    print(f"视频生成完成！输出路径: {output_path}")

if __name__ == "__main__":
    # 示例调用：使用纹理图像
    render_model("/Users/lizhicq/GitHub/Chuang/model/model_from_local_image.glb")  # 替换为你的纹理路径
    # 示例调用：无纹理，默认红色
    # render_model("model/moster_mask_red.glb")