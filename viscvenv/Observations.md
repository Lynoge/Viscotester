Quando rodar o programa, fazer as leituras na estrutura de dict com as RPM como keys e as viscosidades como listas de cada key.

Ex:

leituras = {1: [100, 200, 100, 150, 250, 100, 150], 1.5: [50, 70, 60, 50, 60, 80, 70, 60], 2: [40, 50, 40, 35, 55, 40, 45]}

E no processamento, usar este modelo de algoritmo:
for value in leituras.values():
    for item in value:
        if item < mean or item > mean:
            value.remove(item)
