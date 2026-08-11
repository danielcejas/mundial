from src.pipeline import build_context
from src.tournament import monte_carlo_champions


def main():
    print("Cargando datos y entrenando modelo…")
    ctx = build_context()

    print(f"\nPartidos históricos: {len(ctx.historical_df):,}")
    print(f"Rango: {ctx.historical_df['date'].min().date()} → {ctx.historical_df['date'].max().date()}")

    print("\nParámetros óptimos:")
    for k, v in ctx.params.items():
        if isinstance(v, float):
            print(f"  {k:<14} = {v:.6f}")

    print("\nTop 10 Elo:")
    print(ctx.ranking_df.head(10).to_string(index=False))

    print("\nSimulando 1,000 torneos (Monte Carlo)…")
    mc = monte_carlo_champions(ctx.groups, ctx.ratings, ctx.params, ctx.third_mapping_df, n=1000, seed=42)
    print("\nProbabilidades de ganar el Mundial:")
    print(mc.head(15).assign(probability=lambda d: d["probability"].map(lambda x: f"{100*x:.2f}%")).to_string(index=False))


if __name__ == "__main__":
    main()
