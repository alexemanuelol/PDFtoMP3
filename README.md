# PDFtoMP3
Converts a .pdf file to a .mp3 file. Basically identifies text within the .pdf file and using Text to Speech (TTS) library to export it into a .mp3 file.

## Clone and setup
To clone the repository:
	$ git clone https://github.com/alexemanuelol/PDFtoMP3.git

Install the required packages:
``` bash
$ cd pdftomp3
$ pip install -r requirements.txt
```

## Basic Usage
``` bash
$ py pdftomp3.py sample.pdf -f 1-3 5
```

Explanation:
**-f 1-3 5** : Ignore the text from pages 1 to 3 and 5. 
