MODEL_CONFIGS = {
    "sd2": {
        "default_steps": 50,
        "default_guidance": 7.5,
        "min_img_size": 512,
        "max_img_size": 768,
        "default": False,
    },
    "sdxl": {
        "default_steps": 25,
        "default_guidance": 7.5,
        "min_img_size": 512,
        "max_img_size": 1024,
        "default": False,
    },
    "flux": {
        "default_steps": 4,
        "default_guidance": 0.0,
        "min_img_size": 256,
        "max_img_size": 1024,
        "default": False,
    },
    "sdxl-turbo": {
        "default_steps": 1,
        "default_guidance": 0.0,
        "min_img_size": 512,
        "max_img_size": 1024,
        "default": False,
    },
    "sdxl-lightning": {
        "default_steps": 4,
        "default_guidance": 0.0,
        "min_img_size": 512,
        "max_img_size": 1024,
        "default": True,
    },
}