from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

class ModelController:
    def __init__(self, model_name: str):
        self._tokenizer = AutoTokenizer.from_pretrained(model_name)
        self._model = AutoModelForCausalLM.from_pretrained(model_name, cache_dir=os.environ.get("CACHE_DIR"))

        self._device = "cuda" if torch.cuda.is_available() else "cpu"
        self._model.to(self._device)
        self._model.eval()
    
    def form_prompt(self, question: str) -> str:
        """Формирование промпта для модели на основании переданного вопроса
        
        Keyword arguments:
        \tquestion -- текст запроса
        Return:
        \tСформированный промпт
        """
        # NOTE: Пока для промпта используется тестовая заглушка
        
        # Контекст для модели
        context_text = """

Это был человек лет тридцати двух-трех от роду, среднего роста, приятной наружности, с темно-серыми глазами, но с отсутствием всякой определенной идеи, всякой сосредоточенности в чертах лица. Мысль гуляла вольной птицей по лицу, порхала в глазах, садилась на полуотворенные губы, пряталась в складках лба, потом совсем пропадала, и тогда во всем лице теплился ровный свет беспечности. С лица беспечность переходила в позы всего тела, даже в складки шлафрока.
        """

        prompt = f"Прочитай текст ниже и ответь на вопрос по нему.\n\nТекст:\n{context_text}\n\nВопрос: {question}\nОтвет:"

        return prompt

    def generate(self, prompt: str, max_new_tokens=50, temperature=0.7, top_k=50, top_p=0.95):
        """Сгенерировать моделью ответ на промпт
        
        Keyword arguments:
        \tprompt -- промпт
        \t[max_new_tokens, temperature, top_k, top_p] -- параметры модели (опционально)
        Return: 
        \tОтвет, сгенерированный моделью
        """
        
        inputs = self._tokenizer.encode(prompt, return_tensors="pt").to(self._device)
        outputs = self._model.generate(
            inputs,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            top_k=top_k,
            top_p=top_p,
            do_sample=True,
            eos_token_id=self._tokenizer.eos_token_id,
            pad_token_id=self._tokenizer.eos_token_id,
            no_repeat_ngram_size=2,
        )

        prompt_length = inputs.shape[1]  # Длина промпта в токенах
        response_tokens = outputs[0][prompt_length:] # Обрезаем промпт

        text = self._tokenizer.decode(response_tokens, skip_special_tokens=True)
        return text

