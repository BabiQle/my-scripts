"""
LabelMe标注工具（改进像素模式版）
修复点：
1. 基于相对位置的平移算法
2. 形状完整性校验
3. 动态调整机制
"""

import json
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any, Union
import numpy as np

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('shape_preserve_scaler.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class AdvancedScaler:
    """高级缩放处理器（保持形状完整性）"""

    def __init__(self):
        self.origin_cache = {}
        self.last_operations = {}

    def _validate_polygon(self, pts: np.ndarray) -> bool:
        """验证多边形有效性"""
        if pts.shape[0] < 3:
            return False
        area = 0.5 * np.abs(np.dot(pts[:, 0], np.roll(pts[:, 1], 1)) - np.dot(pts[:, 1], np.roll(pts[:, 0], 1)))
        return area > 1e-6

    def _preserve_original(self, file_path: Path, data: dict):
        """保存原始数据"""
        if file_path not in self.origin_cache:
            self.origin_cache[file_path] = {
                'shapes': [{
                    'points': np.array(s['points'], dtype=np.float64),
                    'label': s['label']
                } for s in data['shapes']],
                'image_size': (data['imageWidth'], data['imageHeight'])
            }

    def _shape_preserve_move(self, original_pts: np.ndarray, pixels: int) -> np.ndarray:
        """
        形状保持平移算法
        Args:
            original_pts: 原始坐标 (N×2)
            pixels: 平移像素数（正外扩/负内缩）
        Returns:
            平移后的坐标数组
        """
        # 计算质心
        centroid = np.mean(original_pts, axis=0)

        # 计算各边向量
        vectors = original_pts - centroid
        norms = np.linalg.norm(vectors, axis=1)

        # 自动调整机制
        min_norm = np.min(norms[norms > 0])
        safe_pixels = pixels * (min_norm / (min_norm + abs(pixels)))

        # 计算平移方向
        with np.errstate(divide='ignore', invalid='ignore'):
            unit_vectors = vectors / norms[:, None]
        unit_vectors[np.isnan(unit_vectors)] = 0

        # 应用平移
        new_pts = original_pts + unit_vectors * safe_pixels

        # 保持形状比例
        scale_factor = np.linalg.norm(new_pts - centroid) / np.linalg.norm(original_pts - centroid)
        return centroid + (new_pts - centroid) / scale_factor

    def process_file(self, file_path: Path,
                     mode: str,
                     value: Union[float, int],
                     allowed_labels: Optional[List[str]] = None):
        """处理单个文件"""
        try:
            with file_path.open('r', encoding='utf-8') as f:
                current_data = json.load(f)

            self._preserve_original(file_path, current_data)
            origin = self.origin_cache[file_path]
            modified = False

            for shape_idx, shape in enumerate(current_data['shapes']):
                original_shape = origin['shapes'][shape_idx]

                # 过滤条件
                if shape['shape_type'] != 'polygon':
                    continue
                if allowed_labels and original_shape['label'] not in allowed_labels:
                    continue

                # 获取原始坐标
                original_pts = original_shape['points']

                if mode == 'scale':
                    # 比例模式（原有逻辑）
                    center = np.mean(original_pts, axis=0)
                    scaled_pts = (original_pts - center) * value + center
                elif mode == 'pixel':
                    # 改进后的像素模式
                    scaled_pts = self._shape_preserve_move(original_pts, value)
                else:
                    raise ValueError("未知模式")

                # 坐标处理
                img_w, img_h = origin['image_size']
                scaled_pts = np.clip(scaled_pts, [0, 0], [img_w, img_h])
                int_pts = np.round(scaled_pts).astype(int)

                # 形状校验
                if not self._validate_polygon(int_pts):
                    logger.warning(f"无效多边形: {file_path} 标签: {shape['label']}")
                    continue

                # 更新数据
                shape['points'] = int_pts.tolist()
                modified = True

            if modified:
                with file_path.open('w', encoding='utf-8') as f:
                    json.dump(current_data, f, ensure_ascii=False, indent=2)
                logger.info(f"成功处理: {file_path}")

        except Exception as e:
            logger.error(f"处理失败: {file_path} - {str(e)}")

    def batch_process(self, root: str,
                      mode: str,
                      value: Union[float, int],
                      allowed_labels: Optional[List[str]] = None):
        """批量处理"""
        root_path = Path(root)
        if not root_path.exists():
            raise FileNotFoundError(f"目录不存在: {root}")

        logger.info(f"开始处理 | 模式: {mode} | 值: {value}")

        processed = 0
        for json_file in root_path.rglob('*.json'):
            try:
                self.process_file(json_file, mode, value, allowed_labels)
                processed += 1
            except Exception:
                continue

        logger.info(f"处理完成 | 成功: {processed}")


if __name__ == '__main__':
    try:
        scaler = AdvancedScaler()

        # 配置参数
        root_dir = Path(r'D:\##########\temp\examples')
        mode = 'pixel'  # 测试像素模式
        value = 5  # 外扩5像素
        labels = ['1']

        scaler.batch_process(root_dir, mode, value, labels)
        logger.info("处理完成")

    except Exception as e:
        logger.error(f"运行错误: {str(e)}")
