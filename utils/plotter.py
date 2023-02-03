import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import pandas as pd

def plot(sym_0, sym_1, symbol_0_close, symbol_1_close, spreads, z_scores):
    fig, axs = plt.subplots(3, 1, constrained_layout=True, figsize=(16, 8))
    df = pd.DataFrame(columns=[sym_0, sym_1])
    df[sym_0] = symbol_0_close
    df[sym_1] = symbol_1_close

    df[f"{sym_0} delta"] = df[sym_0] / symbol_0_close[0]
    df[f"{sym_1} delta"] = df[sym_1] / symbol_1_close[0]

    delta_0 = df[f"{sym_0} delta"].astype(float).values
    delta_1 = df[f"{sym_1} delta"].astype(float).values

    axs[0].plot(delta_0, color="BLUE")
    axs[0].plot(delta_1, color="ORANGE")
    axs[0].set_title(f"Prices for {sym_0} & {sym_1}")

    axs[1].plot(spreads)
    axs[1].set_title("Spread")

    axs[2].plot(z_scores)
    axs[2].set_title("Z-Score")

    plt.close()

    return fig

def generate_pdf(figs):
    print("Generating report...")
    with PdfPages("generated/report.pdf") as pdf:
        for fig in figs:
            pdf.savefig(fig)

def save_report(pairs):
    figs = []
    for pair in pairs:
        fig = plot(
            pair["sym_0"],
            pair["sym_1"],
            pair["close_prices_0"],
            pair["close_prices_1"],
            pair["spread_data"],
            pair["z_score_data"],
        )
        figs.append(fig)

    generate_pdf(figs)