import subprocess

def install_dependencies():
    subprocess.check_call(['pip', 'install', '-r', 'requirements.txt'])
    print("Installation finished")
    input()

install_dependencies()