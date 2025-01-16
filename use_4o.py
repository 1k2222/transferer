import base64
import glob
import os.path

import pdfplumber
from openai import OpenAI

pdf_file = pdfplumber.open("assets/wiley-trading-giles-peter-jewitt-fx-derivatives-trader-school-2015-wiley.pdf")
openai_client = OpenAI(
    base_url='https://40.chatgptsb.net/v1',
    api_key='sk-GHA4sccxWtn4PWgf0c32B2Aa0cB44fFfB3A20516B2A44c59', timeout=600.0
)


def page_to_images():
    output_path = './assets/raw_pages'
    for i in range(594, 619):
        page = pdf_file.pages[i]
        page.to_image(resolution=300, antialias=True).save(os.path.join(output_path, f'page_{i + 1}.png'))


def img_to_message(path):
    buf = open(path, 'rb').read()
    base64_image = base64.b64encode(buf).decode()
    return {
        "type": "image_url",
        "image_url": {"url": f"data:image/png;base64,{base64_image}"},
    }


def extract_text():
    pages = glob.glob('./assets/raw_pages/page_*.png')
    page_contents = []
    for i, p in enumerate(pages):
        message_content = [
            {
                "type": "text",
                "text": "Here are some continuous pages scanned from a book as image format. "
                        "Each image is one page in the book. "
                        "Extract all the texts and from these pages. "
                        "Then output them in good markdown format. \n\n"
                        "Notes:\n"
                        "\t1. Always remember you should output markdown format text. "
                        "DO NOT output any HTML tags or symbols such as '<br>', '&nbsp'. \n"
                        "\t2. Make sure all the words you output are from the given pages. "
                        "DO NOT output any other hints because I need to use a program to auto process your output.\n"
                        "\t3. DO NOT use code block for plain text. i.e. DO NOT output separators like '```plaintext'. "
            }
        ]
        pages.sort()
        message_content.append(img_to_message(p))
        messages = [
            {
                "role": "user",
                "content": message_content
            }
        ]
        response = openai_client.chat.completions.create(model='gpt-4o', messages=messages)
        usage = response.usage
        page_contents.append(response.choices[0].message.content)
        print(response.choices[0].message.content)
        print(f'[{i + 1}/{len(pages)}]', "input tokens: ", f'{usage.prompt_tokens:,}', "output tokens: ",
              f'{usage.completion_tokens:,}',
              "total tokens: ", f'{usage.total_tokens:,}')
    print("### Final Pages ###")
    print('\n'.join(page_contents))


if __name__ == '__main__':
    extract_text()

