from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
from crontab import CronTab
from datetime import datetime
import numpy as np

import math
import os
from image_processing.image_processor import ImageProcessor
from instagram_uploader.uploader import InstagramUploader
from image_processing.excel_processor import ExcelProcessor
import pandas as pd  # Make sure to have pandas installed (you can install it with 'pip install pandas')

from pydantic import BaseModel

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


class SetTimeModel(BaseModel):
    date: str | None = None
    time: str



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
        await extract_parameters(save_to)   
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Internal Server Error: {e}")

    # Return successful response
    return {"detail": "File uploaded successfully"}


# API endpoint to set hour and minute
@app.post("/set_time/")
async def set_time(item:SetTimeModel):
    script_dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(script_dir_path, 'insta_bot.py')

    date_str = item.date
    time_str = item.time

    time = datetime.strptime(time_str, "%H:%M")
    date = None if date_str is None else datetime.strptime(date_str, "%m/%d/%Y")

    month =  None if date is None else date.month
    day =  None if date is None else date.day
    hour= time.hour
    minute= time.minute
    
    # print(f"month: {month}")
    # print(f"day: {day}")
    # print(f"hour: {hour}")
    # print(f"minute: {minute}")

    try:
        await schedule_task(month, day, hour, minute, script_path)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))


def append_to_master_file(file_upload:UploadFile):
    # Use pandas to read Excel content
    excel_data = pd.read_excel(file_upload)

    # Convert the DataFrame to a list of dictionaries
    excel_data_list = excel_data.to_dict(orient='records')

    # Append the Excel data to the master Excel file using ExcelProcessor
    excel_processor = ExcelProcessor(DIR_PATH)
    excel_processor.append_to_master_excel(excel_data_list)

    print('excel parsed and append to master file')


async def extract_parameters(file_upload:UploadFile):
    try:
        
        # Open the Excel file
        excel_data = pd.read_excel(file_upload, sheet_name=1)  # Read the second worksheet

        # Extract Date and Time (assuming only 1 row)
        date = excel_data.at[0, 'Date']
        time = excel_data.at[0, 'Time']
        date_is_nan = isinstance(date, float) and np.isnan(date)
        time_is_nan = isinstance(time, float) and np.isnan(date)

        month =  None if date_is_nan else date.month
        day =  None if date_is_nan else date.day
        hour =  None if time_is_nan else time.hour
        minute =  None if time_is_nan else time.minute

        script_dir_path = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.join(script_dir_path, 'insta_bot.py')

        await schedule_task(month, day, hour, minute, script_path)

        return {"message": "Task scheduled successfully"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))



async def schedule_task(month, day, hour, minute, script_path):
    try:
        # Validate hour and minute
        if (hour is not None  and not 0 <= hour <= 23):
            raise HTTPException(status_code=400, detail="Invalid hour")

        if ( minute is not None and not 0 <= minute <= 59):
            raise HTTPException(status_code=400, detail="Invalid minute")


        print('befor run cronjob')
        
        cron = CronTab(user=True)
        cron.remove_all()
        job = cron.new(command=f"python3 {script_path}")
        

        print('after run cronjob')

        # print(f"day is not None: {day is not None}")

        if minute is not None:
            job.minute.on(minute)

        if hour is not None:
            job.hour.on(hour)
            
        if day is not None:
            job.day.on(day)

        if month is not None:
            job.month.on(month)

        # Write cron job to the crontab
        cron.write()

        return {"message": f"Script scheduled successfully"}
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
