import os
import readRawData
import xml.dom
import xml.dom.minidom

def makeXML(db):
    impl = xml.dom.minidom.getDOMImplementation()
    xmlOut = impl.createDocument(None, 'EPICS_PVs', None)
    docElement = xmlOut.documentElement
    for pv, fields in db.items():
        pvElement = xmlOut.createElement('EPICS_PV')
        docElement.appendChild(pvElement)
        pvElement.setAttribute('name', pv)
        if fields.has_key('DMOV'):
            pvElement.setAttribute('dtyp', 'motor')
        if fields.has_key('CNT') & fields.has_key('TP'):
            pvElement.setAttribute('dtyp', 'scaler')
        for field, value in fields.items():
            fieldElement = xmlOut.createElement('field')
            pvElement.appendChild(fieldElement)
            fieldElement.setAttribute('name', field)
            #text = xmlOut.createTextNode('%s.%s = %s' % (pv, field, value))
            text = xmlOut.createTextNode(value)
            fieldElement.appendChild(text)
    return xmlOut

if __name__ == '__main__':
    db = readRawData.readRawData('rawdata.txt')
    result = makeXML(db)
    #print the result using a supplied formatter
    print result.toprettyxml()

