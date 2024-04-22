import datetime
import threading
from urllib.parse import urlparse

import data_retriever
import event_bus
import gui
import loader
import results_gui
import settings_mode
from assessment import evaluator
from console_print import c_print, MyColors as Color


def find_portal(url):
    c_print.myprint("Checking for CKAN instances on the selected URL", Color.YELL)
    if not urlparse(url).scheme:
        url_ = "https://" + url
        c_print.myprint(f"URL INPUT '{url}' MISS SCHEMA. Trying with {url_}", Color.RED, 0)
    else:
        url_ = url

    try:
        data_retriever.DataRetriever(url_).try_ckan()
        return url_

    except data_retriever.DataRetrieverError:
        url__ = url_ + ('/' if not url_.endswith('/') else '') + 'ckan'
        c_print.myprint(f"CKAN NOT COMPATIBLE WITH INPUT URL '{url}'. Trying with {url__}", Color.RED, 0)
        try:
            data_retriever.DataRetriever(url__).try_ckan()
            c_print.myprint(f"CKAN FOUND ON: {url__}", Color.GREEN + Color.BOLD)
            return url__
        except data_retriever.DataRetrieverError:
            c_print.myprint("CKAN NOT COMPATIBLE WITH PORTAL", Color.RED, 0)
            raise data_retriever.DataRetrieverError


def find_id(dataset_id):
    portal_instance = data_retriever.DataRetriever(url)
    portal_dataset = portal_instance.get_package_list()
    if dataset_id not in portal_dataset:
        c_print.myprint("ERROR: ID NOT FOUND ON CKAN INSTANCE", Color.RED)
        return None
    else:
        return dataset_id


def do_work_for_portal():
    try:
        loader_ = loader.Loader(use_cloud, use_geo)
        loader_.load_system_for_portal()

        event = {'type': 'portal', 'portal': url}
        event_bus.event_bus.publish(event)

        database = loader_.get_database()

        known_portals = database.get_portal_list()
        portal_instance = data_retriever.DataRetriever(url)
        if url not in known_portals:
            database.save_portal(url, (portal_name if portal_name else ''))

        database.set_portal_id(url)

        known_dataset = database.get_dataset_list()
        portal_dataset = portal_instance.get_package_list()
        expired_dataset = database.get_expired_datasets_list()
        unknown_dataset = list(set(portal_dataset).difference(known_dataset))
        evaluator_ = evaluator.Evaluator()

        if deepness == 1:
            evaluator_.start_eval(loader_.get_cloud(), database, portal_dataset, portal_instance, loader_.get_geo())
        if deepness == 2:
            evaluator_.start_eval(loader_.get_cloud(), database, expired_dataset, portal_instance, loader_.get_geo())
        elif deepness == 3:
            evaluator_.start_eval(loader_.get_cloud(), database, unknown_dataset, portal_instance, loader_.get_geo())

    except data_retriever.DataRetrieverError:
        c_print.myprint("FATAL ERROR WITH CKAN PORTAL", Color.RED, 2)

    except RuntimeError:
        c_print.myprint("FATAL ERROR WITH CKAN PORTAL", Color.RED, 2)

def do_work_for_dataset(dataset_id):
    try:
        loader_ = loader.Loader(use_cloud, use_geo)
        loader_.load_system_for_portal()

        database = loader_.get_database()

        known_portals = database.get_portal_list()
        portal_instance = data_retriever.DataRetriever(url)
        if url not in known_portals:
            database.save_portal(url, (portal_name if portal_name else ''))

        database.set_portal_id(url)

        evaluator_ = evaluator.Evaluator()
        evaluator_.start_eval(loader_.get_cloud(), database, [dataset_id], portal_instance, loader_.get_geo())

    except data_retriever.DataRetrieverError:
        c_print.myprint("FATAL ERROR WITH CKAN PORTAL", Color.RED, 2)

    except RuntimeError:
        c_print.myprint("FATAL ERROR WITH CKAN PORTAL", Color.RED, 2)


def on_close():
    event_bus.event_bus.publish({'type': 'c_window'})
    event_bus.event_bus.publish({'type': 'forced_closure'})


if __name__ == "__main__":
    session_id = str(datetime.datetime.now()).replace('-', '').replace(' ', '').replace(':', '')[:-7]
    c_print.myprint('WELCOME TO ckanFAIR', Color.CYAN, 0)
    c_print.myprint('SESSION ID: ' + session_id, Color.CYAN)

    c_print.myprint("""
                     .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.  .----------------.                     
                    | .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |                    
                    | | _____  _____ | || |  _________   | || |   _____      | || |     ______   | || |     ____     | || | ____    ____ | || |  _________   | |                    
                    | ||_   _||_   _|| || | |_   ___  |  | || |  |_   _|     | || |   .' ___  |  | || |   .'    `.   | || ||_   \  /   _|| || | |_   ___  |  | |                    
                    | |  | | /\ | |  | || |   | |_  \_|  | || |    | |       | || |  / .'   \_|  | || |  /  .--.  \  | || |  |   \/   |  | || |   | |_  \_|  | |                    
                    | |  | |/  \| |  | || |   |  _|  _   | || |    | |   _   | || |  | |         | || |  | |    | |  | || |  | |\  /| |  | || |   |  _|  _   | |                    
                    | |  |   /\   |  | || |  _| |___/ |  | || |   _| |__/ |  | || |  \ `.___.'\  | || |  \  `--'  /  | || | _| |_\/_| |_ | || |  _| |___/ |  | |                    
                    | |  |__/  \__|  | || | |_________|  | || |  |________|  | || |   `._____.'  | || |   `.____.'   | || ||_____||_____|| || | |_________|  | |                    
                    | |              | || |              | || |              | || |              | || |              | || |              | || |              | |                    
                    | '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |                    
                     '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'                     
                                                 .----------------.  .----------------.                                                                                             
                                                | .--------------. || .--------------. |                                                                                            
                                                | |  _________   | || |     ____     | |                                                                                            
                                                | | |  _   _  |  | || |   .'    `.   | |                                                                                            
                                                | | |_/ | | \_|  | || |  /  .--.  \  | |                                                                                            
                                                | |     | |      | || |  | |    | |  | |                                                                                            
                                                | |    _| |_     | || |  \  `--'  /  | |                                                                                            
                                                | |   |_____|    | || |   `.____.'   | |                                                                                            
                                                | |              | || |              | |                                                                                            
                                                | '--------------' || '--------------' |                                                                                            
                                                 '----------------'  '----------------'                                                                                             
                     .----------------.  .----------------.  .----------------.  .-----------------. .----------------.  .----------------.  .----------------.  .----------------. 
                    | .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. || .--------------. |
                    | |     ______   | || |  ___  ____   | || |      __      | || | ____  _____  | || |  _________   | || |      __      | || |     _____    | || |  _______     | |
                    | |   .' ___  |  | || | |_  ||_  _|  | || |     /  \     | || ||_   \|_   _| | || | |_   ___  |  | || |     /  \     | || |    |_   _|   | || | |_   __ \    | |
                    | |  / .'   \_|  | || |   | |_/ /    | || |    / /\ \    | || |  |   \ | |   | || |   | |_  \_|  | || |    / /\ \    | || |      | |     | || |   | |__) |   | |
                    | |  | |         | || |   |  __'.    | || |   / ____ \   | || |  | |\ \| |   | || |   |  _|      | || |   / ____ \   | || |      | |     | || |   |  __ /    | |
                    | |  \ `.___.'\  | || |  _| |  \ \_  | || | _/ /    \ \_ | || | _| |_\   |_  | || |  _| |_       | || | _/ /    \ \_ | || |     _| |_    | || |  _| |  \ \_  | |
                    | |   `._____.'  | || | |____||____| | || ||____|  |____|| || ||_____|\____| | || | |_____|      | || ||____|  |____|| || |    |_____|   | || | |____| |___| | |
                    | |              | || |              | || |              | || |              | || |              | || |              | || |              | || |              | |
                    | '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' || '--------------' |
                     '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------'  '----------------' 
                    """, Color.CYAN)

    c_print.myprint("You want to enter setup? (Y/N) ", Color.GREEN)
    if input().lower() == 'y':
        settings_mode.run()

    use_cloud = None
    use_geo = None
    deepness = None
    gui_mode = None
    portal_name = None
    mode = None

    while not mode:
        c_print.myprint("Choose the assessment mode:", Color.GREEN)
        print(Color.GREEN + "You want to assess:\n\t1 - an entire portal\n\t2 - a single dataset" + Color.ENDC)
        sel = input()
        if sel in ["1", "2"]:
            mode = int(sel)

    if mode == 1:
        url = None
        while not url:
            c_print.myprint("Enter the portal url", Color.GREEN)
            url = input().strip()
            try:
                url = find_portal(url)
            except Exception as e:
                url = None

        while use_geo is None:
            c_print.myprint("You want to use IPA to geo features? (Y/N | H for help)", Color.GREEN)
            sel = input().lower()
            if sel == 'h':
                print("The holder identifier is used to determine the IPA codes of the holder of the dataset.\n"
                      "This code is used to determine the geocoordinates of the holder for data visualization features\n"
                      "(Only works with italian IPA codes)")
            elif sel == 'y':
                use_geo = True
            elif sel == 'n':
                use_geo = False

        while use_cloud is None:
            c_print.myprint("You want to use cloud features? (Y/N | H for help)", Color.GREEN)
            sel = input().lower()
            if sel == 'h':
                print("This feature save a copy of the metadata and data on a google cloud folder.\n"
                      "It allow the user to check for changes on the (meta)data\n"
                      "(Must be set on .env)")
            elif sel == 'y':
                use_cloud = True
            elif sel == 'n':
                use_cloud = False

        while not deepness:
            c_print.myprint("Choose the deepness of the analysis\n"
                            "\t1 - All datasets on the portal"
                            "\t2 - Only datasets previously analyzed for a time greater than their accrual periodicity"
                            "\t3 - Only new datasets on the portal", Color.GREEN)
            sel = input()
            if sel in ["1", "2" , "3"]:
                deepness = int(sel)

        event = {'type': 'portal', 'portal': url}
        event_bus.event_bus.publish(event)

        app = gui.DatabaseUpdate()

        thread_ = threading.Thread(target=do_work_for_portal)
        thread_.daemon = True
        thread_.start()
        app.protocol("WM_DELETE_WINDOW", lambda: on_close())
        app.mainloop()


    else:
        dataset_id = None
        url = None
        while not url:
            c_print.myprint("Enter the portal url", Color.GREEN)
            url = input().strip()
            try:
                url = find_portal(url)
            except Exception as e:
                pass

        while use_geo is None:
            c_print.myprint("You want to use IPA to geo features? (Y/N | H for help)", Color.GREEN)
            sel = input().lower()
            if sel == 'h':
                print("The holder identifier is used to determine the IPA codes of the holder of the dataset.\n"
                      "This code is used to determine the geocoordinates of the holder for data visualization features\n"
                      "(Only works with italian IPA codes)")
            elif sel == 'y':
                use_geo = True
            elif sel == 'n':
                use_geo = False

        while use_cloud is None:
            c_print.myprint("You want to use cloud features? (Y/N | H for help)", Color.GREEN)
            sel = input().lower()
            if sel == 'h':
                print("This feature save a copy of the metadata and data on a google cloud folder.\n"
                      "It allow the user to check for changes on the (meta)data\n"
                      "(Must be set on .env)")
            elif sel == 'y':
                use_cloud = True
            elif sel == 'n':
                use_cloud = False

        while not dataset_id:
            c_print.myprint("Enter the dataset id")
            sel = input().lower()
            dataset_id = find_id(sel)


        event = {'type': 'portal', 'portal': url}
        event_bus.event_bus.publish(event)

        app = gui.DatabaseUpdate()

        thread_ = threading.Thread(target=do_work_for_dataset, args=(dataset_id,))
        thread_.daemon = True
        thread_.start()
        app.protocol("WM_DELETE_WINDOW", lambda: on_close())
        app.mainloop()

        with open('logs/report2.txt', 'r') as f:
            import json
            results = json.load(f)

        results_gui.display_results(results)


    exit()