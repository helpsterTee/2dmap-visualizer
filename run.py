import sys, time
import pygame
import csv
import math
import random

# defines
DEBUG = True
MAXRES = [800,800]
BACKGROUND_COLOR = (255,255,255)
MARKER_COLORS = [(0,0,0),(255,20,0)]
PADDING_FAC = 300

# vars
game_display = 0
clock = 0
csv_data = []
csv_data_pointers = []
circles = {}
arcs = {}
images = []
max_x = max_y = max_t = -65535.0
min_x = min_y = min_t = 65535.0
res_x = res_y = 0
origin_x = origin_y = 0
scale = 1

# reads one csv file
def read_csv(filename):
    global csv_data, MARKER_COLORS

    with open(filename) as f:
        reader = csv.reader(f)
        data = list(reader)
        # remove heading line
        del data[0]
        csv_data.append([filename, data])
        csv_data_pointers.append(0)
        #MARKER_COLORS.append((random.randint(0,255),random.randint(0,255),random.randint(0,255)))

# reads multiple csv files
def read_csvs(filenames):
    for filename in filenames:
        read_csv(filename)

def read_pngs(filenames):
    global images
    for filename in filenames:
        image = pygame.image.load(filename)
        images.append(image)

# finds dimensions
def calculate_dimensions():
    global csv_data, DEBUG, max_x, max_y, min_x, min_y, max_t, min_t, res_x, res_y, origin_x, origin_y
    for data in csv_data:
        for row in data[1]:
            #print(row)
            # time
            if float(row[0]) < min_t:
                min_t = float(row[0])
            if float(row[0]) > max_t:
                max_t = float(row[0])
            if float(row[1]) < min_x:
                min_x = float(row[1])
            if float(row[1]) > max_x:
                max_x = float(row[1])
            if float(row[2]) < min_y:
                min_y = float(row[2])
            if float(row[2]) > max_y:
                max_y = float(row[2])

    # padding
    max_x += PADDING_FAC
    max_y += PADDING_FAC
    min_x -= PADDING_FAC
    min_y -= PADDING_FAC

    # game window resolution
    res_x = max_x - min_x
    res_y = max_y - min_y

    # scaling
    if res_x > MAXRES[0] or res_y > MAXRES[1]:
        global scale
        if res_x > res_y:
            scale = res_x / MAXRES[0]
        else:
            scale = res_y / MAXRES[1]
        res_x = math.floor(res_x / scale)
        res_y = math.floor(res_y / scale)

    # translate origin
    if origin_x < 0:
        origin_x = min_x / scale
    else:
        origin_x = -min_x / scale
    if origin_y < 0:
        origin_y = min_y / scale
    else:
        origin_y = -min_y / scale

    if DEBUG:
        print("Found dimension of data:")
        print("\tSeconds:["+str(min_t)+", "+str(max_t)+"]")
        print("\tx:\t["+str(min_x)+", "+str(max_x)+"]")
        print("\ty:\t["+str(min_y)+", "+str(max_y)+"]\n")
        print("\tOrigin x:\t["+str(origin_x)+", Origin y: "+str(origin_y)+"]\n")
        print("\tScale factor for resolution: "+str(scale))
        print("\tGame resolution: "+str(res_x)+", "+str(res_y))

def update_markers(timediff):
    global csv_data_pointers, circles

    for image in images:
        rect = image.get_rect()
        #image = image.convert()
        game_display.blit(image, rect)

    for idx, data in enumerate(csv_data):
        if csv_data_pointers[idx] < len(data[1]):
            if float(data[1][csv_data_pointers[idx]][0]) < timediff:
                scaled_x = float(data[1][csv_data_pointers[idx]][1]) / scale
                scaled_y = float(data[1][csv_data_pointers[idx]][2]) / scale
                print(str(scaled_x)+", "+str(scaled_y))
                circles[idx] = (int(origin_x) + int(scaled_x), int(origin_y) + int(scaled_y))
                if len(data[1][csv_data_pointers[idx]]) == 5:
                    arcs[idx] = float(data[1][csv_data_pointers[idx]][4])
                csv_data_pointers[idx] += 1

    for key in circles.keys():
        circle = circles[key]
        game_display.lock()
        pygame.draw.circle(game_display, MARKER_COLORS[key], circle, 5, 2)
        if key in arcs.keys():
            arc = arcs[key]
            rect = (circle[0]-40, circle[1]-40, 80, 80)
            #pygame.draw.rect(game_display, MARKER_COLOR, rect, 1)
            pygame.draw.arc(game_display, MARKER_COLORS[key], rect, math.radians(-arc-45), math.radians(-arc+45), 1)
            line_a_x = math.cos(math.radians(arc-45)) * 40 + circle[0];
            line_a_y = math.sin(math.radians(arc-45)) * 40 + circle[1];
            line_b_x = math.cos(math.radians(arc+45)) * 40 + circle[0];
            line_b_y = math.sin(math.radians(arc+45)) * 40 + circle[1];
            pygame.draw.line(game_display, MARKER_COLORS[key], (line_a_x, line_a_y), circle, 1)
            pygame.draw.line(game_display, MARKER_COLORS[key], (line_b_x, line_b_y), circle, 1)
        else:
            # circle radius for everyone else
            pygame.draw.circle(game_display, MARKER_COLORS[key], circle, 50, 1)
        game_display.unlock()

# check if all data was parsed
def markers_finished():
    count = 0
    for idx, pointer in enumerate(csv_data_pointers):
        if pointer == len(csv_data[idx][1]):
            count += 1
    if count == len(csv_data):
        return True
    else:
        return False


# initialize pygame with custom resolution, determined by x,y csv coordinates
def init_pygame(xres, yres):
    global game_display, clock
    pygame.init()
    game_display = pygame.display.set_mode((int(xres), int(yres)))
    pygame.display.set_caption('2DMap Visualizer')
    game_display.fill(BACKGROUND_COLOR)
    clock = pygame.time.Clock()

def pygame_mainloop():
    global clock

    crashed = False

    # time measurement
    start_time = time.time() - min_t

    while not crashed:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                crashed = True
        current_time = time.time()
        elapsed_time = current_time - start_time

        if not markers_finished():
            game_display.fill((255,255,255))
            #print(elapsed_time)
            update_markers(elapsed_time)
            pygame.display.flip()
            clock.tick(60)
        else:
            print("Finished processing")
            pygame.display.flip()
            clock.tick(1)

# error messages
def msg_err_csv():
    print("Error: \tPlease supply at least one CSV file as parameter. You may mix png files for backgrounds and csv files for positions.")
    print("\tE.g.: python3 run.py a.csv b.csv bg.png")

# main
if len(sys.argv) > 1:
    # iterate over parameters to get all csv files
    csv_files = []
    png_files = []

    for arg in sys.argv:
        if arg.split('.')[1] == 'csv':
            csv_files.append(arg)
        elif arg.split('.')[1] == 'png':
            png_files.append(arg)

    print(csv_files)
    print(png_files)

    if len(csv_files) > 0:
        #ready here, let's do some parsing
        read_csvs(csv_files)
        read_pngs(png_files)
        calculate_dimensions()
        input("Press Enter to continue...")
        init_pygame(res_x,res_y)
        pygame_mainloop()
        # quit, then
        #pygame.quit()
    else:
        msg_err_csv()
else:
    msg_err_csv()

quit()
