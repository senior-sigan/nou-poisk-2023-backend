def read_cities(path):
    last = list()
    dict_city ={}
    with open(path, 'r') as file:
        for i in file:
            i.replace(' ','')
            if  (i!='\n'):
                if i[:1] in last:
                    dict_city[i[:1]].append(i[:-1])
                else: 
                    last.append(i[:1])
                    dict_city[i[:1]] = [i[:-1]]
    return dict_city


DICT_CITY = read_cities('city-data.txt')