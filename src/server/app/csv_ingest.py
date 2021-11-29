import pandas
import numpy
from typing import List
from transformers import GPT2Tokenizer
from transformers import BertTokenizer
from transformers import BertModel
from transformers import OpenAIGPTTokenizer


def convert_bp_encoded_fields(value: str) -> List[int]:
    return [int(x.strip('[] ')) for x in value.split(',')]


def IngestPpData(path: str) -> pandas.DataFrame:
    # tokenizer = BertTokenizer.from_pretrained('bert-base-uncased', do_lower_case=True)
    tokenizer = OpenAIGPTTokenizer.from_pretrained('openai-gpt')
    pp_recipes_df = pandas.read_csv(path,
                                    converters={
                                        "name_tokens":
                                        convert_bp_encoded_fields,
                                        "ingredient_tokens":
                                        convert_bp_encoded_fields,
                                        "steps_tokens":
                                        convert_bp_encoded_fields,
                                    })
    print("PP Recipes DF\n{}\n{}".format(pp_recipes_df.columns, pp_recipes_df))
    print("PP Recipes DF name_tokens {}".format(
        pp_recipes_df['name_tokens'].iloc[:10].values.flatten().tolist()))
    # print("PP Recipes DF name_tokens2 {} {}".format(type(pp_recipes_df['name_tokens'].iloc[0]), pp_recipes_df['name_tokens'].iloc[0]))
    test = [
        tokenizer.decode(x)
        for x in pp_recipes_df['name_tokens'].iloc[:20].values
    ]
    print("Tokenizer output{}".format(test))
    # pp_recipes_df['name_tokens', 'ingredient_tokens', 'steps_tokens'].apply(tokenizer.decode(x))
    pp_recipes_df['name_tokens'] = pp_recipes_df['name_tokens'].apply(
        tokenizer.decode)
    pp_recipes_df.sort_values(['name_tokens'], inplace=True)
    print("PP Recipes DF name_tokens2 {} {}".format(
        type(pp_recipes_df['name_tokens'].iloc[0]),
        pp_recipes_df['name_tokens'].iloc[:20]))

    return pp_recipes_df


def IngestRawData(path: str) -> pandas.DataFrame:
    raw_recipes_df = pandas.read_csv(path)
    raw_recipes_df.sort_values(['name'], inplace=True)
    print("RAW Recipes DF name {} {}".format(
        type(raw_recipes_df['name'].iloc[0]),
        raw_recipes_df['name'].iloc[:20]))
    print("RAW Recipes DF description {} {}".format(
        type(raw_recipes_df['description'].iloc[0]),
        raw_recipes_df[['name',
                        'description']].iloc[:5].values.flatten().tolist()))
    print("RAW Recipes DF steps {} {}".format(
        type(raw_recipes_df['steps'].iloc[0]),
        raw_recipes_df['steps'].iloc[:5].values.tolist()))
    print("RAW Recipes DF\n{}\n{}".format(raw_recipes_df.columns,
                                          raw_recipes_df))
    return raw_recipes_df
