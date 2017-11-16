import requests
import xml.etree.ElementTree as etree

TIMEOUT = 5


def main():
    # put your target device list here:
    target_list = ("192.168.1.1",
                   "192.168.1.2"
                )

    device_info = "/upnp/control/deviceinfo1"
    manuf_info = "/upnp/control/manufacture1"
    event_info = "/upnp/control/basicevent1"
    meta_info = "/upnp/control/metainfo1"

    # Some useful things
    #setup_xml="setup.xml"
    #device_xml="deviceinfoservice.xml"
    #event_xml="eventservice.xml"

    #action1="GetDeviceInformation"
    #action2="GetInformation"

    wemo_port = 49153

    verb_device = "GetInformation" #GetInformation, GetDeviceInformation, GetRouterInformation can't get this one to work.
    verb_event = "GetFriendlyName"
    verb_meta = "GetMetaInfo" #GetMetaInfo, GetExtMetaInfo isn't really useful

    data_dev = "<?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:"+verb_device+" xmlns:u=\"urn:Belkin:service:deviceinfo:1\"></u:"+verb_device+"></s:Body></s:Envelope>"
    data_manuf = "<?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:GetManufactureData xmlns:u=\"urn:Belkin:service:manufacture:1\"></u:GetManufactureData></s:Body></s:Envelope>"
    data_event = "<?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:"+verb_event+" xmlns:u=\"urn:Belkin:service:basicevent:1\"></u:"+verb_event+"></s:Body></s:Envelope>"
    data_meta = "<?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:"+verb_meta+" xmlns:u=\"urn:Belkin:service:metainfo:1\"></u:"+verb_meta+"></s:Body></s:Envelope>"

    headers_dev = {
        "Content-Type" : "text/xml; charset=utf-8",
        "SOAPACTION" : "\"urn:Belkin:service:deviceinfo:1#"+verb_device+"\"",
        "Connection" : "keep-alive",
        "Content-Length" : str(len(data_dev))
    }
    headers_manuf = {
        "Content-Type" : "text/xml; charset=utf-8",
        "SOAPACTION" : "\"urn:Belkin:service:manufacture:1#GetManufactureData\"",
        "Connection" : "keep-alive",
        "Content-Length" : str(len(data_dev))
    }
    headers_event = {
        "Content-Type" : "text/xml; charset=utf-8",
        "SOAPACTION" : "\"urn:Belkin:service:basicevent:1#"+verb_event+"\"",
        "Connection" : "keep-alive",
        "Content-Length" : str(len(data_dev))
    }
    headers_meta = {
        "Content-Type": "text/xml; charset=utf-8",
        "SOAPACTION": "\"urn:Belkin:service:metainfo:1#" + verb_meta + "\"",
        "Connection": "keep-alive",
        "Content-Length": str(len(data_dev))
    }
    # GetFriendlyName just returns friendly name
    #GetSmartDevInfo was a dud. GetHomeInfo returns some base64 encoded blob. maybe creds

    for i in target_list:
        try:
            r_dev = requests.post("http://{}:{}{}".format(i, wemo_port, device_info), headers=headers_dev, data=data_dev,
                                  stream=True, timeout=TIMEOUT)
            #r_man = requests.post("http://{}:{}{}".format(i, wemo_port, manuf_info), headers=headers_manuf,
            #                      data=data_manuf, stream=True, timeout=TIMEOUT)
            #r_event = requests.post("http://{}:{}{}".format(i, wemo_port, event_info), headers=headers_event,
            #                          data=data_event, stream=True, timeout=TIMEOUT)
            r_meta = requests.post("http://{}:{}{}".format(i, wemo_port, meta_info), headers=headers_meta,
                                    data=data_meta, stream=True, timeout=TIMEOUT)

        except requests.exceptions.Timeout:
            continue
        except requests.exceptions.ConnectionError:
            continue
        parse_wemo_xml_dev(r_dev, i, verb_device)
        #parse_wemo_xml_manuf(r_man, i)
        #parse_wemo_xml_event(r_event, i)
        parse_wemo_xml_meta(r_meta, i, verb_meta)

def parse_wemo_xml_dev(resp, ip, verb):
    tree = etree.parse(resp.raw)
    root = tree.getroot()
    if root is not None:
        info = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        if info is None:
            return
        if verb == "GetInformation":
            info = info.find('{urn:Belkin:service:deviceinfo:1}GetInformationResponse')
            if info is None:
                return
            info = info.find('Information')
            tree2 = etree.fromstring(info.text)

            fw = tree2.find('DeviceInformation').find('firmwareVersion').text
            product = tree2.find('DeviceInformation').find('productName').text
            full = tree2.find('DeviceInformation').find('FriendlyName').text
            print("[*] found a {} of type {} at ?.?.{} with version {}".format(full, product, ".".join(ip.split(".")[-2:]), fw))

def parse_wemo_xml_manuf(resp, ip):
    tree = etree.parse(resp.raw)
    root = tree.getroot()
    if root is not None:
        info = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        if info is None:
            return
        info = info.find('{urn:Belkin:service:manufacture:1}GetManufactureDataResponse')
        if info is None:
            return
        #TODO: parse this out
        info = info.find('Information')
        if info is None:
            return
        tree2 = etree.fromstring(info.text)

        fw = tree2.find('DeviceInformation').find('firmwareVersion').text
        product = tree2.find('DeviceInformation').find('productName').text
        full = tree2.find('DeviceInformation').find('FriendlyName').text
        print("[*] found a {} of type {} at ?.?.{} with version {}".format(full, product, ".".join(ip.split(".")[-2:]), fw))

def parse_wemo_xml_event(resp, ip):
    tree = etree.parse(resp.raw)
    root = tree.getroot()
    if root is not None:
        info = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        if info is None:
            return
        info = info.find('{urn:Belkin:service:deviceinfo:1}GetInformationResponse')
        if info is None:
            return
        info = info.find('Information')
        tree2 = etree.fromstring(info.text)

        fw = tree2.find('DeviceInformation').find('firmwareVersion').text
        product = tree2.find('DeviceInformation').find('productName').text
        full = tree2.find('DeviceInformation').find('FriendlyName').text
        print("[*] found a {} of type {} at ?.?.{} with version {}".format(full, product, ".".join(ip.split(".")[-2:]), fw))

def parse_wemo_xml_meta(resp, ip, verb):
    tree = etree.parse(resp.raw)
    root = tree.getroot()
    if root is not None:
        info = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
        if info is None:
            return

        if verb == "GetMetaInfo":
            info = info.find('{urn:Belkin:service:metainfo:1}GetMetaInfoResponse')
            if info is None:
                return
            info = info.find('MetaInfo')
            meta = info.text.split('|')
            serial = meta[1]
            cat = meta[2]
            fw = meta[3]
            name = meta[4]
            type = meta[5]

            print("[*] found a {} category {} at ?.?.{} named with version {} and serial {}".format(cat, type, ".".join(ip.split(".")[-2:]), name, fw, serial))


if __name__ == "__main__":
    main()


