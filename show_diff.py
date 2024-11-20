import os
import re
from collections import defaultdict

import gradio as gr


def extract_file_info(filename):
    parts = filename.split("_")
    if len(parts) < 2:
        return None, None, None
    model = parts[0]
    timestamp_pattern = r"_(\d{8}_\d{6})"
    hash_pattern = r"_([a-f0-9]{8})_"
    timestamp_match = re.search(timestamp_pattern, filename)
    hash_match = re.search(hash_pattern, filename)
    if not (timestamp_match and hash_match):
        return None, None, None
    prompt = filename[len(model) + 1 :]
    prompt = prompt[: prompt.find(hash_match.group(0))]
    return prompt.strip(), hash_match.group(1), model


def load_image_pairs():
    files = [f for f in os.listdir(".") if f.endswith(".png")]
    groups = defaultdict(lambda: defaultdict(dict))
    models_found = set()
    for file in files:
        prompt, id_hash, model = extract_file_info(file)
        if prompt:
            groups[prompt][id_hash][model] = file
            models_found.add(model)
    return groups, sorted(list(models_found))


def create_interface():
    groups, models = load_image_pairs()
    with gr.Blocks(theme=gr.themes.Default()) as interface:
        gr.Markdown("# Diffusion Model Comparison")
        gr.Markdown(f"### Models detected: {', '.join(models)}")
        with gr.Tabs() as tabs:
            for prompt in sorted(groups.keys()):
                with gr.Tab(prompt):
                    for id_hash in groups[prompt]:
                        gr.Markdown(f"#### Generation ID: {id_hash}")
                        with gr.Row():
                            image_pairs = groups[prompt][id_hash]
                            for model in models:
                                if model in image_pairs:
                                    gr.Image(
                                        value=image_pairs[model],
                                        label=model.upper(),
                                        show_label=True,
                                    )

    return interface


interface = create_interface()
interface.launch(server_name="0.0.0.0", share=True, server_port=9000)
