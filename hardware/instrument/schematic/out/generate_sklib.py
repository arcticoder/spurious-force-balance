from collections import defaultdict
from skidl import Pin, Part, Alias, SchLib, SKIDL, TEMPLATE

from skidl.pin import pin_types

SKIDL_lib_version = '0.0.1'

generate = SchLib(tool=SKIDL).add_parts(*[
        Part(**{ 'name':'SM04B-SRSS-TB', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'SM04B-SRSS-TB'}), 'ref_prefix':'CN', 'fplist':['jlc:CONN-SMD_4P-P1.00_SM04B-SRSS-TB-LF-SN'], 'footprint':'jlc:CONN-SMD_4P-P1.00_SM04B-SRSS-TB-LF-SN', 'keywords':'Wire To Board / Wire To Wire Connector', 'description':'', 'datasheet':'https://lcsc.com/product-detail/Others_JST-Sales-America__JST-Sales-America-SM04B-SRSS-TB-LF-SN_C160404.html', 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE),
            Pin(num='3',name='3',func=pin_types.PASSIVE),
            Pin(num='4',name='4',func=pin_types.PASSIVE),
            Pin(num='5',name='5',func=pin_types.PASSIVE),
            Pin(num='6',name='6',func=pin_types.PASSIVE)], 'unit_defs':[] }),
        Part(**{ 'name':'TMP117AIDRVR', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'TMP117AIDRVR'}), 'ref_prefix':'U', 'fplist':['jlc:WSON-6_L2.0-W2.0-P0.65-TL-EP'], 'footprint':'jlc:WSON-6_L2.0-W2.0-P0.65-TL-EP', 'keywords':'Temperature Sensors', 'description':'', 'datasheet':'https://www.lcsc.com/datasheet/C699536.pdf', 'pins':[
            Pin(num='1',name='SCL',func=pin_types.INPUT),
            Pin(num='2',name='GND',func=pin_types.PWRIN),
            Pin(num='3',name='ALERT',func=pin_types.OUTPUT),
            Pin(num='4',name='ADD0',func=pin_types.INPUT),
            Pin(num='5',name='V+',func=pin_types.PWRIN),
            Pin(num='6',name='SDA',func=pin_types.BIDIR),
            Pin(num='7',name='EP',func=pin_types.PWRIN)], 'unit_defs':[] }),
        Part(**{ 'name':'CC0603KRX7R9BB104', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'CC0603KRX7R9BB104'}), 'ref_prefix':'C', 'fplist':['jlc:C0603'], 'footprint':'jlc:C0603', 'keywords':'Multilayer Ceramic Capacitors MLCC - SMD/SMT', 'description':'', 'datasheet':'https://lcsc.com/product-detail/Multilayer-Ceramic-Capacitors-MLCC-SMD-SMT_100nF-104-10-50V_C14663.html', 'pins':[
            Pin(num='1',name='1',func=pin_types.PASSIVE),
            Pin(num='2',name='2',func=pin_types.PASSIVE)], 'unit_defs':[] }),
        Part(**{ 'name':'PWR_FLAG', 'dest':TEMPLATE, 'tool':SKIDL, 'aliases':Alias({'PWR_FLAG'}), 'ref_prefix':'#FLG', 'fplist':[''], 'footprint':'', 'keywords':'flag power', 'description':'', 'datasheet':'~', 'pins':[
            Pin(num='1',name='pwr',func=pin_types.PWROUT)], 'unit_defs':[] })])