from flask import Flask, render_template, request
from datetime import datetime
import csv
import os
import logging

app = Flask(__name__)

# Configurar logging
logging.basicConfig(level=logging.INFO)

def calcular_pontuacao(data_abertura, quantidade_socios, troca_socios, score_credito, restricao_nome_socios, cheque_devolvido, spc_serasa, protesto, historico_faturamento, historico_atraso, historico_compras, sugestao_limite, valor_compra_desejado):
    pontuacao = 0
    motivos_positivos = []
    motivos_negativos = []

    hoje = datetime.now()
    data_abertura = datetime.strptime(data_abertura, '%Y-%m-%d')
    tempo_existencia = (hoje - data_abertura).days / 365

    if tempo_existencia < 2:
        pontuacao -= 5
        motivos_negativos.append("Tempo de existência da empresa menor que 2 anos.")
    else:
        pontuacao += 10
        motivos_positivos.append("Tempo de existência da empresa maior ou igual a 2 anos.")

    if quantidade_socios < 1:
        pontuacao -= 10
        motivos_negativos.append("Quantidade de sócios menor que 1.")
    elif quantidade_socios >= 2:
        pontuacao += 10
        motivos_positivos.append("Quantidade de sócios maior ou igual a 2.")

    if troca_socios:
        if quantidade_socios == 1:
            pontuacao -= 10
            motivos_negativos.append("Troca de sócios e quantidade de sócios igual a 1.")
        elif quantidade_socios >= 2:
            pontuacao -= 5
            motivos_negativos.append("Troca de sócios e quantidade de sócios maior ou igual a 2.")

    if score_credito <= 300:
        pontuacao -= 20
        motivos_negativos.append("Score de crédito muito baixo (0 a 300).")
    elif score_credito <= 500:
        pontuacao -= 10
        motivos_negativos.append("Score de crédito regular (301 a 500).")
    elif score_credito <= 700:
        pontuacao += 5
        motivos_positivos.append("Score de crédito bom (501 a 700).")
    else:
        pontuacao += 20
        motivos_positivos.append("Score de crédito excelente (701 a 1000).")

    if restricao_nome_socios:
        pontuacao -= 10
        motivos_negativos.append("Restrição no nome dos sócios.")
    if cheque_devolvido:
        pontuacao -= 10
        motivos_negativos.append("Cheque devolvido.")
    if spc_serasa:
        pontuacao -= 15
        motivos_negativos.append("Restrições no SPC/Serasa.")
    if protesto:
        pontuacao -= 10
        motivos_negativos.append("Protesto.")
    if historico_faturamento:
        pontuacao += 10
        motivos_positivos.append("Histórico de faturamento positivo.")
    if historico_atraso:
        pontuacao -= 10
        motivos_negativos.append("Histórico de atrasos.")
    if historico_compras:
        pontuacao += 10
        motivos_positivos.append("Histórico de compras positivo.")
    if valor_compra_desejado > sugestao_limite:
        pontuacao -= 10
        motivos_negativos.append("Valor de compra desejado maior que o limite sugerido.")
    else:
        pontuacao += 5
        motivos_positivos.append("Valor de compra desejado dentro do limite sugerido.")

    return pontuacao, motivos_positivos, motivos_negativos

def classificar_risco(pontuacao):
    if pontuacao <= 0:
        return "Alto"
    elif pontuacao <= 20:
        return "Médio"
    else:
        return "Baixo"

def salvar_historico(cliente, cnpj, pontuacao, risco, motivos_positivos, motivos_negativos):
    try:
        os.makedirs('data', exist_ok=True)
        file_path = os.path.join('data', 'historico_analises.csv')

        file_exists = os.path.isfile(file_path)

        with open(file_path, mode='a', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            if not file_exists:
                writer.writerow(["Data", "Cliente", "CNPJ", "Pontuação", "Risco", "Motivos Positivos", "Motivos Negativos"])
            writer.writerow([datetime.now(), cliente, cnpj, pontuacao, risco, '; '.join(motivos_positivos), '; '.join(motivos_negativos)])
        logging.info(f"Dados salvos em: {file_path}")
    except Exception as e:
        logging.error(f"Erro ao salvar o histórico: {e}")

@app.route('/', methods=['GET', 'POST'])
def index():
    pontuacao = None
    risco = None
    motivos_positivos = None
    motivos_negativos = None

    if request.method == 'POST':
        cliente = request.form['cliente']
        cnpj = request.form['cnpj']
        data_abertura = request.form['data_abertura']
        quantidade_socios = int(request.form['quantidade_socios'])
        troca_socios = int(request.form['troca_socios']) == 1
        score_credito = int(request.form['score_credito'])
        restricao_nome_socios = request.form['restricao_nome_socios'] == 'Sim'
        cheque_devolvido = request.form['cheque_devolvido'] == 'Sim'
        spc_serasa = request.form['spc_serasa'] == 'Sim'
        protesto = request.form['protesto'] == 'Sim'
        historico_faturamento = request.form.get('historico_faturamento') == 'Sim'
        historico_atraso = request.form.get('historico_atraso') == 'Sim'
        historico_compras = request.form.get('historico_compras') == 'Sim'
        sugestao_limite = float(request.form['sugestao_limite'])
        valor_compra_desejado = float(request.form['valor_compra_desejado'])

        pontuacao, motivos_positivos, motivos_negativos = calcular_pontuacao(data_abertura, quantidade_socios, troca_socios, score_credito, restricao_nome_socios,
                                                cheque_devolvido, spc_serasa, protesto, historico_faturamento, historico_atraso,
                                                historico_compras, sugestao_limite, valor_compra_desejado)

        risco = classificar_risco(pontuacao)
        salvar_historico(cliente, cnpj, pontuacao, risco, motivos_positivos, motivos_negativos)

    return render_template('index.html', pontuacao=pontuacao, risco=risco, motivos_positivos=motivos_positivos, motivos_negativos=motivos_negativos)

@app.route('/historico')
def historico():
    file_path = os.path.join('data', 'historico_analises.csv')
    historico = []
    try:
        with open(file_path, mode='r', newline='', encoding='utf-8') as file:
            reader = csv.reader(file)
            for row in reader:
                historico.append(row)
    except FileNotFoundError:
        logging.error(f"Arquivo não encontrado: {file_path}")
    return render_template('historico.html', historico=historico)

if __name__ == '__main__':
    app.run(debug=True)
