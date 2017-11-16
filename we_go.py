import requests
import xml.etree.ElementTree as etree

TIMEOUT = 5


def main():
    # put your target device list here:
    target_list = ("192.168.1.1",
                   "192.168.1.2"
                )

    device_info = "/upnp/control/deviceinfo1"

    # Some useful things
    #setup_xml="setup.xml"
    #device_xml="deviceinfoservice.xml"
    #event_xml="eventservice.xml"

    #action1="GetDeviceInformation"
    #action2="GetInformation"

    wemo_port = 49153

    data = "<?xml version=\"1.0\" encoding=\"utf-8\"?><s:Envelope xmlns:s=\"http://schemas.xmlsoap.org/soap/envelope/\" s:encodingStyle=\"http://schemas.xmlsoap.org/soap/encoding/\"><s:Body><u:GetInformation xmlns:u=\"urn:Belkin:service:deviceinfo:1\"></u:GetInformation></s:Body></s:Envelope>"

    headers = {
        "Content-Type" : "text/xml; charset=utf-8",
        "SOAPACTION" : "\"urn:Belkin:service:deviceinfo:1#GetInformation\"",
        "Connection" : "keep-alive",
        "Content-Length" : str(len(data))
    }

    for i in target_list:
        try:
            r = requests.post("http://{}:{}{}".format(i, wemo_port, device_info), headers=headers, data=data, stream=True, timeout=TIMEOUT)
        except requests.exceptions.Timeout:
            continue
        tree = etree.parse(r.raw)
        root = tree.getroot()
        if root is not None:
            info = root.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
            if info is None:
                continue
            info = info.find('{urn:Belkin:service:deviceinfo:1}GetInformationResponse')
            if info is None:
                continue
            info = info.find('Information')
            tree2 = etree.fromstring(info.text)

            fw = tree2.find('DeviceInformation').find('firmwareVersion').text
            product = tree2.find('DeviceInformation').find('productName').text
            full = tree2.find('DeviceInformation').find('FriendlyName').text
            print("[*] found a {} of type {} at ?.?.{} with version {}".format(full, product, ".".join(i.split(".")[-2:]), fw))

if __name__ == "__main__":
    main()
