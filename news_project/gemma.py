from transformers import AutoTokenizer, AutoModelForCausalLM, BitsAndBytesConfig
import torch
from typing import List, Dict, Optional


class ChatModel:
    def __init__(self, model_name: str = "google/gemma-3-12b-it-qat-int4-unquantized", local_files_only: bool = True):
        """
        Initialize the chat model with quantization and safety settings.

        Args:
            model_name: Name/path of the model to load
            local_files_only: Whether to use only local files
        """
        self.tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=local_files_only)

        # Configure 4-bit quantization for efficient inference
        quant_config = BitsAndBytesConfig(
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
            bnb_4bit_compute_dtype=torch.bfloat16
        )

        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            local_files_only=local_files_only,
            device_map="auto",
            attn_implementation="sdpa",  # Use efficient attention
            quantization_config=quant_config,
            torch_dtype=torch.bfloat16,
            low_cpu_mem_usage=True
        ).eval()

        # Set pad token if not set
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

    def generate_response(
            self,
            prompt: str,
            max_new_tokens: int = 1024,
            temperature: float = 0.7,
            top_p: float = 0.9,
            do_sample: bool = True
    ) -> str:
        """
        Generate a response to the given prompt.

        Args:
            prompt: Input text prompt
            max_new_tokens: Maximum number of tokens to generate
            temperature: Sampling temperature (lower = more deterministic)
            top_p: Nucleus sampling probability threshold
            do_sample: Whether to use sampling

        Returns:
            Generated response text
        """
        # Tokenize input
        inputs = self.tokenizer(
            prompt,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=1024
        ).to(self.model.device)

        # Generate response
        with torch.no_grad():
            outputs = self.model.generate(
                **inputs,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                do_sample=do_sample,
                pad_token_id=self.tokenizer.pad_token_id
            )

        # Decode and clean up response
        response = self.tokenizer.decode(
            outputs[0][inputs.input_ids.shape[1]:],
            skip_special_tokens=True
        ).strip()

        return response

    def chat(self, conversation: Optional[List[Dict[str, str]]] = None) -> str:
        prompt = self.tokenizer.apply_chat_template(
                    conversation,
                    tokenize=False,
                    add_generation_prompt=True
                )

        # Generate response
        response = self.generate_response(prompt)
        print(f"Assistant: {response}")

def get_article(topic="not_stated"):
    chat_model = ChatModel()

    # Single prompt example
    prompt = (
        f"Ты — креативная модель новостного агентства «Шуточные Известия». Твоя задача — придумывать короткие юмористические новости в формате:"

        "Заголовок: Краткий, цепкий и ироничный заголовок (не более 8–10 слов).  "
        "Статья: Несколько предложений с лёгкой (или не очень легкой) сатирой и абсурдом, развивающими идею заголовка."

        "Примеры выходных сообщений:"
        "⚡️ «КитКат, Кола и доллар по 30». Стали известны требования российской делегации в Стамбуле  "
        "Росатом сокращает сотрудников на 30%. Стало известно, что их место займут гномы "
        "⚡️ АвтоВАЗ показал, как не будут выглядеть его автомобили"

        "Инструкции:"
        "1. Всегда начинай с «Заголовок:», затем текст заголовка.  "
        "2. После заголовка ставь перевод строки и «Статья:», а далее — сам текст статьи.  "
        "3. Используй современную тематику, известные бренды или события, но добавляй «изюминку» абсурда (гномы, говорящие коты, внезапные требования и т. д.).  "
        "4. Длина статьи — 2–4 предложения.  "
        "5. Не используй цитаты реальных людей; вымышленные диалоги и комментарии приветствуются.  "
        "6. Сохраняй лёгкий, ироничный тон."

        "Теперь сгенерируй такую новость:")

    response = chat_model.generate_response(prompt)
    print(response)

if __name__ == "__main__":
    # Example usage

