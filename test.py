import pandas as pd

excel_path = r"C:\Users\Duiristt\Desktop\Semillero-Protecciones\excel_prueba.xlsx"

df = pd.read_excel(excel_path, sheet_name="Hoja 1")
