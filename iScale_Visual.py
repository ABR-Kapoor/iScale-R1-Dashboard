import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
import os
import json
import warnings
warnings.filterwarnings('ignore')

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from iScale_DA import iScaleDataAnalyzer

st.set_page_config(
    page_title="iScale Visual Analytics by Abeer Kapoor",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        text-align: center;
        margin-bottom: 1.5rem;
        background: linear-gradient(90deg, #FF6B35, #F7931E);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-card {
        background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 0.5rem 0;
        border: 1px solid #4a5568;
    }
    
    .insight-box {
        background: linear-gradient(135deg, #1a202c 0%, #2d3748 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        border: 1px solid #4a5568;
    }
    
    .success-box {
        background: linear-gradient(135deg, #1a365d 0%, #2c5282 100%);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        margin: 1rem 0;
        border: 1px solid #3182ce;
    }
    
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        border: none;
        padding: 0.5rem;
        font-weight: bold;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    }
</style>
""", unsafe_allow_html=True)

CSV_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iScale_MaskedData.csv')
JSON_RESULTS_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iScale_analysis_results.json')

@st.cache_data
def load_analysis_results():
    """Load pre-computed analysis results from JSON file"""
    try:
        with open(JSON_RESULTS_PATH, 'r') as f:
            results = json.load(f)
        return results
    except Exception as e:
        st.warning(f"Could not load pre-computed results: {str(e)}")
        return None

@st.cache_data
def load_analyzer():
    """Load and initialize the iScale analyzer with data"""
    try:
        analyzer = iScaleDataAnalyzer(CSV_FILE_PATH)
        if analyzer.load_and_process_data():
            return analyzer
        else:
            st.error("Failed to load data")
            return None
    except Exception as e:
        st.error(f"Error initializing analyzer: {str(e)}")
        return None

def main():
    st.markdown('<h1 class="main-header">iScale Visual Analytics Dashboard</h1>', unsafe_allow_html=True)
    st.markdown('<h3 style="text-align: center; color: #666; margin-bottom: 2rem;">Created by Abeer Kapoor</h3>', unsafe_allow_html=True)
    
    # Navigation
    st.markdown("### Choose Your Analysis View:")
    col1, col2, col3, col4, col5 = st.columns(5)
    
    views = [
        "Overview", 
        "3D/7D Conversions", 
        "Hourly Performance",
        "Coach Insights",
        "Key Recommendations"
    ]
    
    # Session state for current view
    if 'current_view' not in st.session_state:
        st.session_state.current_view = views[0]
    
    with col1:
        if st.button(views[0], key="btn1"):
            st.session_state.current_view = views[0]
    
    with col2:
        if st.button(views[1], key="btn2"):
            st.session_state.current_view = views[1]
    
    with col3:
        if st.button(views[2], key="btn3"):
            st.session_state.current_view = views[2]
    
    with col4:
        if st.button(views[3], key="btn4"):
            st.session_state.current_view = views[3]
    
    with col5:
        if st.button(views[4], key="btn5"):
            st.session_state.current_view = views[4]
    
    st.markdown("---")
    
    # Load pre-computed analysis results first
    analysis_results = load_analysis_results()
    
    # Load data using the analyzer (for charts and detailed analysis)
    with st.spinner("Loading and processing consultation data..."):
        analyzer = load_analyzer()
    
    if analyzer is None:
        st.error("Failed to load data. Please check the file path and try again.")
        return
    
    # Get current view
    analysis_type = st.session_state.current_view
    
    # Display content based on selected view
    if analysis_type == "Overview":
        display_overview(analyzer, analysis_results)
    elif analysis_type == "3D/7D Conversions":
        display_conversion_analysis(analyzer, analysis_results)
    elif analysis_type == "Hourly Performance":
        display_hourly_analysis(analyzer, analysis_results)
    elif analysis_type == "Coach Insights":
        display_coach_analysis(analyzer, analysis_results)
    elif analysis_type == "Key Recommendations":
        display_key_insights(analyzer, analysis_results)

def display_overview(analyzer, analysis_results=None):
    """Display overview metrics and distributions"""
    st.header("Business Overview")
    
    # Use JSON data if available, otherwise compute from analyzer
    if analysis_results and 'data_summary' in analysis_results:
        data_summary = analysis_results['data_summary']
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Consultations</h3>
                <h2>{data_summary['total_consultations']:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total Conversions</h3>
                <h2>{data_summary['total_conversions']:,}</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Conversion Rate</h3>
                <h2>{data_summary['overall_conversion_rate']:.1f}%</h2>
            </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Active Coaches</h3>
                <h2>{data_summary['active_coaches']:,}</h2>
            </div>
            """, unsafe_allow_html=True)
    else:
        # Fallback to computed insights
        insights = analyzer.get_key_insights()
        
        if insights:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Consultations</h3>
                    <h2>{insights['total_consultations']:,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Total Conversions</h3>
                    <h2>{insights['total_conversions']:,}</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Conversion Rate</h3>
                    <h2>{insights['overall_conversion_rate']:.1f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col4:
                st.markdown(f"""
                <div class="metric-card">
                    <h3>Active Coaches</h3>
                    <h2>{insights['active_coaches']:,}</h2>
                </div>
                """, unsafe_allow_html=True)
    
    st.markdown("---")
    col1, col2 = st.columns(2)
    
    with col1:
        funnel_counts = analyzer.df['funnel'].value_counts()
        fig = px.pie(values=funnel_counts.values, names=funnel_counts.index, 
                    title="Distribution by Funnel")
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        lead_counts = analyzer.df['lead_type'].value_counts()
        fig = px.pie(values=lead_counts.values, names=lead_counts.index,
                    title="Distribution by Lead Type")
        st.plotly_chart(fig, use_container_width=True)

def display_conversion_analysis(analyzer, analysis_results=None):
    """Display 3-day and 7-day conversion analysis"""
    st.header("3-Day & 7-Day Conversion Analysis")
    if analysis_results and 'segment_performance' in analysis_results:
        segment_perf = analysis_results['segment_performance']
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Best 3-Day Segment</h3>
                <h2>{segment_perf['best_3d_segment']}</h2>
                <p>{segment_perf['best_3d_rate']:.1f}% conversion</p>
            </div>
            """, unsafe_allow_html=True)
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Best 7-Day Segment</h3>
                <h2>{segment_perf['best_7d_segment']}</h2>
                <p>{segment_perf['best_7d_rate']:.1f}% conversion</p>
            </div>
            """, unsafe_allow_html=True)

    conv_3d = analyzer.calculate_conversion_rates(3)
    conv_7d = analyzer.calculate_conversion_rates(7)

    if conv_3d is not None and conv_7d is not None:
        conversion_summary = conv_3d.merge(
            conv_7d[['funnel', 'lead_type', 'conversion_rate_7d']], 
            on=['funnel', 'lead_type']
        )
        st.subheader("Conversion Rates by Funnel & Lead Type")
        st.dataframe(conversion_summary[['funnel', 'lead_type', 'user_id', 'conversion_flag', 
                                       'conversion_rate_3d', 'conversion_rate_7d']], 
                    use_container_width=True)
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('3-Day Conversion Rate', '7-Day Conversion Rate')
        )
        conversion_summary['segment_label'] = conversion_summary['funnel'] + ' - ' + conversion_summary['lead_type']
        fig.add_trace(
            go.Bar(x=conversion_summary['segment_label'], y=conversion_summary['conversion_rate_3d'],
                  name='3-Day Rate', marker_color='lightblue'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=conversion_summary['segment_label'], y=conversion_summary['conversion_rate_7d'],
                  name='7-Day Rate', marker_color='lightgreen'),
            row=1, col=2
        )
        fig.update_layout(height=500, title="Conversion Rates Comparison", showlegend=False)
        fig.update_xaxes(tickangle=45)
        st.plotly_chart(fig, use_container_width=True)

def display_hourly_analysis(analyzer, analysis_results=None):
    """Display hourly performance analysis"""
    st.header("Hourly Performance Analysis")
    
    if analysis_results and 'key_findings' in analysis_results:
        key_findings = analysis_results['key_findings']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Best Connectivity</h3>
                <h2>{key_findings['best_connectivity_hour']:02d}:00 eve</h2>
                <p>Peak performance hour</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Best Conversion</h3>
                <h2>{key_findings['best_conversion_hour']:02d}:00 eve</h2>
                <p>Peak sales hour</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col3:
            top_hours = ', '.join([f"{h:02d}:00" for h in key_findings['top_conversion_hours']])
            st.markdown(f"""
            <div class="metric-card">
                <h3>Golden Hours</h3>
                <h2>{top_hours}</h2>
                <p>Top conversion hours</p>
            </div>
            """, unsafe_allow_html=True)
    
    hourly_stats = analyzer.analyze_hourly_performance()
    
    if hourly_stats is not None:
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Connectivity Rate by Hour', 'Conversion Rate by Hour'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(x=hourly_stats['slot_hour'], y=hourly_stats['connectivity_rate'],
                      mode='lines+markers', name='Connectivity Rate', line=dict(color='blue')),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(x=hourly_stats['slot_hour'], y=hourly_stats['conversion_rate'],
                      mode='lines+markers', name='Conversion Rate', line=dict(color='green')),
            row=2, col=1
        )
        
        fig.update_xaxes(title_text="Hour of Day", row=2, col=1)
        fig.update_yaxes(title_text="Connectivity Rate (%)", row=1, col=1)
        fig.update_yaxes(title_text="Conversion Rate (%)", row=2, col=1)
        fig.update_layout(height=600, title="Performance by Time of Day")
        
        st.plotly_chart(fig, use_container_width=True)
        
        best_connectivity_hour = hourly_stats.loc[hourly_stats['connectivity_rate'].idxmax(), 'slot_hour']
        best_conversion_hour = hourly_stats.loc[hourly_stats['conversion_rate'].idxmax(), 'slot_hour']
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Best Connectivity", f"{best_connectivity_hour}:00 evening")
        with col2:
            st.metric("Best Conversion", f"{best_conversion_hour}:00 evening")
        with col3:
            avg_performance = (hourly_stats['connectivity_rate'].mean() + hourly_stats['conversion_rate'].mean()) / 2
            st.metric("Average Performance", f"{avg_performance:.1f}%")

def display_coach_analysis(analyzer, analysis_results=None):
    """Display coach and funnel performance analysis"""
    st.header("Coach & Funnel Performance")
    
    if analysis_results and 'key_findings' in analysis_results:
        key_findings = analysis_results['key_findings']
        
        st.markdown(f"""
        <div class="insight-box">
            <h3>Top Performing Funnel</h3>
            <h2>{key_findings['best_funnel']}</h2>
            <p>{key_findings['best_funnel_rate']:.1f}% conversion rate</p>
        </div>
        """, unsafe_allow_html=True)
    
    funnel_performance = analyzer.df.groupby('funnel').agg({
        'user_id': 'count',
        'conversion_flag': 'sum'
    }).reset_index()
    funnel_performance['conversion_rate'] = (funnel_performance['conversion_flag'] / funnel_performance['user_id'] * 100).round(2)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(funnel_performance, x='funnel', y='conversion_rate',
                    title="Conversion Rate by Funnel", color='conversion_rate')
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        fig = px.bar(funnel_performance, x='funnel', y='user_id',
                    title="Consultation Volume by Funnel", color='user_id')
        st.plotly_chart(fig, use_container_width=True)

def display_key_insights(analyzer, analysis_results=None):
    """Display key business insights and recommendations"""
    st.header("Abeer's Strategic Business Insights")
    
    if analysis_results:
        data_summary = analysis_results.get('data_summary', {})
        key_findings = analysis_results.get('key_findings', {})
        segment_perf = analysis_results.get('segment_performance', {})
        
        st.markdown('<div class="success-box">', unsafe_allow_html=True)
        st.markdown("### **Top Performance Insights**")
        if 'best_funnel' in key_findings:
            st.write(f"• **Best Funnel**: {key_findings['best_funnel']} ({key_findings['best_funnel_rate']:.1f}% conversion)")
        if 'best_connectivity_hour' in key_findings:
            st.write(f"• **Peak Connectivity**: {key_findings['best_connectivity_hour']:02d}:00")
        if 'best_conversion_hour' in key_findings:
            st.write(f"• **Peak Conversion**: {key_findings['best_conversion_hour']:02d}:00")
        if 'best_7d_segment' in segment_perf:
            st.write(f"• **Best 7-day Segment**: {segment_perf['best_7d_segment']} ({segment_perf['best_7d_rate']:.1f}%)")
        st.markdown('</div>', unsafe_allow_html=True)
        
        if 'overall_conversion_rate' in data_summary:
            current_rate = data_summary['overall_conversion_rate']
            potential_rate = current_rate * 1.2  
            additional_conversions = data_summary['total_consultations'] * (potential_rate - current_rate) / 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Rate", f"{current_rate:.1f}%")
            with col2:
                st.metric("Potential Rate", f"{potential_rate:.1f}%", f"+{potential_rate - current_rate:.1f}%")
            with col3:
                st.metric("Additional Conversions", f"+{int(additional_conversions):,}")
    else:
        insights = analyzer.get_key_insights()
        
        if insights:
            st.markdown('<div class="success-box">', unsafe_allow_html=True)
            st.markdown("### **Top Performance Insights**")
            if 'best_funnel' in insights:
                st.write(f"• **Best Funnel**: {insights['best_funnel']} ({insights['best_funnel_rate']:.1f}% conversion)")
            if 'best_connectivity_hour' in insights:
                st.write(f"• **Peak Connectivity**: {insights['best_connectivity_hour']:02d}:00 ({insights['best_connectivity_rate']:.1f}%)")
            if 'best_conversion_hour' in insights:
                st.write(f"• **Peak Conversion**: {insights['best_conversion_hour']:02d}:00 ({insights['best_conversion_rate']:.1f}%)")
            st.markdown('</div>', unsafe_allow_html=True)
            
            current_rate = insights['overall_conversion_rate']
            potential_rate = current_rate * 1.2  # 20% improvement
            additional_conversions = insights['total_consultations'] * (potential_rate - current_rate) / 100
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Current Rate", f"{current_rate:.1f}%")
            with col2:
                st.metric("Potential Rate", f"{potential_rate:.1f}%", f"+{potential_rate - current_rate:.1f}%")
            with col3:
                st.metric("Additional Conversions", f"+{int(additional_conversions):,}")
    
    st.markdown('<div class="insight-box">', unsafe_allow_html=True)
    st.markdown("### **Strategic Recommendations**")
    st.write("1. **Schedule 70% of consultations during peak hours** for maximum ROI")
    st.write("2. **Focus marketing spend on top-performing funnels**")
    st.write("3. **Implement follow-up strategy for 7-day conversion improvement**")
    st.write("4. **Train coaches based on top performer best practices**")
    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()