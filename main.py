from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
from crontab import CronTab

import os
from image_processing.image_processor import ImageProcessor
from instagram_uploader.uploader import InstagramUploader
from image_processing.excel_processor import ExcelProcessor
import pandas as pd  # Make sure to have pandas installed (you can install it with 'pip install pandas')


ALLOWED_EXTENSIONS = {'.xlsx', '.xls'}
UPLOAD_DIR = Path() / 'uploads'


OUTPUT_PREFIX = "output"
CREDENTIAL_FILE = "credentials.txt"
DIR_PATH = os.path.abspath(os.path.dirname(__file__))


app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def main():
    content = """
<body>
<form action="/uploadfile/" enctype="multipart/form-data" method="post">
<input name="file_upload" type="file"
 accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel" 
>
<input type="submit">
</form>
</body>
    """
    return HTMLResponse(content=content)


@app.post("/uploadfile/")
async def create_upload_file(file_upload: UploadFile):
     # Check if file has allowed extension
    ext = Path(file_upload.filename).suffix
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only Excel files (.xlsx, .xls) are allowed.")

    data = await file_upload.read()
    save_to = UPLOAD_DIR / file_upload.filename
    
    # Save the uploaded file
    with open(save_to, 'wb') as f:
        f.write(data)


    # Append the content of the uploaded file to another Excel file
    try:

        # # Check if the master Excel file exists, create it if not
        if not os.path.exists(ExcelProcessor.master_excel_file):
            ExcelProcessor.initialize_master_excel_file()

        append_to_master_file(save_to)   
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

    # Return successful response
    return {"detail": "File uploaded successfully"}

    

    # data = await file_upload.read()
    # save_to = UPLOAD_DIR / file_upload.filename
    # with open(save_to, 'wb') as f:
    #     f.write(data)
    
    # return {"filename": file_upload.filename}



def append_to_master_file(file_upload:UploadFile):
    # Use pandas to read Excel content
    excel_data = pd.read_excel(file_upload)

    # Convert the DataFrame to a list of dictionaries
    excel_data_list = excel_data.to_dict(orient='records')

    # Append the Excel data to the master Excel file using ExcelProcessor
    excel_processor = ExcelProcessor(DIR_PATH)
    excel_processor.append_to_master_excel(excel_data_list)

    print('excel parsed')


# API endpoint to set hour and minute
@app.post("/set_time/")
async def set_time(hour: int, minute: int, caption: str):
    try:
        # Validate hour and minute
        if not 0 <= hour <= 23 or not 0 <= minute <= 59:
            raise HTTPException(status_code=400, detail="Invalid hour or minute")

        # Initialize cron job
        cron = CronTab(user=True)

        # Remove existing cron jobs
        cron.remove_all()

        # Add new cron job to run the script at the specified time
        job = cron.new(command=f"python3 /home/farshad/Desktop/insta_bot/Application/Server/insta_bot.py {caption}")  # Replace '/path/to/your/script.py' with the actual path
        job.minute.on(minute)
        job.hour.on(hour)

        # Write cron job to the crontab
        cron.write()

        return {"message": f"Script will run daily at {hour:02d}:{minute:02d}"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))