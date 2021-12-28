# MythOS v1.0.0
MythOS is the successor to Rune OS (https://github.com/IY314/Rune-OS), created
by the same team. It focuses on an entirely new user experience that is way more
intuitive and interactive, while keeping the text-based aspects of the system.

## Credits
All credits go to the original Rune OS team (@IY314, @mrfoogles). Myth OS, 
however, is solely created by @IY314.

## Installation
### Prerequisites
- Git
- Python 3.8 or newer
- A 24-bit terminal

To install from the command-line, run this in a terminal:
```shell
git clone https://github.com/IY314/MythOS.git
cd MythOS
make install

# On Windows
env/Scripts/activate.bat

# On Linux and Mac
source venv/bin/activate

# At this point, make sure that the virtual environment
# is set up correctly by doing this
# The output should be in <directory>/MythOS/venv/bin/pip
# If not, reconfigure your virtual environment
which pip

pip install -r requirements.txt
python src/mythos.py
```
