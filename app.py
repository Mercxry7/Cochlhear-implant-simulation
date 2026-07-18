import streamlit as st
import numpy as np
import scipy.signal as signal
import plotly.graph_objects as go
import librosa
import io 

# --- 1. DIGITAL SIGNAL PROCESSING (THE MATH) ---
def create_filterbank(num_channels, fs, low_freq=200, high_freq=8000):
    """Creates a bank of bandpass filters logarithmically spaced."""
    edges = np.logspace(np.log10(low_freq), np.log10(high_freq), num_channels + 1)
    filters = []

    for i in range(num_channels):
        # Normalize frequencies to Nyquist
        low = edges[i] / (0.5 * fs)
        high = edges[i + 1] / (0.5 * fs)

        # Prevent high cutoff from exceeding Nyquist frequency
        if high >= 1.0:
            high = 0.99

        b, a = signal.butter(N=3, Wn=[low, high], btype='bandpass')
        filters.append((b, a))

    return filters


def process_audio(audio_data, fs, num_channels):
    """Filters audio and extracts the envelope to simulate electrode firing."""
    filters = create_filterbank(num_channels, fs)
    electrodogram = np.zeros((num_channels, len(audio_data)))

    # Lowpass filter for envelope extraction (400 Hz cutoff)
    b_env, a_env = signal.butter(N=2, Wn=400 / (0.5 * fs), btype='lowpass')

    for i, (b, a) in enumerate(filters):
        # 1. Bandpass filter the audio
        filtered_signal = signal.filtfilt(b, a, audio_data)
        # 2. Half-wave rectification (simulate nerve firing strictly on positive pressure)
        rectified = np.maximum(filtered_signal, 0)
        # 3. Low-pass filter to get the amplitude envelope
        envelope = signal.filtfilt(b_env, a_env, rectified)
        # 4. Store in our 2D array
        electrodogram[i, :] = envelope

    return electrodogram


# --- 2. STREAMLIT USER INTERFACE ---
st.set_page_config(page_title="Cochlear Electrodogram", layout="wide")

st.title("Cochlear Tonotopic Mapping & Electrodogram Visualizer")
st.markdown("""
This application simulates how a Cochlear Implant processes sound. It takes a raw acoustic waveform,
splits it through a logarithmically spaced bandpass filterbank (simulating the tonotopic map of the human cochlea),
and extracts the amplitude envelopes to visualize real-time electrode activation.
""")

st.sidebar.header("Implant Settings")
num_channels = st.sidebar.slider("Number of Electrodes (Channels)", min_value=4, max_value=32, value=22, step=2)
st.sidebar.markdown("*Modern implants typically use 16 to 22 active electrodes.*")

uploaded_file = st.file_uploader("Upload an audio file (.wav format)", type=["wav"])

if uploaded_file is not None:
    st.audio(uploaded_file, format='audio/wav')

    with st.spinner("Simulating neuroprosthetic processing..."):
        # Load audio using librosa (resample to 16kHz to save memory/processing time)
        y, sr = librosa.load(io.BytesIO(uploaded_file.read()), sr=16000)

        # If stereo, convert to mono
        if len(y.shape) > 1:
            y = librosa.to_mono(y)

        # Guard against silent/empty uploads before running filters
        if len(y) < 10:
            st.error("This audio file is too short or empty to process. Please upload a longer clip.")
        else:
            # Downsample the array length for the visualization to prevent browser crash
            # (Plotly struggles rendering millions of data points)
            downsample_factor = max(1, len(y) // 2000)

            # Generate the electrodogram
            e_gram = process_audio(y, sr, num_channels)
            e_gram_visual = e_gram[:, ::downsample_factor]

            time_axis = np.linspace(0, len(y) / sr, e_gram_visual.shape[1])
            electrode_axis = np.arange(1, num_channels + 1)

            # --- 3. PLOTLY VISUALIZATION ---
            fig = go.Figure(data=go.Heatmap(
                z=e_gram_visual,
                x=time_axis,
                y=electrode_axis,
                colorscale='Inferno',
                zsmooth='best'
            ))

            fig.update_layout(
                title=f"Simulated Electrodogram ({num_channels} Channels)",
                xaxis_title="Time (seconds)",
                yaxis_title="Electrode Number (1 = Apex/Low Freq, Top = Base/High Freq)",
                height=600,
                template="plotly_dark"
            )

            st.plotly_chart(fig, use_container_width=True)
            st.success("Processing complete!")
