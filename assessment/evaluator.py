import json
import datetime
import re
import threading
from typing import Optional

import requests

import reporter as reporter_
from console_print import c_print, MyColors as Color
import cloud_manager as cloud_manager
from constants import Constants
import geo_manager as geo_manager
import data_retriever as data_retriever
import database_manager as database_manager
from event_bus import event_bus
from file_manager import file_manager
from assessment.metadata.findability import FindabilityTest as FindMeta
from assessment.metadata.accessibility import AccessibilityTest as AccMeta
from assessment.metadata.interoperability import InteroperabilityTest as IntMeta
from assessment.metadata.reusability import ReusabilityTest as ReuMeta
from assessment.data.findability import FindabilityTest as FindData
from assessment.data.accessibility import AccessibilityTest as AccData
from assessment.data.interoperability import InteroperabilityTest as IntData
from assessment.data.reusability import ReusabilityTest as ReuData
import assessment.test as test
import signal

def get_accrual(payload: dict) -> Optional[int]:
    """
    Extract from the metadata the accrual periodicity of the dataset
    :param payload: the dataset metadata
    :return: the accrual periodicity as an int number of days
    """
    if 'frequency' in payload['result']:
        frequency = payload['result']['frequency']
        for frequency_value in Constants.FREQUENCIES.keys():
            if frequency == frequency_value:
                return Constants.FREQUENCIES[frequency_value]

    return None


def is_modified(dataset_id: str, payload: dict, cloud_service: cloud_manager.Cloud) -> bool:
    """
    Check if the dataset has been modified since last evaluation
    :param dataset_id: the id of the dataset
    :param payload: the new payload of the dataset
    :param cloud_service: the cloud service instance
    :return: True if the dataset has been modified, False otherwise
    """
    old_payload_id = cloud_service.search_folder_and_get_latest_file(dataset_id, 'ckan')

    if old_payload_id:
        old_payload_file_id = cloud_service.download_file(old_payload_id)
        old_payload = json.loads(file_manager.open_file(old_payload_file_id, 'txt', True, 'temp'))

        file_manager.delete_file(old_payload_file_id, 'txt')
        print(isinstance(old_payload, dict))
        print(isinstance(payload, dict))

        if json.dumps(old_payload) != json.dumps(payload):
            for key in old_payload['result'].keys():
                if key != 'metadata_modified':
                    print('f')

                    if payload['result'][key] != old_payload['result'][key]:
                        return True
    return False


def find_url(poss_url):
    try:
        for url in poss_url:
            if requests.get(url).status_code == 200:
                return url
    except requests.RequestException as e:
        print(e)


class Evaluator:
    def __init__(self):
        self.running = True
        event_bus.subscribe(self)

    def eval_dataset(self, dataset_id, portal_instance: data_retriever.DataRetriever):
        all_reports = {}
        payload = portal_instance.get_dataset(dataset_id)

        if payload is None:
            return 0

        portal_url = portal_instance.get_url() + '/'
        temp_url = portal_url + '/dataset/'
        poss_url = [
                portal_url + payload['result']['name'],
            portal_url + payload['result']['id'],
            temp_url + payload['result']['name'],
            temp_url + payload['result']['id']
        ]

        page_url = find_url(poss_url)

        reporter = reporter_.MyReporter()

        metadata = test.Structure("METADATA", [
            FindMeta(payload, page_url),
            AccMeta(payload),
            IntMeta(payload, portal_instance.get_url()),
            ReuMeta(payload)
        ], reporter)

        metadata.run()
        all_reports['metadata'] = reporter.reports

        if 'resources' in payload['result'] and payload['result']['resources']:
            try:
                for idx_, resource in enumerate(payload['result']['resources']):
                    resource_payload = resource
                    resource_file = None
                    try:
                        print(resource, resource_payload['url'])

                        if not str(resource_payload['url']).endswith('rss.xml'):
                            if data_retriever.get_dataset_distribution(resource_payload['url']):
                                print(resource, resource_payload['url'])
                                resource_file = data_retriever.retrieve_dataset(resource_payload['url'])
                    except TimeoutError as e:
                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)
                    except requests.exceptions.SSLError as e:
                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)
                    except requests.exceptions.RequestException as e:
                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)
                    except data_retriever.DataRetrieverError as e:
                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)
                    except Exception as e:
                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)

                    # TODO: aggiungere cloud per file
                    is_file_modified = None
                    resource_file_id = None
                    reporter = reporter_.MyReporter()
                    data = test.Structure(f'DATA FOR RESOURCE: {resource_payload["id"]}',
                                          [FindData(resource_payload),
                                           AccData(resource_payload),
                                           IntData(resource_payload, resource_file),
                                           ReuData(payload, resource_payload, resource_file)
                                           ], reporter)
                    data_assessment = data.run()

                    all_reports[resource_payload['name'] + (resource_payload['format'] if 'format' in resource_payload and resource_payload['format'] else resource_payload['id'])] = reporter.reports

                if resource_file:
                    file_manager.delete_file(resource_file[:resource_file.rfind(".")],
                                             resource_file.split('.')[-1])
            except test.TestError as e:
                print(e)
        return all_reports

    def start_eval(self, cloud_service: cloud_manager.Cloud, database: database_manager.DatabaseManager, datasets,
                   portal_instance: data_retriever.DataRetriever, locator: geo_manager.CoorFinder):
        all_reports = {}
        portal_report = {}
        length = len(datasets)

        event = {
            'type': 'update_text_toplevel',
            'text': f'{length} DATASETS TO UPDATE FOUND',
            'text1': '',
            'text2': '',
            'text3': ''

        }
        event_bus.publish(event)
        first = True

        with open('logs/report2.txt', "w") as f:
            f.write("")

        with open('logs/report.txt', "a") as file, open('logs/report2.txt', "a") as file2:
            while self.running and first:
                first = False
                for idx, dataset_id in enumerate(datasets):
                    reporter = reporter_.MyReporter()
                    portal_report[dataset_id] = 0

                    known_holders = database.get_holders_list()
                    known_datasets = database.get_dataset_list()
                    known_categories = database.get_category_list()

                    try:
                        file2.write('{"' + f"{dataset_id}" + '":')
                        payload = portal_instance.get_dataset(dataset_id)
                        curr_holder = payload['result']['holder_identifier']

                        event = {
                            'type': 'update_text_toplevel',
                            'text': f'UPDATING DATASET {idx + 1} OF {length}: {dataset_id}',
                            'text1': 'CHECKING DATABASE HOLDER',
                            'text2': '',
                            'text3': ''

                        }
                        event_bus.publish(event)
                        if curr_holder not in known_holders:
                            event = {
                                'type': 'update_text_toplevel',
                                'text': None,
                                'text1': 'CHECKING DATABASE HOLDER',
                                'text2': 'NEW HOLDER FOUND',
                                'text3': 'SAVING'

                            }
                            event_bus.publish(event)

                            database.save_holder(curr_holder, payload['result']['holder_name'],
                                                 (locator.get_location(curr_holder) if locator else None),
                                                 (locator.get_prov(curr_holder) if locator else None),
                                                 (locator.get_city(curr_holder) if locator else None))

                        event = {
                            'type': 'update_text_toplevel',
                            'text': None,
                            'text1': 'CHECKING DATASET',
                            'text2': '',
                            'text3': ''

                        }
                        event_bus.publish(event)

                        if dataset_id not in known_datasets:
                            event = {
                                'type': 'update_text_toplevel',
                                'text': None,
                                'text1': 'CHECKING DATASET',
                                'text2': 'NEW DATASET FOUND',
                                'text3': 'SAVING'

                            }
                            event_bus.publish(event)

                            database.save_dataset(dataset_id, curr_holder, get_accrual(payload),
                                                  (payload['name'] if 'name' in payload else None))

                        dataset_categories = []

                        event = {
                            'type': 'update_text_toplevel',
                            'text': None,
                            'text1': 'CHECKING DATABASE CATEGORY',
                            'text2': ' ',
                            'text3': ' '

                        }
                        event_bus.publish(event)

                        if 'groups' in payload['result'] and payload['result']['groups']:
                            for category in payload['result']['groups']:
                                dataset_categories.append(category['name'])

                        for category in dataset_categories:
                            if category not in known_categories:
                                event = {
                                    'type': 'update_text_toplevel',
                                    'text': None,
                                    'text1': 'CHECKING DATABASE CATEGORY',
                                    'text2': f'NEW CATEGORY FOUND: {category}',
                                    'text3': 'SAVING'

                                }
                                event_bus.publish(event)
                                database.save_category(category)

                        known_dataset_categories = database.get_category_for_dataset(dataset_id)

                        for category in dataset_categories:
                            if category not in known_dataset_categories:
                                event = {
                                    'type': 'update_text_toplevel',
                                    'text': None,
                                    'text1': 'CHECKING DATABASE CATEGORY',
                                    'text2': f'NEW DATASET-CATEGORY RELATIONSHIP FOUND FOR: {category}',
                                    'text3': 'SAVING'

                                }
                                event_bus.publish(event)
                                database.save_category_dataset_relation(dataset_id, category)

                        if dataset_id not in known_datasets:
                            event = {
                                'type': 'update_text_toplevel',
                                'text': None,
                                'text1': 'DATASET NOT ASSESSED -> ASSESSING',
                                'text2': ' ',
                                'text3': ' '

                            }

                            event_bus.publish(event)

                        is_modified_ = None
                        cloud_payload_id = None

                        if cloud_service:
                            is_modified_ = is_modified(dataset_id, payload, cloud_service)

                            file_name = 'ckan-' + dataset_id + str(datetime.datetime.now()).replace(' ', '-')
                            file_name = re.sub(r'[^\w\-_.]', '-', file_name)

                            file_manager.write_file(file_name + '.txt', payload, file_manager.temp_file_path, True)
                            cloud_payload_id = cloud_service.upload(file_name, dataset_id)

                            file_manager.delete_file(file_name)

                        portal_url = portal_instance.get_url() + '/'
                        temp_url = portal_url + '/dataset/'
                        poss_url = [
                            portal_url + payload['result']['name'],
                            portal_url + payload['result']['id'],
                            temp_url + payload['result']['name'],
                            temp_url + payload['result']['id']
                        ]

                        page_url = find_url(poss_url)
                        event = {
                            'type': 'update_text_toplevel',
                            'text': None,
                            'text1': 'DATASET NOT ASSESSED -> ASSESSING',
                            'text2': 'ASSESSING METADATA',
                            'text3': None

                        }

                        event_bus.publish(event)

                        assessment_id = database.new_assessment(dataset_id)

                        metadata = test.Structure("METADATA", [
                            FindMeta(payload, page_url),
                            AccMeta(payload),
                            IntMeta(payload, portal_instance.get_url()),
                            ReuMeta(payload)
                        ], reporter)

                        metadata_assessment = metadata.run()
                        all_reports[dataset_id] = {'metadata': reporter.reports}

                        def count_elements(dictionary):
                            total_elements = 0
                            for value in dictionary.values():
                                if isinstance(value, dict):
                                    total_elements += count_elements(
                                        value)  # Ricorsivamente conta gli elementi dei dizionari interni
                                else:
                                    total_elements += 1  # Conta l'elemento singolo
                            return total_elements

                        portal_report[dataset_id] += count_elements(reporter.reports)

                        database.save_metadata_assessment(assessment_id, metadata_assessment,
                                                          (is_modified_ if cloud_service else None),
                                                          (cloud_payload_id if cloud_service else None))

                        event = {
                            'type': 'update_text_toplevel',
                            'text': None,
                            'text1': None,
                            'text2': 'ASSESSING DATA',
                            'text3': None

                        }

                        event_bus.publish(event)
                        if 'resources' in payload['result'] and payload['result']['resources']:
                            try:
                                for idx_, resource in enumerate(payload['result']['resources']):

                                    reporter = reporter_.MyReporter()

                                    event = {
                                        'type': 'update_text_toplevel',
                                        'text': None,
                                        'text1': None,
                                        'text2': None,
                                        'text3': f'DISTRIBUTION {idx_ + 1} OF {len(payload["result"]["resources"])}: '
                                                 f'{resource["name"]}'

                                    }

                                    event_bus.publish(event)
                                    resource_payload = resource
                                    resource_file = None
                                    try:

                                        if not str(resource_payload['url']).endswith('rss.xml'):
                                            if data_retriever.get_dataset_distribution(resource_payload['url']):
                                                resource_file = data_retriever.retrieve_dataset(resource_payload['url'])
                                    except TimeoutError as e:
                                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)
                                    except requests.exceptions.SSLError as e:
                                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)
                                    except requests.exceptions.RequestException as e:
                                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)
                                    except data_retriever.DataRetrieverError as e:
                                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)
                                    except Exception as e:
                                        c_print.myprint(f'IMPOSSIBILE SCARICARE LA DISTRIBUZIONE {str(e)}', Color.RED, 2)

                                    # TODO: aggiungere cloud per file
                                    is_file_modified = None
                                    resource_file_id = None
                                    data = test.Structure(f'DATA FOR RESOURCE: {resource_payload["id"]}',
                                                                     [FindData(resource_payload),
                                                                      AccData(resource_payload),
                                                                      IntData(resource_payload, resource_file),
                                                                      ReuData(payload, resource_payload, resource_file)
                                                                      ], reporter)
                                    data_assessment = data.run()
                                    all_reports[dataset_id][resource_payload['id'] + resource_payload['format']] = reporter.reports
                                    portal_report[dataset_id] += count_elements(reporter.reports)
                                    database.save_data_assessment(assessment_id, resource_payload['id'],
                                                                  (resource_payload[
                                                                       'name'] if 'name' in resource_payload else None),
                                                                  data_assessment,
                                                                  (is_file_modified if cloud_service else None),
                                                                  (resource_file_id if cloud_service else None))
                                    if resource_file:
                                        file_manager.delete_file(resource_file[:resource_file.rfind(".")],
                                                                 resource_file.split('.')[-1])
                            except test.TestError as e:
                                print(e)

                        file2.write(json.dumps(all_reports[dataset_id], indent=4))
                        file2.write('}')

                        file.write(f"dataset id: {dataset_id} -> errori: {portal_report[dataset_id]}")
                    except KeyError as e:
                        print('ke:', e)
                    except test.TestError as e:
                        print('te:', e)
                    except Exception as e:
                        print('e:', e)


                event = {
                    'type': 'update_text_toplevel',
                    'text1': 'DONE',
                    'text2': ' ',
                    'text3': ' '
                }
                event_bus.publish(event)
                event = {
                    'type': 'done'
                }
                event_bus.publish(event)

    def handle_event(self, event):
        if event['type'] == 'c_window':
            self.running = False
