# Cochlear Tonotopic Mapping & Electrodogram Visualizer

An interactive simulation of how a cochlear implant processes sound. Upload any `.wav` file and watch it get split across a bank of electrodes, mimicking the way a real implant's sound processor drives an electrode array along the tonotopic map of the cochlea.

**Live demo:** _add your Streamlit Cloud URL here once deployed_


## Why this project

Cochlear implants restore hearing by bypassing damaged hair cells and stimulating the auditory nerve directly through an array of electrodes. Each electrode is tuned to a different frequency band, following the cochlea's natural **tonotopic organization** — low frequencies near the apex, high frequencies near the base. This app visualizes that process end to end: raw waveform in, simulated electrode firing pattern out.

## How it works

1. **Filterbank** — the incoming audio is split into N frequency bands using logarithmically-spaced Butterworth bandpass filters (`scipy.signal.butter`), matching how real implant sound processors (and the cochlea itself) allocate more frequency resolution to lower frequencies.
2. **Half-wave rectification** — each band is rectified to keep only the positive-going signal, simulating how auditory nerve fibers respond to pressure in one direction.
3. **Envelope extraction** — a low-pass filter (400 Hz cutoff) pulls out the amplitude envelope of each band, representing the stimulation intensity that would be sent to each electrode.
4. **Visualization** — the resulting electrode-by-time matrix is rendered as an interactive Plotly heatmap, with electrode number on the y-axis (low frequency at the bottom, high frequency at the top) and time on the x-axis.

## Tech stack

- [Streamlit](https://streamlit.io/) — web UI
- [NumPy](https://numpy.org/) / [SciPy](https://scipy.org/) — signal processing (filterbank, rectification, envelope extraction)
- [librosa](https://librosa.org/) — audio loading and resampling
- [Plotly](https://plotly.com/python/) — interactive heatmap visualization

## Running locally

```bash
git clone https://github.com/<your-username>/cochlear-implant-simulator.git
cd cochlear-implant-simulator
pip install -r requirements.txt
streamlit run app.py
```

A browser window will open automatically at `http://localhost:8501`. Upload a `.wav` file (or try the sample in `examples/sample_sweep_200hz_8000hz.wav`, a synthetic logarithmic sweep from 200 Hz to 8000 Hz) and use the sidebar slider to adjust the number of simulated electrodes (4–32; real implants typically use 16–22).

## Deploying to Streamlit Community Cloud

1. Push this repo to GitHub.
2. Go to [share.streamlit.io](https://share.streamlit.io/) and sign in with GitHub.
3. Click **New app**, select this repository, and set the main file path to `app.py`.
4. Click **Deploy**. Streamlit Cloud will read `requirements.txt` for Python dependencies and `packages.txt` for the system-level `libsndfile1` package that librosa needs.

## Project structure

```
cochlear-implant-simulator/
├── app.py                              # Main Streamlit app (DSP + UI + visualization)
├── requirements.txt                    # Python dependencies
├── packages.txt                        # System-level dependencies (libsndfile1)
├── .streamlit/
│   └── config.toml                     # Theme and upload size limits
├── examples/
│   └── sample_sweep_200hz_8000hz.wav   # Synthetic test tone for quick demoing
├── .gitignore
├── LICENSE
└── README.md
```

## Limitations & possible extensions

- The current model is a simplified envelope-based simulation (an approximation of a CIS-style strategy), not a clinically accurate model of any specific implant manufacturer's actual sound-coding strategy.
- Uploads are capped at 25 MB (configurable in `.streamlit/config.toml`) to keep processing responsive on free-tier hosting.
- Possible extensions: adding an n-of-m channel selection strategy (like Advanced Combination Encoder), pulse-rate visualization, or a side-by-side comparison between two electrode-count settings.

