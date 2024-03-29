import json

def read_config_json(filename):
  try:
    with open(filename, 'r') as f:
      config = json.load(f)
  except FileNotFoundError:
    raise FileNotFoundError(f"File not found: {filename}")
  except json.JSONDecodeError:
    raise ValueError(f"Invalid JSON format: {filename}")
  return config

config = read_config_json("config.json")

for apsw_word in config["tool_and_invocation"]["unique_apsw_word"]:
    print(f"APSW word: {apsw_word}")

for bsw_word in config["tool_and_invocation"]["unique_apsw_word"]:
    print(f"BSW word: {bsw_word}")

for integration_layer_word in config["tool_and_invocation"]["unique_apsw_word"]:
    print(f"APSW word: {integration_layer_word}")
  
def get_tool_and_invocation_conf(filename) -> dict:
    config = read_config_json(filename=filename)
    print(config["tool_and_invocation"])
    return config["tool_and_invocation"]

get_tool_and_invocation_conf("config.json")