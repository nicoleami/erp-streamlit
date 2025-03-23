import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
import seaborn as sns

# Interface Streamlit
def main():
    st.title("ERP Financeiro com Streamlit")
    
    menu = ["Clientes", "Contas a Pagar", "Clientes com maior receita", "Contas a Receber", "Lançamentos", "Relatórios", "Status das Contas a Pagar e Receber", "Comparação Receita vs Despesa"]
    choice = st.sidebar.selectbox("Selecione uma opção", menu)
    conn = sqlite3.connect("erp_finance.db", detect_types=sqlite3.PARSE_DECLTYPES)
    
    if choice == "Clientes":
        st.subheader("Cadastro de Clientes")
        df = pd.read_sql_query("SELECT * FROM clientes", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Pagar":
        st.subheader("Contas a Pagar")
        df = pd.read_sql_query("SELECT * FROM contas_pagar", conn)
        st.dataframe(df)
        
    elif choice == "Contas a Receber":
        st.subheader("Contas a Receber")
        df = pd.read_sql_query("SELECT * FROM contas_receber", conn)
        st.dataframe(df)
        
    elif choice == "Lançamentos":
        st.subheader("Lançamentos Financeiros")
        df = pd.read_sql_query("SELECT * FROM lancamentos", conn)
        st.dataframe(df)
        
    elif choice == "Relatórios":
        st.subheader("Relatório de Fluxo de Caixa")
        df = pd.read_sql_query("SELECT tipo, SUM(valor) as total FROM lancamentos GROUP BY tipo", conn)
        st.dataframe(df)

    elif choice == "Clientes com maior receita":
        st.subheader("Top Clientes com Maior Receita")

        query = """
        SELECT 
            c.id, 
            c.nome, 
            c.email, 
            c.telefone, 
            SUM(cr.valor) AS total_receita
        FROM 
            clientes c
        JOIN 
            contas_receber cr ON c.id = cr.cliente_id
        WHERE 
            cr.status = 'Recebido'
        GROUP BY 
            c.id
        ORDER BY 
            total_receita DESC
        LIMIT 5;
        """
        df = pd.read_sql_query(query, conn)
        st.dataframe(df)

        plt.figure(figsize=(10, 6))
        sns.barplot(x="total_receita", y="nome", data=df, palette="viridis")
        plt.title("Top 5 Clientes com Maior Receita")
        plt.xlabel("Total Receita")
        plt.ylabel("Clientes")
        st.pyplot(plt)
        
    elif choice == "Status das Contas a Pagar e Receber":
        st.subheader("Status das Contas a Pagar e Receber")

        query_pagar = """
        SELECT status, SUM(valor) AS total
        FROM contas_pagar
        GROUP BY status
        """
        query_receber = """
        SELECT status, SUM(valor) AS total
        FROM contas_receber
        GROUP BY status
        """
        
        df_pagar = pd.read_sql_query(query_pagar, conn)
        df_receber = pd.read_sql_query(query_receber, conn)

        df_pagar['tipo'] = 'Contas a Pagar'
        df_receber['tipo'] = 'Contas a Receber'
        df_combined = pd.concat([df_pagar, df_receber])

        st.dataframe(df_combined)

        plt.figure(figsize=(10, 6))
        sns.barplot(x="status", y="total", hue="tipo", data=df_combined, palette="Set2")
        plt.title("Total de Contas Pendentes vs Pagas/Recebidas")
        plt.xlabel("Status")
        plt.ylabel("Total")
        st.pyplot(plt)
        
    elif choice == "Comparação Receita vs Despesa":
        st.subheader("Comparação Receita vs Despesa (Mês Atual)")

        today = datetime.today()
        first_day_of_month = today.replace(day=1)

        next_month = today.replace(day=28) + timedelta(days=4)  
        last_day_of_month = next_month - timedelta(days=next_month.day) 

        query_receita = """
        SELECT SUM(valor) AS total_receita
        FROM lancamentos
        WHERE tipo = 'Receita' AND data BETWEEN ? AND ?
        """
        
        query_despesa = """
        SELECT SUM(valor) AS total_despesa
        FROM lancamentos
        WHERE tipo = 'Despesa' AND data BETWEEN ? AND ?
        """

        df_receita = pd.read_sql_query(query_receita, conn, params=(first_day_of_month, last_day_of_month))
        df_despesa = pd.read_sql_query(query_despesa, conn, params=(first_day_of_month, last_day_of_month))

        total_receita = df_receita['total_receita'].iloc[0] if df_receita['total_receita'].iloc[0] is not None else 0
        total_despesa = df_despesa['total_despesa'].iloc[0] if df_despesa['total_despesa'].iloc[0] is not None else 0

        st.write(f"Total de Receitas no Mês: R${total_receita:,.2f}")
        st.write(f"Total de Despesas no Mês: R${total_despesa:,.2f}")

        plt.figure(figsize=(10, 6))
        categories = ['Receitas', 'Despesas']
        values = [total_receita, total_despesa]
        
        plt.bar(categories, values, color=['green', 'red'])
        plt.title("Comparação Receita vs Despesa - Mês Atual")
        plt.xlabel("Categoria")
        plt.ylabel("Valor (R$)")
        st.pyplot(plt)

    conn.close()
    
if __name__ == "__main__":
    main()
