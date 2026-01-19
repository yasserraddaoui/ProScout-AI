"""
ProScout AI - Professional Football Scouting Platform
Modern Streamlit application with dark mode, player cards, tactical formations, and advanced analytics
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import sys
import os
from pathlib import Path
import requests
from PIL import Image
from io import BytesIO
import base64

# Add src to path
sys.path.append(str(Path(__file__).parent / "src"))

try:
    from src.preprocess import load_all_data, create_player_stats_df
    from src.player_scoring import compute_player_score
    from src.clustering import cluster_players, find_similar_players
    from src.recommend import recommend
    from src.lineup_recommend import get_historical_lineups
except ImportError:
    # Fallback if imports fail
    import sys
    sys.path.insert(0, 'src')
    from preprocess import load_all_data, create_player_stats_df
    from player_scoring import compute_player_score
    from clustering import cluster_players, find_similar_players
    from recommend import recommend
    from lineup_recommend import get_historical_lineups

# Page configuration
st.set_page_config(
    page_title="ProScout AI",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for dark mode and professional styling
st.markdown("""
<style>
    /* Dark theme */
    .stApp {
        background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
        color: #ffffff;
    }
    
    /* Sidebar styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    
    /* Cards */
    .player-card {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
        box-shadow: 0 8px 16px rgba(0,0,0,0.3);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stat-box {
        background: rgba(255,255,255,0.05);
        padding: 15px;
        border-radius: 10px;
        text-align: center;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .formation-player-card {
        background: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 10px;
        margin: 5px;
        text-align: center;
        border: 2px solid rgba(255,255,255,0.2);
        transition: transform 0.2s;
    }
    
    .formation-player-card:hover {
        transform: scale(1.05);
        border-color: #4fc3f7;
    }
    
    /* Headers */
    h1, h2, h3 {
        color: #ffffff;
    }
    
    /* Metrics */
    [data-testid="stMetricValue"] {
        color: #4fc3f7;
    }
    
    /* Buttons */
    .stButton>button {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1.5rem;
        font-weight: 600;
    }
    
    .stButton>button:hover {
        background: linear-gradient(90deg, #764ba2 0%, #667eea 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'data_loaded' not in st.session_state:
    st.session_state.data_loaded = False
if 'player_stats' not in st.session_state:
    st.session_state.player_stats = None
if 'all_data' not in st.session_state:
    st.session_state.all_data = None

@st.cache_data
def load_player_image(image_url):
    """Load player image from URL with caching"""
    if pd.isna(image_url) or not image_url or image_url == '':
        return None
    try:
        response = requests.get(str(image_url), timeout=5, headers={'User-Agent': 'Mozilla/5.0'})
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            return img
    except Exception as e:
        return None
    return None

def get_player_image_url(player_name, player_id, all_data):
    """Get player image URL from all_data"""
    try:
        if 'players' in all_data and not all_data['players'].empty:
            players_df = all_data['players']
            if 'name' in players_df.columns:
                player_row = players_df[players_df['name'] == player_name]
            elif 'player_name' in players_df.columns:
                player_row = players_df[players_df['player_name'] == player_name]
            else:
                return None
            
            if not player_row.empty and 'image_url' in player_row.columns:
                img_url = player_row.iloc[0]['image_url']
                if pd.notna(img_url) and img_url != '':
                    return img_url
    except:
        pass
    return None

@st.cache_data
def load_data():
    """Load and prepare all data"""
    try:
        # Load all CSV files
        all_data = load_all_data("data")
        
        # Create enriched player stats
        player_stats = create_player_stats_df(all_data)
        
        # Compute scores
        player_stats = compute_player_score(player_stats)
        
        # Rename columns for compatibility
        if 'name' in player_stats.columns:
            player_stats = player_stats.rename(columns={'name': 'player_name'})
        
        return all_data, player_stats
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return None, None

def create_radar_chart(player_data, similar_players_df=None):
    """Create a radar chart for player stats"""
    # Select key stats for radar
    stats = ['goals_per_game', 'assists_per_game', 'minutes_per_game']
    
    # Normalize values (0-1 scale)
    max_values = {
        'goals_per_game': player_data['goals_per_game'].max() if len(player_data) > 1 else player_data['goals_per_game'].iloc[0] * 2,
        'assists_per_game': player_data['assists_per_game'].max() if len(player_data) > 1 else player_data['assists_per_game'].iloc[0] * 2,
        'minutes_per_game': 90  # Max minutes per game
    }
    
    fig = go.Figure()
    
    # Main player
    main_player = player_data.iloc[0]
    values = [
        (main_player['goals_per_game'] / max_values['goals_per_game']) * 100,
        (main_player['assists_per_game'] / max_values['assists_per_game']) * 100,
        (main_player['minutes_per_game'] / max_values['minutes_per_game']) * 100
    ]
    
    fig.add_trace(go.Scatterpolar(
        r=values + [values[0]],  # Close the loop
        theta=['Goals/Game', 'Assists/Game', 'Minutes/Game', 'Goals/Game'],
        fill='toself',
        name=main_player['player_name'],
        line_color='#4fc3f7'
    ))
    
    # Similar players (if provided)
    if similar_players_df is not None and len(similar_players_df) > 0:
        for idx, row in similar_players_df.head(2).iterrows():
            sim_values = [
                (row['goals_per_game'] / max_values['goals_per_game']) * 100 if 'goals_per_game' in row else 0,
                (row['assists_per_game'] / max_values['assists_per_game']) * 100 if 'assists_per_game' in row else 0,
                (row['minutes_per_game'] / max_values['minutes_per_game']) * 100 if 'minutes_per_game' in row else 0
            ]
            fig.add_trace(go.Scatterpolar(
                r=sim_values + [sim_values[0]],
                theta=['Goals/Game', 'Assists/Game', 'Minutes/Game', 'Goals/Game'],
                fill='toself',
                name=row.get('player_name', f'Player {idx}'),
                line_color='#ff6b6b',
                opacity=0.5
            ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100]
            )),
        showlegend=True,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        height=400
    )
    
    return fig

def create_formation_433_html(selected_players, all_data=None):
    """Create a professional HTML/CSS formation visualization with player images"""
    positions_layout = {
        'GK': [(50, 5)],
        'DEF': [(15, 25), (35, 25), (65, 25), (85, 25)],
        'MID': [(25, 50), (50, 50), (75, 50)],
        'ATT': [(20, 80), (50, 80), (80, 80)]
    }
    
    html = """
    <div style="position: relative; width: 100%; height: 600px; background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%); 
                border-radius: 15px; padding: 20px; margin: 20px 0;">
        <div style="text-align: center; color: white; font-size: 24px; font-weight: bold; margin-bottom: 20px;">
            Formation 4-3-3
        </div>
        <div style="position: relative; width: 100%; height: 500px; background: rgba(34,139,34,0.3); 
                    border: 3px solid white; border-radius: 10px;">
    """
    
    # Organize players
    gk_players = []
    def_players = []
    mid_players = []
    att_players = []
    other_players = []
    
    for player in selected_players[:11]:
        position = str(player.get('position', '')).lower()
        if 'goalkeeper' in position or 'gk' in position:
            gk_players.append(player)
        elif 'defender' in position or 'def' in position or 'back' in position:
            def_players.append(player)
        elif 'midfielder' in position or 'mid' in position:
            mid_players.append(player)
        elif 'attacking' in position or 'forward' in position or 'striker' in position or 'winger' in position:
            att_players.append(player)
        else:
            other_players.append(player)
    
    # Fill positions
    final_players = []
    
    # GK
    if len(gk_players) > 0:
        final_players.append(('GK', gk_players[0], positions_layout['GK'][0]))
    elif len(other_players) > 0:
        final_players.append(('GK', other_players[0], positions_layout['GK'][0]))
        other_players = other_players[1:]
    
    # DEF (4)
    for i in range(4):
        if i < len(def_players):
            final_players.append(('DEF', def_players[i], positions_layout['DEF'][i]))
        elif len(other_players) > 0:
            final_players.append(('DEF', other_players[0], positions_layout['DEF'][i]))
            other_players = other_players[1:]
    
    # MID (3)
    for i in range(3):
        if i < len(mid_players):
            final_players.append(('MID', mid_players[i], positions_layout['MID'][i]))
        elif len(other_players) > 0:
            final_players.append(('MID', other_players[0], positions_layout['MID'][i]))
            other_players = other_players[1:]
    
    # ATT (3)
    for i in range(3):
        if i < len(att_players):
            final_players.append(('ATT', att_players[i], positions_layout['ATT'][i]))
        elif len(other_players) > 0:
            final_players.append(('ATT', other_players[0], positions_layout['ATT'][i]))
            other_players = other_players[1:]
    
    # Add player cards
    position_colors = {
        'GK': '#ff6b6b',
        'DEF': '#4ecdc4',
        'MID': '#95e1d3',
        'ATT': '#f38181'
    }
    
    for pos_type, player, (x, y) in final_players:
        player_name = str(player.get('player_name', player.get('name', 'Player')))[:15]
        img_url = player.get('image_url')
        color = position_colors.get(pos_type, '#4fc3f7')
        
        # Try to get image
        player_img_base64 = None
        if img_url and all_data:
            try:
                img = load_player_image(img_url)
                if img:
                    img = img.resize((60, 60), Image.Resampling.LANCZOS)
                    buffered = BytesIO()
                    img.save(buffered, format="PNG")
                    player_img_base64 = base64.b64encode(buffered.getvalue()).decode()
            except:
                pass
        
        html += f"""
        <div style="position: absolute; left: {x}%; top: {y}%; transform: translate(-50%, -50%); 
                    text-align: center; z-index: 10;">
            <div style="width: 80px; height: 80px; background: {color}; border-radius: 50%; 
                        border: 3px solid white; display: flex; align-items: center; justify-content: center;
                        box-shadow: 0 4px 8px rgba(0,0,0,0.3); margin-bottom: 5px;">
        """
        
        if player_img_base64:
            html += f'<img src="data:image/png;base64,{player_img_base64}" style="width: 100%; height: 100%; border-radius: 50%; object-fit: cover;" />'
        else:
            html += f'<span style="color: white; font-size: 24px;">⚽</span>'
        
        html += f"""
            </div>
            <div style="background: rgba(0,0,0,0.7); color: white; padding: 5px 8px; border-radius: 5px; 
                        font-size: 10px; font-weight: bold; white-space: nowrap; margin-top: 5px;">
                {player_name}
            </div>
        </div>
        """
    
    html += """
        </div>
    </div>
    """
    
    return html

def create_formation_433(selected_players, all_data=None):
    """Create a 4-3-3 formation visualization - improved version"""
    positions = {
        'GK': [(50, 10)],
        'DEF': [(20, 30), (35, 30), (65, 30), (80, 30)],
        'MID': [(30, 50), (50, 50), (70, 50)],
        'ATT': [(25, 75), (50, 75), (75, 75)]
    }
    
    fig = go.Figure()
    
    # Draw field with professional styling
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, 
                  line=dict(color="#ffffff", width=4), fillcolor="rgba(34,139,34,0.5)")
    
    # Center circle
    fig.add_shape(type="circle", xref="x", yref="y",
                  x0=40, y0=40, x1=60, y1=60,
                  line=dict(color="#ffffff", width=3))
    
    # Center line
    fig.add_shape(type="line", x0=0, y0=50, x1=100, y1=50,
                  line=dict(color="#ffffff", width=3, dash="dash"))
    
    # Penalty boxes
    fig.add_shape(type="rect", x0=0, y0=20, x1=20, y1=80,
                  line=dict(color="#ffffff", width=3), fillcolor="rgba(0,0,0,0)")
    fig.add_shape(type="rect", x0=80, y0=20, x1=100, y1=80,
                  line=dict(color="#ffffff", width=3), fillcolor="rgba(0,0,0,0)")
    
    # Organize players
    gk_players = []
    def_players = []
    mid_players = []
    att_players = []
    other_players = []
    
    for player in selected_players[:11]:
        position = str(player.get('position', '')).lower()
        if 'goalkeeper' in position or 'gk' in position:
            gk_players.append(player)
        elif 'defender' in position or 'def' in position or 'back' in position:
            def_players.append(player)
        elif 'midfielder' in position or 'mid' in position:
            mid_players.append(player)
        elif 'attacking' in position or 'forward' in position or 'striker' in position or 'winger' in position:
            att_players.append(player)
        else:
            other_players.append(player)
    
    # Build final lineup ensuring 11 players
    final_lineup = []
    
    # GK (1)
    if len(gk_players) > 0:
        final_lineup.append(('GK', gk_players[0], positions['GK'][0], '#ff6b6b'))
    elif len(other_players) > 0:
        final_lineup.append(('GK', other_players[0], positions['GK'][0], '#ff6b6b'))
        other_players = other_players[1:]
    
    # DEF (4)
    for i in range(4):
        if i < len(def_players):
            final_lineup.append(('DEF', def_players[i], positions['DEF'][i], '#4ecdc4'))
        elif len(other_players) > 0:
            final_lineup.append(('DEF', other_players[0], positions['DEF'][i], '#4ecdc4'))
            other_players = other_players[1:]
    
    # MID (3)
    for i in range(3):
        if i < len(mid_players):
            final_lineup.append(('MID', mid_players[i], positions['MID'][i], '#95e1d3'))
        elif len(other_players) > 0:
            final_lineup.append(('MID', other_players[0], positions['MID'][i], '#95e1d3'))
            other_players = other_players[1:]
    
    # ATT (3)
    for i in range(3):
        if i < len(att_players):
            final_lineup.append(('ATT', att_players[i], positions['ATT'][i], '#f38181'))
        elif len(other_players) > 0:
            final_lineup.append(('ATT', other_players[0], positions['ATT'][i], '#f38181'))
            other_players = other_players[1:]
    
    # Add players to plot
    for pos_type, player, (x, y), color in final_lineup:
        player_name = str(player.get('player_name', player.get('name', 'Player')))[:12]
        fig.add_trace(go.Scatter(
            x=[x], y=[y],
            mode='markers+text',
            marker=dict(
                size=40,
                color=color,
                line=dict(width=4, color='white'),
                symbol='circle'
            ),
            text=[player_name],
            textposition="middle center",
            textfont=dict(size=10, color='white', family='Arial Black'),
            name=player.get('player_name', 'Player'),
            hovertemplate=f'<b>{player_name}</b><br>Position: {pos_type}<extra></extra>'
        ))
    
    fig.update_layout(
        xaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(range=[0, 100], showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=700,
        showlegend=False,
        margin=dict(l=20, r=20, t=40, b=20),
        title=dict(text="Formation 4-3-3", font=dict(size=24, color='white', family='Arial Black'), x=0.5)
    )
    
    return fig

def main():
    # Header
    col1, col2, col3 = st.columns([1, 3, 1])
    with col2:
        st.markdown("""
        <div style="text-align: center; padding: 20px;">
            <h1 style="font-size: 3.5em; background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;
                       margin-bottom: 10px;">⚽ ProScout AI</h1>
            <p style="color: #888; font-size: 1.2em;">Professional Football Intelligence Platform</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Sidebar
    with st.sidebar:
        st.markdown("## 🎯 Navigation")
        page = st.radio(
            "Select Page",
            ["🏠 Dashboard", "👤 Player Analysis", "⚽ Team Lineup", "📊 Analytics", "🔍 Player Search"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Load data button
        if st.button("🔄 Load Data", use_container_width=True):
            with st.spinner("Loading data..."):
                all_data, player_stats = load_data()
                if all_data is not None and player_stats is not None:
                    st.session_state.all_data = all_data
                    st.session_state.player_stats = player_stats
                    st.session_state.data_loaded = True
                    st.success("Data loaded successfully!")
                else:
                    st.error("Failed to load data")
    
    # Auto-load data if not loaded
    if not st.session_state.data_loaded:
        with st.spinner("Loading data for the first time..."):
            all_data, player_stats = load_data()
            if all_data is not None and player_stats is not None:
                st.session_state.all_data = all_data
                st.session_state.player_stats = player_stats
                st.session_state.data_loaded = True
            else:
                st.error("Failed to load data. Please check your data files.")
                return
    
    player_stats = st.session_state.player_stats
    all_data = st.session_state.all_data
    
    # Main content based on page selection
    if page == "🏠 Dashboard":
        show_dashboard(player_stats, all_data)
    elif page == "👤 Player Analysis":
        show_player_analysis(player_stats, all_data)
    elif page == "⚽ Team Lineup":
        show_team_lineup(all_data)
    elif page == "📊 Analytics":
        show_analytics(player_stats, all_data)
    elif page == "🔍 Player Search":
        show_player_search(player_stats)

def show_dashboard(player_stats, all_data):
    """Dashboard overview"""
    st.markdown("## 📊 Dashboard Overview")
    
    # Key metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Players", f"{len(player_stats):,}")
    with col2:
        st.metric("Avg Score", f"{player_stats['score'].mean():.1f}")
    with col3:
        st.metric("Top Scorer", player_stats.loc[player_stats['goals'].idxmax(), 'player_name'] if len(player_stats) > 0 else "N/A")
    with col4:
        st.metric("Total Goals", f"{player_stats['goals'].sum():,}")
    
    st.markdown("---")
    
    # Top players
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 🏆 Top 10 Players by Score")
        top_players = player_stats.nlargest(10, 'score')[['player_name', 'score', 'goals', 'assists', 'position']]
        st.dataframe(top_players, use_container_width=True, hide_index=True)
    
    with col2:
        st.markdown("### 📈 Score Distribution")
        fig = px.histogram(
            player_stats, 
            x='score', 
            nbins=30,
            title="Player Score Distribution",
            color_discrete_sequence=['#4fc3f7']
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig, use_container_width=True)

def show_player_analysis(player_stats, all_data):
    """Detailed player analysis"""
    st.markdown("## 👤 Player Analysis")
    
    # Player selection
    player_names = sorted(player_stats['player_name'].dropna().unique())
    selected_player = st.selectbox("Select Player", player_names, key="player_select")
    
    if selected_player:
        player_data = player_stats[player_stats['player_name'] == selected_player]
        
        if len(player_data) > 0:
            player = player_data.iloc[0]
            
            # Player card with image
            col1, col2, col3 = st.columns([2, 3, 2])
            
            with col1:
                # Get player image
                player_img_url = player.get('image_url')
                if not player_img_url or pd.isna(player_img_url):
                    player_img_url = get_player_image_url(player['player_name'], player.get('player_id'), all_data)
                
                player_img = None
                if player_img_url:
                    player_img = load_player_image(player_img_url)
                
                if player_img:
                    st.image(player_img, width=200, use_container_width=True)
                else:
                    st.markdown("""
                    <div style="width: 200px; height: 250px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                border-radius: 10px; display: flex; align-items: center; justify-content: center; color: white; font-size: 3em;">
                        ⚽
                    </div>
                    """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="player-card" style="margin-top: 10px;">
                    <h2>{player['player_name']}</h2>
                    <p><strong>Position:</strong> {player.get('position', 'N/A')}</p>
                    <p><strong>Club ID:</strong> {player.get('current_club_id', 'N/A')}</p>
                    <p><strong>Nationality:</strong> {player.get('country_of_citizenship', 'N/A')}</p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                # Key stats
                col2a, col2b, col2c = st.columns(3)
                with col2a:
                    st.metric("Score", f"{player['score']:.1f}")
                with col2b:
                    st.metric("Goals", int(player['goals']))
                with col2c:
                    st.metric("Assists", int(player['assists']))
                
                col2d, col2e, col2f = st.columns(3)
                with col2d:
                    st.metric("Games", int(player['games_played']))
                with col2e:
                    st.metric("Goals/Game", f"{player['goals_per_game']:.2f}")
                with col2f:
                    st.metric("Assists/Game", f"{player['assists_per_game']:.2f}")
            
            with col3:
                st.markdown(f"""
                <div class="stat-box">
                    <h3>Market Value</h3>
                    <p style="font-size: 1.5em;">€{player.get('market_value_in_eur', 0):,.0f}</p>
                </div>
                """, unsafe_allow_html=True)
            
            st.markdown("---")
            
            # Radar chart
            st.markdown("### 📊 Performance Radar")
            
            # Get similar players for comparison
            try:
                # Prepare data for similarity search
                player_stats_for_sim = player_stats.copy()
                if 'cluster' not in player_stats_for_sim.columns:
                    # Perform clustering if not done
                    player_stats_for_sim, _, _ = cluster_players(player_stats_for_sim.copy(), n_clusters=5)
                
                similar_players = find_similar_players(player_stats_for_sim, selected_player, top_n=3)
                similar_players_data = player_stats_for_sim[player_stats_for_sim['player_name'].isin(similar_players['player_name'].values)]
                
                radar_fig = create_radar_chart(player_data, similar_players_data)
                st.plotly_chart(radar_fig, use_container_width=True)
            except Exception as e:
                radar_fig = create_radar_chart(player_data)
                st.plotly_chart(radar_fig, use_container_width=True)
            
            # Similar players
            st.markdown("### 🔍 Similar Players")
            try:
                if 'cluster' not in player_stats.columns:
                    player_stats_clustered, _, _ = cluster_players(player_stats.copy(), n_clusters=5)
                    st.session_state.player_stats = player_stats_clustered
                else:
                    player_stats_clustered = player_stats.copy()
                
                similar = find_similar_players(player_stats_clustered, selected_player, top_n=5)
                
                if len(similar) > 0:
                    # Afficher avec plus de détails
                    display_cols = ['player_name']
                    if 'score' in similar.columns:
                        display_cols.append('score')
                    if 'position' in similar.columns:
                        display_cols.append('position')
                    if 'goals' in similar.columns:
                        display_cols.append('goals')
                    if 'assists' in similar.columns:
                        display_cols.append('assists')
                    if 'cluster' in similar.columns:
                        display_cols.append('cluster')
                    
                    st.dataframe(similar[display_cols], use_container_width=True, hide_index=True)
                else:
                    st.warning("No similar players found")
            except Exception as e:
                st.error(f"Error finding similar players: {str(e)}")
                import traceback
                st.code(traceback.format_exc())

def show_team_lineup(all_data):
    """Team lineup recommendation"""
    st.markdown("## ⚽ Team Lineup Recommendation")
    
    # Get team names
    if 'clubs' in all_data and not all_data['clubs'].empty:
        team_names = sorted(all_data['clubs']['name'].dropna().unique())
        
        if len(team_names) > 0:
            selected_team = st.selectbox("Select Team", team_names)
            
            if selected_team and st.button("Generate Best Lineup", use_container_width=True):
                with st.spinner("Analyzing team history..."):
                    try:
                        best_lineup = get_historical_lineups(selected_team, all_data, top_n=10)
                        
                        if not best_lineup.empty and len(best_lineup) >= 11:
                            st.markdown("### 🏆 Best Historical Lineup")
                            
                            # Display lineup with images
                            col1, col2 = st.columns([2, 1])
                            
                            with col1:
                                # Create a custom display with images
                                for idx, row in best_lineup.head(11).iterrows():
                                    player_name = row.get('name', row.get('player_name', 'Unknown'))
                                    position = row.get('position', 'Midfielder')
                                    goals = row.get('goals', 0)
                                    assists = row.get('assists', 0)
                                    score = row.get('contrib_score', 0)
                                    img_url = row.get('image_url')
                                    
                                    # Get image
                                    player_img = None
                                    if img_url and pd.notna(img_url):
                                        player_img = load_player_image(img_url)
                                    
                                    # Display player card
                                    player_col1, player_col2 = st.columns([1, 4])
                                    with player_col1:
                                        if player_img:
                                            st.image(player_img, width=80, use_container_width=False)
                                        else:
                                            st.markdown("""
                                            <div style="width: 80px; height: 80px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                                        border-radius: 50%; display: flex; align-items: center; justify-content: center; color: white; font-size: 2em;">
                                                ⚽
                                            </div>
                                            """, unsafe_allow_html=True)
                                    
                                    with player_col2:
                                        st.markdown(f"""
                                        <div style="padding: 10px;">
                                            <h4 style="margin: 0; color: white;">{player_name}</h4>
                                            <p style="margin: 5px 0; color: #888;">{position} | Goals: {int(goals)} | Assists: {int(assists)} | Score: {score:.1f}</p>
                                        </div>
                                        """, unsafe_allow_html=True)
                                    
                                    st.markdown("---")
                            
                            with col2:
                                st.markdown("### 📐 Formation 4-3-3")
                                
                                # Get player details for formation
                                lineup_players = []
                                for _, row in best_lineup.head(11).iterrows():
                                    player_name = row.get('name', row.get('player_name', 'Unknown'))
                                    position = row.get('position', 'Midfielder')
                                    img_url = row.get('image_url')
                                    player_info = {
                                        'player_name': str(player_name),
                                        'position': str(position),
                                        'image_url': str(img_url) if pd.notna(img_url) else None
                                    }
                                    lineup_players.append(player_info)
                                
                                if len(lineup_players) == 11:
                                    formation_fig = create_formation_433(lineup_players, all_data)
                                    st.plotly_chart(formation_fig, use_container_width=True)
                                else:
                                    st.warning(f"Only {len(lineup_players)} players found. Need 11 for formation.")
                            
                            # Also show as dataframe
                            st.markdown("### 📊 Detailed Stats")
                            display_cols = ['name', 'position', 'goals', 'assists', 'contrib_score']
                            if 'image_url' in best_lineup.columns:
                                display_cols = [c for c in display_cols if c != 'image_url']
                            st.dataframe(best_lineup[display_cols].head(11), use_container_width=True, hide_index=True)
                        elif not best_lineup.empty:
                            st.warning(f"Only {len(best_lineup)} players found. Need at least 11 for a complete lineup.")
                            st.dataframe(best_lineup[['name', 'position', 'goals', 'assists', 'contrib_score']], 
                                       use_container_width=True, hide_index=True)
                        else:
                            st.warning(f"No lineup data found for {selected_team}. The team may not have enough match history.")
                            
                    except Exception as e:
                        st.error(f"Error generating lineup: {str(e)}")
                        import traceback
                        with st.expander("Error Details"):
                            st.code(traceback.format_exc())
        else:
            st.warning("No teams found in the dataset")
    else:
        st.warning("Team data not available. Please ensure clubs.csv is loaded.")

def show_analytics(player_stats, all_data):
    """Advanced analytics"""
    st.markdown("## 📊 Advanced Analytics")
    
    # Position analysis
    st.markdown("### 📍 Performance by Position")
    
    if 'position' in player_stats.columns:
        position_stats = player_stats.groupby('position').agg({
            'score': 'mean',
            'goals': 'sum',
            'assists': 'sum'
        }).reset_index()
        
        fig = px.bar(
            position_stats,
            x='position',
            y='score',
            title="Average Score by Position",
            color='score',
            color_continuous_scale='Viridis'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='white'),
            xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Goals vs Assists scatter
    st.markdown("### 🎯 Goals vs Assists Analysis")
    fig = px.scatter(
        player_stats,
        x='goals',
        y='assists',
        size='score',
        color='score',
        hover_data=['player_name'],
        title="Goals vs Assists (Size = Score)",
        color_continuous_scale='Viridis'
    )
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    st.plotly_chart(fig, use_container_width=True)

def show_player_search(player_stats):
    """Player search and filter"""
    st.markdown("## 🔍 Player Search")
    
    # Search box
    search_term = st.text_input("Search by name", "")
    
    # Filters
    col1, col2, col3 = st.columns(3)
    with col1:
        min_score = st.slider("Min Score", 0.0, 100.0, 0.0)
    with col2:
        min_goals = st.number_input("Min Goals", 0, int(player_stats['goals'].max()), 0)
    with col3:
        if 'position' in player_stats.columns:
            positions = ['All'] + sorted(player_stats['position'].dropna().unique().tolist())
            selected_position = st.selectbox("Position", positions)
    
    # Filter data
    filtered = player_stats.copy()
    
    if search_term:
        filtered = filtered[filtered['player_name'].str.contains(search_term, case=False, na=False)]
    
    filtered = filtered[filtered['score'] >= min_score]
    filtered = filtered[filtered['goals'] >= min_goals]
    
    if 'position' in player_stats.columns and selected_position != 'All':
        filtered = filtered[filtered['position'] == selected_position]
    
    # Display results
    st.markdown(f"### Found {len(filtered)} players")
    st.dataframe(
        filtered[['player_name', 'position', 'score', 'goals', 'assists', 'games_played']].head(100),
        use_container_width=True,
        hide_index=True
    )

if __name__ == "__main__":
    main()
