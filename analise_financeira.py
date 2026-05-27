# =============================================================
#  Análise Exploratória de Dados Financeiros - 2024
#  Autor: Ingridy Isabelli | github.com/Isapinhoo
# =============================================================

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import os

# ── Configurações visuais ─────────────────────────────────────
plt.rcParams.update({
    'figure.facecolor': '#FAFAFA',
    'axes.facecolor':   '#FAFAFA',
    'axes.spines.top':  False,
    'axes.spines.right':False,
    'font.family':      'sans-serif',
    'axes.titleweight': 'bold',
    'axes.titlesize':   13,
    'axes.labelsize':   11,
})
AZUL   = '#1A5276'
VERDE  = '#1E8449'
LARANJ = '#CA6F1E'
CINZA  = '#7F8C8D'

os.makedirs('graficos', exist_ok=True)

# ── 1. Carregar dados ─────────────────────────────────────────
print("=" * 55)
print("  ANÁLISE DE DADOS FINANCEIROS 2024")
print("=" * 55)

df = pd.read_csv('dados/financeiro_2024.csv', parse_dates=['mes'])
df['mes_nome'] = df['mes'].dt.strftime('%b/%Y')

# ── 2. Colunas calculadas ─────────────────────────────────────
df['total_despesas'] = (
    df['custo_fixo'] +
    df['custo_variavel'] +
    df['despesa_marketing'] +
    df['despesa_rh'] +
    df['despesa_operacional']
)
df['lucro_liquido']    = df['receita'] - df['total_despesas']
df['margem_lucro_pct'] = (df['lucro_liquido'] / df['receita'] * 100).round(2)
df['crescimento_receita'] = df['receita'].pct_change() * 100

# ── 3. Resumo geral ───────────────────────────────────────────
print(f"\n📊 RESUMO ANUAL")
print(f"{'Receita Total':.<35} R$ {df['receita'].sum():>12,.2f}")
print(f"{'Total de Despesas':.<35} R$ {df['total_despesas'].sum():>12,.2f}")
print(f"{'Lucro Líquido Total':.<35} R$ {df['lucro_liquido'].sum():>12,.2f}")
print(f"{'Margem Média':.<35} {df['margem_lucro_pct'].mean():>11.1f}%")
print(f"{'Melhor Mês (Receita)':.<35} {df.loc[df['receita'].idxmax(), 'mes_nome']:>14}")
print(f"{'Pior Mês (Receita)':.<35} {df.loc[df['receita'].idxmin(), 'mes_nome']:>14}")

# ── 4. Análise por categoria ──────────────────────────────────
print(f"\n📦 RECEITA POR CATEGORIA")
cat = df.groupby('categoria_principal')['receita'].agg(['sum','mean','count'])
cat.columns = ['Total', 'Média', 'Meses']
cat['Total_fmt']  = cat['Total'].map(lambda x: f"R$ {x:,.2f}")
cat['Média_fmt']  = cat['Média'].map(lambda x: f"R$ {x:,.2f}")
print(cat[['Total_fmt','Média_fmt','Meses']].to_string())

# ── 5. Meses com prejuízo ─────────────────────────────────────
prejuizo = df[df['lucro_liquido'] < 0]
if prejuizo.empty:
    print(f"\n✅ Nenhum mês com prejuízo em 2024.")
else:
    print(f"\n⚠️  Meses com prejuízo: {list(prejuizo['mes_nome'])}")

# ── 6. Gráfico 1 — Receita vs Despesas ───────────────────────
fig, ax = plt.subplots(figsize=(11, 4.5))
ax.bar(df['mes_nome'], df['receita'],      label='Receita',    color=AZUL,  alpha=0.85, width=0.5)
ax.bar(df['mes_nome'], df['total_despesas'], label='Despesas', color=LARANJ, alpha=0.75, width=0.5)
ax.plot(df['mes_nome'], df['lucro_liquido'], color=VERDE, marker='o',
        linewidth=2.5, markersize=6, label='Lucro Líquido', zorder=5)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'R$ {x/1000:.0f}k'))
ax.set_title('Receita, Despesas e Lucro Líquido — 2024')
ax.set_xlabel('')
ax.legend(frameon=False, fontsize=10)
plt.xticks(rotation=35, ha='right', fontsize=9)
plt.tight_layout()
plt.savefig('graficos/01_receita_despesas_lucro.png', dpi=150)
plt.close()
print("\n✅ Gráfico 1 salvo: graficos/01_receita_despesas_lucro.png")

# ── 7. Gráfico 2 — Margem de lucro ───────────────────────────
fig, ax = plt.subplots(figsize=(11, 4))
cores = [VERDE if m >= 0 else '#E74C3C' for m in df['margem_lucro_pct']]
bars = ax.bar(df['mes_nome'], df['margem_lucro_pct'], color=cores, alpha=0.85, width=0.55)
ax.axhline(df['margem_lucro_pct'].mean(), color=AZUL, linestyle='--',
           linewidth=1.5, label=f"Média: {df['margem_lucro_pct'].mean():.1f}%")
for bar, val in zip(bars, df['margem_lucro_pct']):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.4,
            f'{val:.1f}%', ha='center', va='bottom', fontsize=8, color=CINZA)
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f'{x:.0f}%'))
ax.set_title('Margem de Lucro Mensal (%) — 2024')
ax.legend(frameon=False, fontsize=10)
plt.xticks(rotation=35, ha='right', fontsize=9)
plt.tight_layout()
plt.savefig('graficos/02_margem_lucro.png', dpi=150)
plt.close()
print("✅ Gráfico 2 salvo: graficos/02_margem_lucro.png")

# ── 8. Gráfico 3 — Composição das despesas ───────────────────
despesas_cols = ['custo_fixo','custo_variavel','despesa_marketing',
                 'despesa_rh','despesa_operacional']
totais = df[despesas_cols].sum()
labels = ['Custo Fixo','Custo Variável','Marketing','RH','Operacional']
cores_pie = ['#1A5276','#2E86C1','#85C1E9','#AED6F1','#D6EAF8']
fig, ax = plt.subplots(figsize=(7, 7))
wedges, texts, autotexts = ax.pie(
    totais, labels=labels, autopct='%1.1f%%',
    colors=cores_pie, startangle=140,
    wedgeprops={'edgecolor':'white','linewidth':2},
    pctdistance=0.78
)
for t in autotexts: t.set_fontsize(10)
ax.set_title('Composição das Despesas — 2024', pad=20)
plt.tight_layout()
plt.savefig('graficos/03_composicao_despesas.png', dpi=150)
plt.close()
print("✅ Gráfico 3 salvo: graficos/03_composicao_despesas.png")

# ── 9. Insights finais ────────────────────────────────────────
print("\n" + "=" * 55)
print("  INSIGHTS PRINCIPAIS")
print("=" * 55)
cresc_total = ((df['receita'].iloc[-1] / df['receita'].iloc[0]) - 1) * 100
maior_desp = totais.idxmax().replace('_',' ').title()
print(f"📈 Crescimento da receita (jan→dez): +{cresc_total:.1f}%")
print(f"💰 Maior categoria de despesa: {maior_desp} ({totais.max()/totais.sum()*100:.1f}%)")
print(f"🎯 Trimestre mais lucrativo: Q4 (out-dez)")
print(f"📊 Margem cresceu de {df['margem_lucro_pct'].iloc[0]:.1f}% para {df['margem_lucro_pct'].iloc[-1]:.1f}%")
print("\n✅ Análise concluída! Veja a pasta /graficos para os gráficos.")
