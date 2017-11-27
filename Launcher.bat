ECHO OFF 

python get-pip.py
pip install beautifulsoup4

ECHO Pip and BS4 installed... trying to run program..

python myscraper.py
