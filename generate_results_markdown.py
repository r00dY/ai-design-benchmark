import json

results_json_path = 'results/data.json'

def loadResults():
    with open(results_json_path, 'r') as file:
        data = json.load(file)
        return data


def changeStringToQuote(original_string):
    lines = original_string.splitlines()

    # Prepending "> " to each line
    quoted_lines = [f"> {line}" for line in lines]

    # Joining the lines back together
    return "\n".join(quoted_lines)


def main():
    data = loadResults()

    resultMarkdown = ""

    for index, result in enumerate(data):
        resultMarkdown = resultMarkdown + f"""
### Example {index + 1 }

- {result['resultStatus']} {"❌" if result['resultStatus'] == 'wrong' else "✅"}
- correct answer: {result['correctAnswer']}
- AI answer: {result['realAnswer']}

Reasoning:
{ changeStringToQuote(result['reasoning']) }

![image A](./results/screenshots/{index}/A.png)
![image B](./results/screenshots/{index}/B.png)
![image C](./results/screenshots/{index}/C.png)
![image D](./results/screenshots/{index}/D.png)
"""

    print(resultMarkdown)

if __name__ == "__main__":
    main()

