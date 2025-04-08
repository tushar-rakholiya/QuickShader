from qs.projectManager import ProjectManager
import os
import numpy as np
from qs.shaderPreview import ShaderPreview
class ShaderGenerator:
    def __init__(self, shader_name="GeneratedShader"):
        self.shader_name = shader_name
        self.shader_code_u = ""  # Unity HLSL/Cg
        self.shader_code_p = ""  # Preview GLSL (only fragment shader)
        self.checkpoints = []
        self.current_checkpoint_index = -1
        self.template_index = 1  # Default template index

    def set_shader_template(self, index: int):
        self.template_index = index
        print(f"🎨 Shader template set to index {index}")

    def generate_shader_code(self, extracted_data: dict):
        templates = {
            1: self._generate_shader_template_1,
            2: self._generate_shader_template_2,
            3: self._generate_shader_template_3,
        }
        shader_func = templates.get(self.template_index, self._generate_shader_template_1)
        shader_func(extracted_data)

    def _generate_shader_template_1(self, extracted_data: dict):
        brightness = extracted_data.get("brightness", 128) / 255.0
        contrast = extracted_data.get("contrast", 128) / 255.0
        light_dir = extracted_data.get("light_direction", 0.0)
        texture_complexity = extracted_data.get("texture_complexity", 0.0)
        gradient_magnitude = extracted_data.get("gradient_magnitude", 0.0) / 255.0
        
        # Ensure average_color is a list of 3 values, defaulting to [128, 128, 128]
        average_color = extracted_data.get("average_color", [128, 128, 128])  # Defaults to RGB(128, 128, 128)
        
        # If average_color is a single value (e.g., numpy.float64), convert it to a list
        if isinstance(average_color, (int, float, np.float64)):
            average_color = [average_color] * 3  # Repeat the value for all three components
        
        # Normalize to [0, 1] range for shader
        average_color = [c / 255.0 for c in average_color]  

        is_high_contrast = extracted_data.get("is_high_contrast", False)

        contrast_factor = 2.0 if is_high_contrast else 1.0
        edge_boost = gradient_magnitude * 0.5

        # Generate Unity Shader Code
        self.shader_code_u = f"""
        Shader \"{self.shader_name}\" {{
            Properties {{
                _MainTex (\"Texture\", 2D) = \"white\" {{}}
            }}
            SubShader {{
                Tags {{ \"RenderType\"=\"Opaque\" }}
                LOD 100

                Pass {{
                    CGPROGRAM
                    #pragma vertex vert
                    #pragma fragment frag
                    #include \"UnityCG.cginc\"

                    struct appdata {{
                        float4 vertex : POSITION;
                        float2 uv : TEXCOORD0;
                    }};

                    struct v2f {{
                        float2 uv : TEXCOORD0;       
                        float4 vertex : SV_POSITION; 
                    }};

                    sampler2D _MainTex;

                    v2f vert (appdata v) {{
                        v2f o;
                        o.vertex = UnityObjectToClipPos(v.vertex);
                        o.uv = v.uv;
                        return o;
                    }}

                    fixed4 frag (v2f i) : SV_Target {{
                        fixed4 col = tex2D(_MainTex, i.uv);
                        col.rgb *= {brightness:.3f};
                        col.rgb = ((col.rgb - 0.5) * {contrast_factor:.3f} + 0.5);
                        col.rgb += {edge_boost:.3f};
                        
                        // Ensure average_color is a list of 3 values
                        float3 avg_color = float3({average_color[0]:.3f}, {average_color[1]:.3f}, {average_color[2]:.3f});
                        col.rgb = lerp(col.rgb, avg_color, 0.2);
                        
                        return col;
                    }}
                    ENDCG
                }}
            }}
        }}
        """

        self.save_checkpoint()
        


    def _generate_shader_template_2(self, extracted_data: dict):
        self.shader_code_u = "// Unity Shader Template 2"  # placeholder
        self.shader_code_p = "// GLSL Shader Template 2"   # placeholder
        self.save_checkpoint()

    def _generate_shader_template_3(self, extracted_data: dict):
        self.shader_code_u = "// Unity Shader Template 3"  # placeholder
        self.shader_code_p = "// GLSL Shader Template 3"   # placeholder
        self.save_checkpoint()

    def save_shader(self, output_path=None):
        if output_path is None:
            project_path = ProjectManager.get_current_project_path()
            if project_path is None:
                print("⚠️ Cannot save shader: No project is currently loaded or created.")
                return
            output_path = os.path.join(project_path, f"{self.shader_name}.shader")

        with open(output_path, "w") as f:
            f.write(self.shader_code_u)

        print(f"✅ Shader saved to {output_path}")

    def get_shader_code(self):
        return self.shader_code_u  # Only for preview use

    def apply_modifications(self, modified_data: dict):
        if 'append_code' in modified_data:
            extra = modified_data['append_code']
            self.shader_code_u += f"\n// Unity Modification\n{extra}"
            self.shader_code_p += f"\n// GLSL Modification\n{extra}"
        self.save_checkpoint()

    def reset_settings(self):
        self.shader_code_u = ""
        self.shader_code_p = ""
        self.checkpoints = []
        self.current_checkpoint_index = -1

    def save_checkpoint(self):
        checkpoint = {
            'shader_code_u': self.shader_code_u,
            'shader_code_p': self.shader_code_p
        }
        self.checkpoints = self.checkpoints[:self.current_checkpoint_index + 1]
        self.checkpoints.append(checkpoint)
        self.current_checkpoint_index += 1
        print("📌 Checkpoint saved.")

    def undo(self):
        if self.current_checkpoint_index > 0:
            self.current_checkpoint_index -= 1
            checkpoint = self.checkpoints[self.current_checkpoint_index]
            self.shader_code_u = checkpoint['shader_code_u']
            self.shader_code_p = checkpoint['shader_code_p']
            print("↩️ Undo applied.")

    def redo(self):
        if self.current_checkpoint_index < len(self.checkpoints) - 1:
            self.current_checkpoint_index += 1
            checkpoint = self.checkpoints[self.current_checkpoint_index]
            self.shader_code_u = checkpoint['shader_code_u']
            self.shader_code_p = checkpoint['shader_code_p']
            print("↪️ Redo applied.")
