from transformers import AutoModelForSequenceClassification, AutoTokenizer
import torch

# GPU가 사용 가능한지 확인(mac 기준)
device = "mps" if torch.backends.mps.is_available() else "cpu"

# 저장된 모델과 토크나이저 불러오기
model = AutoModelForSequenceClassification.from_pretrained(
    "./reviews/sentiment_analysis_model", use_safetensors=True
)
tokenizer = AutoTokenizer.from_pretrained("./reviews/sentiment_analysis_model")

# 모델을 GPU로 이동 없으면 cpu로 진행
model.to(device)


# 모델로 예측하기
def predict(text):
    """
    예측이 1이면 긍정, 0이면 부정
    """
    # 텍스트를 토큰화하고 GPU로 이동
    inputs = tokenizer(text, return_tensors="pt").to(device)

    # 모델을 평가 모드로 전환
    model.eval()

    with torch.no_grad():  # 그래디언트 계산 비활성화
        outputs = model(**inputs)
        logits = outputs.logits
        predictions = torch.argmax(logits, dim=-1)  # 예측 결과
    return predictions.item()  # 예측 결과 반환
