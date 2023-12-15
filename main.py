import os
import base64
import io
import random
import json
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont


load_dotenv()
OPENAI_SECRET_KEY = os.getenv('OPENAI_SECRET_KEY')

PROMPT = """
Hey, here a couple screenshots of a section from a webpage. Each section has the same content but is designed a bit differently. Sections are labelled "A", "B", "C" and "D".

Only one of the sections is correctly and cleanly designed, the rest have some obvious design flaws. Tell me which one is correct.

Please make the first 2 characters of your answer #A, #B, #C or #D depending on which section you think is correctly designed. This is SUPER IMPORTANT. After that you can give your reasoning.
"""


MAX_CORRECT_ITERATIONS = 4
MAX_TOTAL_ITERATIONS = 12

def main():
    print("Initializing OpenAI client...")
    client = OpenAI(api_key=OPENAI_SECRET_KEY)

    results = []

    for dataset_index in range(12):
        print(f"######### DATASET ENTRY {dataset_index} #########")

        path_prefix = f"./data/screenshots/{dataset_index}"

        correctIterationIndex = 0

        for iterationIndex in range(0, MAX_TOTAL_ITERATIONS):

            print("--------------------")
            print(f"Iteration number: {iterationIndex + 1}")


            indexes = [0, 1, 2, 3]
            random.shuffle(indexes)

            if (indexes[0] == 0):
                correctAnswer = "A"
            elif (indexes[1] == 0):
                correctAnswer = "B"
            elif (indexes[2] == 0):
                correctAnswer = "C"
            elif (indexes[3] == 0):
                correctAnswer = "D"

            print("Printing labels on images...")

            imageA = getImageWithLabel("Section A:", f"{path_prefix}/{indexes[0]}.png")
            imageB = getImageWithLabel("Section B:", f"{path_prefix}/{indexes[1]}.png")
            imageC = getImageWithLabel("Section C:", f"{path_prefix}/{indexes[2]}.png")
            imageD = getImageWithLabel("Section D:", f"{path_prefix}/{indexes[3]}.png")

            print("Calling API...")
            response = client.chat.completions.create(
                model="gpt-4-vision-preview",
                max_tokens=2048,
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": PROMPT
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{imageToBase64(imageA)}",
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{imageToBase64(imageB)}",
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{imageToBase64(imageC)}",
                                    "detail": "high"
                                }
                            },
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{imageToBase64(imageD)}",
                                    "detail": "high"
                                }
                            }
                        ]
                    },
                ]
            )

            parsedResponse = parseResponse(response.choices[0].message.content)

            if (parsedResponse == None):
                if (iterationIndex == MAX_TOTAL_ITERATIONS - 1):
                    results.append({
                        "resultStatus": "error"
                    })
                    print("ERROR")

            else:
                realAnswer = parsedResponse[0]
                reasoning = parsedResponse[1]

                if ((realAnswer == correctAnswer and correctIterationIndex == (MAX_CORRECT_ITERATIONS - 1)) or realAnswer != correctAnswer):
                    resultStatus = "correct" if correctAnswer == realAnswer else "wrong"

                    print("Result: " + resultStatus)

                    output_path_prefix = path_prefix.replace("data", "results")

                    os.makedirs(output_path_prefix, exist_ok=True)

                    imageA.save(f"{output_path_prefix}/A.png")
                    imageB.save(f"{output_path_prefix}/B.png")
                    imageC.save(f"{output_path_prefix}/C.png")
                    imageD.save(f"{output_path_prefix}/D.png")

                    results.append({
                       "resultStatus": resultStatus,
                       "correctAnswer": correctAnswer,
                       "realAnswer": realAnswer,
                       "reasoning": reasoning,
                       "try": correctIterationIndex + 1
                    })

                    break

                correctIterationIndex += 1

    json_string = json.dumps(results, indent=4)

    with open('results/data.json', 'w') as file:
        file.write(json_string)




def parseResponse(response):
    if response and response[0] == '#' and response[1] in ('A', 'B', 'C', 'D'):
        return (response[1], response[2:])
    else:
        return None


def getImageWithLabel(label, image_path):

    # Load the image
    image = Image.open(image_path)

    imageWithExtraSpace = Image.new('RGB', (image.width, image.height + 100), 'black')
    imageWithExtraSpace.paste(image, (0, 100))

    # Initialize the drawing context with the image as background
    draw = ImageDraw.Draw(imageWithExtraSpace)

    # Specify the font and size (optional, if you want a specific font style)
    font = ImageFont.truetype('./data/Inter-Regular.ttf', size=36)

    # Position for the label
    (x, y) = (25, 25)

    # Text color
    color = 'rgb(255,255,255)'

    # Add text to image
    draw.text((x, y), label, fill=color, font=font)

    return imageWithExtraSpace

def imageToBase64(image):
    # Create a buffer
    buffer = io.BytesIO()

    # Save image to buffer
    image.save(buffer, format='PNG')  # Use the appropriate format

    # Convert buffer contents to base64
    encoded_image = base64.b64encode(buffer.getvalue())

    # Decode bytes to string if necessary
    return encoded_image.decode()



if __name__ == "__main__":
    main()

