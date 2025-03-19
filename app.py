import os
import re
import shutil
import time
from groq import Groq
import magic
import plotly.express as px
import streamlit as st
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Constants
CO2_PER_KWH = 0.475  # kg CO2 per kWh
AVG_SERVER_POWER = 500  # Watts
MODEL_NAME = "mixtral-8x7b-32768"  # Groq available models

# Initialize Groq client
groq_client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def calculate_impact(execution_time_ms, monthly_executions):
    """Calculate energy and carbon impact"""
    energy_kwh = (AVG_SERVER_POWER * (execution_time_ms / 1000) * monthly_executions) / 1000
    co2_kg = energy_kwh * CO2_PER_KWH
    return energy_kwh, co2_kg

def analyze_with_groq(code):
    """Analyze code using Groq's high-speed LLM"""
    system_prompt = f"""Act as a Senior Energy Efficiency Engineer. For provided code:

1. Estimate current monthly executions (default: 1M if not specified)
2. Calculate baseline energy usage using:
   - Server Power: {AVG_SERVER_POWER}W
   - CO2/kWh: {CO2_PER_KWH}kg
3. Propose optimizations with estimated % efficiency gain
4. Calculate projected savings
5. Give the Optimized Green Code changes old code vs new code changes in line by line  by marking - and +
6. Give the complete Optimized Green Code  also in efficient manner with applied annomization and hipaaa and other resposible ai applied on this . write in in markdown format only with explanation
   
Format response as:
## Current Impact
- ⚡ Energy Usage: [X] kWh/month
- 🌍 CO2 Emissions: [Y] kg/month

## Proposed Optimizations
- [Optimization 1] (+[%] efficiency)
- [Optimization 2] (+[%] efficiency)

## Projected Savings
- 🔋 Energy Savings: [X] kWh/month
- 🍃 CO2 Reduction: [Y] kg/month
"""

    try:
        response = groq_client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": code}
            ],
            temperature=0.3,
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None
    
def extract_optimized_code(response_text):
    """Extract optimized code from Groq response"""
    # This regex captures code enclosed in ```python ... ``` blocks
    match = re.search(r'```python\s+(.*?)\s+```', response_text, re.DOTALL)
    return match.group(1) if match else "No optimized code found."


def main():
    st.set_page_config(
        page_title="EcoCode Sentinel🚀",
        layout="wide",
        page_icon="🌿"
    )

    # Initialize session state
    if 'analytics' not in st.session_state:
        st.session_state.analytics = {
            'total_energy': 0.0,
            'total_co2': 0.0,
            'history': []
        }

    # Sidebar Configuration
    with st.sidebar:
        st.header("🌿 EcoCode Sentinel")
        st.subheader("⚙️ Project Setup")
        project_path = st.text_input("📂 Enter Project Path", value=os.getcwd())
        st.divider()
        # Model Selection
        model_provider = st.selectbox(
            "🤖 Select AI Provider",
            options=["Groq", "Ollama"],
            index=0,
            help="Choose between Groq's high-speed inference or Ollama's local models"
        )
        
        # Provider-specific configuration
        if model_provider == "Groq":
            st.info("Using Groq's accelerated inference")
            if not os.getenv("GROQ_API_KEY"):
                st.error("GROQ_API_KEY not found in environment variables")
        else:
            st.info("Using Ollama's local models - gemma 3")
            if not shutil.which("ollama"):
                st.error("Ollama not found. Please install Ollama first.")
                
            
        
        
        st.divider()
        st.subheader("🌍 Cumulative Impact")
        st.metric("Total Energy Saved", f"{st.session_state.analytics['total_energy']:,.1f} kWh")
        st.metric("CO2 Reduction", f"{st.session_state.analytics['total_co2']:,.1f} kg")

    # Main Interface
    col1, col2 = st.columns([0.3, 0.7])

    # File Browser
    with col1:
        st.subheader("📁 Project Explorer")
        project_dir = Path(project_path)
        if project_dir.exists():
            for entry in project_dir.iterdir():
                if entry.is_dir():
                    with st.expander(f"📂 {entry.name}", expanded=False):
                        for file in entry.glob('*'):
                            if st.button(f"📄 {file.name}", key=str(file)):
                                st.session_state.selected_file = file
                else:
                    if st.button(f"📄 {entry.name}", key=str(entry)):
                        st.session_state.selected_file = entry

    # Code Analysis Panel
    with col2:
        if 'selected_file' in st.session_state:
            try:
                # Verify file type using python-magic with MIME type enabled
                mime = magic.Magic(mime=True)
                file_type = mime.from_file(str(st.session_state.selected_file))
                
                if "text" not in file_type:
                    st.error("⚠️ Binary file detected - Analysis available only for text-based files")
                else:
                    with st.session_state.selected_file.open('r', encoding='utf-8') as f:
                        code_content = f.read()

                    st.subheader(f"🔍 Analyzing: {st.session_state.selected_file.name}")
                    with st.expander("📜 Code Preview", expanded=True):
                        st.code(code_content, line_numbers=True)

                    if st.button("🚀 Run Sustainability Analysis", type="primary"):
                        with st.spinner("🔬 Analyzing code with Groq..."):
                            analysis = analyze_with_groq(code_content)
                            
                            if analysis:
                                # Extract metrics using regex (add checks in case regex doesn't match)
                                energy_match = re.search(r"⚡ Energy Usage:\s*([\d.]+)\s*kWh", analysis)
                                savings_match = re.search(r"🔋 Energy Savings:\s*([\d.]+)\s*kWh", analysis)
                                
                                if energy_match and savings_match:
                                    current_energy = float(energy_match.group(1))
                                    projected_savings = float(savings_match.group(1))
                                    
                                    # Update analytics
                                    st.session_state.analytics['total_energy'] += projected_savings
                                    st.session_state.analytics['total_co2'] += (projected_savings * CO2_PER_KWH)
                                    st.session_state.analytics['history'].append({
                                        'file': st.session_state.selected_file.name,
                                        'savings': projected_savings,
                                        'timestamp': time.strftime("%Y-%m-%d %H:%M")
                                    })

                                    # Display results
                                    st.markdown(analysis)
                                    
                                    # Visualization
                                    fig = px.bar(
                                        x=['Current', 'Projected'],
                                        y=[current_energy, current_energy - projected_savings],
                                        labels={'y': 'Energy (kWh)', 'x': 'Scenario'},
                                        title="Energy Consumption Comparison",
                                        color_discrete_sequence=['#FF4B4B', '#00CC96']
                                    )
                                    st.plotly_chart(fig)
                                else:
                                    st.error("⚠️ Unable to extract metrics from analysis output.")
            except Exception as e:
                st.error(f"Error processing file: {str(e)}")

if __name__ == "__main__":
    main()
