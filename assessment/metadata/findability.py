import copy
import csv
import json

import data_retriever
from file_manager import file_manager, FileManagerError
from assessment.metadata import support_f2, support_f4
from assessment.test import *


def apri():
    # Definisci il nome del file CSV
    csv_file = 'file/graphs/IPA_to_istat.csv'

    # Definisci l'array in cui memorizzare i valori della colonna
    colonna_array = []

    # Apre il file CSV in modalità lettura
    with open(csv_file, newline='') as file:
        # Leggi il contenuto del file CSV
        reader = csv.reader(file)

        # Itera sulle righe del file CSV
        for riga in reader:
            # Aggiungi il valore della colonna alla lista
            # Assicurati di sostituire 'indice_colonna' con l'indice della colonna desiderata
            colonna_array.append(riga[1])

    return colonna_array

class F1(Metric):
    def __init__(self, payload):
        super().__init__( 'F1', 'finding dataset permanent URL')
        self.payload = payload

    def run_test(self):
        self.start_test()
        ipas = apri()

        try:
            permalinks = file_manager.open_file('permanent_link', 'json', True, 'set')['formats']
            if "url" in self.payload["result"] and self.payload["result"]["url"]:
                for permalink in permalinks:
                    if self.payload["result"]["url"].find(permalink) == -1:
                        self.info_test('permalink not found', 1)
                    else:
                        self.info_test('permalink found', 1)
                        self.scored_point = 1
                        break

            elif "extras" in self.payload["result"]:
                for extra in self.payload["result"]["extras"]:
                    if extra["key"] == "uri":
                        for permalink in permalinks:
                            if extra["value"].find(permalink) == -1:
                                self.info_test('permalink not found', 1)
                            else:
                                self.info_test('permalink found', 1)
                                self.scored_point = 1
                                break

            if self.scored_point == 0:
                self.hint_test("The dataset doesn't seem to have a permalink.")

            self.max_point += 1
            if "identifier" in self.payload["result"] and self.payload["result"]["identifier"]:
                if self.payload['result']["identifier"].find(':') != -1:
                    cc = self.payload['result']["identifier"].split(':')
                    if len(cc) == 2:
                        ipa = cc[0]
                        if ipa in ipas:
                            self.scored_point += 1
                        else:
                            self.hint_test(f"IPA in identifier not known -> {ipa}")
                    else:
                        self.hint_test(f"L'identifier del dataset non rispetta il formato IPA:id -> {self.payload['result']['identifier']}")
                else:
                    self.hint_test(
                        f"L'identifier del dataset non rispetta il formato IPA:id -> {self.payload['result']['identifier']}")
            else:
                self.hint_test(
                    f"Dataset identifier not found")
            return self.end_test()

        except FileManagerError as e:
            raise TestError('F1', e)


class F22(Metric):
    def __init__(self, payload, method, portal_url):
        super().__init__('F2', 'calculating metadata richness')
        self.payload = payload
        self.method = method
        self.portal_url = portal_url

    def run_test(self):
        self.start_test()
        with open("file/settings/properties.json", "r") as file:
            properties = json.load(file)

        def calculate_max_score(_property):
            score = 0
            for prop in properties[_property]:
                score += support_f2.calc_point(properties[_property][prop])
            return score

        self.max_point += calculate_max_score("result") - 1
        for _property in properties["result"].keys():
            self.info_test(f"evaluating {str(_property)}", 1)
            if _property == 'resources':
                resources = self.payload['result'][_property]
                max_score = calculate_max_score('resources')
                score = 0
                for resource in resources:
                    for prop in properties[_property]:
                        if prop in resource and resource[prop]:
                            score += support_f2.calc_point(properties[_property][prop])
                        else:
                            self.hint_test(f"**Property:::** {prop}; **Resource:** {resource['name']}; **Warning:** "
                                           f"not implemented."
                                           f" -- **Obligatory level:**: {'MANDATORY' if properties[_property][prop] == 'M' else ('RECOMMENDED' if properties[_property][prop] == 'R' else 'OPTIONAL')}")
                score = score / len(resources)
                self.scored_point += (score / max_score)

            elif _property == 'extras':
                max_score = calculate_max_score('extras')
                score = 0

                for prop in properties[_property]:
                    found = 0
                    for elem in self.payload['result'][_property]:
                        if elem['key'] == prop:
                            found = 1
                            if elem['value']:
                                score += support_f2.calc_point(properties[_property][prop])
                            else:
                                self.hint_test(f"**Property:** {prop} **Attribute:** extras; **Warning:** la proprietà non sembra implementata"
                                       f" -- **Obligatory level:** {'MANDATORY' if properties[_property][prop] == 'M' else ('RECOMMENDED' if properties[_property][prop] == 'R' else 'OPTIONAL')}")

                    if not found:
                        self.hint_test(
                            f"**Property:** {prop} **Attribute:** extras; **Warning:** la proprietà non sembra implementata"
                            f" -- **Obligatory level:** {'MANDATORY' if properties[_property][prop] == 'M' else ('RECOMMENDED' if properties[_property][prop] == 'R' else 'OPTIONAL')}")

                self.scored_point += (score/max_score)

            elif _property in self.payload['result'] and self.payload['result'][_property]:
                if _property not in properties.keys():
                    self.scored_point += support_f2.calc_point(properties["result"][_property])
                else:
                    sub_max_point = 0
                    for sub_p in properties[_property].keys():

                        sub_max_point += support_f2.calc_point(properties[_property][sub_p])
                        sub_point = 0

                        if sub_p in self.payload['result'][_property]:
                            if isinstance(self.payload['result'][_property], str):
                                sub_property = json.loads(self.payload['result'][_property])
                            else:
                                sub_property = self.payload['result'][_property]
                            if sub_property:
                                if sub_p not in properties.keys():
                                    sub_point += support_f2.calc_point(properties[_property][sub_p])
                                else:
                                    ssub_max_point = 0
                                    ssub_point = 0
                                    for ssub_p in properties[sub_p].keys():
                                        ssub_max_point += support_f2.calc_point(properties[sub_p][ssub_p])
                                        if ssub_p in self.payload['result'][_property] and \
                                                self.payload['result'][_property][sub_p]:
                                            ssub_point += support_f2.calc_point(properties[sub_p][ssub_p])
                                        else:
                                            self.hint_test(f"**Property:** {_property} -> {sub_p} -> {ssub_p}  **Warning:** not implemented"
                                                           f" -- **Obligatory level:** {'MANDATORY' if properties[_property][prop] == 'M' else ('RECOMMENDED' if properties[_property][prop] == 'R' else 'OPTIONAL')}")

                                    sweight = ssub_point / ssub_max_point
                                    sub_point += sweight * support_f2.calc_point(properties[_property][sub_p])
                        else:
                            self.hint_test(
                                f"**Property:** {_property} -> {sub_p} **Warning:** not implemented"
                                f" -- **Obligatory level:** {'MANDATORY' if properties[_property][prop] == 'M' else ('RECOMMENDED' if properties[_property][prop] == 'R' else 'OPTIONAL')}")

                        weight = sub_point / sub_max_point
                    self.scored_point += weight * support_f2.calc_point(properties["result"][_property])
            else:
                self.hint_test(f"**Property:** {_property}; **Warning:** not implemented"
                               f" -- **Obligatory level:** {'MANDATORY' if properties['result'][_property] == 'M' else ('RECOMMENDED' if properties['result'][_property] == 'R' else 'OPTIONAL')}")

        return self.end_test()


class F3(Metric):
    def __init__(self, payload):
        super().__init__("F3", "finding data identifier in the metadata")
        self.payload = payload

    def run_test(self):
        self.start_test()

        if "resources" not in self.payload["result"] or len(self.payload["result"]["resources"]) == 0:
            self.hint_test("No resource found")
            return self.end_test()

        self.max_point = len(self.payload["result"]["resources"])

        self.info_test(f"found {str(len(self.payload['result']['resources']))} distributions", 1)

        for idx, distribution in enumerate(self.payload["result"]["resources"]):
            if distribution["id"] is not None:
                self.info_test(f"for distribution {str(idx +1)} found id: {str(distribution['id'])}", 2)
                self.scored_point += 1
            else:
                self.hint_test(f"Distribution {self.payload['result']['resources'][idx]['name']} has no id")
        return self.end_test()


class F4(Metric):
    def __init__(self, payload, portal_url: str):
        super().__init__('F4', 'searching for metadata indexing')
        self.payload = payload

    def run_test(self):
        self.start_test()
        try:
            if support_f4.duckduckgo_indexed('https://dati.puglia.it/ckan/dataset/' + self.payload['result']['name']):
                self.info_test(f"found {self.portal_url + self.payload['result']['name']}", 2)
                self.scored_point += 1
                return self.end_test()


            else:
                pass
                # self.hint_test('La risorsa non è indicizzata nei motori di ricerca')

        except support_f4.DuckDuckGoError as e:
            pass

        return self.end_test()


class GuidelinesF(Metric):
    def __init__(self, payload):
        super().__init__('GUIDELINES F', '')
        self.payload = payload

    def run_test(self):
        self.start_test()

        empty_fields = 0
        payload_text = json.dumps(self.payload)

        self.info_test("evaluating null values count in the metadata", 1)
        fields = payload_text.count('": "') + payload_text.count('": [') + payload_text.count('": {') + 1
        empty_fields += payload_text.count("null")
        empty_fields += payload_text.count("[]")
        empty_fields += payload_text.count("{}")
        self.info_test(f"found {str(empty_fields)} empty fields: {str(round(empty_fields / fields * 100, 2))}%", 2)
        self.scored_point += (fields - empty_fields) / fields
        if empty_fields:
            self.hint_test(f"Found {empty_fields} empty fields for {fields} fields in metadata")

        self.info_test("evaluating important field presence in the metadata", 1)
        if 'tags' in self.payload.keys() and self.payload['result']['tags']:
            self.scored_point += 1
            self.info_test("keywords(tags) field found", 2)
        else:
            self.hint_test("Keywords not found")
        # TODO: find categories equivalent in CKAN response

        if 'groups' in self.payload['result'] and self.payload['result']['groups']:
            self.scored_point += 1
            self.info_test("categories field found", 2)
        else:
            self.hint_test("Themes not found")

        if 'extras' in self.payload['result']:
            print(self.payload['result']['extras'])
            not_found = 1
            for extra in self.payload['result']['extras']:
                if not_found:
                    if extra['key'] == 'temporal_end' or extra['key'] == 'temporal_start':
                        if extra['value']:
                            self.scored_point += 1
                            self.info_test("temporal field found", 2)
                            not_found = 0
                            break
                        else:
                            self.hint_test("Temporal not found")
            if not_found:
                if 'temporal_coverage' in self.payload['result'] and self.payload['result']['temporal_coverage']:
                    self.scored_point += 1
                    self.hint_test("Temporal not found")
                else:
                    self.hint_test("Spatial not found")

            not_found = 1
            for extra in self.payload['result']['extras']:
                if not_found:
                    if extra['key'] == 'spatial_uri':
                        if extra['value']:
                            self.scored_point += 1
                            self.info_test("temporal field found", 2)
                            not_found = 0
                            break
                        else:
                            self.hint_test("Spatial not found")
            if not_found:
                self.hint_test("Spatial not found")

        else:
            self.hint_test("Spatial not found")
            self.hint_test("Temporal not found")

        return self.end_test()


class FindabilityTest(Principle):
    def __init__(self, payload, portal_url, method='DCAT_AP-IT'):
        self.payload = payload
        self.method = method
        self.portal_url = portal_url
        metric_test = [F1(self.payload), F22(self.payload, self.method, self.portal_url), F3(self.payload), F4(self.payload, self.portal_url), GuidelinesF(self.payload)]
        super().__init__('F', metric_test)


