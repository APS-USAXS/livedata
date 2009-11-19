import os


def readRawData(fileName):
    db = {}
    try:
        # try to open the named file
        f = open(fileName, 'r')
    except:
        # if that fails, then return an empty database, caller has to handle it
        return db
    for line in f:
        fullpv = line.strip().split()[0]
        value = line[len(fullpv):-1].strip()
        if len(fullpv.split('.')) == 1:
            pv = fullpv
            field = 'VAL'
        else:
            pv, field = fullpv.split('.')
        if db.has_key(pv) == False:
            db[pv] = {}
        db[pv][field] = value
    f.close()
    return db

if __name__ == '__main__':
    db = readRawData('rawdata.txt')
    # print the result in a simple indented format
    for pv in db:
        print pv
        for field in db[pv]:
            print '', field, db[pv][field]