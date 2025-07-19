from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from math import cos, sin, pi, radians

window_width, window_height = 800, 600
shapes = []
current_shape = {'type': 'point', 'coords': [], 'color': (1.0, 0.0, 0.0), 'thickness': 2.0}
window_rect = [100, 100, 500, 400]
window_click_mode = False
window_clicks = []

INSIDE, LEFT, RIGHT, BOTTOM, TOP = 0, 1, 2, 4, 8

def compute_out_code(x, y):
   xmin, ymin, xmax, ymax = window_rect
   code = INSIDE
   if x < xmin: code |= LEFT
   elif x > xmax: code |= RIGHT
   if y < ymin: code |= BOTTOM
   elif y > ymax: code |= TOP
   return code

# Algoritma Cohen-Sutherland untuk clipping
def cohen_sutherland_clip(x0, y0, x1, y1):
   xmin, ymin, xmax, ymax = window_rect
   outcode0 = compute_out_code(x0, y0)
   outcode1 = compute_out_code(x1, y1)
   accept = False

   while True:
       if not (outcode0 | outcode1):
           accept = True
           break
       elif outcode0 & outcode1:
           break
       else:
           x, y = 0.0, 0.0
           outcode_out = outcode0 if outcode0 else outcode1

           # Menghitung titik potong dengan batas window
           if outcode_out & TOP:
               x = x0 + (x1 - x0) * (ymax - y0) / (y1 - y0)
               y = ymax
           elif outcode_out & BOTTOM:
               x = x0 + (x1 - x0) * (ymin - y0) / (y1 - y0)
               y = ymin
           elif outcode_out & RIGHT:
               y = y0 + (y1 - y0) * (xmax - x0) / (x1 - x0)
               x = xmax
           elif outcode_out & LEFT:
               y = y0 + (y1 - y0) * (xmin - x0) / (x1 - x0)
               x = xmin

           if outcode_out == outcode0:
               x0, y0 = x, y
               outcode0 = compute_out_code(x0, y0)
           else:
               x1, y1 = x, y
               outcode1 = compute_out_code(x1, y1)

   if accept:
       return [(x0, y0), (x1, y1)]
   else:
       return None

# Menggambar semua objek (titik, garis, persegi, elips)
def draw_shapes():
   for shape in shapes:
       shape_type = shape['type']
       glLineWidth(shape['thickness'])  # Mengatur ketebalan garis (2b)

       if shape_type == 'point':  # Menggambar titik (1a)
           x, y = shape['coords'][0]
           if compute_out_code(x, y) == INSIDE:  # Warna asli jika di dalam window (4a)
               glColor3f(*shape['color'])
           else:  # Warna abu-abu jika di luar window (4b)
               glColor3f(0.5, 0.5, 0.5)
           glPointSize(shape['thickness'] * 2)
           glBegin(GL_POINTS)
           glVertex2f(x, y)
           glEnd()
           glPointSize(1.0)

       elif shape_type == 'line':  # Menggambar garis (1b)
           x0, y0 = shape['coords'][0]
           x1, y1 = shape['coords'][1]
           clipped = cohen_sutherland_clip(x0, y0, x1, y1)  # Clipping garis (4b)

           if clipped:  # Menggambar bagian garis di dalam window
               glColor3f(*shape['color'])
               glBegin(GL_LINES)
               glVertex2f(*clipped[0])
               glVertex2f(*clipped[1])
               glEnd()

           if clipped != [(x0, y0), (x1, y1)]:  # Menggambar bagian luar window dengan abu-abu
               glColor3f(0.5, 0.5, 0.5)  # Warna abu-abu (4b)
               glBegin(GL_LINES)
               if clipped:
                   cx0, cy0 = clipped[0]
                   cx1, cy1 = clipped[1]
                   if (x0, y0) != (cx0, cy0):
                       glVertex2f(x0, y0)
                       glVertex2f(cx0, cy0)
                   if (x1, y1) != (cx1, cy1):
                       glVertex2f(x1, y1)
                       glVertex2f(cx1, cy1)
               else:
                   glVertex2f(x0, y0)
                   glVertex2f(x1, y1)
               glEnd()

       elif shape_type == 'rectangle':  # Menggambar persegi (1c)
           x0, y0 = shape['coords'][0]
           x1, y1 = shape['coords'][1]
           corners = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
           if all(compute_out_code(x, y) == INSIDE for x, y in corners):  # Warna asli jika di dalam window (4a)
               glColor3f(*shape['color'])
           else:  # Warna abu-abu jika di luar window (4b)
               glColor3f(0.5, 0.5, 0.5)
           glBegin(GL_LINE_LOOP)
           glVertex2f(x0, y0)
           glVertex2f(x1, y0)
           glVertex2f(x1, y1)
           glVertex2f(x0, y1)
           glEnd()

       elif shape_type == 'ellipse':  # Menggambar elips (1d)
           x0, y0 = shape['coords'][0]
           x1, y1 = shape['coords'][1]
           rx = abs(x1 - x0) / 2
           ry = abs(y1 - y0) / 2
           cx = (x0 + x1) / 2
           cy = (y0 + y1) / 2
           if compute_out_code(cx, cy) == INSIDE:  # Warna asli jika pusat di dalam window (4a)
               glColor3f(*shape['color'])
           else:  # Warna abu-abu jika pusat di luar window (4b)
               glColor3f(0.5, 0.5, 0.5)
           glBegin(GL_LINE_LOOP)
           for angle in range(360):
               theta = angle * pi / 180
               glVertex2f(cx + rx * cos(theta), cy + ry * sin(theta))
           glEnd()

# Menggambar window aktif
def draw_window():
   glColor3f(0, 0, 0)  # Warna hitam untuk window
   glLineWidth(3)
   glBegin(GL_LINE_LOOP)
   glVertex2f(window_rect[0], window_rect[1])
   glVertex2f(window_rect[2], window_rect[1])
   glVertex2f(window_rect[2], window_rect[3])
   glVertex2f(window_rect[0], window_rect[3])
   glEnd()
   glLineWidth(1)

# Menggeser window (4: Window dapat digeser)
def translate_window(dx, dy):
   window_rect[0] += dx
   window_rect[1] += dy
   window_rect[2] += dx
   window_rect[3] += dy

# Transformasi translasi untuk objek (3a)
def apply_translation(shape, dx, dy):
   shape['coords'] = [(x + dx, y + dy) for (x, y) in shape['coords']]

# Transformasi scaling untuk objek (3c)
def apply_scaling(shape, scale):
   cx = sum(x for x, _ in shape['coords']) / len(shape['coords'])
   cy = sum(y for _, y in shape['coords']) / len(shape['coords'])
   shape['coords'] = [((x - cx) * scale + cx, (y - cy) * scale + cy) for (x, y) in shape['coords']]

# Transformasi rotasi untuk objek (3b)
def apply_rotation(shape, angle_deg):
   angle_rad = radians(angle_deg)
   cx = sum(x for x, _ in shape['coords']) / len(shape['coords'])
   cy = sum(y for _, y in shape['coords']) / len(shape['coords'])
   new_coords = []
   for x, y in shape['coords']:
       x_shift, y_shift = x - cx, y - cy
       x_rot = x_shift * cos(angle_rad) - y_shift * sin(angle_rad)
       y_rot = x_shift * sin(angle_rad) + y_shift * cos(angle_rad)
       new_coords.append((x_rot + cx, y_rot + cy))
   shape['coords'] = new_coords

# Fungsi display untuk merender semua objek dan window
def display():
   glClear(GL_COLOR_BUFFER_BIT)
   draw_window()
   draw_shapes()
   glutSwapBuffers()

# Menangani input klik mouse untuk koordinat objek atau window (1: Input koordinat)
def mouse_click(button, state, x, y):
   global window_rect, window_clicks
   y = window_height - y
   if state == GLUT_DOWN:
       if window_click_mode:  # Mode untuk menentukan window (4)
           window_clicks.append((x, y))
           if len(window_clicks) == 2:  # Dua klik untuk menentukan window
               x0, y0 = window_clicks[0]
               x1, y1 = window_clicks[1]
               window_rect[:] = [min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)]
               window_clicks.clear()
       else:  # Mode untuk menentukan koordinat objek
           current_shape['coords'].append((x, y))
           if current_shape['type'] == 'point' or len(current_shape['coords']) == 2:
               shapes.append(current_shape.copy())
               current_shape['coords'] = []
   glutPostRedisplay()

# Menangani input keyboard untuk memilih objek, warna, ketebalan, transformasi, dan window
def keyboard(key, x, y):
   global current_shape, window_click_mode
   try:
       key_str = key.decode('utf-8')
   except:
       key_str = key
   if key_str == '1':
       current_shape['type'] = 'point'  # Pilih titik (1a)
       window_click_mode = False
   elif key_str == '2':
       current_shape['type'] = 'line'  # Pilih garis (1b)
       window_click_mode = False
   elif key_str == '3':
       current_shape['type'] = 'rectangle'  # Pilih persegi (1c)
       window_click_mode = False
   elif key_str == '4':
       current_shape['type'] = 'ellipse'  # Pilih elips (1d)
       window_click_mode = False
   elif key_str == 'r':
       current_shape['color'] = (1, 0,0)  # Warna merah (2a)
   elif key_str == 'g':
       current_shape['color'] = (0, 1, 0)  # Warna hijau (2a)
   elif key_str == 'b':
       current_shape['color'] = (0, 0, 1)  # Warna biru (2a)
   elif key_str == '+':
       current_shape['thickness'] += 1  # Tambah ketebalan (2b)
   elif key_str == '-':
       current_shape['thickness'] = max(1, current_shape['thickness'] - 1)  # Kurangi ketebalan (2b)
   elif key_str == 'w':
       if shapes: apply_translation(shapes[-1], 0, 10)  # Translasi ke atas (3a)
   elif key_str == 's':
       if shapes: apply_translation(shapes[-1], 0, -10)  # Translasi ke bawah (3a)
   elif key_str == 'a':
       if shapes: apply_translation(shapes[-1], -10, 0)  # Translasi ke kiri (3a)
   elif key_str == 'd':
       if shapes: apply_translation(shapes[-1], 10, 0)  # Translasi ke kanan (3a)
   elif key_str == 'q':
       if shapes: apply_rotation(shapes[-1], 10)  # Rotasi searah jarum jam (3b)
   elif key_str == 'e':
       if shapes: apply_rotation(shapes[-1], -10)  # Rotasi berlawanan jarum jam (3b)
   elif key_str == 'z':
       if shapes: apply_scaling(shapes[-1], 0.9)  # Skala mengecil (3c)
   elif key_str == 'x':
       if shapes: apply_scaling(shapes[-1], 1.1)  # Skala membesar (3c)
   elif key_str == 'c':
       window_click_mode = True  # Aktifkan mode window (4)
   elif key_str == GLUT_KEY_UP:
       translate_window(0, 10)  # Geser window ke atas (4)
   elif key_str == GLUT_KEY_DOWN:
       translate_window(0, -10)  # Geser window ke bawah (4)
   elif key_str == GLUT_KEY_LEFT:
       translate_window(-10, 0)  # Geser window ke kiri (4)
   elif key_str == GLUT_KEY_RIGHT:
       translate_window(10, 0)  # Geser window ke kanan (4)

   glutPostRedisplay()

def main():
   glutInit()
   glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
   glutInitWindowSize(window_width, window_height)  # Ukuran jendela
   glutCreateWindow(b"Grafika 2D - PyOpenGL (Window Interaktif)")
   glutDisplayFunc(display)
   glutMouseFunc(mouse_click)  # Set fungsi penanganan klik mouse
   glutKeyboardFunc(keyboard)  # Set fungsi penanganan keyboard
   glutSpecialFunc(keyboard)  # Set fungsi penanganan tombol khusus (misalnya panah)
   glClearColor(1, 1, 1, 1)  # Warna latar belakang putih
   gluOrtho2D(0, window_width, 0, window_height)
   glutMainLoop()

if __name__ == '__main__':
   main()
