import argparse
import datetime
import threading
from urllib.parse import urlparse

import data_retriever
import event_bus
import gui
import loader
from assessment import evaluator
from console_print import c_print, MyColors as Color


def find_portal(url):
    print(urlparse(url).scheme)
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
            return url__
        except data_retriever.DataRetrieverError:
            c_print.myprint("CKAN NOT COMPATIBLE WITH PORTAL", Color.RED, 0)
            raise data_retriever.DataRetrieverError


def do_work_for_portal():
    try:
        loader_ = loader.Loader(use_cloud, use_geo)
        loader_.load_system_for_portal()

        event = {'type': 'portal', 'portal': (portal_name if portal_name != 'none' else portal_id)}
        event_bus.event_bus.publish(event)

        database = loader_.get_database()

        known_portals = database.get_portal_list()
        portal_instance = data_retriever.DataRetriever(portal_id)
        if portal_id not in known_portals:
            database.save_portal(portal_id, (portal_name if portal_name else ''))

        database.set_portal_id(portal_id)

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


def on_close():
    event_bus.event_bus.publish({'type': 'c_window'})
    event_bus.event_bus.publish({'type': 'forced_closure'})


if __name__ == "__main__":
    session_id = str(datetime.datetime.now()).replace('-', '').replace(' ', '').replace(':', '')[:-7]
    c_print.myprint('WELCOME TO euFAIR', Color.CYAN, 0)
    c_print.myprint('SESSION ID: ' + session_id, Color.CYAN)

    parser = argparse.ArgumentParser(
        description='Lo script permette la valutazione della FAIRness dei dataset di un portale compatibile CKAN')

    parser.add_argument('--entity', type=str, default='portale',
                        help='Modalità da usare: "dataset" (singolo dataset per cui viene generato un report) '
                             'o "portale". Opzionale, default portale')
    parser.add_argument('--url', type=str, required=True,
                        help='Url(path) del portale(dataset) da analizzare')
    parser.add_argument('--cloud', type=bool, default=False,
                        help='Specifica se utilizzare o meno il sistema di cloud '
                             'per la conservarzione delle copie dei metadati e il confronto con i nuovi')
    parser.add_argument('--geo', type=bool, default=False,
                        help='Specifica se calcolare e salvare le informazioni geospaziali degli holder'
                             'Compatibile solo con holder che hanno come id il codice IPA')
    parser.add_argument('--deepness', type=int, default=1,
                        help="Specifica la profondità dell'analisi. "
                             "1. Tutti i dataset del portale | "
                             "2. Solo i dataset con accPeriodicity scaduta | "
                             "3 solo i nuovi dataset")
    parser.add_argument('--gui', type=bool, default=True,
                        help='Specifica se visualizzare o meno un interfaccia grafica sullo stato della valutazione')
    parser.add_argument('--name', type=str, default='none',
                        help='Salva il portale con un nome a scelta')
    args = parser.parse_args()

    entity = args.entity

    if entity == 'portale':
        portal_id = find_portal(args.url)
        use_cloud = args.cloud
        use_geo = args.geo
        deepness = args.deepness
        gui_mode = args.gui
        portal_name = args.name
        event = {'type': 'portal', 'portal': (portal_name if portal_name != 'none' else portal_id)}
        event_bus.event_bus.publish(event)
        event = {'type': 'portal', 'portal': 'ciao'}
        event_bus.event_bus.publish(event)

        if gui_mode:
            app = gui.DatabaseUpdate()

            thread_ = threading.Thread(target=do_work_for_portal)
            thread_.daemon = True
            thread_.start()
            app.protocol("WM_DELETE_WINDOW", lambda: on_close())
            app.mainloop()
        else:
            do_work_for_portal()

    elif entity == 'dataset':
        pass