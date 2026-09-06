"""Plotly-Visualisierungen: Konvergenz der LP-Schranke über die Iterationen (fallende
Treppenlinie, Gegenstück zu bb_visualization.build_incumbent_chart) und die aktuelle
fraktionale LP-Lösung als Balkendiagramm, mit hervorgehobenem Cover."""

COVER_COLOR = "#d68a2e"
NORMAL_COLOR = "#1f77b4"
INTEGRAL_COLOR = "#2ca02c"


def build_bound_chart(result, true_optimum, step):
    import plotly.graph_objects as go

    xs = list(range(step + 1))
    ys = [result.iterations[i].bound for i in xs]

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=xs, y=ys, mode="lines+markers", line=dict(color="#14233B", width=3, shape="hv"),
            marker=dict(size=8), name="LP-Schranke",
        )
    )
    fig.add_hline(
        y=true_optimum, line=dict(color=INTEGRAL_COLOR, width=1.5, dash="dash"),
        annotation_text="Wahres Optimum", annotation_position="bottom right",
    )
    fig.update_layout(
        template="plotly_white", height=280,
        xaxis=dict(title="Iteration (Anzahl hinzugefügter Schnitte)", fixedrange=True, dtick=1),
        yaxis=dict(title="LP-Schranke", fixedrange=True),
        showlegend=False, margin=dict(t=20, l=10, r=10, b=40),
    )
    return fig


def build_solution_chart(instance, result, step):
    import plotly.graph_objects as go

    it = result.iterations[step]
    cover = set(it.cover) if it.cover else set()
    n = instance.n_items
    colors = [COVER_COLOR if i in cover else NORMAL_COLOR for i in range(n)]
    if it.is_integral:
        colors = [INTEGRAL_COLOR if it.x[i] > 0.5 else NORMAL_COLOR for i in range(n)]

    labels = [f"Paket {i + 1}<br>w={instance.weights[i]}, v={instance.values[i]}" for i in range(n)]
    texts = [f"{it.x[i]:.3f}" for i in range(n)]

    fig = go.Figure(
        data=go.Bar(
            x=[f"P{i + 1}" for i in range(n)], y=list(it.x), marker_color=colors,
            text=texts, textposition="outside", hovertext=labels, hoverinfo="text",
        )
    )
    fig.update_layout(
        template="plotly_white", height=280,
        xaxis=dict(title="Paket", fixedrange=True),
        yaxis=dict(title="LP-Wert x_i", range=[0, 1.15], fixedrange=True),
        margin=dict(t=20, l=10, r=10, b=40),
    )
    return fig
