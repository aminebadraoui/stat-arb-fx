import json

def dump_json(data, filename):
    json_object = json.dumps(data, indent=4)

    # Writing to sample.json
    with open(f"{filename}.json", "w") as outfile:
        outfile.write(json_object)
