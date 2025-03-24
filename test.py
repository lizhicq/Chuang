import pyrender
import trimesh
import numpy as np
import imageio
from PIL import Image

def render_model(model_path="texture_output_model.glb"):
    # 加载 GLB 文件
    glb_file = model_path
    scene = trimesh.load(glb_file)
    pyrender_scene = pyrender.Scene.from_trimesh_scene(scene, ambient_light=[0.3, 0.3, 0.3])  # 添加环境光

    # 获取模型的边界框，计算中心和大小
    bounding_box = scene.bounds
    model_center = (bounding_box[0] + bounding_box[1]) / 2
    model_size = np.linalg.norm(bounding_box[1] - bounding_box[0])
    radius = model_size * 1.5

    # 设置相机
    camera = pyrender.PerspectiveCamera(yfov=np.pi / 3.0, aspectRatio=1920/1080)
    camera_node = pyrender.Node(camera=camera, matrix=np.eye(4))
    pyrender_scene.add_node(camera_node)

    # 添加多个光源以增强亮度
    # 主点光源（跟随相机）
    light1 = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=8.0)  # 提高强度
    light_node1 = pyrender.Node(light=light1, matrix=np.eye(4))
    pyrender_scene.add_node(light_node1)
    
    # 辅助光源（顶部固定）
    light2 = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=5.0)
    light_node2 = pyrender.Node(light=light2, translation=[0, model_size, 0])
    pyrender_scene.add_node(light_node2)
    
    # 辅助光源（底部固定）
    light3 = pyrender.PointLight(color=[1.0, 1.0, 1.0], intensity=5.0)
    light_node3 = pyrender.Node(light=light3, translation=[0, -model_size, 0])
    pyrender_scene.add_node(light_node3)

    # 初始化渲染器
    r = pyrender.OffscreenRenderer(viewport_width=1920, viewport_height=1080)

    # 生成旋转动画帧（增加上下环绕）
    frames = []
    num_frames = 120  # 总帧数
    for i in range(num_frames):
        # 计算水平和垂直角度
        horizontal_angle = np.radians((i / num_frames) * 360)  # 水平360度旋转
        vertical_angle = np.radians(np.sin(np.radians(i * 3)) * 45)  # 上下45度范围内摆动
        
        # 更新相机位置（球面坐标系）
        x = radius * np.cos(vertical_angle) * np.sin(horizontal_angle)
        y = radius * np.sin(vertical_angle)
        z = radius * np.cos(vertical_angle) * np.cos(horizontal_angle)
        
        camera_pose = np.array([
            [1, 0, 0, x],
            [0, 1, 0, y],
            [0, 0, 1, z],
            [0, 0, 0, 1]
        ])
        
        # 相机朝向模型中心
        direction = model_center - np.array([x, y, z])
        direction = direction / np.linalg.norm(direction)
        z_axis = -direction  # 相机朝向相反方向
        x_axis = np.cross([0, 1, 0], z_axis)
        x_axis = x_axis / np.linalg.norm(x_axis)
        y_axis = np.cross(z_axis, x_axis)
        
        camera_pose[:3, 0] = x_axis
        camera_pose[:3, 1] = y_axis
        camera_pose[:3, 2] = z_axis
        camera_pose[:3, 3] = [x, y, z] + model_center * 0.1

        # 更新主光源位置（跟随相机）
        light_pose = camera_pose.copy()
        pyrender_scene.remove_node(light_node1)
        light_node1 = pyrender.Node(light=light1, matrix=light_pose)
        pyrender_scene.add_node(light_node1)

        # 更新相机节点
        pyrender_scene.remove_node(camera_node)
        camera_node = pyrender.Node(camera=camera, matrix=camera_pose)
        pyrender_scene.add_node(camera_node)

        # 渲染当前帧
        color, _ = r.render(pyrender_scene)
        frames.append(color)

    # 保存为视频
    output_path = model_path.replace('.glb', '_enhanced.mp4')
    imageio.mimwrite(output_path, frames, format="FFMPEG", fps=24, codec="libx264")

    # 清理
    r.delete()
    print(f"视频生成完成！输出路径: {output_path}")

if __name__ == "__main__":
    render_model("/Users/lizhicq/GitHub/Chuang/model/model_from_local_image.glb")