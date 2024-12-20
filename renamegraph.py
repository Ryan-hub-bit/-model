import shutil
import os
import random

# def copy_and_rename(src_path, dest_path, index):
#     # Copy the file

#     # Rename the copied file
#     #old_name = src_path.split("/")[-1]
#     num = int(src_path.split("/")[-1].split(".")[0])
#     new_name = str(num + index) + "." + src_path.split("/")[-1].split(".")[1]
#     new_path = f"{dest_path}/{new_name}"
#     print(new_path)
#     # shutil.move(f"{dest_path}/{old_name}", new_path)
#     shutil.copy2(src_path, new_path)
#     return new_path

# Example usage
source_folder = "/home/isec/Documents/differentopdata/Reorganized_Dataset/graph_dir_90"
destination_folder = "/home/isec/Documents/differentopdata/Reorganized_Dataset/graph_dir_90_random"
numbers = list(range(0, 1531))
random.shuffle(numbers)
print(numbers)
j = 0
for i in numbers:
    func_path = os.path.join(source_folder, str(i) + ".funcaddr")
    graph_path = os.path.join(source_folder, str(i) + ".graph")
    pe_path = os.path.join(source_folder, str(i) + ".graphpe")
    if os.path.exists(func_path):
        new_func_path = os.path.join(destination_folder, str(j) + ".funcaddr")
        shutil.move(func_path, new_func_path)
    if os.path.exists(graph_path):
        new_graph_path = os.path.join(destination_folder, str(j) + ".graph")
        shutil.move(graph_path, new_graph_path)
    if os.path.exists(pe_path):
        new_pe_path = os.path.join(destination_folder, str(j) + ".graphpe")
        shutil.move(pe_path, new_pe_path)
    j += 1
    print(f"{func_path} -> {new_func_path}")


# for root, dirs, files in os.walk(source_folder):
#     for file in files:
#         abpath = os.path.join(root, file)
#         new_file_path = copy_and_rename(abpath, destination_folder, numbers)