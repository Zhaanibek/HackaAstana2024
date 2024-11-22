import requests
import json
from deepface import DeepFace
import streamlit as st


class EmotionAnalyzer:
    def __init__(self, api_key):
        self.api_key = api_key
        self.GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
        self.NEGATIVE_EMOTIONS = ['angry', 'sad', 'fear', 'disgust']

    def notify(self, authority, emotion, details):
        """Отправка уведомления о негативной эмоции"""
        st.warning(f"⚠ Уведомление для {authority}: Обнаружена негативная эмоция ({emotion}).")
        st.write(f"  Дополнительные данные: {details}")

    def explain_with_gemini(self, prompt):
        """Запрос к Gemini API"""
        try:
            payload = {
                "contents": [{"parts": [{"text": prompt}]}]
            }
            headers = {"Content-Type": "application/json"}
            response = requests.post(self.GEMINI_URL, json=payload, headers=headers)

            if response.status_code == 200:
                candidates = response.json().get("candidates", [])
                return candidates[0]["content"]["parts"][0]["text"] if candidates else "Нет ответа от Gemini"
            else:
                return f"Ошибка Gemini API: {response.status_code} - {response.text}"
        except Exception as e:
            return f"Ошибка при обращении к Gemini: {str(e)}"

    def analyze_image_emotion(self, image_path):
        """Анализ эмоций на изображении"""
        try:
            # Анализ эмоций с помощью DeepFace
            analysis = DeepFace.analyze(img_path=image_path, actions=['emotion'])

            if analysis:
                result = analysis[0]  # Результаты для первого обнаруженного лица
                dominant_emotion = result['dominant_emotion']

                st.subheader(f"Доминирующая эмоция: {dominant_emotion}")

                # Проверка на негативную эмоцию
                if dominant_emotion in self.NEGATIVE_EMOTIONS:
                    self.notify(
                        authority="Психолога и Командира",
                        emotion=dominant_emotion,
                        details=result
                    )

                # Подготовка промпта для Gemini
                emotions_summary = "\n".join(
                    [f"{emotion}: {score:.2f}%" for emotion, score in result['emotion'].items()]
                )
                gemini_prompt = (
                    f"Я проанализировал изображение. Доминирующая эмоция: {dominant_emotion}. "
                    f"Все вероятности эмоций: \n{emotions_summary}. "
                    f"Объясните, что это может означать и как можно интерпретировать эти данные."
                    f"Все это для предотвращения несчастных случаев в армии, дается и анализируется изображение солдата."
                )

                # Запрос к Gemini
                gemini_response = self.explain_with_gemini(gemini_prompt)
                st.write("**Ответ Gemini:**")
                st.write(gemini_response)

                # Вывод всех эмоций
                st.write("\n**Все эмоции (вероятности):**")
                for emotion, score in result['emotion'].items():
                    st.write(f"  - {emotion.capitalize()}: {score:.2f}%")

                # Вывод информации о лице
                st.write("\n**Регион лица:**")
                st.write(f"  - Координаты: x={result['region']['x']}, y={result['region']['y']}, "
                         f"ширина={result['region']['w']}, высота={result['region']['h']}")
                st.write(f"  - Уверенность в лице: {result['face_confidence']:.2f}")
            else:
                st.write("Лицо не обнаружено на изображении.")

        except Exception as e:
            st.write(f"Произошла ошибка: {str(e)}")


# Использование Streamlit для взаимодействия с пользователем
def main():
    API_KEY = "AIzaSyBZ1P73TqceCvS-0uYUhaZ8Qb7KtGoakuE"  # Замените на ваш API-ключ

    st.title("Анализ эмоций на изображении")
    st.write("Загрузите изображение для анализа эмоций.")

    # Загружаем изображение через Streamlit
    uploaded_file = st.file_uploader("Выберите изображение", type=["jpg", "jpeg", "png"])

    if uploaded_file is not None:
        # Сохраняем изображение в локальной папке
        image_path = "temp_image.jpg"
        with open(image_path, "wb") as f:
            f.write(uploaded_file.getbuffer())

        analyzer = EmotionAnalyzer(API_KEY)
        analyzer.analyze_image_emotion(image_path)


if __name__ == "__main__":
    main()
