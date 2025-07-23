
from transformers import (
    AutoTokenizer,
    AutoModelForSequenceClassification
)
import torch
import torch.nn.functional as F
import os

class SentimentPredictor:
    def __init__(self, local_model_path="fine_tuned_finbert"):
        
        # --- CORRECTED LOGIC ---
        # First, decide which model to use based on whether the local directory exists.
        if os.path.isdir(local_model_path):
            print(f"Found local fine-tuned model at '{local_model_path}'. Loading...")
            model_to_load = local_model_path
            # The label mapping for our fine-tuned model
            self.label_map = {0: 'neutral', 1: 'positive', 2: 'negative'} 
        else:
            print(f"Local model not found at '{local_model_path}'.")
            print("Falling back to pre-trained 'ProsusAI/finbert' from Hugging Face Hub.")
            model_to_load = "ProsusAI/finbert"
            # The label mapping for the default pre-trained model
            self.label_map = {0: 'positive', 1: 'negative', 2: 'neutral'}

        # Now, load the tokenizer and model using the determined path/name
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(model_to_load)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_to_load)
        except Exception as e:
            print(f"An error occurred while loading the model: {e}")
            raise

        # Set up the device (GPU or CPU) and put the model in evaluation mode
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model.to(self.device)
        self.model.eval()
        print(f"Model loaded successfully on device: {self.device}")


    def predict(self, text: str):
        if not text or not isinstance(text, str):
            return {"sentiment": "neutral", "confidence": 1.0}

        # Tokenize the input text
        inputs = self.tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            padding=True,
            max_length=512
        ).to(self.device)

        # Get model predictions
        with torch.no_grad():
            outputs = self.model(**inputs)

        # Convert logits to probabilities
        probs = F.softmax(outputs.logits, dim=-1)
        
        # Get the top prediction
        confidence, predicted_class_id = torch.max(probs, dim=1)
        
        # Map the prediction ID to the sentiment label
        sentiment = self.label_map.get(predicted_class_id.item(), "unknown")

        return {
            "sentiment": sentiment,
            "confidence": confidence.item()
        }

# Example usage for testing the script directly
if __name__ == '__main__':
    predictor = SentimentPredictor()
    sample_text = "The company reported a significant increase in profits this quarter."
    prediction = predictor.predict(sample_text)
    print(f"\n--- Test Prediction ---")
    print(f"Text: '{sample_text}'")
    print(f"Prediction: {prediction}")
    print("-----------------------")
