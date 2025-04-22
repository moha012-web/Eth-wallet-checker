import requests
import pandas as pd
import streamlit as st

API_KEY = st.secrets["API_KEY"]
BASE_URL = "https://api.etherscan.io/api"

def get_balance(address):
    params = {
        "module": "account",
        "action": "balance",
        "address": address,
        "tag": "latest",
        "apikey": API_KEY
    }
    try:
        response = requests.get(BASE_URL, params=params, timeout=10)
        if response.status_code == 200 and response.json()["status"] == "1":
            balance_wei = int(response.json()["result"])
            return balance_wei / 10**18
    except Exception as e:
        st.error(f"Error al consultar {address}: {e}")
    return 0

def check_old_wallets(file):
    df = pd.read_csv(file)
    results = []
    for address in df["Address"]:
        address = address.strip()
        if address:
            balance = get_balance(address)
            if balance > 0:
                results.append({"Address": address, "Balance (ETH)": balance})
    return pd.DataFrame(results)

st.set_page_config(page_title="Buscador Ético de Wallets", layout="centered")
st.title("Buscador Ético de Wallets (Demo)")

st.markdown("""
Esta aplicación permite subir un archivo CSV con direcciones de Ethereum y busca cuáles aún tienen fondos.  
Ideal para auditar wallets antiguas u olvidadas.
""")

uploaded_file = st.file_uploader("Sube un archivo CSV con una columna llamada 'Address':", type="csv")

if uploaded_file:
    with st.spinner("Consultando balances..."):
        results_df = check_old_wallets(uploaded_file)
    if not results_df.empty:
        st.success("¡Se encontraron wallets con fondos!")
        st.dataframe(results_df)
        st.download_button("Descargar resultados", results_df.to_csv(index=False), "wallets_con_fondos.csv", "text/csv")
    else:
        st.info("No se encontraron wallets con fondos.")
