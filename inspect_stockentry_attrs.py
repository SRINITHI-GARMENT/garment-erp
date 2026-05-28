from app import StockEntry
print('colour_text attr type:', type(StockEntry.__dict__['colour_text']).__name__)
print('dia_text attr type:', type(StockEntry.__dict__['dia_text']).__name__)
print('colour_text attr repr:', repr(getattr(StockEntry, 'colour_text')))
print('dia_text attr repr:', repr(getattr(StockEntry, 'dia_text')))
print('colour attr repr:', repr(getattr(StockEntry, 'colour')))
print('dia attr repr:', repr(getattr(StockEntry, 'dia')))
