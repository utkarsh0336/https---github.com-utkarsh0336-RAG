import os
# Attempt to fix DLL error by allowing duplicate libs (common fix for MKL/OpenMP issues)
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

import streamlit as st
import sys

st.write(f"Python: {sys.version}")
st.write("Importing torch...")

try:
    import torch
    st.success(f"Torch imported! Version: {torch.__version__}")
except Exception as e:
    st.error(f"Failed: {e}")
