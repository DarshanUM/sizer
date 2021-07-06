from xml.etree import ElementTree as ET
import requests
from math import ceil
from datetime import datetime
import logging.config
import os
logger = logging.getLogger(__name__)


def fetch_layout(hyper_node, comp_node, hyper_count, comp_count, fi_opt):

    if int(hyper_count) + int(comp_count) > 25:
        wiring = False
    else:
        wiring = True

    if hyper_node['disk_cage'] == 'LFF' or hyper_node['subtype'] == 'veeam':
        model_name = "C245L"
    else:
        model_name = 'HX'

        if '220' in hyper_node['name']:
            model_name += '22'
        elif '240' in hyper_node['name']:
            model_name += '24'
        else:
            logger.error('Unknown node model - %s in UCS layout' % hyper_node['name'])
            return []

        if 'M5' in hyper_node['name']:
            model_name += '5'
        else:
            logger.error('Unknown node model - %s in UCS layout' % hyper_node['name'])
            return []

        if 'all-flash' in hyper_node['subtype'] or 'epic' in hyper_node['subtype']:
            model_name += 'F'
        elif 'hyperconverged' in hyper_node['subtype']:
            model_name += 'H'
        elif 'allnvme' in hyper_node['subtype']:
            model_name += 'N'
        elif 'robo' in hyper_node['subtype'] or 'robo_allflash' in hyper_node['subtype']:
            model_name += 'E'
        else:
            model_name += 'H'

    seqno = datetime.now().strftime('%H%M')
    layout = ET.Element('layout', attrib={"mode": "AUTO",
                                          "src": "HXS",
                                          "seq": seqno
                                          })

    if fi_opt:
        fi_translate = {'HX-FI-48P': 'FI6248',
                        'HX-FI-6332': 'FI6332',
                        'HX-FI-6332-16UP': 'FI6340',
                        'HX-FI-6454': 'FI6454',
                        'HX-FI-96P': 'FI6296'}

        try:
            fi_opt = fi_translate[fi_opt]
        except KeyError:
            logger.error('Unknown FI model %s in UCS layout' % fi_opt)
            return []

        ET.SubElement(layout, 'fabint', {"model": fi_opt, "qty": "2"})

    rackmount = ET.SubElement(layout, 'rackmount')

    ET.SubElement(rackmount, 'server', {"model": model_name, "qty": str(hyper_count)})

    if comp_node and comp_count:
        if 'B200' in comp_node['name']:
            model_name = 'B205'

            for blades in range(0, int(ceil(comp_count / 8.0))):
                chassis = ET.SubElement(layout, 'chassis', {"model": "UCS5108", "cfg": str(blades + 1), "qty": "1"})
                ET.SubElement(chassis, 'blade', {"model": model_name, "qty": str(min(comp_count, 8))})
                ET.SubElement(chassis, 'power', {"qty": "4"})
                comp_count -= 8

        else:

            model_name = 'C'

            if '220' in comp_node['name']:
                model_name += '22'
            elif '240' in comp_node['name']:
                model_name += '24'
            elif '480' in comp_node['name']:
                model_name += "48"
            else:
                logger.error('Unknown compute node model %s in UCS layout' % comp_node['name'])
                return []

            if 'M5' in comp_node['name']:
                model_name += '5'
            else:
                logger.error('Unknown compute node model %s in UCS layout' % comp_node['name'])
                return []

            if comp_node['subtype'] == 'aiml':
                model_name += "A"
            else:
                model_name += 'S'
            ET.SubElement(rackmount, 'server', {"model": model_name, "qty": str(comp_count)})

    # ET.SubElement(layout, 'params', {"extra": "0",
    #                                  "face": "FRONT",
    #                                  "fill": "LINEAR",
    #                                  "size": "MEDIUM",
    #                                  "trans": "NO",
    #                                  "format": "OVERLAY"})

    ET.SubElement(layout, 'params', {"ru": "30",
                                     "bezel": "YES",
                                     "format": "OVERLAY"})

    xmldata = '<?xml version="1.0" encoding="UTF-8"?>' + ET.tostring(layout)

    # Cisco Ucstools link, for proper billing.
    if 'SIZER_INSTANCE' in os.environ:
        base_url = "http://ucstools.cisco.com/ucs/engine/ucs-%s.cgi"
        headers = {
            'host': "ucstools.cisco.com",
            'content-type': "text/xml",
            'connection': "close"
        }
    else:
        # Willem URL link-Used only in Local setup as can't get UCS images without Cisco VPN
        base_url = "http://ucs4.us/ucs/engine/ucs-%s.cgi"
        headers = {
            'host': "ucs4.us",
            'content-type': "text/xml",
            'connection': "close"
        }

    url_responses = list()
    url_resp = requests.request("POST", base_url % 'engine', data=xmldata, headers=headers)
    if url_resp.status_code == 200 and len(url_resp.headers["content-length"]) > 0:
        url_responses.append(url_resp)
    else:
        logger.error('layout/wiring API failed. kindly check the XML code %s' % xmldata)

    if wiring:

        logger.info('The XML code for layout/wiring API %s: %s' % (base_url, xmldata))
        url_resp = requests.request("POST", base_url % 'wiring', data=xmldata, headers=headers)
        if url_resp.status_code == 200 and len(url_resp.headers["content-length"]) > 0:
            url_responses.append(url_resp)
        else:
            logger.error('layout/wiring API failed. kindly check the XML code %s' % xmldata)

        if any(url_resp.status_code != 200 or not url_resp.headers["content-length"] for url_resp in url_responses):
            logger.error('layout/wiring API failed. kindly check the XML code %s' % xmldata)
            return []

    return [url_resp.url for url_resp in url_responses]
