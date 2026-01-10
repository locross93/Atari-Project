import os
import csv
import statistics
import matplotlib.pyplot as plt

# ----------------------- CONFIG -----------------------
ROOT = "results"
PLOTS_DIR = os.path.join(ROOT, "plots")
MODELS = ["Breakout", "SpaceInvaders", "Enduro"]
NOISES = ["gaussian", "saltpepper", "occlusion", "blur", "framedrop", "pixelation"]
SEVERITIES = [1, 2, 3, 4, 5]
os.makedirs(PLOTS_DIR, exist_ok=True)
# ------------------------------------------------------


def read_returns(csv_path):
    """Read numeric return values from the CSV file (skip 'mean' row)."""
    returns = []
    try:
        with open(csv_path, newline="") as fh:
            rows = list(csv.reader(fh))
        start = next(
            (
                i
                for i, r in enumerate(rows)
                if len(r) >= 3
                and r[0].strip().lower() == "episode"
                and r[1].strip().lower() == "return"
            ),
            None,
        )
        if start is None:
            return returns
        for r in rows[start + 1 :]:
            if not r:
                continue
            ep = r[0].strip().lower()
            if ep == "mean":
                continue
            if ep.isdigit():
                try:
                    returns.append(float(r[1]))
                except Exception:
                    pass
    except FileNotFoundError:
        pass
    return returns


# ============================================================
# =============== PLOT 1, 3, 4 (Aggregated) ==================
# ============================================================

def make_aggregated_plots():
    """Make aggregated plots (Mean vs Noise, Drop vs Noise, Std vs Noise)."""
    data = {}  # key=(model, noise) -> [returns]
    clean_mean = {}

    for m in MODELS:
        # Clean file
        clean_file = os.path.join(ROOT, m, f"{m}_Clean.csv")
        vals = read_returns(clean_file)
        if vals:
            clean_mean[m] = statistics.fmean(vals)

        # Noisy files (aggregate all severities)
        for nz in NOISES:
            all_returns = []
            for s in SEVERITIES:
                f = os.path.join(ROOT, m, f"{m}_{nz}_{s}.csv")
                all_returns += read_returns(f)
            if all_returns:
                data[(m, nz)] = all_returns

    # ---------- Plot 1: Mean Return vs Noise Type ----------
    plt.figure()
    for m in MODELS:
        xs = [nz for nz in NOISES if (m, nz) in data]
        ys = [statistics.fmean(data[(m, nz)]) for nz in xs]
        plt.plot(xs, ys, marker="o", label=m)
    plt.title("Mean Return vs Noise Type (averaged over severities)")
    plt.xlabel("Noise Type")
    plt.ylabel("Mean Return")
    plt.legend()
    plt.xticks(rotation=20)
    plt.tight_layout()
    plt.savefig(os.path.join(PLOTS_DIR, "plot1_mean_vs_noise_all_sev.png"), dpi=200)
    plt.close()

    # ---------- Plot 3: Percentage Drop vs Noise Type ----------
    for m in MODELS:
        clean = clean_mean.get(m)
        if not clean or clean == 0:
            continue
        xs, ys = [], []
        for nz in NOISES:
            if (m, nz) in data:
                mean_noisy = statistics.fmean(data[(m, nz)])
                drop = (clean - mean_noisy) / clean * 100.0
                xs.append(nz)
                ys.append(drop)
        if not xs:
            continue
        plt.figure()
        plt.bar(xs, ys)
        plt.title(f"{m}: % Drop vs Noise Type (averaged over severities)")
        plt.ylabel("Drop (%)")
        plt.xlabel("Noise Type")
        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"plot3_{m}_percent_drop_all_sev.png"), dpi=200)
        plt.close()

    # ---------- Plot 4: Standard Deviation vs Noise Type ----------
    for m in MODELS:
        xs, ys = [], []
        for nz in NOISES:
            if (m, nz) in data:
                ys.append(statistics.pstdev(data[(m, nz)]))
                xs.append(nz)
        if not xs:
            continue
        plt.figure()
        plt.bar(xs, ys)
        plt.title(f"{m}: Std(Return) vs Noise Type (averaged over severities)")
        plt.ylabel("Std of Return")
        plt.xlabel("Noise Type")
        plt.xticks(rotation=20)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"plot4_{m}_std_vs_noise_all_sev.png"), dpi=200)
        plt.close()

    print(f"✅ Saved aggregated plots to: {PLOTS_DIR}")


# ============================================================
# =============== PLOT 2 (Per Model) =========================
# ============================================================

def make_severity_plots():
    """Make Plot 2: Mean Return vs Severity (for each model)."""
    data = {}  # key=(model, noise, severity) -> [returns]
    clean_mean = {}

    for m in MODELS:
        # Clean
        clean_file = os.path.join(ROOT, m, f"{m}_Clean.csv")
        vals = read_returns(clean_file)
        if vals:
            clean_mean[m] = statistics.fmean(vals)

        # Noisy
        for nz in NOISES:
            for s in SEVERITIES:
                f = os.path.join(ROOT, m, f"{m}_{nz}_{s}.csv")
                vals = read_returns(f)
                if vals:
                    data[(m, nz, s)] = vals

    # ---------- Plot 2: Mean Return vs Severity ----------
    for m in MODELS:
        plt.figure()
        for nz in NOISES:
            xs, ys = [], []
            for s in SEVERITIES:
                key = (m, nz, s)
                if key in data:
                    xs.append(s)
                    ys.append(statistics.fmean(data[key]))
            if xs and ys:
                plt.plot(xs, ys, marker="o", label=nz)

        plt.title(f"{m}: Mean Return vs Severity (per noise)")
        plt.xlabel("Severity")
        plt.ylabel("Mean Return")
        plt.legend(title="Noise Type", ncol=2)
        plt.xticks(SEVERITIES)
        plt.tight_layout()
        plt.savefig(os.path.join(PLOTS_DIR, f"plot2_{m}_mean_vs_severity_all_noise.png"), dpi=200)
        plt.close()

    print(f"✅ Saved plot2 (Mean Return vs Severity) to: {PLOTS_DIR}")


# ============================================================
# ======================= MAIN ===============================
# ============================================================

if __name__ == "__main__":
    make_aggregated_plots()
    make_severity_plots()

