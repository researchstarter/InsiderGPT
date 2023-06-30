import json, os, sys
import datetime, time


def main(file_name):

    with open(file_name, "r") as f:
        logs = json.load(f)
    user_inputs = logs["user"]
    bot_responses = logs["insiderGPT"]
    merged_list = [[user_input[0], user_input[1], "user"] for user_input in user_inputs]
    merged_list.extend(
        [bot_response[0], bot_response[1], "insiderGPT"]
        for bot_response in bot_responses
    )
    merged_list.sort(key=lambda x: x[0])


    output = ""
    for element in merged_list:

        timestamp = datetime.datetime.fromtimestamp(int(element[0])).strftime(
            "%Y-%m-%d %H:%M:%S"
        )
        output += f"{timestamp} [{element[2]}]: {element[1]}\n"

        if element[2] == "insiderGPT":
            output += "----------------------------------------\n\n"

    print("Conversation log: ")

    print(output)


if __name__ == "__main__":

    if len(sys.argv) == 1:
        file_name = "logs/sample_insiderGPT_log.txt"
    else:
        file_name = sys.argv[1]
    main(file_name)
