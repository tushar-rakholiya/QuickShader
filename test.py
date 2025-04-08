from qs.imageAnalyzer import ImageAnalyzer
from qs.shaderGenerator import ShaderGenerator
from qs.shaderPreview import ShaderPreview
from qs.projectManager import ProjectManager
def main():
    # Step 1: Analyze the input image
    print("🔍 Analyzing image...")
    analyzer = ImageAnalyzer()
    extracted_data = analyzer.analyze_image()

    # Step 2: Generate shader code based on extracted data
    print("⚙️ Generating shader code...")
    shader_generator = ShaderGenerator()
    shader_generator.generate_shader_code(extracted_data)

    # Step 3: Preview the shader (optional)
    print("👀 Previewing shader...")
    preview = ShaderPreview(template_index=shader_generator.template_index,imageanalyzer=analyzer)  
    preview.preview_shader()

    # Step 4: Save the generated shader to disk
    print("💾 Saving shader to disk...")
    shader_generator.save_shader("GeneratedShader.shader")

    print("✅ Shader generation complete.")

if __name__ == "__main__":
    main()
