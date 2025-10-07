import pandas as pd

ctk = pd.read_csv('C:\\Users\\Morningside\\MetaDataCreator\\data\\CTK.csv')
fnd = pd.read_csv('C:\\Users\\Morningside\\MetaDataCreator\\data\\FND.csv')
print(ctk[['Identifier (add 4 zeros) no extension', 'Title']].info())
print(fnd[['Identifier', 'Title']].info())