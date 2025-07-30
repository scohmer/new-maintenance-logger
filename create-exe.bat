python -m venv venv
.\venv\Scripts\activate.bat
# run this: pip install --no-index --find-links=.\client-depends -r .\client-requirements.txt
# customize .env file
# run this: pyinstaller -F --add-data=".env;." .\client.py

# FOR SERVER
# python -m venv .venv
# source .venv\bin\activate
# pip install --no-index --find-links=.\server-depends\ -r .\server-requirements.txt
# create a systemd unit:
# TBD
