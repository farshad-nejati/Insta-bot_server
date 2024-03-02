import pandas as pd
import os

class ExcelProcessor:
    master_excel_file = "master_file.xlsx"
    CHOICE_LETTERS = ["A", "B", "C", "D"]

    def __init__(self, dir_path):
        self.dir_path = dir_path
        self.file_name = ExcelProcessor.master_excel_file

    @staticmethod
    def initialize_master_excel_file():
        # Create the master Excel file with a header (you can customize the header as needed)
        header = ["caption", "equation", "answer1", "answer2", "answer3", "answer4", "right answer"]  # Add caption column
        df = pd.DataFrame(columns=header)
        
        df.to_excel(ExcelProcessor.master_excel_file, index=False)

    def get_file_path(self):
        file_path = os.path.join(self.dir_path, self.file_name)
        return file_path
    
    

    def get_df(self, sheet_name=0):
        file_path = self.get_file_path()
        df = pd.read_excel(file_path, sheet_name=sheet_name)
        return df

    def read_parameter_worksheet(self):
        try:
            df = self.get_df(sheet_name=1)  # Read the second worksheet
            rows_list = []
            for index, row in df.iterrows():
                date = pd.to_datetime(row['Date'], format='%Y/%m/%d')
                # time = pd.to_datetime(row['Time'], format='%H:%M').time()
                time = pd.to_datetime(row['Time'], format='%H:%M:%S').time()

                post_no = int(row['PostNo'])
                rows_list.append({'Date': date, 'Time': time, 'PostNo': post_no})
            
            return rows_list
        except Exception as e:
            print(f"Error reading second worksheet: {e}")
            return None
        
    def remove_first_row(self):
        file_path = self.get_file_path()
        df = self.get_df()
        output_df = df.iloc[1:, :]
        output_df.to_excel(file_path, index=False)

    def extract_caption(self):
        df = self.get_df()
        caption = df.iloc[0, 0]
        return caption

    def extract_equation_and_choices(self):
        df = self.get_df()
        latex_equation = df.iloc[0, 1]
        choices = df.iloc[0, 2:].tolist()
        choices = [f"{letter}) {choice}" for letter, choice in zip(ExcelProcessor.CHOICE_LETTERS, choices)]
        return latex_equation, choices

    def process_equation_file(self):
        caption = self.extract_caption()
        latex_equation, choices = self.extract_equation_and_choices()
        return caption, latex_equation, choices

    def append_to_master_excel(self, excel_data_list):
        try:
            # Read the existing content of the master Excel file
            master_df = pd.read_excel(self.file_name)

            # Extract variables from each row in excel_data_list and append to the master DataFrame
            for excel_data in excel_data_list:
                caption = excel_data.get("caption", "")
                equation = excel_data.get("equation", "")
                answer1 = excel_data.get("answer1", "")
                answer2 = excel_data.get("answer2", "")
                answer3 = excel_data.get("answer3", "")
                answer4 = excel_data.get("answer4", "")
                right_answer = excel_data.get("right answer", "")

                new_data = pd.DataFrame([{"caption": caption, "equation": equation, "answer1": answer1,
                                           "answer2": answer2, "answer3": answer3, "answer4": answer4,
                                           "right answer": right_answer}])

                master_df = pd.concat([master_df, new_data], ignore_index=True)

            # Write the updated DataFrame back to the master Excel file
            master_df.to_excel(self.file_name, index=False)
        except Exception as e:
            print(f"Error appending to master Excel file: {e}")
