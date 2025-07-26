import sys
import os

class CustomerSupportException(Exception):
    """
    custom class to handele exception errors
    """
    def __init__(self, error_message, error_details:sys):
        self.error_message = error_message
        _,_,ext_tb = error_details.exc_info()
        self.lineno = ext_tb.tb_lineno
        self.file_name = ext_tb.tb_frame.f_code.co_filename

    def __str__(self):
        return f"Error occured in the python script name {self.file_name} line number {self.lineno} error message {self.error_message}"
    
if __name__ == "__main__":
    try:
        result = 20 / 0
        print("This will not work", result)
    except Exception as e:
        raise CustomerSupportException(e, sys)
    

        