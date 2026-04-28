from ..loader import load_model  # your new loader


def load_cunny_model(model_name, variant="", push_constant_size=0):
    return load_model(model_name, variant, push_constant_size)
