import numpy as np
from PIL import Image
from sklearn.cluster import KMeans
from qs.imageAnalyzer import ImageAnalyzer as IA

class ShaderModifier:
    def __init__(self, ia=None):
        self.ia = ia
        self.data = ia.analyze_image() if ia else {}

    def normalize_brightness(self):
        brightness = self.data.get("brightness", 128)
        return min(max(brightness / 255.0, 0.0), 1.0)

    def normalize_contrast(self):
        contrast = self.data.get("contrast", 128)
        return min(max((contrast - 128) / 127.0, -1.0), 1.0)

    def get_light_direction_vector(self):
        direction = self.data.get("light_direction", 0.0)
        return [np.cos(np.radians(direction)), np.sin(np.radians(direction)), 0.0]

    def normalize_texture_complexity(self):
        complexity = self.data.get("texture_complexity", 128)
        return min(max(complexity / 1000.0, 0.0), 1.0)

    def normalize_gradient_magnitude(self):
        gradient = self.data.get("gradient_magnitude", 128)
        return min(max(gradient / 1000.0, 0.0), 1.0)

    def get_average_color(self):
        avg = self.data.get("average_color", 128)
        normalized = min(max(avg / 255.0, 0.0), 1.0)
        return [normalized] * 3

    def get_dominant_color(self, k=1):
        if not self.ia:
            return [1.0, 1.0, 1.0]  # fallback white

        # Load full color image
        img = Image.open(self.ia.image_path).convert("RGB")
        img = img.resize((64, 64))  # Resize to reduce processing
        pixels = np.array(img).reshape(-1, 3)

        kmeans = KMeans(n_clusters=k)
        kmeans.fit(pixels)
        dominant_rgb = kmeans.cluster_centers_[0] / 255.0
        return dominant_rgb.tolist()

    def is_high_contrast_enabled(self):
        return 1.0 if self.data.get("is_high_contrast", False) else 0.0

    def generate_shader_inputs(self):
        return {
            "brightness": self.normalize_brightness(),
            "contrast_factor": self.normalize_contrast(),
            "light_direction_vec": self.get_light_direction_vector(),
            "texture_complexity": self.normalize_texture_complexity(),
            "gradient_magnitude": self.normalize_gradient_magnitude(),
            "average_color": self.get_average_color(),
            "dominant_color": self.get_dominant_color(),
            "high_contrast_enabled": self.is_high_contrast_enabled(),
        }

    def debug_print(self):
        print("Shader Inputs:")
        for k, v in self.generate_shader_inputs().items():
            print(f"  {k}: {v}")
