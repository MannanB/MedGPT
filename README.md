# MedGPT

An AI medical advisor.

To use it, follow these steps:

1. Download the zip and unzip it
2. Due to copywrite, you need to buy the medical text book as an EBook in amazon at https://www.amazon.com/Handbook-Symptoms-Lippincott-Williams-Wilkiins-ebook/dp/B00SBRHU02/ref=tmm_kin_swatch_0?_encoding=UTF8&qid=1683166921&sr=1-1
3. Download the ebook from amazon and convert it to a pdf following these directions: https://www.softwaretestinghelp.com/convert-kindle-to-pdf/
4. Download the medical forumn data from https://drive.google.com/drive/folders/1g29ssimdZ6JzTST6Y8g6h-ogUNReBtJD
5. Create a new folder called "raw_data" in the extracted zip and add all of the downloaded data to it
6. Start the api. You must install FastAPI, openai, tiktoken, nltk, fitz, chroma, streamlit and uvicorn with pip. Then go into terminal and run uvicorn api:app
7. When prompted with if you want to re-generate the data, press enter
8. Run the frontend with streamlit run frontend.py
