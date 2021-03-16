import yaml

def intersection(lst1, lst2):
    """Recibe dos objetos iterables y devuelve una lista los elementos
    con los elementos en común entre ambos.
    """
    temp = set(lst2)
    lst3 = [value for value in lst1 if value in temp]
    return lst3

def difference(lst1, lst2):
    """Recibe dos objetos iterables y devuelve una lista con los elementos
    que son únicos entre ambos.
    """
    set1 = set(lst1)
    set2 = set(lst2)
    return list((set1 - set2).union(set2 - set1))

def pretty_str(elem):
    """Transforma elem en un string con formato 'lindo'.
    """
    return yaml.dump(elem, default_flow_style=False)
