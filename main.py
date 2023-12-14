import os
import base64
import io
from openai import OpenAI
from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageFont


load_dotenv()
OPENAI_SECRET_KEY = os.getenv('OPENAI_SECRET_KEY')

PROMPT = """
Hey, here a couple screenshots of a section from a webpage. Each section has the same content but is designed a bit differently. Sections files are labelled "A", "B", "C" and "D".

Only one of the sections is correctly and cleanly designed, the rest have some obvious design flaws. Tell me which one is correct.

Start your answer with "A", "B", "C" or "D", then give me your reasoning."""

# PROMPT = """"
# Hey, here a couple screenshots of a section from a webpage. Each section has the same content but is designed a bit differently. Sections files are labelled "A", "B", "C" and "D".
#
# Can you tell me what Section "A" show?"""

def encode_image(image_path):
  with open(image_path, "rb") as image_file:
    return base64.b64encode(image_file.read()).decode('utf-8')


def main():
    print("Initializing OpenAI client...")
    client = OpenAI(api_key=OPENAI_SECRET_KEY)

    print("Printing labels on images...")
    imageA = getImageWithLabel("Section A:", "./data/screenshots/1/A.png")
    imageB = getImageWithLabel("Section B:", "./data/screenshots/1/B.png")
    imageC = getImageWithLabel("Section C:", "./data/screenshots/1/C.png")
    imageD = getImageWithLabel("Section D:", "./data/screenshots/1/D.png")

#     imageA.save("A.png")
#     imageB.save("B.png")
#     imageC.save("C.png")
#     imageD.save("D.png")

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

    print(response.choices[0].message.content)


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

