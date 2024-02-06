import matplotlib.pyplot as plt
from datetime import datetime
import os

class ImageProcessor:
    def __init__(self, dir_path, output_prefix):
        self.dir_path = dir_path
        self.output_prefix = output_prefix

    def create_equation_image(self, latex_equation, choices):
        output_directory = os.path.join(self.dir_path, 'generated')

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        fig, ax = plt.subplots(figsize=(8, 6))  # Increase the size of the figure 
        ax.text(-0.13, 0.9, latex_equation, size=13, ha='left', va='center')  # Adjusted y position 
        ax.axis('off')  # Turn off the axis 
 
        for i, choice in enumerate(choices):
            ax.text(-0.15, 0.6 - i * 0.15, choice, size=14, ha='left', va='center')


        current_date = datetime.now().strftime("%Y%m%d")
        filename_with_date = f"{self.output_prefix.split('.')[0]}_{current_date}.jpg"
        output_path = os.path.join(output_directory, filename_with_date)

        plt.savefig(output_path, format="jpeg", bbox_inches='tight', pad_inches=0, dpi=300)
        plt.close()

        return output_path

    def generate_image_from_excel(self, excel_processor):
        latex_equation, choices = excel_processor.process_equation_file()
        output_image_path = self.create_equation_image(latex_equation, choices )
        return output_image_path
