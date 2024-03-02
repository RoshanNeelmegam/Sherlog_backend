import os
import subprocess
import sys

directory_path = sys.argv[1]
sw_command = sys.argv[2]
current_script_dir = os.path.dirname(os.path.realpath(__file__))
filenames = sorted(os.listdir(directory_path), key=lambda x: os.path.getmtime(os.path.join(directory_path, x)), reverse=False)
for filename in filenames:
    try:
        file_path = os.path.join(directory_path, filename)
        main_script_path = os.path.join(current_script_dir, "Main.py")
        command = f"python3 {main_script_path} {file_path} '{sw_command}'"
        print(filename)
        result = subprocess.run(command, shell=True, stdout=subprocess.PIPE, text=True)
        print(result.stdout)
        print('*'*20+'\n')
    except KeyboardInterrupt as e:
        print("Aborting command")
        sys.exit()


