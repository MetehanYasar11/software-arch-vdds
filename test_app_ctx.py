from app import create_app
app = create_app()
with app.app_context():
    from app.detection import get_current_model_filename, get_available_models
    print('Available models:', get_available_models())
    print('Current model:', get_current_model_filename())
