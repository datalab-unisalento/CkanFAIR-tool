import inspect


class MyReporter:
    """
    Class to build a reporter system which allow the user to have a detailed report of the dataset evaluations
    """
    def __init__(self):
        self.report = ''
        self.report_path = ''
        self.report += "euFAIR - THE TOOL FOR YOUR EU ORIENTED FAIRIFICATION\n"
        self.reports = {}




class LogError(Exception):
    def __init__(self, capt_error: Exception):
        """
        Exception raised from error happening to create, write or save the log
        :param capt_error:  error captured
        """
        self.capt_error = str(capt_error)
        # Get the name of the function which called the error
        self.caller_function = inspect.currentframe().f_back.f_code.co_name
        print(f"NOT LOGGABLE ERROR DURING {self.caller_function}  -> {self.capt_error}")
        super().__init__(f"ERROR DURING {self.caller_function}  -> {self.capt_error}")


reporter = MyReporter()