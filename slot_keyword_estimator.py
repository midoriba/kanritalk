from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.chains import SimpleSequentialChain
from langchain.chains import SequentialChain
from openai.error import AuthenticationError
import os
import json
from logger import log


MODEL_NAME = 'gpt-3.5-turbo'
PROMPT_DIRECTORY = os.path.join(os.path.dirname(__file__), 'prompts')
ESTIMATE_SLOT_VALUE_PROMPT = 'estimate_slot_value_prompt.txt'

class SlotKeywordEstimator:
    def __init__(self) -> None:
        # OPENAI_API_KEYが見つからない場合、APIを使用せずにスロットを埋める
        self.is_llm_enabled = True
        if os.getenv('OPENAI_API_KEY', None) is None:
            log.error('Did not found openai api key.')
            self.is_llm_enabled = False
            return
        # LLMの読み込み
        self.llm = ChatOpenAI(model_name=MODEL_NAME) 
        # プロンプトの読み込み
        self.estimate_slot_value_txt = ''
        with open(os.path.join(PROMPT_DIRECTORY, ESTIMATE_SLOT_VALUE_PROMPT), encoding='utf-8', mode='r') as f:
            self.estimate_slot_value_txt = f.read()

        # チェインの作成
        self.estimate_slot_value_prompt = PromptTemplate(
            input_variables=['slot_value_list', 'example_list', 'user_utterance'],
            template=self.estimate_slot_value_txt
        )
        self.slot_fill_chain = LLMChain(llm=self.llm, prompt=self.estimate_slot_value_prompt, output_key='output_slot_value')
    
    # OPENAI API を使ったスロット値キーワードの推定
    def estimate_slot_keyword(self, user_utterance, slot_value_dic):
        if not self.is_llm_enabled:
            return self.search_slot_keyword(user_utterance, slot_value_dic)
        
        slot_value_list = '\n'.join([f'- {k}' for k in slot_value_dic.keys()])
        example_list = '\n'.join(['\n'.join([f'- {v} -> {k}' for v in l]) for k, l in slot_value_dic.items()])
        
        try:
            response = self.slot_fill_chain({"slot_value_list":slot_value_list, "example_list":example_list, "user_utterance":user_utterance})
            result = response['output_slot_value'].strip()
            return result if result in slot_value_list else None
        except AuthenticationError:
            log.error('Incorrect API key provided.')
            self.is_llm_enabled = False
            return self.search_slot_keyword(user_utterance, slot_value_dic)
    
    # APIを使わずに探索でスロット値を埋める
    def search_slot_keyword(self, user_utterance, slot_value_dic):
        for key, value in slot_value_dic.items():
            if any([True if word in user_utterance else False for word in value]):
                return key
        return None
        
    def _load_json(self, path) -> dict:
        with open(path, "r", encoding="utf-8_sig") as f:
            return json.load(f)
    
if(__name__ == '__main__'):
    sve = SlotKeywordEstimator()
    dic = sve._load_json('rules/NLU/slot_value.json')['weather']['type_detail']
    user_utterance = '夕立でした'
    print(f'"{user_utterance}" -> "{sve.estimate_slot_keyword(user_utterance, dic)}"')
    slot_value_list = '\n'.join([f'- {k}' for k in dic.keys()])
    example_list = '\n'.join(['\n'.join([f'- {v} -> {k}' for v in l]) for k, l in dic.items()])
    print(sve.estimate_slot_value_prompt.format(slot_value_list=slot_value_list, example_list=example_list, user_utterance=user_utterance))