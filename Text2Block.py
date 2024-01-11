import os
from PIL import Image
import sys
from func_timeout import func_set_timeout, FunctionTimedOut
import msvcrt
from tqdm import tqdm

VERSION = "v1.0"
print("Text2Block |", VERSION)
print("Program By HShiDianLu. (2024.1)")

file = ''


@func_set_timeout(0.1)
def get_input_file(pre_str=''):
    global file
    file = pre_str
    while True:
        file += msvcrt.getwch()


print()
if len(sys.argv) != 2:
    print("Drag a file to start.")
    first_chr = msvcrt.getwch()
    try:
        get_input_file(first_chr)
    except FunctionTimedOut:
        print("Read file:", file)
else:
    print("Read file:", sys.argv[1])
    file = sys.argv[1]

if not file.endswith(".png"):
    print("File format error. Please use .png file for generation.")
    os.system("pause")
    sys.exit()
print()

print("Opening file...", end=" ")
img_src = Image.open(file)
img_src = img_src.convert('RGBA')
src_RGBAlist = img_src.load()
src_list = []
src_alphalist = []
height = img_src.height
width = img_src.width
print("[DONE]")
print("Fetched file data:", width, "x", height, "->", int(width / 2), "x", int(height / 2))
print()

# 预处理
print("Converting to GRAY...")
for i in tqdm(range(width), desc="Processing",
              bar_format="{l_bar}{bar}| Elapsed {elapsed} | ETA {remaining} | {rate_fmt}{postfix}"):
    src_list.append([])
    src_alphalist.append([])
    for j in range(height):
        g = 0
        if src_RGBAlist[i, j][3] == 255:
            g = 255
        src_list[i].append(g)
        src_alphalist[i].append(src_RGBAlist[i, j][3])
tmp = []
output = [[]]
posX = 0
print()

# 划分2x2 进行方块判定
print("Generating...")
for i in tqdm(range(width - 1), desc="Processing",
              bar_format="{l_bar}{bar}| Elapsed {elapsed} | ETA {remaining} | {rate_fmt}{postfix}"):
    for j in range(height - 1):
        if i % 2 == 0 and j % 2 == 0:
            tmp = [[src_list[i][j], src_list[i + 1][j]], [src_list[i][j + 1], src_list[i + 1][j + 1]]]
            tmpAlpha = [[src_alphalist[i][j], src_alphalist[i + 1][j]],
                        [src_alphalist[i][j + 1], src_alphalist[i + 1][j + 1]]]
            if tmp == [[0, 0], [0, 0]]:  # Air
                output[posX].append("-")
            elif tmp == [[0, 0], [0, 255]] or tmp == [[0, 255], [255, 255]]:  # Q_rb
                output[posX].append("quartz_stairs 0")
            elif tmp == [[0, 0], [255, 0]] or tmp == [[255, 0], [255, 255]]:  # Q_lb
                output[posX].append("quartz_stairs 1")
            elif tmp == [[255, 0], [0, 0]] or tmp == [[255, 255], [255, 0]]:  # Q_lt
                output[posX].append("quartz_stairs 5")
            elif tmp == [[0, 255], [0, 0]] or tmp == [[255, 255], [0, 255]]:  # Q_rt
                output[posX].append("quartz_stairs 4")
            elif tmp == [[255, 255], [0, 0]]:  # Q_t
                output[posX].append("stone_slab 15")
            elif tmp == [[0, 0], [255, 255]]:  # Q_b
                output[posX].append("stone_slab 7")

            # It seems that they almost have no effect
            elif tmpAlpha[0][0] == 255 and tmpAlpha[1][0] == 255:
                if tmpAlpha[0][1] != 0 and tmpAlpha[1][1] == 0:  # Q_lt
                    output[posX].append("quartz_stairs 5")
                elif tmpAlpha[0][1] == 0 and tmpAlpha[1][1] != 0:  # Q_lb
                    output[posX].append("quartz_stairs 1")
                else:  # Q_full
                    output[posX].append("quartz_block")
            elif tmpAlpha[0][1] == 255 and tmpAlpha[1][1] == 255:
                if tmpAlpha[0][0] != 0 and tmpAlpha[1][0] == 0:  # Q_rt
                    output[posX].append("quartz_stairs 5")
                elif tmpAlpha[0][0] == 0 and tmpAlpha[1][0] != 0:  # Q_rb
                    output[posX].append("quartz_stairs 0")
                else:  # Q_full
                    output[posX].append("quartz_block")
            else:  # Q_full
                output[posX].append("quartz_block")
    if i % 2 == 0:
        output.append([])
        posX += 1
print()

# 保存
print("Saving...")
f = open(file + ".mcfunction", "w", encoding="utf-8")
f.write('tellraw @a {"text":"§aGenerating Text..."}\n')
for i in tqdm(range(int(width / 2)), desc="Processing",
              bar_format="{l_bar}{bar}| Elapsed {elapsed} | ETA {remaining} | {rate_fmt}{postfix}"):
    for j in range(int(height / 2)):
        # x+ y+ z=
        if output[i][j] == "-":
            continue
        # print("setblock ~" + str(i) + " ~-" + str(j) + " ~ " + output[i][j])
        f.write("setblock ~" + str(i) + " ~-" + str(j) + " ~ " + output[i][j] + "\n")
        # f.write('title @a actionbar "§eGenerating §b(' + str(i) + ',' + str(j) + ')"\n')
f.write('tellraw @a {"text":"§aGenerated!"}\n')
f.write('tellraw @a {"text":"§eMade by §bText2Block"}\n')
f.close()
print("File generated.")
print("Saved to", file + ".mcfunction")
os.system("pause")
