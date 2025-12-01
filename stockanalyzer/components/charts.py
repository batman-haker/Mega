"""
STOCKANALYZER - Chart Components (Plotly)

Reusable Plotly chart functions z cyberpunk theme:
- Time-series line charts
- Gauge meters (score indicators)
- Bar charts (indicators breakdown)
- Candlestick charts (price)
- Tables (indicators display)

Wszystkie wykresy używają CHART_COLORS z constants.py.

Użycie:
    from components.charts import create_time_series, create_gauge_meter

    fig = create_time_series(data, title="VIX Over Time")
    st.plotly_chart(fig)
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
from typing import Dict, List, Optional
import pandas as pd

from utils.constants import CHART_COLORS, format_large_number, format_percentage
from components.cyberpunk_theme import apply_chart_theme


# ============================================
# TIME-SERIES CHARTS
# ============================================

def create_time_series(
    data: pd.DataFrame,
    x_column: str,
    y_column: str,
    title: str,
    y_axis_title: str = None,
    color: str = None,
    show_markers: bool = False
) -> go.Figure:
    """
    Tworzy time-series line chart z cyberpunk theme.

    Args:
        data: DataFrame z danymi
        x_column: Nazwa kolumny z datami (oś X)
        y_column: Nazwa kolumny z wartościami (oś Y)
        title: Tytuł wykresu
        y_axis_title: Nazwa osi Y (opcjonalne)
        color: Kolor linii (opcjonalne, default: cyan)
        show_markers: Czy pokazać markery (default: False)

    Returns:
        go.Figure: Plotly figure

    Example:
        >>> df = pd.DataFrame({
        ...     'date': pd.date_range('2024-01-01', periods=30),
        ...     'vix': [15, 18, 20, ...]
        ... })
        >>> fig = create_time_series(df, 'date', 'vix', 'VIX Over Time')
    """
    color = color or CHART_COLORS['line_neutral']

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=data[x_column],
        y=data[y_column],
        mode='lines+markers' if show_markers else 'lines',
        line=dict(color=color, width=2),
        marker=dict(size=4, color=color) if show_markers else None,
        name=y_column
    ))

    # Apply cyberpunk theme
    theme_config = apply_chart_theme()
    theme_config.pop('title', None)

    fig.update_layout(
        **theme_config,
        title=title,
        xaxis_title='Data',
        yaxis_title=y_axis_title or y_column,
        hovermode='x unified',
        height=400,
    )

    return fig


def create_multi_line_chart(
    data: pd.DataFrame,
    x_column: str,
    y_columns: List[str],
    title: str,
    colors: List[str] = None
) -> go.Figure:
    """
    Tworzy wykres z wieloma liniami (multi-line chart).

    Args:
        data: DataFrame z danymi
        x_column: Kolumna z datami
        y_columns: Lista kolumn do wykreślenia
        title: Tytuł wykresu
        colors: Lista kolorów (opcjonalne)

    Returns:
        go.Figure: Plotly figure
    """
    if colors is None:
        colors = [
            CHART_COLORS['line_neutral'],
            CHART_COLORS['line_secondary'],
            CHART_COLORS['line_up'],
            CHART_COLORS['line_down']
        ]

    fig = go.Figure()

    for i, column in enumerate(y_columns):
        color = colors[i % len(colors)]
        fig.add_trace(go.Scatter(
            x=data[x_column],
            y=data[column],
            mode='lines',
            name=column,
            line=dict(color=color, width=2)
        ))

    theme_config = apply_chart_theme()
    theme_config.pop('title', None)
    theme_config.pop('legend', None)  # Remove legend from theme to avoid duplicate

    fig.update_layout(
        **theme_config,
        title=title,
        xaxis_title='Data',
        hovermode='x unified',
        height=450,
        legend=dict(
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        )
    )

    return fig


# ============================================
# GAUGE METER (Score Indicator)
# ============================================

def create_gauge_meter(
    value: float,
    title: str,
    min_value: float = -100,
    max_value: float = 100,
    threshold_good: float = 30,
    threshold_bad: float = -30
) -> go.Figure:
    """
    Tworzy gauge meter (wskaźnik) dla score.

    Args:
        value: Wartość do wyświetlenia (-100 to +100)
        title: Tytuł gauge
        min_value: Minimum scale (default: -100)
        max_value: Maximum scale (default: +100)
        threshold_good: Próg dla zielonego (default: 30)
        threshold_bad: Próg dla czerwonego (default: -30)

    Returns:
        go.Figure: Gauge chart

    Example:
        >>> fig = create_gauge_meter(65, "Combined Score")
        >>> st.plotly_chart(fig)
    """
    # Określ kolor bazując na wartości
    if value >= threshold_good:
        bar_color = CHART_COLORS['line_up']  # Green
    elif value <= threshold_bad:
        bar_color = CHART_COLORS['line_down']  # Red
    else:
        bar_color = CHART_COLORS['line_neutral']  # Yellow/Cyan

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=value,
        domain={'x': [0, 1], 'y': [0, 1]},
        title={'text': title, 'font': {'size': 24, 'family': 'Orbitron'}},
        number={'font': {'size': 48, 'family': 'Share Tech Mono'}},
        gauge={
            'axis': {
                'range': [min_value, max_value],
                'tickwidth': 1,
                'tickcolor': CHART_COLORS['text']
            },
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': CHART_COLORS['background'],
            'borderwidth': 2,
            'bordercolor': CHART_COLORS['axis'],
            'steps': [
                {'range': [min_value, threshold_bad], 'color': 'rgba(255, 7, 58, 0.2)'},
                {'range': [threshold_bad, threshold_good], 'color': 'rgba(255, 237, 78, 0.2)'},
                {'range': [threshold_good, max_value], 'color': 'rgba(57, 255, 20, 0.2)'}
            ],
            'threshold': {
                'line': {'color': CHART_COLORS['text'], 'width': 4},
                'thickness': 0.75,
                'value': value
            }
        }
    ))

    fig.update_layout(
        **apply_chart_theme(),
        height=300,
        margin=dict(l=20, r=20, t=60, b=20)
    )

    return fig


# ============================================
# BAR CHARTS
# ============================================

def create_horizontal_bar(
    labels: List[str],
    values: List[float],
    title: str,
    color_column: Optional[List[str]] = None
) -> go.Figure:
    """
    Tworzy horizontal bar chart (np. dla breakdown score).

    Args:
        labels: Lista nazw (Y axis)
        values: Lista wartości (X axis)
        title: Tytuł wykresu
        color_column: Opcjonalna lista kolorów dla każdego bara

    Returns:
        go.Figure: Bar chart

    Example:
        >>> labels = ['FRED', 'Stock', 'Twitter']
        >>> values = [65, 48, 32]
        >>> fig = create_horizontal_bar(labels, values, 'Score Breakdown')
    """
    # Auto-color based on values if not provided
    if color_column is None:
        color_column = [
            CHART_COLORS['line_up'] if v > 30 else
            CHART_COLORS['line_down'] if v < -30 else
            CHART_COLORS['line_neutral']
            for v in values
        ]

    fig = go.Figure(go.Bar(
        y=labels,
        x=values,
        orientation='h',
        marker=dict(
            color=color_column,
            line=dict(color=CHART_COLORS['axis'], width=1)
        ),
        text=[f"{v:+.1f}" for v in values],
        textposition='outside',
        textfont=dict(family='Share Tech Mono', size=14)
    ))

    # Apply theme first
    theme_config = apply_chart_theme()
    theme_config.pop('title', None)  # Remove title from theme to avoid conflict

    fig.update_layout(
        **theme_config,
        title=title,
        xaxis_title='Score',
        yaxis_title='',
        height=300,
        margin=dict(l=120, r=40, t=60, b=40)
    )

    return fig


# ============================================
# CANDLESTICK CHART (Stock Price)
# ============================================

def create_candlestick(
    data: pd.DataFrame,
    title: str,
    show_volume: bool = True
) -> go.Figure:
    """
    Tworzy candlestick chart dla cen akcji.

    Args:
        data: DataFrame z kolumnami: Date, Open, High, Low, Close, Volume
        title: Tytuł wykresu
        show_volume: Czy pokazać volume subplot (default: True)

    Returns:
        go.Figure: Candlestick chart

    Example:
        >>> data = yf.download('AAPL', period='3mo')
        >>> fig = create_candlestick(data.reset_index(), 'AAPL Price')
    """
    # Candlestick colors
    increasing_color = CHART_COLORS['candle_up']
    decreasing_color = CHART_COLORS['candle_down']

    if show_volume:
        # Create subplots: candlestick + volume
        fig = make_subplots(
            rows=2, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.03,
            row_heights=[0.7, 0.3],
            subplot_titles=(title, 'Volume')
        )

        # Candlestick
        fig.add_trace(
            go.Candlestick(
                x=data['Date'],
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                increasing_line_color=increasing_color,
                decreasing_line_color=decreasing_color,
                name='Price'
            ),
            row=1, col=1
        )

        # Volume bars
        colors = [
            increasing_color if close >= open else decreasing_color
            for close, open in zip(data['Close'], data['Open'])
        ]

        fig.add_trace(
            go.Bar(
                x=data['Date'],
                y=data['Volume'],
                marker_color=colors,
                opacity=0.6,
                name='Volume'
            ),
            row=2, col=1
        )

        fig.update_yaxes(title_text="Price", row=1, col=1)
        fig.update_yaxes(title_text="Volume", row=2, col=1)

    else:
        fig = go.Figure(go.Candlestick(
            x=data['Date'],
            open=data['Open'],
            high=data['High'],
            low=data['Low'],
            close=data['Close'],
            increasing_line_color=increasing_color,
            decreasing_line_color=decreasing_color
        ))

    theme_config = apply_chart_theme()
    theme_config.pop('title', None)

    fig.update_layout(
        **theme_config,
        title=title if not show_volume else '',
        xaxis_title='Date',
        xaxis_rangeslider_visible=False,
        height=500,
    )

    return fig


# ============================================
# INDICATOR TABLE (Streamlit-friendly)
# ============================================

def create_indicators_table(indicators: Dict[str, Dict]) -> pd.DataFrame:
    """
    Tworzy DataFrame dla tabeli wskaźników (do st.dataframe).

    Args:
        indicators: Dict z wskaźnikami {'name': {'value': X, 'change_pct': Y, 'interpretation': Z}}

    Returns:
        pd.DataFrame: Tabela gotowa do wyświetlenia

    Example:
        >>> indicators = {
        ...     'VIX': {'value': 18.5, 'change_pct': 2.1, 'interpretation': 'Umiarkowany'},
        ...     'SOFR': {'value': 5.32, 'change_pct': 0.05, 'interpretation': 'Stabilny'}
        ... }
        >>> df = create_indicators_table(indicators)
        >>> st.dataframe(df)
    """
    rows = []
    for name, data in indicators.items():
        rows.append({
            'Wskaźnik': name,
            'Wartość': data.get('value', 'N/A'),
            'Zmiana %': format_percentage(data.get('change_pct', 0) / 100) if data.get('change_pct') else 'N/A',
            'Interpretacja': data.get('interpretation', '-')
        })

    return pd.DataFrame(rows)


# ============================================
# TESTING
# ============================================

if __name__ == "__main__":
    print("STOCKANALYZER - Chart Components")
    print("=" * 60)

    # Test data
    import numpy as np
    from datetime import datetime, timedelta

    # Sample time series
    dates = [datetime.now() - timedelta(days=i) for i in range(30, 0, -1)]
    vix_data = np.random.uniform(15, 25, 30)

    df = pd.DataFrame({
        'Date': dates,
        'VIX': vix_data
    })

    print("\nCreating sample charts...")

    # Time series
    fig1 = create_time_series(df, 'Date', 'VIX', 'VIX Over Time')
    print("[OK] Time series created")

    # Gauge
    fig2 = create_gauge_meter(65, 'Combined Score')
    print("[OK] Gauge meter created")

    # Bar chart
    fig3 = create_horizontal_bar(
        ['FRED', 'Stock', 'Twitter'],
        [65, 48, 32],
        'Score Breakdown'
    )
    print("[OK] Bar chart created")

    # Indicators table
    indicators = {
        'VIX': {'value': 18.5, 'change_pct': 2.1, 'interpretation': 'Umiarkowany'},
        'SOFR': {'value': 5.32, 'change_pct': 0.05, 'interpretation': 'Stabilny'}
    }
    table = create_indicators_table(indicators)
    print("[OK] Indicators table created")
    print(table)

    print("\n" + "=" * 60)
    print("[OK] All chart components working!")
