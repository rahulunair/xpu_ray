import streamlit as st
import requests
import os
from pathlib import Path
from datetime import datetime
import re
from typing import Optional
import json
import time


class RateLimit:
    def __init__(self):
        self.last_request = 0
        self.min_interval = 0.1  # 10 requests per second
        self.reset()

    def can_make_request(self) -> bool:
        now = time.time()
        if now - self.last_request >= self.min_interval:
            self.last_request = now
            return True
        return False

    def reset(self):
        self.last_request = 0


class APIClient:
    def __init__(self, config):
        self.config = config
        self.session = requests.Session()

    def make_request(
        self, endpoint: str, method: str = "GET", data: dict = None
    ) -> requests.Response:
        """Make secure API requests with retry and validation."""
        if endpoint == "generate" and not self.config.rate_limiter.can_make_request():
            raise ValueError("Rate limit exceeded")

        try:
            url = f"{self.config.base_url}/imagine/{endpoint}"

            if endpoint == "generate" and data:
                if data.get("img_size", 0) < 512 or data.get("img_size", 0) > 1024:
                    raise ValueError("Image size must be between 512 and 1024")
                if (
                    data.get("guidance_scale", 0) < 0.0
                    or data.get("guidance_scale", 0) > 10.0
                ):
                    raise ValueError("Guidance scale must be between 0.0 and 10.0")
                if (
                    data.get("num_inference_steps", 0) < 1
                    or data.get("num_inference_steps", 0) > 50
                ):
                    raise ValueError(
                        "Number of inference steps must be between 1 and 50"
                    )

            response = self.session.request(
                method=method,
                url=url,
                headers={
                    "Authorization": f"Bearer {self.config.token}",
                    "Content-Type": "application/json",
                },
                json=data,
                timeout=180,
                verify=True,
            )

            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            if hasattr(e, "response"):
                if e.response.status_code == 401:
                    raise ValueError("Invalid token")
                elif e.response.status_code == 429:
                    raise ValueError("Rate limit exceeded")
            raise ValueError(f"API request failed: {str(e)}")


class HistoryManager:
    def __init__(self, output_dir: Path):
        self.history_file = output_dir / "generation_history.json"
        self.max_history_size = 50

    def load(self) -> list:
        """Safely load history."""
        if not self.history_file.exists():
            return []
        try:
            with open(self.history_file, "r") as f:
                history = json.load(f)
                return history[-self.max_history_size :]
        except (json.JSONDecodeError, IOError):
            return []

    def save(self, history: list):
        """save history."""
        temp_file = self.history_file.with_suffix(".tmp")
        try:
            with open(temp_file, "w") as f:
                json.dump(history[-self.max_history_size :], f)
            temp_file.rename(self.history_file)
        except Exception as e:
            if temp_file.exists():
                temp_file.unlink()
            raise e


class ImageConfig:
    def __init__(self):
        self.base_url = "http://localhost:9000"
        self.output_dir = Path("generated_images")
        self.output_dir.mkdir(exist_ok=True, mode=0o755)
        self.token = os.getenv("VALID_TOKEN")
        self.rate_limiter = RateLimit()
        self.api_client = APIClient(self)
        self.history_manager = HistoryManager(self.output_dir)
        self.rate_limiter.reset()
        if not self.token:
            raise ValueError("VALID_TOKEN environment variable not set")


def clean_prompt(prompt: str) -> str:
    """input sanitization."""
    if not prompt:
        return ""
    if len(prompt) > 200:
        raise ValueError("Prompt too long (max 200 characters)")
    cleaned = re.sub(r"[^a-zA-Z0-9\s.,!?-]", "", prompt)
    return " ".join(cleaned.split())


def get_model_info() -> Optional[dict]:
    """Fetch current model information from the API."""
    try:
        response = config.api_client.make_request("info")
        info = response.json()
        if not info.get("is_loaded", False):
            st.error("⚠️ Model service is not fully loaded")
            return None
        return info
    except Exception as e:
        st.error("❌ Cannot connect to model service. Please ensure it's running.")
        return None


def get_default_params(model_info: dict) -> dict:
    """Get default parameters based on model type."""
    model_type = model_info.get("model", "sdxl-lightning")  # Default to lightning
    defaults = {
        "sdxl-lightning": {"steps": 4, "guidance": 0.0},
        "sdxl-turbo": {"steps": 1, "guidance": 0.0},
        "sdxl": {"steps": 20, "guidance": 7.5},
        "sd2": {"steps": 30, "guidance": 7.5},
        "flux": {"steps": 4, "guidance": 0.0},
    }
    model_defaults = defaults.get(model_type, defaults["sdxl-lightning"])
    return model_defaults


def load_api_docs() -> str:
    """Load and format API documentation."""
    try:
        with open("API.md", "r") as f:
            return f.read()
    except Exception:
        return "API documentation not available"


def format_token_display(token: str) -> str:
    """Securely format token display."""
    if not token:
        return ""
    return f"{token[:4]}...{token[-4:]}"


def copy_to_clipboard():
    """Handle token copying with feedback."""
    if config.token:
        st.session_state.clipboard = config.token
        st.session_state.token_copied = True


def display_history_entry(entry: dict):
    """Display a single history entry."""
    st.markdown('<div class="image-history-card">', unsafe_allow_html=True)
    st.markdown('<div class="image-container">', unsafe_allow_html=True)
    st.image(entry["path"])
    st.markdown("</div>", unsafe_allow_html=True)
    with st.expander(entry["prompt"][:50] + "..."):
        params = entry.get("parameters", {})
        st.code(
            f"""
Size: {params.get('img_size')}x{params.get('img_size')}
Steps: {params.get('num_inference_steps')}
Guidance: {params.get('guidance_scale')}
Time: {datetime.fromisoformat(entry['timestamp']).strftime('%Y-%m-%d %H:%M')}
        """
        )


def display_history(history: list, page_size: int = 9):
    """Display history with pagination."""
    if not history:
        st.info("No generation history yet.")
        return

    total_pages = len(history) // page_size + (1 if len(history) % page_size else 0)
    page = (
        st.select_slider("Page", options=range(1, total_pages + 1))
        if total_pages > 1
        else 1
    )
    start_idx = (page - 1) * page_size
    page_history = list(reversed(history[start_idx : start_idx + page_size]))
    cols = st.columns(3)
    for idx, entry in enumerate(page_history):
        with cols[idx % 3]:
            display_history_entry(entry)


def safe_save_image(image_path: Path, image_data: bytes):
    """Safely save image file."""
    try:
        temp_path = image_path.with_suffix(".tmp")
        with open(temp_path, "wb") as f:
            f.write(image_data)
        temp_path.rename(image_path)
    except Exception as e:
        if temp_path.exists():
            temp_path.unlink()
        raise e


def main():
    st.set_page_config(
        page_title="Image Generation Demo on Intel XPUs",
        page_icon=":frame_with_picture:",
        layout="centered",
        initial_sidebar_state="auto",
    )
    st.markdown(
        """
        <style>
        /* Custom theme */
        :root {
            --font-main: 'Poppins', sans-serif;
            --font-code: 'JetBrains Mono', monospace;
            --primary-color: #FF1493;
            --secondary-color: #FF69B4;
            --background-color: #ffffff;
        }

        /* Import Google Fonts */
        @import url('https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600&display=swap');
        @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap');

        /* Global styles */
        .stApp {
            background-color: var(--background-color);
            font-family: var(--font-main);
        }

        /* Headers */
        h1, h2, h3, h4, h5, h6 {
            font-family: var(--font-main);
            color: var(--secondary-color);
            font-weight: 600;
        }

        /* Streamlit elements styling */
        .stTextInput > div > div > input,
        .stTextArea > div > div > textarea {
            border-radius: 10px;
            border: 2px solid var(--primary-color) !important;
        }

        .stTextInput > div > div > input:focus,
        .stTextArea > div > div > textarea:focus {
            box-shadow: 0 0 0 2px var(--secondary-color) !important;
        }

        /* Buttons */
        .stButton > button {
            font-family: var(--font-main);
            background-color: var(--primary-color) !important;
            color: white !important;
            border-radius: 8px !important;
            padding: 0.5rem 1rem !important;
            font-weight: 500 !important;
            transition: all 0.3s ease !important;
        }

        .stButton > button:hover {
            background-color: var(--secondary-color) !important;
            box-shadow: 0 4px 8px rgba(255,20,147,0.3) !important;
            transform: translateY(-2px) !important;
        }

        /* Cards and containers */
        .stForm, .api-docs, .image-history-card {
            border-radius: 12px;
            box-shadow: 0 4px 6px rgba(0,0,0,0.05);
            background-color: white;
        }

        /* Image container */
        .image-container {
            border-radius: 8px;
            overflow: hidden;
            margin-bottom: 1rem;
        }

        /* Info box styling */
        .info-box {
            background-color: #e7f3ef;
            border-left: 4px solid #2e7d32;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 4px;
        }

        .info-box p {
            color: #1e4620;
            margin: 0;
            padding: 0.2rem 0;
        }

        .info-box strong {
            color: #2e7d32;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )

    st.markdown(
        '<h1 class="title">Image Generation Demo on Intel XPUs</h1>',
        unsafe_allow_html=True,
    )
    tab1, tab2, tab3 = st.tabs(
        ["🎨 Image Generation", "📚 API Documentation", "🔑 Authentication"]
    )

    with tab1:
        model_info = get_model_info()
        defaults = (
            get_default_params(model_info)
            if model_info
            else {"steps": 20, "guidance": 7.5}
        )

        if model_info:
            st.markdown(
                f'<div class="model-info">🤖 Model: {model_info.get("model", "Unknown")}</div>',
                unsafe_allow_html=True,
            )
        st.markdown(
            "Generate images using our API. For advanced options, check the API Documentation tab."
        )
        with st.form("generation_form"):
            prompt = st.text_area(
                "✍️ Enter your prompt:",
                height=100,
                help="Describe the image you want to generate",
            )
            col1, col2 = st.columns(2)
            with col1:
                img_size = st.select_slider(
                    "Image Size",
                    options=[512, 576, 640, 704, 768, 832, 896, 960, 1024],
                    value=512,
                )
            with st.expander("⚙️ Advanced Configuration", expanded=False):
                adv_col1, adv_col2 = st.columns(2)
                with adv_col1:
                    inference_steps = st.number_input(
                        "Inference Steps",
                        min_value=1,
                        max_value=50,
                        value=defaults["steps"],
                    )
                with adv_col2:
                    guidance_scale = st.number_input(
                        "Guidance Scale",
                        min_value=0.0,
                        max_value=10.0,
                        value=defaults["guidance"],
                        step=0.5,
                    )
            submitted = st.form_submit_button("🖼️ Generate Image")
            if submitted:
                try:
                    if not prompt:
                        st.error("Please enter a prompt.")
                        return
                    cleaned_prompt = clean_prompt(prompt)
                    if not cleaned_prompt:
                        st.error("Invalid prompt after cleaning, please try again.")
                        return
                    params = {
                        "prompt": cleaned_prompt,
                        "img_size": img_size,
                        "num_inference_steps": inference_steps,
                        "guidance_scale": guidance_scale,
                    }

                    with st.spinner("Generating image..."):
                        try:
                            response = config.api_client.make_request(
                                "generate", method="POST", data=params
                            )
                            image_data = response.content
                            timestamp = datetime.now().isoformat()
                            image_path = config.output_dir / f"image_{timestamp}.png"
                            safe_save_image(image_path, image_data)
                            history = config.history_manager.load()
                            history.append(
                                {
                                    "prompt": cleaned_prompt,
                                    "timestamp": timestamp,
                                    "path": str(image_path),
                                    "parameters": params,
                                }
                            )
                            config.history_manager.save(history)
                            st.success("✨ Image generated successfully!")
                        except Exception as e:
                            st.error(f"❌ Error during generation: {e}")
                except Exception as e:
                    st.error(f"❌ Error during generation: {e}")

    with tab2:
        st.markdown("### API Documentation")
        st.markdown("Complete API documentation for advanced usage and integration.")
        api_docs = load_api_docs()
        st.markdown(f'<div class="api-docs">{api_docs}</div>', unsafe_allow_html=True)

    with tab3:
        st.markdown("### 🔐 Authentication")
        st.markdown("🔑 Your current authentication token:")
        col1, col2 = st.columns([6, 1])
        with col1:
            token_display = st.text_input(
                "Token:",
                value=(
                    config.token
                    if st.session_state.get("show_token", False)
                    else format_token_display(config.token)
                ),
                disabled=True,
                key="token_input",
                label_visibility="collapsed",
            )
        with col2:
            button_label = (
                "Hide" if st.session_state.get("show_token", False) else "Show"
            )
            if st.button(
                button_label,
                use_container_width=True,
                type="secondary",
                key="token_button",
            ):
                st.session_state.show_token = not st.session_state.get(
                    "show_token", False
                )
                st.rerun()

        st.markdown(
            """
        <div class="info-box">
            <p><strong>ℹ️ Note:</strong> This token is required for API requests.</p>
            <p>📖 See the API Documentation tab for usage examples.</p>
        </div>
        """,
            unsafe_allow_html=True,
        )

    st.markdown('<div class="history-section">', unsafe_allow_html=True)
    st.markdown("### 📜 Generation History")
    history = config.history_manager.load()
    search_term = st.text_input("🔍 Search history by prompt")
    if search_term:
        history = [h for h in history if search_term.lower() in h["prompt"].lower()]
    display_history(history)
    st.markdown("</div>", unsafe_allow_html=True)


if __name__ == "__main__":
    config = ImageConfig()
    main()
