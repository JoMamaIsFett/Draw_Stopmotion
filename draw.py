import pygame
import sys
import time
import os
import numpy as np
import cv2

pygame.init()
screen = pygame.display.set_mode((800, 800))
pygame.display.set_caption("draw")

mouse_old = (0, 0)
mouse_new = (0, 0)
mouse_trigger = False
draw_trigger = True

try:
    frame_list = np.load("frame_data.npy", allow_pickle=True).tolist()
except FileNotFoundError:
    frame_list = [[]]
current_frame = 0

current_color = (0, 0, 0)
BACKGROUND_COLOR = (245, 255, 252)

thickness = 3

gui_lines = [((0, 42), (800, 42)), ((82, 0), (82, 40)), ((758, 0), (758, 40)), ((674, 0), (674, 40)),
             ((630, 0), (630, 40)), ((546, 0), (546, 40)),
             ((5, 5), (5, 35)), ((5, 5), (35, 5)), ((5, 35), (35, 35)), ((35, 5), (35, 35)), ((10, 10), (30, 20)),
             ((10, 30), (30, 20)), ((10, 10), (10, 30)),
             ((45, 5), (45, 35)), ((45, 5), (75, 5)), ((45, 35), (75, 35)), ((75, 5), (75, 35)), ((65, 5), (65, 15)),
             ((55, 5), (55, 15)), ((55, 15), (65, 15)),
             ((786, 35), (774, 35)), ((786, 35), (795, 10)), ((774, 35), (765, 10)), ((765, 10), (780, 5)),
             ((795, 10), (780, 5)), ((765, 10), (780, 15)), ((795, 10), (780, 15)), ((778, 35), (774, 15)),
             ((782, 35), (786, 15)),
             ((751, 20), (736, 5)), ((751, 20), (736, 35)), ((736, 15), (736, 5)), ((736, 25), (736, 35)),
             ((736, 25), (721, 25)), ((736, 15), (721, 15)), ((721, 15), (721, 25)),
             ((711, 15), (711, 25)), ((711, 25), (696, 25)), ((711, 15), (696, 15)), ((696, 15), (696, 5)),
             ((696, 25), (696, 35)), ((681, 20), (696, 35)), ((681, 20), (696, 5)),
             ((667, 20), (637, 5)), ((667, 20), (637, 35)), ((637, 35), (637, 5)),
             ((608, 35), (608, 5)), ((593, 20), (623, 20)),
             ((553, 20), (583, 20))]
gui_collider = [pygame.Rect(0, 0, 40, 40), pygame.Rect(40, 0, 40, 40), pygame.Rect(758, 0, 40, 40),
                pygame.Rect(717, 0, 40, 40), pygame.Rect(674, 0, 40, 40), pygame.Rect(630, 0, 40, 40),
                pygame.Rect(546, 0, 40, 40), pygame.Rect(586, 0, 40, 40)]

color_list = [(0, 0, 0), (136, 0, 21), (237, 28, 36), (255, 127, 39), (255, 201, 14), (255, 242, 0), (181, 230, 29),
              (34, 177, 76), (0, 162, 232), (63, 72, 204), (163, 73, 164)]
color_rect_list = [pygame.Rect(100, 5, 30, 30), pygame.Rect(140, 5, 30, 30), pygame.Rect(180, 5, 30, 30),
                   pygame.Rect(220, 5, 30, 30), pygame.Rect(260, 5, 30, 30), pygame.Rect(300, 5, 30, 30),
                   pygame.Rect(340, 5, 30, 30), pygame.Rect(380, 5, 30, 30), pygame.Rect(420, 5, 30, 30),
                   pygame.Rect(460, 5, 30, 30), pygame.Rect(500, 5, 30, 30)]

selection_list = []
selected = False
render_selection = False
setting_selection = False
start_selection = (0, 0)
real_selection = (0, 0)
selection_size = (0, 0)


def render():
    screen.fill(BACKGROUND_COLOR)
    render_gui()
    if render_selection:
        x, y = real_selection
        width, height = selection_size
        pygame.draw.rect(screen, (152, 186, 245), pygame.Rect(x, y, width, height))
        pygame.draw.rect(screen, (42, 126, 245), pygame.Rect(x, y, width, height), 3)
    if current_frame != 0:
        for line in frame_list[current_frame - 1]:
            start, end, color, thick = line
            grey = sum(color) / 3 + 150
            if grey > 200:
                grey = 200
            color = (grey, grey, grey)
            pygame.draw.line(screen, color, start, end, thick)
    for line in frame_list[current_frame]:
        start, end, color, thick = line
        pygame.draw.line(screen, color, start, end, thick)
    if render_selection:
        for line in selection_list:
            start, end, color, thick = line
            pygame.draw.line(screen, color, start, end, thick)
    pygame.display.update()


def render_gui():
    for line in gui_lines:
        start, end = line
        pygame.draw.line(screen, (0, 0, 0), start, end, 3)
    for i in range(len(color_rect_list)):
        pygame.draw.rect(screen, color_list[i], color_rect_list[i])


def draw():
    global mouse_new, mouse_old, mouse_trigger, draw_trigger
    pos = pygame.mouse.get_pos()
    if draw_trigger:
        if pygame.mouse.get_pressed(3)[0]:
            if mouse_trigger:
                mouse_new = pos
                frame_list[current_frame].append((mouse_old, mouse_new, current_color, thickness))
            else:
                mouse_trigger = True
        else:
            mouse_trigger = False
    mouse_old = pos


def select():
    global selected
    selection_list.clear()
    x, y = real_selection
    width, height = selection_size
    selection_rect = pygame.Rect(x, y, width, height)
    poplist = []
    for i in range(len(frame_list[current_frame])):
        line = frame_list[current_frame][i]
        line_start, line_end, color, thick = line
        lox, loy = line_start
        rux, ruy = line_start
        if selection_rect.collidepoint(lox, loy) or selection_rect.collidepoint(rux, ruy):
            selection_list.append(frame_list[current_frame][i])
            poplist.insert(0, i)
    for index in poplist:
        frame_list[current_frame].pop(index)
    selected = True


def keypress(key):
    global thickness, current_frame, render_selection, draw_trigger, selected
    if key[pygame.K_KP_PLUS]:
        if not selected:
            thickness += 1
    if key[pygame.K_KP_MINUS]:
        if not selected:
            if thickness >= 2:
                thickness -= 1
    if key[pygame.K_LEFT]:
        if selected:
            move_selection(5, 0)
        else:
            if current_frame > 0:
                current_frame -= 1
    if key[pygame.K_RIGHT]:
        if selected:
            move_selection(-5, 0)
        else:
            current_frame += 1
            if current_frame >= len(frame_list):
                frame_list.append([])
    if key[pygame.K_UP]:
        if selected:
            move_selection(0, 5)
    if key[pygame.K_DOWN]:
        if selected:
            move_selection(0, -5)
    if key[pygame.K_SPACE]:
        if not selected:
            play()
    if key[pygame.K_DELETE]:
        if selected:
            selection_list.clear()
            render_selection = False
            selected = False
            draw_trigger = True
        else:
            delete_frame()
    if key[pygame.K_s]:
        if not selected:
            save()
    if key[pygame.K_c]:
        if selected:
            frame_list[current_frame] += selection_list
            render_selection = False
            selected = False
    if key[pygame.K_v]:
        render_selection = True
        selected = True


def delete_frame():
    global current_frame
    frame_list.pop(current_frame)
    if current_frame >= len(frame_list):
        current_frame -= 1
    if len(frame_list) == 0:
        frame_list.append([])
        current_frame = 0


def gui_handler(pos):
    global draw_trigger, current_frame, thickness, current_color, render_selection, selected
    index = -1
    if not selected:
        for rect in gui_collider:
            if rect.collidepoint(pos):
                index = gui_collider.index(rect)
                draw_trigger = False
        if index == 0:
            render_video()
        elif index == 1:
            save()
        elif index == 2:
            if selected:
                selection_list.clear()
                render_selection = False
                selected = False
                draw_trigger = True
            else:
                delete_frame()
        elif index == 3:
            current_frame += 1
            if current_frame >= len(frame_list):
                frame_list.append([])
        elif index == 4:
            if current_frame > 0:
                current_frame -= 1
        elif index == 5:
            play()
        elif index == 6:
            if thickness >= 2:
                thickness -= 1
        elif index == 7:
            thickness += 1

        for rect in color_rect_list:
            if rect.collidepoint(pos):
                draw_trigger = False
                current_color = color_list[color_rect_list.index(rect)]


def handle_events():
    global draw_trigger, start_selection, setting_selection, render_selection, selected
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN:
            keypress(pygame.key.get_pressed())
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                gui_handler(pygame.mouse.get_pos())
                if selected:
                    selected = False
                    render_selection = False
                    draw_trigger = False
                    frame_list[current_frame] += selection_list
                    selection_list.clear()

            elif event.button == 3:
                start_selection = pygame.mouse.get_pos()
                frame_list[current_frame] += selection_list
                selection_list.clear()
                setting_selection = True
                render_selection = True
        if event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1:
                draw_trigger = True
            elif event.button == 3:
                setting_selection = False
                select()


def selecting():
    global selection_size, real_selection
    x, y = start_selection
    mouse_x, mouse_y = pygame.mouse.get_pos()
    selection_width = mouse_x - x
    selection_height = mouse_y - y

    if selection_width < 0:
        x += selection_width
        selection_width = -selection_width
    if selection_height < 0:
        y += selection_height
        selection_height = -selection_height

    selection_size = (selection_width, selection_height)
    real_selection = (x, y)


def move_selection(x, y):
    global selection_list, real_selection
    for i in range(len(selection_list)):
        start, end, color, thick = selection_list[i]
        sx, sy, = start
        ex, ey, = end
        sx -= x
        ex -= x
        sy -= y
        ey -= y
        start = (sx, sy)
        end = (ex, ey)
        selection_list[i] = (start, end, color, thick)
    sx, sy = real_selection
    sx -= x
    sy -= y
    real_selection = (sx, sy)


def play():
    for frame in frame_list:
        screen.fill(BACKGROUND_COLOR)
        for line in frame:
            start, end, color, thick = line
            pygame.draw.line(screen, color, start, end, thick)
        pygame.display.update()
        time.sleep(0.1)


def save():
    frame_list_np = np.array(frame_list, dtype=object)
    np.save("frame_data.npy", frame_list_np)


def render_video():
    folder_contents = os.listdir("frames")

    for content in folder_contents:
        content_path = os.path.join("frames", content)
        if os.path.isfile(content_path):
            os.remove(content_path)
        elif os.path.isdir(content_path):
            os.rmdir(content_path)

    for frame_number in range(len(frame_list)):
        screen.fill(BACKGROUND_COLOR)
        for line in frame_list[frame_number]:
            start, end, color, thick = line
            pygame.draw.line(screen, color, start, end, thick)
        pygame.display.update()
        pygame.image.save(screen, f"frames/{frame_number + 1}.png")

    images_to_video()


def images_to_video():
    images = [img for img in os.listdir("frames") if img.endswith(".png")]
    images = sorted(images, key=lambda x: int(x.split('.')[0]))

    frame = cv2.imread(os.path.join("frames", images[0]))
    height, width, layers = frame.shape

    video = cv2.VideoWriter("video.mp4", cv2.VideoWriter_fourcc(*"mp4v"), 10, (width, height))

    for image in images:
        video.write(cv2.imread(os.path.join("frames", image)))

    cv2.destroyAllWindows()
    video.release()


while True:
    handle_events()
    draw()
    render()
    if setting_selection:
        selecting()
