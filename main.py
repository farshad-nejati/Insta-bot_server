from fastapi import FastAPI, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from pathlib import Path
from crontab import CronTab
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
    caption: str
    day: int | None = None
    hour: int| None = None
    minute: int| None = None



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

    

    # data = await file_upload.read()
    # save_to = UPLOAD_DIR / file_upload.filename
    # with open(save_to, 'wb') as f:
    #     f.write(data)
    
    # return {"filename": file_upload.filename}

# API endpoint to set hour and minute
@app.post("/set_time/")
async def set_time(item:SetTimeModel):
    script_dir_path = os.path.dirname(os.path.realpath(__file__))
    script_path = os.path.join(script_dir_path, 'insta_bot.py')

    caption= item.caption
    day= item.day
    hour= item.hour
    minute= item.minute

    try:
        await schedule_task(caption, day, hour, minute, script_path)
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
    
    # try:
    #     # Validate hour and minute
    #     if not 0 <= hour <= 23 or not 0 <= minute <= 59:
    #         raise HTTPException(status_code=400, detail="Invalid hour or minute")

    #     # Initialize cron job
    #     cron = CronTab(user=True)

    #     # Remove existing cron jobs
    #     cron.remove_all()

    #     # Add new cron job to run the script at the specified time
    #     job = cron.new(command=f"python3 {script_path} '{caption}'")  # Replace '/path/to/your/script.py' with the actual path
    #     job.minute.on(minute)
    #     job.hour.on(hour)

    #     if(day):
    #         job.day.on(day)

    #     # Write cron job to the crontab
    #     cron.write()

    #     if(day):
    #         return {"message": f"Script will run at {day:02d}, {hour:02d}:{minute:02d}"}
    #     else:
    #         return {"message": f"Script will run daily at {hour:02d}:{minute:02d}"}
    # except Exception as e:
    #     print(e)
    #     raise HTTPException(status_code=500, detail=str(e))
    



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

        # Extract values for caption, day, minute, and hour (assuming only 1 row)
        caption = excel_data.at[0, 'caption']
        day = excel_data.at[0, 'day']
        hour = excel_data.at[0, 'hour']
        minute = excel_data.at[0, 'minute']

        # print(f"caption: {caption}")
        # print(f"day: {day}")
        # print(f"hour: {hour}")
        # print(f"minute: {minute}")

        script_dir_path = os.path.dirname(os.path.realpath(__file__))
        script_path = os.path.join(script_dir_path, 'insta_bot.py')

        await schedule_task(caption, day, hour, minute, script_path)

        return {"message": "Task scheduled successfully"}

    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))



async def schedule_task(caption, day, hour, minute, script_path):
    try:
        # Validate hour and minute
        if (hour is not None  and not 0 <= hour <= 23):
            raise HTTPException(status_code=400, detail="Invalid hour")

        if ( minute is not None and not 0 <= minute <= 59):
            raise HTTPException(status_code=400, detail="Invalid minute")

        
        cron = CronTab(user=True)
        cron.remove_all()
        job = cron.new(command=f"python3 {script_path} '{caption}'")
        


        # print(f"day is not None: {day is not None and not math.isnan(day)}")

        if minute is not None and not math.isnan(minute):
            job.minute.on(minute)

        if hour is not None and not math.isnan(hour):
            job.hour.on(hour)
            
        if day is not None and not math.isnan(day):
            job.day.on(day)

        # Write cron job to the crontab
        cron.write()

        return {"message": f"Script scheduled successfully for '{caption}' at {day:02d}, {hour:02d}:{minute:02d}" if day else f"Script scheduled daily for '{caption}' at {hour:02d}:{minute:02d}"}
        
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail=str(e))
