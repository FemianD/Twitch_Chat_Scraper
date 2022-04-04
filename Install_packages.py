import subprocess
import sys

def install(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install('selenium')
install('tabulate')
install('webdriver-manager')