#TODO: deberiamos usar algo mas liviano que pandas para hacer el import
import pandas

def read_client_list(fn):
    df = pandas.read_excel(fn)
    # Find the first row of the table and set it as headers.

    return df
