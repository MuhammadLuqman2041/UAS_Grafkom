from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import sys

angle_x, angle_y = 0, 0  # Sudut rotasi pada sumbu X dan Y (2)
translate_z = -6  # Posisi translasi pada sumbu Z (2)
mouse_down = False  # Status klik mouse untuk rotasi
last_x, last_y = 0, 0


def init():
    glEnable(GL_DEPTH_TEST)  # Aktifkan depth testing untuk rendering 3D (4)
    glEnable(GL_LIGHTING)  # Aktifkan pencahayaan (3)
    glEnable(GL_LIGHT0)  # Aktifkan sumber cahaya LIGHT0 (3)
    glShadeModel(GL_SMOOTH)  # Gunakan Gouraud shading (3)

    # Pengaturan cahaya (3)
    glLightfv(GL_LIGHT0, GL_AMBIENT, [0.2, 0.2, 0.2, 1.0])
    glLightfv(GL_LIGHT0, GL_DIFFUSE, [0.7, 0.7, 0.7, 1.0])
    glLightfv(GL_LIGHT0, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glLightfv(GL_LIGHT0, GL_POSITION, [5.0, 5.0, 5.0, 1.0])

    # Pengaturan material objek (3)
    glMaterialfv(GL_FRONT, GL_AMBIENT_AND_DIFFUSE, [0.8, 0.3, 0.3, 1.0])
    glMaterialfv(GL_FRONT, GL_SPECULAR, [1.0, 1.0, 1.0, 1.0])
    glMaterialf(GL_FRONT, GL_SHININESS, 50.0)

# Menggambar piramida (tetrahedron dengan alas persegi) secara manual (1)
def draw_pyramid():
    glBegin(GL_TRIANGLES)  # Menggambar sisi piramida sebagai segitiga
    # Sisi depan
    glNormal3f(0, 0.5, 0.5)
    glVertex3f(0, 1, 0)
    glVertex3f(-1, -1, 1)
    glVertex3f(1, -1, 1)
    # Sisi kanan
    glNormal3f(0.5, 0.5, 0)
    glVertex3f(0, 1, 0)
    glVertex3f(1, -1, 1)
    glVertex3f(1, -1, -1)  # Sudut kanan belakang alas
    # Sisi belakang
    glNormal3f(0, 0.5, -0.5)
    glVertex3f(0, 1, 0)
    glVertex3f(1, -1, -1)
    glVertex3f(-1, -1, -1)  # Sudut kiri belakang alas
    # Sisi kiri
    glNormal3f(-0.5, 0.5, 0)
    glVertex3f(0, 1, 0)
    glVertex3f(-1, -1, -1)
    glVertex3f(-1, -1, 1)
    glEnd()

    glBegin(GL_QUADS)  # Menggambar alas piramida sebagai quad
    glNormal3f(0, -1, 0)
    glVertex3f(-1, -1, 1)
    glVertex3f(1, -1, 1)
    glVertex3f(1, -1, -1)
    glVertex3f(-1, -1, -1)
    glEnd()

# Fungsi display untuk merender piramida dengan transformasi dan kamera
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    gluLookAt(0, 0, 5, 0, 0, 0, 0, 1, 0)  # Atur posisi kamera (4)

    glTranslatef(0, 0, translate_z)
    glRotatef(angle_x, 1, 0, 0)  # Rotasi pada sumbu X (2)
    glRotatef(angle_y, 0, 1, 0)  # Rotasi pada sumbu Y (2)

    draw_pyramid()
    glutSwapBuffers()

# Menangani perubahan ukuran jendela dan proyeksi perspektif
def reshape(w, h):
    if h == 0:
        h = 1
    glViewport(0, 0, w, h)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, w / h, 1.0, 100.0)
    glMatrixMode(GL_MODELVIEW)

# Menangani input mouse untuk memulai rotasi
def mouse(button, state, x, y):
    global mouse_down, last_x, last_y
    if button == GLUT_LEFT_BUTTON:
        if state == GLUT_DOWN:
            mouse_down = True
            last_x, last_y = x, y
        elif state == GLUT_UP:
            mouse_down = False

# Menangani gerakan mouse untuk rotasi
def motion(x, y):
    global angle_x, angle_y, last_x, last_y
    if mouse_down:
        dx = x - last_x
        dy = y - last_y
        angle_x += dy * 0.5  # Rotasi sumbu X berdasarkan gerakan vertikal (2)
        angle_y += dx * 0.5  # Rotasi sumbu Y berdasarkan gerakan horizontal (2)
        last_x, last_y = x, y
        glutPostRedisplay()

# Menangani input keyboard untuk translasi
def keyboard(key, x, y):
    global translate_z
    key = key.decode('utf-8')
    if key == 'w':
        translate_z += 0.2  # Mendekatkan objek (2)
    elif key == 's':
        translate_z -= 0.2  # Menjauhkan objek (2)
    glutPostRedisplay()

# Fungsi utama untuk inisialisasi dan menjalankan aplikasi
def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(800, 600)
    glutCreateWindow(b"Grafika 3D - PyOpenGL (Modul B)")
    init()
    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutMouseFunc(mouse)
    glutMotionFunc(motion)
    glutKeyboardFunc(keyboard)
    glutMainLoop()

if __name__ == '__main__':
    main()