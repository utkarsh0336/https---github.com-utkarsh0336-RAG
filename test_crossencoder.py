from sentence_transformers import CrossEncoder

print("Testing CrossEncoder initialization...")

try:
    # Test without device parameter
    model = CrossEncoder('cross-encoder/ms-marco-MiniLM-L-6-v2')
    print("✓ CrossEncoder loaded successfully!")
    
    # Test prediction
    pairs = [
        ["What is the capital of France?", "Paris is the capital of France."],
        ["What is the capital of France?", "Berlin is a city in Germany."]
    ]
    
    scores = model.predict(pairs)
    print(f"✓ Scoring works! Scores: {scores}")
    
    print("\nCrossEncoder is ready to use!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
