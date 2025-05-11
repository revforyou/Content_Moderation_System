

FROM quay.io/jupyter/scipy-notebook:latest

# Switch to notebook user
USER ${NB_UID}

# Install Python packages
RUN pip install --no-cache-dir \
    pandas \
    tqdm \
    transformers \
    torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 \
    mlflow \
    ray==2.42.1

# Fix permissions for conda and home directory
RUN fix-permissions "${CONDA_DIR}" && \
    fix-permissions "/home/${NB_USER}"
