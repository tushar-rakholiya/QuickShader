import pygame
from pygame.locals import *
from OpenGL.GL import *
from OpenGL.GLU import *
import pywavefront
from qs.shaderModifier import ShaderModifier
import os

class ShaderPreview:
    def __init__(self, width=800, height=600, template_index=1, imageanalyzer=None):
        self.width = width
        self.height = height
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.model_path = os.path.join(current_dir, "object.obj")
        self.template_index = template_index
        self.background_color = [0.1, 0.1, 0.1, 1.0]

        modifier = ShaderModifier(ia=imageanalyzer)
        self.extracted_data = modifier.generate_shader_inputs()
        
        self.shader_program = None
        self.model = None

        self.vertex_shader_code = """
        #version 120

        varying vec3 Normal;
        varying vec3 FragPos;

        void main() {
            FragPos = vec3(gl_ModelViewMatrix * gl_Vertex);
            Normal = normalize(gl_NormalMatrix * gl_Normal);
            gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
        }
        """

    def _generate_shader_template_1(self):
        data = self.extracted_data
        print("🧠 Modified Shader Inputs:", data)

        dom_r, dom_g, dom_b = data.get("dominant_color", [0.5, 0.5, 0.5])
        brightness = data.get("brightness", 1.0)
        contrast = data.get("contrast_factor", 1.0)
        lx, ly, lz = data.get("light_direction_vec", [0.0, 0.0, 1.0])
        gradient = data.get("gradient_magnitude", 0.5)
        high_contrast = data.get("high_contrast_enabled", 0.0)

        return f"""
        #version 120

        varying vec3 Normal;
        varying vec3 FragPos;

        void main() {{
            vec3 norm = normalize(Normal);
            vec3 lightPos = vec3({lx:.2f}, {ly:.2f}, {lz:.2f});
            vec3 lightDir = normalize(lightPos - FragPos);
            vec3 viewDir = normalize(-FragPos);
            vec3 reflectDir = reflect(-lightDir, norm);

            float diff = max(dot(norm, lightDir), 0.0);
            float spec = pow(max(dot(viewDir, reflectDir), 0.0), 16.0);
            float ambient = 0.2;

            vec3 baseColor = vec3({dom_r:.2f}, {dom_g:.2f}, {dom_b:.2f}) ;
            vec3 lighting = (ambient + diff + 0.3 * spec) * baseColor * {brightness:.2f};
            lighting = mix(vec3(0.5), lighting, {contrast:.2f});

            if ({high_contrast:.1f} > 0.5) {{
                lighting = clamp(lighting * 1.2, 0.0, 1.0);
            }}

            gl_FragColor = vec4(clamp(lighting, 0.0, 1.0), 1.0);
        }}
        """

    def generate_fragment_shader_code(self):
        templates = {
            1: self._generate_shader_template_1,
        }
        return templates.get(self.template_index, self._generate_shader_template_1)()

    def init_pygame(self):
        pygame.init()
        pygame.display.set_mode((self.width, self.height), DOUBLEBUF | OPENGL)
        pygame.display.set_caption("Shader Preview")

    def load_model(self):
        self.model = pywavefront.Wavefront(self.model_path, collect_faces=True)
        print("🗿 3D model loaded.")

    def set_background_color(self, r=None, g=None, b=None, a=1.0):
        if r is None or g is None or b is None:
            # Fetch the dominant color and calculate inverse
            dom_r, dom_g, dom_b = self.extracted_data.get("dominant_color", [0.5, 0.5, 0.5])
            r, g, b = 1.0 - dom_r, 1.0 - dom_g, 1.0 - dom_b
            print(f"🎨 Inverse background color set to: ({r:.2f}, {g:.2f}, {b:.2f})")
        
        self.background_color = [r, g, b, a]


    def init_opengl(self):
        glEnable(GL_DEPTH_TEST)
        glEnable(GL_NORMALIZE)
        glClearColor(*self.background_color)
        glViewport(0, 0, self.width, self.height)
        glMatrixMode(GL_PROJECTION)
        gluPerspective(45, (self.width / self.height), 0.1, 2000.0)
        glMatrixMode(GL_MODELVIEW)

    def compile_shader(self, fragment_code):
        print("🧪 Compiling shaders...")

        vertex = glCreateShader(GL_VERTEX_SHADER)
        fragment = glCreateShader(GL_FRAGMENT_SHADER)

        glShaderSource(vertex, self.vertex_shader_code)
        glCompileShader(vertex)
        if not glGetShaderiv(vertex, GL_COMPILE_STATUS):
            print("❌ Vertex Shader Error:\n", glGetShaderInfoLog(vertex).decode())

        glShaderSource(fragment, fragment_code)
        glCompileShader(fragment)
        if not glGetShaderiv(fragment, GL_COMPILE_STATUS):
            print("❌ Fragment Shader Error:\n", glGetShaderInfoLog(fragment).decode())

        program = glCreateProgram()
        glAttachShader(program, vertex)
        glAttachShader(program, fragment)
        glLinkProgram(program)

        if not glGetProgramiv(program, GL_LINK_STATUS):
            print("❌ Shader Link Error:\n", glGetProgramInfoLog(program).decode())
        else:
            print("✅ Shader compiled and linked.")
        
        self.shader_program = program

    def draw_model(self):
        glBegin(GL_TRIANGLES)
        for mesh in self.model.mesh_list:
            for face in mesh.faces:
                for vertex_i in face:
                    vertex = self.model.vertices[vertex_i]
                    glVertex3f(*vertex)
        glEnd()

    def preview_shader(self):
        self.init_pygame()
        self.init_opengl()
        self.load_model()

        fragment_shader_code = self.generate_fragment_shader_code()
        self.compile_shader(fragment_shader_code)

        running = True
        angle = 0
        clock = pygame.time.Clock()

        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    running = False

            glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
            glLoadIdentity()
            gluLookAt(0, 300, 900, 0, 300, 0, 0, 1, 0)

            glRotatef(angle, 0, 1, 0)
            angle += 0.5

            glUseProgram(self.shader_program)
            self.draw_model()
            glUseProgram(0)

            pygame.display.flip()
            clock.tick(60)

        pygame.quit()
