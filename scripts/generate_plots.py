#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de processamento e geração de gráficos de alta qualidade para o artigo IEEE.
Lê os resultados reais da simulação do Jupiter na pasta results/.
"""

import sys
import os
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'
import pandas as pd
import matplotlib.pyplot as plt

# Estilo visual limpo e profissional para publicações IEEE
plt.rcParams.update({
    'font.size': 10,
    'font.family': 'serif',
    'axes.labelsize': 11,
    'axes.titlesize': 11,
    'xtick.labelsize': 9,
    'ytick.labelsize': 9,
    'legend.fontsize': 9,
    'figure.titlesize': 12,
    'lines.linewidth': 1.8,
    'lines.markersize': 6,
    'grid.linestyle': '--',
    'grid.alpha': 0.6,
})

RESULTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'results'))
OUTPUT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'figures'))
os.makedirs(OUTPUT_DIR, exist_ok=True)

def load_and_validate():
    files = {
        'E1': os.path.join(RESULTS_DIR, 'E1_demanda.csv'),
        'E2': os.path.join(RESULTS_DIR, 'E2_servidores.csv'),
        'E3': os.path.join(RESULTS_DIR, 'E3_capacidade.csv'),
        'E4': os.path.join(RESULTS_DIR, 'E4_combinado.csv')
    }
    
    dfs = {}
    missing_data = []
    
    for key, path in files.items():
        if not os.path.exists(path):
            missing_data.append(f"{key}: arquivo {path} não existe.")
            continue
        try:
            df = pd.read_csv(path, comment='#')
            # Verifica se as colunas essenciais estão preenchidas
            required_cols = ['Throughput', 'MeanResponseTime', 'MeanQueueTime', 'Utilization', 'DropProbability']
            if any(col not in df.columns for col in required_cols):
                missing_data.append(f"{key}: colunas requeridas ausentes no CSV.")
            elif df['Throughput'].isna().all() or (df['Throughput'] == '').all():
                missing_data.append(f"{key}: valores de métricas ainda não foram preenchidos (estão vazios).")
            else:
                # Converte para numérico
                for col in required_cols:
                    df[col] = pd.to_numeric(df[col], errors='coerce')
                dfs[key] = df
        except Exception as e:
            missing_data.append(f"{key}: erro ao ler {path}: {e}")
            
    if missing_data:
        print("=== AVISO: DADOS PENDENTES ===")
        for item in missing_data:
            print(f" - {item}")
        print("\nPreencha os arquivos em results/ com os dados reais simulados no Jupiter antes de gerar os gráficos finais.")
        return None
        
    return dfs

def plot_all(dfs):
    df1 = dfs['E1']
    df2 = dfs['E2']
    df3 = dfs['E3']
    df4 = dfs['E4']
    
    # -------------------------------------------------------------
    # Gráfico 1: E1 - Efeito da Taxa de Chegada (Demanda)
    # -------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(6, 4))
    color1 = '#1f77b4'
    color2 = '#d62728'
    
    ax1.plot(df1['lambda'], df1['Throughput'], marker='o', color=color1, label='Throughput (TP)')
    ax1.set_xlabel('Taxa de Chegada $\\lambda$ (req/s)')
    ax1.set_ylabel('Throughput (req/s)', color=color1)
    ax1.tick_params(axis='y', labelcolor=color1)
    ax1.grid(True)
    
    ax2 = ax1.twinx()
    # Se drop probability estiver em fração ou %, ajustar rótulo
    dp_vals = df1['DropProbability'] * 100 if df1['DropProbability'].max() <= 1.0 else df1['DropProbability']
    ax2.plot(df1['lambda'], dp_vals, marker='s', linestyle='--', color=color2, label='Drop Prob. (DP)')
    ax2.set_ylabel('Probabilidade de Descarte (%)', color=color2)
    ax2.tick_params(axis='y', labelcolor=color2)
    
    plt.title(r'E1: Throughput e Descarte vs. Demanda ($\lambda$)')
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico1_demanda.pdf'))
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico1_demanda.png'), dpi=300)
    plt.close()
    print(" -> Gráfico 1 salvo: grafico1_demanda.pdf / .png")

    # -------------------------------------------------------------
    # Gráfico 2: E2 - Efeito da Capacidade de Processamento (Servidores m)
    # -------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(6, 4))
    c_mrt = '#2ca02c'
    c_util = '#ff7f0e'
    
    ax1.plot(df2['m'], df2['MeanResponseTime'] * 1000, marker='^', color=c_mrt, label='MRT (ms)')
    ax1.set_xlabel('Número de Servidores ($m$)')
    ax1.set_ylabel('Tempo Médio de Resposta (ms)', color=c_mrt)
    ax1.tick_params(axis='y', labelcolor=c_mrt)
    ax1.set_xticks(df2['m'].values)
    ax1.grid(True)
    
    ax2 = ax1.twinx()
    u_vals = df2['Utilization'] if df2['Utilization'].max() > 1.0 else df2['Utilization'] * 100
    ax2.plot(df2['m'], u_vals, marker='D', linestyle='--', color=c_util, label='Utilização ($U$)')
    ax2.set_ylabel('Utilização Média dos Servidores (%)', color=c_util)
    ax2.tick_params(axis='y', labelcolor=c_util)
    
    plt.title('E2: Tempo de Resposta e Utilização vs. Servidores ($m$)')
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico2_servidores.pdf'))
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico2_servidores.png'), dpi=300)
    plt.close()
    print(" -> Gráfico 2 salvo: grafico2_servidores.pdf / .png")

    # -------------------------------------------------------------
    # Gráfico 3: E3 - Efeito da Capacidade do Buffer (K)
    # -------------------------------------------------------------
    fig, ax1 = plt.subplots(figsize=(6, 4))
    c_dp = '#d62728'
    c_mqt = '#9467bd'
    
    dp3 = df3['DropProbability'] * 100 if df3['DropProbability'].max() <= 1.0 else df3['DropProbability']
    ax1.plot(df3['K'], dp3, marker='s', color=c_dp, label='Drop Prob. (%)')
    ax1.set_xlabel('Capacidade Total do Sistema ($K$)')
    ax1.set_ylabel('Probabilidade de Descarte (%)', color=c_dp)
    ax1.tick_params(axis='y', labelcolor=c_dp)
    ax1.set_xticks(df3['K'].values)
    ax1.grid(True)
    
    ax2 = ax1.twinx()
    ax2.plot(df3['K'], df3['MeanQueueTime'] * 1000, marker='v', linestyle='--', color=c_mqt, label='MQT (ms)')
    ax2.set_ylabel('Tempo Médio na Fila (ms)', color=c_mqt)
    ax2.tick_params(axis='y', labelcolor=c_mqt)
    
    plt.title('E3: Descarte vs. Tempo na Fila (Trade-off de Buffer)')
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico3_capacidade.pdf'))
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico3_capacidade.png'), dpi=300)
    plt.close()
    print(" -> Gráfico 3 salvo: grafico3_capacidade.pdf / .png")

    # -------------------------------------------------------------
    # Gráfico 4: E4 - Cenários Combinados
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 4))
    scenarios = df4['nome_cenario'] if 'nome_cenario' in df4.columns else df4['scenario_id']
    x = range(len(scenarios))
    
    width = 0.35
    ax.bar([i - width/2 for i in x], df4['Throughput'], width=width, label='Throughput (req/s)', color='#1f77b4')
    ax2 = ax.twinx()
    ax2.bar([i + width/2 for i in x], df4['MeanResponseTime'] * 1000, width=width, label='MRT (ms)', color='#2ca02c', alpha=0.85)
    
    ax.set_ylabel('Throughput (req/s)', color='#1f77b4')
    ax2.set_ylabel('Tempo Médio de Resposta (ms)', color='#2ca02c')
    ax.set_xticks(x)
    ax.set_xticklabels(scenarios, rotation=15, ha='right')
    ax.grid(True, axis='y')
    
    plt.title('E4: Comparação Multidimensional dos Perfis Operacionais')
    fig.tight_layout()
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico4_combinado.pdf'))
    plt.savefig(os.path.join(OUTPUT_DIR, 'grafico4_combinado.png'), dpi=300)
    plt.close()
    print(" -> Gráfico 4 salvo: grafico4_combinado.pdf / .png")

    # -------------------------------------------------------------
    # Tabela Consolidada (LaTeX e Markdown)
    # -------------------------------------------------------------
    generate_consolidated_table(dfs)

def generate_consolidated_table(dfs):
    combined = []
    for exp_id, df in dfs.items():
        for _, row in df.iterrows():
            util_val = row.get('Utilization', 0)
            drop_val = row.get('DropProbability', 0)
            drop_pct = drop_val * 100 if drop_val <= 1.0 else drop_val
            combined.append({
                'Experimento': exp_id,
                'ID': row.get('scenario_id', ''),
                '$\\lambda$': row.get('lambda', ''),
                '$m$': row.get('m', ''),
                '$K$': row.get('K', ''),
                'Throughput': f"{row.get('Throughput', 0):.2f}",
                'MRT (ms)': f"{row.get('MeanResponseTime', 0)*1000:.1f}",
                'MQT (ms)': f"{row.get('MeanQueueTime', 0)*1000:.1f}",
                'Util (\\%)': f"{util_val:.1f}\\%",
                'Drop (\\%)': f"{drop_pct:.2f}\\%"
            })
    table_df = pd.DataFrame(combined)
    
    # Salvar em Markdown (sem depender de tabulate)
    md_path = os.path.join(OUTPUT_DIR, 'tabela_consolidada.md')
    with open(md_path, 'w', encoding='utf-8') as f:
        headers = table_df.columns.tolist()
        f.write('| ' + ' | '.join(headers) + ' |\n')
        f.write('| ' + ' | '.join(['---'] * len(headers)) + ' |\n')
        for _, row in table_df.iterrows():
            f.write('| ' + ' | '.join([str(val) for val in row.values]) + ' |\n')
    
    # Salvar em LaTeX nativo formatado
    tex_path = os.path.join(OUTPUT_DIR, 'tabela_consolidada.tex')
    with open(tex_path, 'w', encoding='utf-8') as f:
        f.write('\\begin{tabular}{llrrrrrrrr}\n\\toprule\n')
        cols = ['Exp.', 'ID', '$\\lambda$', '$m$', '$K$', 'Throughput', 'MRT (ms)', 'MQT (ms)', 'Util. (\\%)', 'Drop (\\%)']
        f.write(' & '.join(cols) + ' \\\\\n\\midrule\n')
        for _, row in table_df.iterrows():
            vals = [str(val) for val in row.values]
            f.write(' & '.join(vals) + ' \\\\\n')
        f.write('\\bottomrule\n\\end{tabular}\n')
        
    print(f" -> Tabela consolidada salva em:\n    - {md_path}\n    - {tex_path}")

if __name__ == '__main__':
    dfs = load_and_validate()
    if dfs is not None:
        plot_all(dfs)
        print("\nTodos os gráficos e tabelas foram gerados com sucesso a partir dos dados reais do Jupiter!")
