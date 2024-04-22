import json

import assessment.probability_test
import file_manager as fm
from file_manager import file_manager, FileManagerError, generic_file_path, temp_file_path
from assessment.test import *
from assessment.data.file_specific.csv import sp_csv
from assessment.data.file_specific.xml import sp_xml
from assessment.data.file_specific.json import sp_json


class I1(Metric):
    def __init__(self, resource_payload: dict):
        super().__init__('I1', 'evaluating data language in metadata and file')
        self.resource_payload = resource_payload

    def run_test(self):
        self.start_test()
        self.scored_point += 1
        # CATALOG USES CKAN API THAT GIVES BACK A JSON RESPONSE a formal, accessible, shared, and broadly
        # applicable language for knowledge representation.
        formats = file_manager.open_file('format', 'json', True, 'set')
        self.max_point += 1
        if ('distribution_format' in self.resource_payload and self.resource_payload['distribution_format']
                and self.resource_payload['distribution_format'].lower() in formats):
            self.scored_point += formats[self.resource_payload['distribution_format'].lower()]['point'] / formats['max_point']
            if formats[self.resource_payload['distribution_format'].lower()]['point'] < formats['max_point']:
                self.hint_test(f"File format has a  {formats[self.resource_payload['distribution_format'].lower()]['point']}/" 
                            f"{formats['max_point']} score -> machine readable: {formats[self.resource_payload['distribution_format'].lower()]['machine-readable']}"
                            f" | non proprietary: {formats[self.resource_payload['distribution_format'].lower()]['non-proprietary']}")

        elif ('format' in self.resource_payload and self.resource_payload['format']
                    and self.resource_payload['format'].lower() in formats):
                self.scored_point += formats[self.resource_payload['format'].lower()]['point'] / formats['max_point']
                if formats[self.resource_payload['format'].lower()]['point'] < formats['max_point']:
                    self.hint_test(
                        f"File format has a  {formats[self.resource_payload['distribution_format'].lower()]['point']}/"
                        f"{formats['max_point']} score -> machine readable: {formats[self.resource_payload['distribution_format'].lower()]['machine-readable']}"
                        f" | non proprietary: {formats[self.resource_payload['distribution_format'].lower()]['non-proprietary']}")
        elif ('distribution_format' in self.resource_payload and self.resource_payload['distribution_format']) or ('format' in self.resource_payload and self.resource_payload['format']):
            self.hint_test("Format not supported")
        else:
            self.hint_test("Format is not declared")
        return self.end_test()


class I2(Metric):
    def __init__(self, resource_payload: dict):
        super().__init__('I2', 'evaluating vocabularies use in resource metadata')
        self.resource_payload = {"resources": resource_payload}

    def run_test(self):
        self.start_test()
        vocabularies = file_manager.open_file('vocabularies_ckan', 'json', True, 'set')

        self.max_point -= 1
        import re
        for payload_property in vocabularies:
            pattern = re.compile(fr'"{payload_property}"\s?:\s?"(\S+)"')
            matches = re.findall(pattern, json.dumps(self.resource_payload))

            pattern2 = re.compile(fr'"{payload_property}"\s?:\s?(\[.+])')
            matches2 = re.findall(pattern2, json.dumps(self.resource_payload))

            pattern3 = re.compile(fr'"key"\s?:\s?"{payload_property}"\s?,\s?"value"\s?:\s?"\s?(\S+)\s?"\s?}}')
            matches3 = re.findall(pattern3, json.dumps(self.resource_payload))

            found = 0
            if matches:
                for match in matches:
                    self.max_point += 1
                    for vocabulary in vocabularies[payload_property]['vocabulary_format']:
                        if vocabulary in match:
                            self.scored_point += 1
                            found = 1
                            break

            if matches2 and not found:
                for match in matches2:
                    self.max_point += 1
                    match = json.loads(match)
                    for vocabulary in vocabularies[payload_property]['vocabulary_format']:
                        for elem_match in match:
                            if vocabulary in elem_match:
                                self.scored_point += 1
                                found = 1
                                break
                        if found:
                            break

            if matches3 and not found:
                for match in matches3:
                    self.max_point += 1
                    for vocabulary in vocabularies[payload_property]['vocabulary_format']:
                        if vocabulary in match:
                            self.scored_point += 1
                            found = 1
                            break
            if (matches or matches2 or matches3) and not found:
                self.hint_test(f"Property {payload_property} does not seem to use known vocabularies"
                               f"-> FOUND: {matches + matches2 + matches3}")

        self.max_point = max(1, self.max_point)
        return self.end_test()


class I3(Metric):
    def __init__(self, resource_payload):
        super().__init__('I3', 'evaluating reference to other metadata')
        self.resource_payload = resource_payload

    def run_test(self):
        self.start_test()
        # TODO: to determine

        return self.end_test()


class GuidelinesI(Metric):
    def __init__(self, file_name: str):
        super().__init__('GUIDELINES I', '')
        self.file_name = file_name

    def run_test(self):
        self.start_test()
        self.scored_point += 1
        # CATALOG USES CKAN API THAT GIVES BACK A VALID UTF8 ENCODED RESPONSE

        if self.file_name:
            file_content = None
            self.max_point += 1
            # TODO: implement format compatibility
            try:
                with open(fm.generic_file_path + fm.temp_file_path + self.file_name, "r",
                          encoding="utf-8") as f:
                    file_content = f.read()

                self.scored_point += 1
            except UnicodeDecodeError:
                self.hint_test("File is not utf-8 encoded")
                with open(fm.generic_file_path + fm.temp_file_path + self.file_name, "r") as f:
                    file_content = f.read()
            except FileNotFoundError as e:
                raise FileManagerError(e)
            except Exception as e:
                raise FileManagerError(e)

            if file_content:
                self.info_test("file utf-8 encoded", 1)
                perc_corr_date_format = assessment.probability_test.date_time_format(file_content)

                if perc_corr_date_format[0] > 0:
                    self.max_point += 1
                    self.scored_point += perc_corr_date_format[1] / perc_corr_date_format[0]

                if self.file_name.split('.')[-1] == 'csv':
                    self.max_point += 1
                    if sp_csv.check_delimiter(self.file_name):
                        self.info_test("csv file delimiter is ; correct", 1)
                        self.scored_point += 1
                    else:
                        self.hint_test("CSV file should use ; as delimiter")
                    self.max_point += 1
                    if sp_csv.is_single_table_csv(self.file_name):
                        self.info_test("file seems to hold just one table", 1)
                        self.scored_point += 1

                    else:
                        self.hint_test("File holds more than one table, not recommended")
                    self.max_point += 1

                    if sp_csv.is_blank_free(self.file_name):
                        self.info_test("file seems to not have blank rows", 1)
                        self.scored_point += 1

                    else:
                        self.hint_test("File has blank rows, not recommended")
                    # TODO: function to verify there isn't a title
                    self.max_point += 1

                    if sp_csv.has_header(self.file_name):
                        self.info_test("file has header", 1)
                        self.scored_point += 1

                    else:
                        self.hint_test("File does not have header, not recommended")
                elif self.file_name.split('.')[-1] == 'xml':
                    self.max_point += 1
                    if sp_xml.check_no_program_info(self.file_name):
                        self.info_test("file does not contain information on creator software", 1)
                        self.scored_point += 1

                    else:
                        self.hint_test("File contains information on creator software, not recommended")

                elif self.file_name.split('.')[-1] == 'rdf':
                        # TODO:  Use HTTP URIs to denote resource
                        pass
                elif self.file_name.split('.')[-1] == 'json':
                    self.max_point += 1
                    if sp_json.validate_var_type(self.file_name):
                        self.info_test("file use correct data type", 1)
                        self.scored_point += 1

                    else:
                        self.hint_test("File use incorrects data type")
        return self.end_test()


class InteroperabilityTest(Principle):
    def __init__(self, resource_payload, name):
        self.resource_payload = resource_payload
        self.file_name = name
        metric_test = [I1(self.resource_payload), I2(self.resource_payload), I3(self.resource_payload), GuidelinesI(self.file_name)]

        super().__init__('I', metric_test)





