from flask import Flask, render_template, request
from datetime import datetime
import csv

app = Flask(__name__)

# Função para calcular a pontuação com base nos critérios fornecidos
def calcular_pontuacao(data_abertura, quantidade_socios, troca_socios, score_credito, restricao_nome_socios, cheque_devolvido, spc_serasa, protesto, historico_faturamento, historico_atraso, historico_compras, sugestao_limite, valor_compra_desejado):
    pontuacao = 0
    motivos_positivos = []
    motivos_negativos = []

    # Calcular tempo de existência da empresa
    hoje = datetime.now()
    data_abertura = datetime.strptime(data_abertura, '%Y-%m-%d')
    tempo_existencia = (hoje - data_abertura).days / 365  # Em anos

    # Data de Abertura da Empresa
    if tempo_existencia < 2:
        pontuacao -= 5
        motivos_negativos.append("Tempo de existência da empresa menor que 2 anos.")
    else:
        pontuacao += 10
        motivos_positivos.append("Tempo de existência da empresa maior ou igual a 2 anos.")

    # Quantidade de Sócios
    if quantidade_socios < 1:
        pontuacao -= 10
        motivos_negativos.append("Quantidade de sócios menor que 1.")
    elif quantidade_socios >= 2:
        pontuacao += 10
        motivos_positivos.append("Quantidade de sócios maior ou igual a 2.")

    # Troca de Sócios
    if troca_socios:
        if quantidade_socios == 1:
            pontuacao -= 10
            motivos_negativos.append("Troca de sócios e quantidade de sócios igual a 1.")
        elif quantidade_socios >= 2:
            pontuacao -= 5
            motivos_negativos.append("Troca de sócios e quantidade de sócios maior ou igual a 2.")

    # Score de Crédito
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

    # Restrição no Nome dos Sócios
    if restricao_nome_socios:
        pontuacao -= 10
        motivos_negativos.append("Restrição no nome dos sócios.")
    else:
        pontuacao += 5
        motivos_positivos.append("Sem restrição no nome dos sócios.")

    # Cheque Devolvido
    if cheque_devolvido:
        pontuacao -= 10
        motivos_negativos.append("Cheque devolvido.")
    else:
        pontuacao += 5
        motivos_positivos.append("Sem cheque devolvido.")

    # Restrição SPC/Serasa
    if spc_serasa:
        pontuacao -= 20
        motivos_negativos.append("Restrição no SPC/Serasa.")
    else:
        pontuacao += 10
        motivos_positivos.append("Sem restrição no SPC/Serasa.")

    # Protesto
    if protesto:
        pontuacao -= 10
        motivos_negativos.append("Protesto registrado.")
    else:
        pontuacao += 5
        motivos_positivos.append("Sem protesto registrado.")

    # Histórico de Faturamento
    if historico_faturamento:
        pontuacao += 10
        motivos_positivos.append("Histórico de faturamento positivo.")

    # Histórico de Atraso
    if historico_atraso:
        pontuacao -= 10
        motivos_negativos.append("Histórico de atraso.")
    else:
        pontuacao += 10
        motivos_positivos.append("Sem histórico de atraso.")

    # Histórico de Compras Conosco
    if historico_compras:
        pontuacao += 10
        motivos_positivos.append("Histórico de compras conosco.")

    # Comparação com Sugestão de Limite
    if sugestao_limite < valor_compra_desejado:
        pontuacao -= 10
        motivos_negativos.append("Sugestão de limite menor que o valor de compra desejado.")
    else:
        pontuacao += 10
        motivos_positivos.append("Sugestão de limite maior ou igual ao valor de compra desejado.")

    return pontuacao, motivos_positivos, motivos_negativos

# Função para classificar o risco com base na pontuação
def classificar_risco(pontuacao):
    if pontuacao >= 70:
        return "Liberado"
    elif 40 <= pontuacao < 70:
        return "Requer revisão adicional"
    else:
        return "Recusado"

# Função para salvar o histórico de análises no arquivo CSV
def salvar_historico(cliente, pontuacao, risco, motivos_positivos, motivos_negativos):
    arquivo_csv = '/historico_analises.csv'  # Caminho absoluto do arquivo CSV
    with open(arquivo_csv, mode='a', newline='') as file:
        writer = csv.writer(file)
        writer.writerow([datetime.now(), cliente, pontuacao, risco, '; '.join(motivos_positivos), '; '.join(motivos_negativos)])

# Rota principal para o formulário de análise de crédito
@app.route('/', methods=['GET', 'POST'])
def index():
    pontuacao = None
    risco = None
    motivos_positivos = None
    motivos_negativos = None

    if request.method == 'POST':
        # Obter dados do formulário
        cliente = request.form['cliente']
        data_abertura = request.form['data_abertura']
        quantidade_socios = int(request.form['quantidade_socios'])
        troca_socios = int(request.form['troca_socios']) == 1  # Convertendo para booleano
        score_credito = int(request.form['score_credito'])
        restricao_nome_socios = request.form['restricao_nome_socios'] == 'Sim'  # Convertendo para booleano
        cheque_devolvido = request.form['cheque_devolvido'] == 'Sim'  # Convertendo para booleano
        spc_serasa = request.form['spc_serasa'] == 'Sim'  # Convertendo para booleano
        protesto = request.form['protesto'] == 'Sim'  # Convertendo para booleano
        historico_faturamento = request.form['historico_faturamento'] == 'Sim'  # Convertendo para booleano
        historico_atraso = request.form['historico_atraso'] == 'Sim'  # Convertendo para booleano
        historico_compras = request.form['historico_compras'] == 'Sim'  # Convertendo para booleano
        sugestao_limite = float(request.form['sugestao_limite'])
        valor_compra_desejado = float(request.form['valor_compra_desejado'])

        # Calcular pontuação e motivos
        pontuacao, motivos_positivos, motivos_negativos = calcular_pontuacao(data_abertura, quantidade_socios, troca_socios, score_credito, restricao_nome_socios,
                                                cheque_devolvido, spc_serasa, protesto, historico_faturamento, historico_atraso,
                                                historico_compras, sugestao_limite, valor_compra_desejado)

        # Classificar risco
        risco = classificar_risco(pontuacao)

        # Salvar histórico
        salvar_historico(cliente, pontuacao, risco, motivos_positivos, motivos_negativos)

    # Renderizar template com resultados
    return render_template('index.html', pontuacao=pontuacao, risco=risco, motivos_positivos=motivos_positivos, motivos_negativos=motivos_negativos)

@app.route('/historico')
def historico():
    historico = []
    arquivo_csv = '/historico_analises.csv'  # Caminho absoluto do arquivo CSV
    try:
        with open(arquivo_csv, mode='r', encoding='utf-16') as file:
            reader = csv.reader(file)
            for row in reader:
                historico.append(row)
    except FileNotFoundError:
        pass  # Se o arquivo não existir, retorna uma lista vazia
    except UnicodeDecodeError:
        # Se ocorrer erro de decodificação, tentar outra codificação
        try:
            with open(arquivo_csv, mode='r', encoding='latin-1') as file:
                reader = csv.reader(file)
                for row in reader:
                    historico.append(row)
        except Exception as e:
            print(f"Erro ao ler arquivo CSV: {e}")
    
    return render_template('historico.html', historico=historico)


if __name__ == '__main__':
    app.run(debug=True)
