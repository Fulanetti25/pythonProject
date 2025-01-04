import tst_json
from tst_prettytable import PrettyTable

value = ['''
       {
           "_id": {
               "$Col1": "XXXXXXX2443"
           },
           "col2": false,
           "col3": "359335050111111",
           "startedAt": {
               "$date": 1633309625000
           },
           "endedAt": {
               "$date": 1633310213000
           },
           "col4": "YYYYYYYYYYYYYYYYYY",
           "created_at": {
               "$date": 1633310846935
           },
           "updated_at": {
               "$date": 1633310846935
           },
           "__v": 0
       }''']

dictionary = json.loads(value[0])
headers = []
values = []
for key in dictionary:
    head = key
    value = ""
    if type(dictionary[key]) == type({}):
        for key2 in dictionary[key]:
            head += "/" + key2
            value = dictionary[key][key2]
            headers.append(head)
            values.append(value)

    else:
        value = dictionary[key]
        headers.append(head)
        values.append(value)

print(headers)
print(values)
myTable = PrettyTable(headers)

myTable.add_row(values)
print(myTable)