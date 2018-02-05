import csv
import os.path
import random

def write_csv_head(writer):
    writer.writerow(['seconds','x','y'])

def fill_files():
    # generate two separate csv test files
    a = []
    b = []

    # ms counter
    a_ms = 0
    b_ms = 0

    # coordinates
    a_pos = [20,20]
    b_pos = [400,200]

    a_angle = 0
    angle_dir = 1

    for i in range(0,60):
        # use dotted seconds format
        a_ms += random.uniform(0,1)
        b_ms += random.uniform(0,1)

        # use float position
        a_pos = [a_pos[0]+random.uniform(0.1,5),a_pos[1]+random.uniform(0.1,5)]
        b_pos = [b_pos[0]+random.uniform(-0.1,-5),b_pos[1]+random.uniform(-0.1,-5)]

        if a_angle == 30:
            angle_dir = -1
        elif a_angle == 0:
            angle_dir = 1

        a_angle += angle_dir

        #write to out array
        a.append([a_ms, a_pos[0], a_pos[1], a_angle])
        b.append([b_ms, b_pos[0], b_pos[1]])

    with open('a.csv', 'w') as f:
        writer = csv.writer(f)
        write_csv_head(writer)
        writer.writerows(a)
    with open('b.csv', 'w') as f:
        writer = csv.writer(f)
        write_csv_head(writer)
        writer.writerows(b)


# main
print('Generating CSV files')
fill_files()
print('Generation complete')
