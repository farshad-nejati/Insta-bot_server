import pandas as pd
import os

class ExcelProcessor:
    master_excel_file = "master_file.xlsx"
    CHOICE_LETTERS = ["A", "B", "C", "D"]


    def __init__(self, dir_path, ):
        self.dir_path = dir_path
        self.file_name = ExcelProcessor.master_excel_file


    @staticmethod
    def initialize_master_excel_file():
        # Create the master Excel file with a header (you can customize the header as needed)
        header = ["equation", "answer1", "answer2", "answer3", "answer4", "right answer"]  # Customize column names
        df = pd.DataFrame(columns=header)
        
        df.to_excel(ExcelProcessor.master_excel_file, index=False)



    def read_excel_and_extract_variables(self, file_path):
        df = pd.read_excel(file_path)
        latex_equation = df.iloc[0, 0]
        choices = df.iloc[0, 1:].tolist()
        choices = [f"{letter}) {choice}" for letter, choice in zip(ExcelProcessor.CHOICE_LETTERS, choices)]
        
        return latex_equation, choices, df
        

    def process_equation_file(self):
        excel_file_path = os.path.join(self.dir_path, self.file_name)
        latex_equation, choices, df = self.read_excel_and_extract_variables(excel_file_path)
        output_df = df.iloc[1:, :]
        output_df.to_excel(excel_file_path, index=False)
        return latex_equation, choices

    def append_to_master_excel(self, excel_data_list):
        try:
            # Read the existing content of the master Excel file
            master_df = pd.read_excel(self.file_name)

            # Extract variables from each row in excel_data_list and append to the master DataFrame
            for excel_data in excel_data_list:
                equation = excel_data.get("equation", "")
                answer1 = excel_data.get("answer1", "")
                answer2 = excel_data.get("answer2", "")
                answer3 = excel_data.get("answer3", "")
                answer4 = excel_data.get("answer4", "")
                right_answer = excel_data.get("right answer", "")

                new_data = pd.DataFrame([{"equation": equation, "answer1": answer1, "answer2": answer2,
                                        "answer3": answer3, "answer4": answer4, "right answer": right_answer}])

                master_df = pd.concat([master_df, new_data], ignore_index=True)

            # Write the updated DataFrame back to the master Excel file
            master_df.to_excel(self.file_name, index=False)
        except Exception as e:
            print(f"Error appending to master Excel file: {e}")
